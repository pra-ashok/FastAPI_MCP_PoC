import chromadb
from chromadb.utils import embedding_functions
import os

class VectorService:
    """
    Manages the Vector Database (ChromaDB) for retrieval-augmented generation.
    Handles document insertion, querying, and persistent storage.
    """
    def __init__(self, db_path: str = "./db"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Using default embedding function (can be customized)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.embedding_fn
        )

    async def add_document(self, content: str, metadata: dict = None):
        """Adds a document to the knowledge base."""
        doc_id = str(hash(content))
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        return doc_id

    async def query(self, query_text: str, n_results: int = 3):
        """Queries the knowledge base for similar documents."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results["documents"][0] if results["documents"] else []

    def get_stats(self):
        """Returns collection statistics."""
        return {
            "count": self.collection.count()
        }
