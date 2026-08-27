import os
import numpy as np
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from src.schemas.env_schema import settings

qdrant_url = settings.QDRANT_URL or os.getenv("QDRANT_URL")
qdrant = QdrantClient(url=qdrant_url, check_compatibility=False)

class documentHandler:
    def __init__(
            self, 
            file_path, 
            file_name, 
            model_name="all-MiniLM-L6-v2"
    ):
        
        self.file_path = file_path
        self.file_name = file_name
        self.model = SentenceTransformer(model_name)

    def load_txt(self) -> str:
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def read_pdf(self):
        try:
            reader = PdfReader(self.file_path)
            text = []
            for page in reader.pages:
                extracted = page.extract_text() or ""
                text.append(extracted)
            return "\n".join(text)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    def load_docx(self):
        try:
            doc = Document(self.file_path)
            paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(paragraphs)
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return None

    def naive_chunk(self, text: str, size: int = 500, overlap_ratio: float = 0.2):
        chunks = []
        overlap = int(size * overlap_ratio)
        step = size - overlap

        for i in range(0, len(text), step):
            chunk = text[i : i + size]
            chunks.append(chunk)

        return chunks

    def embed(self, text: str):
        vec = self.model.encode(
            text,
            normalize_embeddings=True  # important for cosine similarity
        )
        return vec.astype("float32")

    def ingest_into_qdrant(self, collection_name, docs):
        # Determine vector dimension dynamically
        sample_vec = self.embed("sample text")
        vector_dim = len(sample_vec)

        # Create collection if it doesn't exist
        if not qdrant.has_collection(collection_name):
            qdrant.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                size=vector_dim,
                distance=Distance.COSINE
                )
            )

        # Insert chunks
        for doc in docs:
            chunks = self.naive_chunk(doc)
            for chunk in chunks:
                vector = self.embed(chunk)
                point = PointStruct(
                    id=None,  # auto-ID
                    vector=vector.tolist(),
                    payload={
                        "text": chunk,
                        "source": self.file_name
                    }
                )
            qdrant.upsert(collection_name=collection_name, points=[point])

    def load_document(self) -> str:
        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == ".txt":
            self.ingest_into_qdrant(collection_name="documents", docs=[self.load_txt()])
            return self.load_txt()
        elif ext == ".pdf":
            self.ingest_into_qdrant(collection_name="documents", docs=[self.read_pdf()])
            return self.read_pdf()
        elif ext == ".docx":
            self.ingest_into_qdrant(collection_name="documents", docs=[self.load_docx()])
            return self.load_docx()
        else:
            raise ValueError(f"Unsupported file type: {ext}")