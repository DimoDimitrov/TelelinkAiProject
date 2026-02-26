"""
This file's purpose is to define the ChromaDB vector store that will be used
for the properties (and others if needed).
"""

from typing import Any, Dict, Iterable, List, Optional

import chromadb
# from sentence_transformers import SentenceTransformer  # Kept for future use


class ChromaOperator:
    """
    Thin wrapper around a persistent ChromaDB client and a single collection.

    - `location` controls where ChromaDB persists data on disk.
    - `collection_name` is the name of the collection this operator manages.
    - `client` can be provided from outside; if omitted, a PersistentClient
      will be created automatically using `location`.
    """

    def __init__(
        self,
        location: str,
        collection_name: str,
        client: Optional[chromadb.Client] = None,
    ) -> None:
        self.location = location
        self.collection_name = collection_name
        self.client: chromadb.Client = client or chromadb.PersistentClient(
            path=self.location
        )
        self._collection: Optional[chromadb.Collection] = None

    # ------------------------------------------------------------------
    # Client / collection helpers
    # ------------------------------------------------------------------

    def client_create(self) -> chromadb.Client:
        """
        (Re)create the persistent client using `self.location`.
        Normally you don't need to call this explicitly, because the client
        is created in `__init__`, but it's here if you want to reset it.
        """
        self.client = chromadb.PersistentClient(path=self.location)
        # Reset cached collection because the underlying client changed.
        self._collection = None
        return self.client

    @property
    def collection(self) -> chromadb.Collection:
        """
        Lazily get or create the managed collection using self props.
        """
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
        return self._collection

    def create_collection(self) -> chromadb.Collection:
        """
        Explicitly create a new collection and cache it on `self`.
        """
        self._collection = self.client.create_collection(name=self.collection_name)
        return self._collection

    def get_collection(self) -> chromadb.Collection:
        """
        Get an existing collection and cache it on `self`.
        """
        self._collection = self.client.get_collection(name=self.collection_name)
        if self._collection:
            return self._collection
        else:
            return null

    def get_or_create_collection(self) -> chromadb.Collection:
        """
        Get or create the collection and cache it on `self`.
        """
        self._collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        return self._collection

    def list_collections(self) -> List[chromadb.Collection]:
        """
        List all collections known to this client.
        """
        return self.client.list_collections()

    def delete_collection(self) -> None:
        """
        Delete this operator's collection (if it exists) and clear cache.
        """
        self.client.delete_collection(name=self.collection_name)
        self._collection = None

    # ------------------------------------------------------------------
    # Vector helpers
    # ------------------------------------------------------------------

    def view_all_vectors(self) -> Dict[str, List[Any]]:
        """
        Return all documents, metadatas and embeddings in the collection.
        """
        collection = self.collection
        results = collection.get(include=["documents", "embeddings", "metadatas"])
        return results

    def view_vectors(self, ids: Iterable[str]) -> Dict[str, List[Any]]:
        """
        Get specific items by ID from the collection.
        """
        collection = self.collection
        results = collection.get(
            ids=list(ids),
            include=["documents", "embeddings", "metadatas"],
        )
        return results

    def query_vectors(
        self,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[Any]]:
        """
        Query the collection by text, using the underlying Chroma embedding model.
        """
        collection = self.collection
        results = collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            include=["documents", "distances", "metadatas"],
        )
        return results

    def upsert_vectors(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add or update vectors in the collection.
        """
        collection = self.collection
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def delete_vectors_by_id(self, ids: Iterable[str]) -> None:
        """
        Delete vectors by ID.
        """
        collection = self.collection
        collection.delete(ids=list(ids))

    def delete_vectors_by_metadata(self, where: Dict[str, Any]) -> None:
        """
        Delete vectors matching the given metadata filter.
        """
        collection = self.collection
        collection.delete(where=where)
