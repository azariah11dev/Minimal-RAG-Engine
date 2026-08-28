import os
import re
import uuid
from typing import List
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from schemas.env_schema import settings

qdrant_url = settings.QDRANT_URL or os.getenv("QDRANT_URL")
qdrant = QdrantClient(url=qdrant_url, check_compatibility=False)


class documentHandler:
    def __init__(
        self, 
        file_path: str, 
        file_name: str, 
        model_name: str = "BAAI/bge-m3",
        max_chunk_size=1000, 
        overlap=200
    ):
        self.file_path = file_path
        self.file_name = file_name
        # Loads BAAI/bge-m3 (1024-dim, 8192 token context window)
        self.model = SentenceTransformer(model_name)
        #Splitting info
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    # ------------------------------------------------------------------
    # Document Readers (Preserving structure where possible)
    # ------------------------------------------------------------------
    def read_text(self) -> str:
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def read_pdf(self) -> str:
        try:
            reader = PdfReader(self.file_path)
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)
            return "\n\n".join(pages_text)
        except Exception as e:
            print(f"Error reading PDF {self.file_path}: {e}")
            return ""

    def read_docx(self) -> str:
        try:
            doc = Document(self.file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            print(f"Error reading DOCX {self.file_path}: {e}")
            return ""

    # ------------------------------------------------------------------
    # Modern Chunking: Sentence & Paragraph Boundary Awareness
    # ------------------------------------------------------------------
    # ------------------------------------------------------------
    # 1. Naive fallback splitter (character-based)
    # ------------------------------------------------------------
    def naive_split(self, text: str) -> List[str]:
        """Split a huge sentence/paragraph into smaller overlapping chunks."""
        chunks = []
        step = self.max_chunk_size - self.overlap

        for i in range(0, len(text), step):
            chunk = text[i : i + self.max_chunk_size]
            chunks.append(chunk)

        return chunks

    # ------------------------------------------------------------
    # 2. Recursive paragraph/sentence splitter
    # ------------------------------------------------------------
    def split_paragraph(self, paragraph: str) -> List[str]:
        """Split a paragraph recursively if it exceeds max size."""
        # Base case: fits
        if len(paragraph) <= self.max_chunk_size:
            return [paragraph]

        # Try sentence-level splitting
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)

        # If splitting produced multiple sentences, process each
        if len(sentences) > 1:
            result = []
            current_chunk = []
            current_length = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # If sentence itself is huge → fallback split
                if len(sentence) > self.max_chunk_size:
                    result.extend(self.naive_split(sentence))
                    continue

                # If adding sentence exceeds chunk size → commit
                if current_length + len(sentence) > self.max_chunk_size and current_chunk:
                    result.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0

                current_chunk.append(sentence)
                current_length += len(sentence)

            # Commit last chunk
            if current_chunk:
                result.append(" ".join(current_chunk))

            return result

        # Fallback: naive split
        return self.naive_split(paragraph)

    # ------------------------------------------------------------
    # 3. Full semantic chunker
    # ------------------------------------------------------------
    def semantic_chunk(self, text: str) -> List[str]:
        """Split text into semantic chunks with overlap."""
        paragraphs = text.split("\n\n")

        # Step A: Flatten huge paragraphs
        flat_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            flat_paragraphs.extend(self.split_paragraph(p))

        # Step B: Build chunks
        chunks = []
        current_chunk = []
        current_length = 0

        for p in flat_paragraphs:
            if current_length + len(p) > self.max_chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))

                # Overlap logic
                if len(current_chunk[-1]) < self.overlap:
                    current_chunk = [current_chunk[-1]]
                    current_length = len(current_chunk[0])
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(p)
            current_length += len(p)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    # ------------------------------------------------------------------
    # Batch Embedding Generation
    # ------------------------------------------------------------------
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Encodes an array of texts in a single forward pass."""
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32
        )
        return vectors.tolist()

    # ------------------------------------------------------------------
    # Production Qdrant Batch Ingestion
    # ------------------------------------------------------------------
    def ingest_into_qdrant(
        self, 
        collection_name: str, 
        document_text: str,
        batch_size: int = 64
    ) -> None:
        if not document_text:
            return

        # 1. Chunk document
        chunks = self.semantic_chunk(document_text)
        if not chunks:
            return

        # 2. Get dimensionality dynamically
        sample_vec = self.embed_batch(["sample"])[0]
        vector_dim = len(sample_vec)

        # 3. Create collection safely if missing (recreate_collection is DESTRUCTIVE)
        if not qdrant.collection_exists(collection_name):
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_dim,
                    distance=Distance.COSINE
                )
            )

        # 4. Generate embeddings for all chunks in batch
        embeddings = self.embed_batch(chunks)

        # 5. Build PointStruct list with UUIDs and audit metadata
        points = []
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": chunk,
                        "source": self.file_name,
                        "chunk_index": idx,
                        "total_chunks": len(chunks)
                    }
                )
            )

        # 6. Upsert in batches to prevent memory spikes and API thrashing
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            qdrant.upsert(collection_name=collection_name, points=batch)

    # ------------------------------------------------------------------
    # Orchestration Entry Point
    # ------------------------------------------------------------------
    def process_and_ingest(self, collection_name: str = "documents") -> str:
        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == ".txt":
            content = self.read_text()
        elif ext == ".pdf":
            content = self.read_pdf()
        elif ext == ".docx":
            content = self.read_docx()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        self.ingest_into_qdrant(collection_name=collection_name, document_text=content)
        return content
