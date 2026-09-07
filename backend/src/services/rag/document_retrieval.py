from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.models import SearchParams, ScoredPoint
from typing import List, Tuple, Dict, Any

from services.rag.llm import generationModel

qdrant = QdrantClient(host="qdrant", port=6333)


class queryRetrieval:
    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        reranker_name: str = "BAAI/bge-reranker-base",
        collection_name: str = "documents",
    ):
        self.model = SentenceTransformer(model_name)
        self.reranker = CrossEncoder(reranker_name)
        self.collection_name = collection_name

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

    def dense_search(self, query: str, k: int = 10) -> List[ScoredPoint]:
        """Single dense-vector search. Rename/extend to hybrid_search if you
        later add a sparse (BM25/SPLADE) leg and fuse the two result sets."""
        query_vector = self.embed_query(query)

        response = qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=k,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False,
            ),
        )
        return response.points

    def rerank(
        self,
        query: str,
        results: List[ScoredPoint],
        top_k: int = 5,
    ) -> List[Tuple[ScoredPoint, float]]:
        if not results:
            return []

        pairs = [[query, r.payload.get("text", "")] for r in results]
        scores = self.reranker.predict(pairs)

        reranked = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return reranked[:top_k]

    def retrieve(
        self,
        query: str,
        k: int = 10,
    ) -> List[Dict[str, Any]]:
        candidates = self.dense_search(query, k=k)
        top_docs = self.rerank(query=query, results=candidates)

        return [
            {
                "text": doc.payload.get("text", ""),
                "source": doc.payload.get("source", "unknown"),
                "score": float(score),
                "id": doc.id,
            }
            for doc, score in top_docs
        ]

    def answer(self, query: str):
        generation = generationModel()

        # 1. Rephrase query — already returns a plain string
        rewritten_query = generation.rephrase_query(query)

        # 2. Retrieve + rerank
        retrieved = self.retrieve(rewritten_query)

        # 3. Build context string
        context_text = "\n\n".join(doc["text"] for doc in retrieved)

        # 4. Build prompt
        prompt = generation.build_prompt(
            query=rewritten_query,
            context=context_text,
        )

        # 5. Return streaming generator
        return generation.generate_ollama(prompt)