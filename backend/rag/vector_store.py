"""
backend/rag/vector_store.py
----------------------------
ChromaDB-backed vector store with sentence-transformer embeddings.
Supports indexing PDF chunks and Exa search results for RAG retrieval.
"""

from __future__ import annotations

import hashlib
import time
from typing import List

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from backend.core.config import settings
from backend.tools.pdf_processor import PDFDocument
from backend.utils.logger import logger


class VectorStore:
    _model: SentenceTransformer | None = None

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._col = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"VectorStore ready — {self._col.count()} existing chunks.")

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            cls._model = SentenceTransformer(settings.embedding_model)
        return cls._model

    def _embed(self, texts: List[str]) -> List[List[float]]:
        return self._get_model().encode(texts, show_progress_bar=False).tolist()

    # ── Indexing ───────────────────────────────────────────────

    def index_pdf(self, doc: PDFDocument) -> int:
        if not doc.chunks:
            return 0
        ids = [f"{doc.file_hash}_{i}" for i in range(len(doc.chunks))]
        existing = set(self._col.get(ids=ids, include=[])["ids"])
        new_ids = [i for i in ids if i not in existing]
        if not new_ids:
            logger.info(f"{doc.filename} already indexed.")
            return 0
        idx_map = {id_: i for i, id_ in enumerate(ids)}
        new_chunks = [doc.chunks[idx_map[id_]] for id_ in new_ids]
        self._col.add(
            ids=new_ids,
            embeddings=self._embed(new_chunks),
            documents=new_chunks,
            metadatas=[{"source": doc.filename, "chunk": idx_map[id_]} for id_ in new_ids],
        )
        logger.info(f"Indexed {len(new_ids)} new chunks from {doc.filename}.")
        return len(new_ids)

    def index_texts(self, texts: List[str], source: str = "exa_search") -> None:
        if not texts:
            return
        base = hashlib.md5(f"{source}{time.time()}".encode()).hexdigest()[:8]
        ids = [f"{base}_{i}" for i in range(len(texts))]
        self._col.add(
            ids=ids,
            embeddings=self._embed(texts),
            documents=texts,
            metadatas=[{"source": source, "chunk": i} for i in range(len(texts))],
        )

    # ── Retrieval ──────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        if self._col.count() == 0:
            return []
        results = self._col.query(
            query_embeddings=self._embed([query]),
            n_results=min(top_k, self._col.count()),
            include=["documents"],
        )
        return results.get("documents", [[]])[0]

    def clear(self) -> None:
        self._client.delete_collection(settings.chroma_collection_name)
        self._col = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("VectorStore cleared.")

    @property
    def doc_count(self) -> int:
        return self._col.count()


# Singleton shared across the application
_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
