"""
Retriever for property documents stored in Chroma.

This module connects:
- `Embedder` (to embed the user's query)
- `ChromaOperator` (to query the persistent Chroma collection)

It is intended to be used by higher-level agents (e.g. the Must agent) as the
R in a simple RAG pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.database.embedder import Embedder
from core.database.vectorstore.prop_chroma import ChromaOperator


@dataclass
class RetrievedProperty:
    text: str
    metadata: Dict[str, Any]
    score: Optional[float]


class PropertyRetriever:
    """
    Thin wrapper around `Embedder` + `ChromaOperator` for property RAG.
    """

    def __init__(
        self,
        *,
        location: str,
        collection_name: str,
        embedder: Optional[Embedder] = None,
        chroma: Optional[ChromaOperator] = None,
    ) -> None:
        # Use the same embedding model you used when indexing properties
        self.embedder = embedder or Embedder("gemini-embedding-001")
        self.chroma = chroma or ChromaOperator(location=location, collection_name=collection_name)

    def retrieve(self, query: str, n_results: int = 5) -> List[RetrievedProperty]:
        """
        Embed the query string and retrieve the top-N most similar properties.
        """
        query = (query or "").strip()
        if not query:
            return []

        query_vectors = self.embedder.embed_texts([query])
        if not query_vectors:
            return []

        collection = self.chroma.collection
        results = collection.query(
            query_embeddings=query_vectors,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        docs_lists = results.get("documents", [])
        metas_lists = results.get("metadatas", [])
        dists_lists = results.get("distances", [])

        if not docs_lists:
            return []

        docs = docs_lists[0]
        metas = metas_lists[0] if metas_lists else [{} for _ in docs]
        dists = dists_lists[0] if dists_lists else [None for _ in docs]

        retrieved: List[RetrievedProperty] = []
        for text, meta, dist in zip(docs, metas, dists):
            score: Optional[float]
            try:
                score = float(dist) if dist is not None else None
            except (TypeError, ValueError):
                score = None

            retrieved.append(
                RetrievedProperty(
                    text=text,
                    metadata=meta or {},
                    score=score,
                )
            )

        return retrieved

