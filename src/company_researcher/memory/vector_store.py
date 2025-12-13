"""
Vector Store Integration (Phase 11).

Cold memory layer with:
- ChromaDB integration
- Embedding generation
- Semantic search
- Collection management
- Persistence support

This is the persistent storage layer for semantic search over research data.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from ..utils import get_config, utc_now

# Conditional imports for vector databases
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class VectorDocument:
    """A document stored in the vector database."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=utc_now)

    @staticmethod
    def generate_id(content: str, prefix: str = "doc") -> str:
        """Generate a unique ID for content."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{prefix}_{content_hash}"


@dataclass
class SearchResult:
    """A search result from vector store."""
    document: VectorDocument
    score: float
    distance: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.document.id,
            "content": self.document.content,
            "metadata": self.document.metadata,
            "score": self.score,
            "distance": self.distance
        }


class EmbeddingModel(str, Enum):
    """Available embedding models."""
    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"
    OPENAI_ADA = "text-embedding-ada-002"


# ============================================================================
# Embedding Generator
# ============================================================================

class EmbeddingGenerator:
    """
    Generate embeddings for text content.

    Supports:
    - OpenAI embeddings
    - Fallback to simple hashing for testing
    """

    def __init__(
        self,
        model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL,
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding generator.

        Args:
            model: Embedding model to use
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.model = model
        self._api_key = api_key or get_config("OPENAI_API_KEY")
        self._client = None

        if OPENAI_AVAILABLE and self._api_key:
            self._client = OpenAI(api_key=self._api_key)

    @property
    def is_available(self) -> bool:
        """Check if real embeddings are available."""
        return self._client is not None

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self._client:
            return self._embed_openai(text)
        else:
            return self._embed_fallback(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if self._client:
            return self._embed_batch_openai(texts)
        else:
            return [self._embed_fallback(t) for t in texts]

    def _embed_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        response = self._client.embeddings.create(
            model=self.model.value,
            input=text
        )
        return response.data[0].embedding

    def _embed_batch_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch using OpenAI."""
        response = self._client.embeddings.create(
            model=self.model.value,
            input=texts
        )
        return [item.embedding for item in response.data]

    def _embed_fallback(self, text: str) -> List[float]:
        """
        Fallback embedding using simple hashing.

        This creates a pseudo-embedding for testing without API.
        Not suitable for production semantic search.
        """
        # Create a deterministic pseudo-embedding
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()

        # Convert to 384-dim float vector (matches small model)
        embedding = []
        for i in range(384):
            byte_idx = i % 32
            embedding.append((hash_bytes[byte_idx] - 128) / 128.0)

        return embedding


# ============================================================================
# Vector Store
# ============================================================================

class VectorStore:
    """
    Vector database wrapper for semantic search.

    Uses ChromaDB for local persistent storage.

    Usage:
        store = VectorStore("research_memory")
        store.add("doc1", "Tesla is an EV company", {"company": "Tesla"})
        results = store.search("electric vehicles", k=5)
    """

    def __init__(
        self,
        collection_name: str = "research_memory",
        persist_directory: Optional[str] = None,
        embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory for persistent storage
            embedding_model: Model for generating embeddings
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._embedding_generator = EmbeddingGenerator(embedding_model)

        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB not installed. Install with: pip install chromadb"
            )

        # Initialize ChromaDB client
        if persist_directory:
            self._client = chromadb.PersistentClient(path=persist_directory)
        else:
            self._client = chromadb.Client()

        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    @property
    def count(self) -> int:
        """Get number of documents in collection."""
        return self._collection.count()

    @property
    def embedding_available(self) -> bool:
        """Check if real embeddings are available."""
        return self._embedding_generator.is_available

    def add(
        self,
        id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add document to vector store.

        Args:
            id: Document ID
            content: Text content
            metadata: Optional metadata
        """
        # Generate embedding
        embedding = self._embedding_generator.embed(content)

        # Prepare metadata
        doc_metadata = metadata or {}
        doc_metadata["created_at"] = utc_now().isoformat()
        doc_metadata["content_length"] = len(content)

        # Add to collection
        self._collection.add(
            ids=[id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[doc_metadata]
        )

    def add_batch(
        self,
        documents: List[VectorDocument]
    ) -> int:
        """
        Add multiple documents.

        Args:
            documents: List of documents to add

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]

        # Generate embeddings
        embeddings = self._embedding_generator.embed_batch(contents)

        # Prepare metadata
        metadatas = []
        for doc in documents:
            meta = doc.metadata.copy()
            meta["created_at"] = doc.created_at.isoformat()
            meta["content_length"] = len(doc.content)
            metadatas.append(meta)

        # Add to collection
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

        return len(documents)

    def search(
        self,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results
            where: Metadata filter
            where_document: Document content filter

        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self._embedding_generator.embed(query)

        # Query collection
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"]
        )

        # Convert to SearchResult objects
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                doc = VectorDocument(
                    id=doc_id,
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {}
                )
                distance = results["distances"][0][i] if results["distances"] else 0
                # Convert distance to score (cosine: 1 - distance)
                score = 1 - distance

                search_results.append(SearchResult(
                    document=doc,
                    score=score,
                    distance=distance
                ))

        return search_results

    def get(self, id: str) -> Optional[VectorDocument]:
        """
        Get document by ID.

        Args:
            id: Document ID

        Returns:
            Document or None if not found
        """
        results = self._collection.get(
            ids=[id],
            include=["documents", "metadatas"]
        )

        if results["ids"]:
            return VectorDocument(
                id=results["ids"][0],
                content=results["documents"][0],
                metadata=results["metadatas"][0] if results["metadatas"] else {}
            )

        return None

    def delete(self, id: str) -> bool:
        """
        Delete document by ID.

        Args:
            id: Document ID

        Returns:
            True if deleted
        """
        try:
            self._collection.delete(ids=[id])
            return True
        except Exception:
            return False

    def delete_where(self, where: Dict[str, Any]) -> int:
        """
        Delete documents matching filter.

        Args:
            where: Metadata filter

        Returns:
            Number deleted (approximate)
        """
        # Get matching IDs
        results = self._collection.get(
            where=where,
            include=["documents"]
        )

        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            return len(results["ids"])

        return 0

    def update(
        self,
        id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update document.

        Args:
            id: Document ID
            content: New content (regenerates embedding)
            metadata: New metadata

        Returns:
            True if updated
        """
        try:
            update_args = {"ids": [id]}

            if content:
                embedding = self._embedding_generator.embed(content)
                update_args["embeddings"] = [embedding]
                update_args["documents"] = [content]

            if metadata:
                update_args["metadatas"] = [metadata]

            self._collection.update(**update_args)
            return True
        except Exception:
            return False

    def clear(self) -> int:
        """
        Clear all documents.

        Returns:
            Number of documents cleared
        """
        count = self.count
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        return count


# ============================================================================
# Research Vector Store
# ============================================================================

class ResearchVectorStore:
    """
    Specialized vector store for research data.

    Organizes data by:
    - Company
    - Data type (overview, financial, market, etc.)
    - Source
    """

    def __init__(
        self,
        persist_directory: str = "./data/vector_memory",
        collection_name: str = "research_memory"
    ):
        """Initialize research vector store."""
        self._store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )

    @property
    def count(self) -> int:
        return self._store.count

    def store_research(
        self,
        company_name: str,
        data_type: str,
        content: str,
        source_url: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store research data.

        Args:
            company_name: Company being researched
            data_type: Type of data (overview, financial, market, etc.)
            content: Research content
            source_url: Source URL if applicable
            extra_metadata: Additional metadata

        Returns:
            Document ID
        """
        doc_id = VectorDocument.generate_id(
            f"{company_name}_{data_type}_{content[:50]}",
            prefix=data_type
        )

        metadata = {
            "company": company_name.lower(),
            "data_type": data_type,
            "source_url": source_url or "",
            **(extra_metadata or {})
        }

        self._store.add(doc_id, content, metadata)
        return doc_id

    def search_company(
        self,
        company_name: str,
        query: str,
        k: int = 5,
        data_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search research for a specific company.

        Args:
            company_name: Company to search
            query: Search query
            k: Number of results
            data_type: Filter by data type

        Returns:
            Search results
        """
        where = {"company": company_name.lower()}
        if data_type:
            where["data_type"] = data_type

        return self._store.search(query, k=k, where=where)

    def search_all(
        self,
        query: str,
        k: int = 10,
        data_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search all research data.

        Args:
            query: Search query
            k: Number of results
            data_type: Filter by data type

        Returns:
            Search results
        """
        where = {"data_type": data_type} if data_type else None
        return self._store.search(query, k=k, where=where)

    def get_company_data(
        self,
        company_name: str,
        data_type: Optional[str] = None
    ) -> List[VectorDocument]:
        """
        Get all stored data for a company.

        Args:
            company_name: Company name
            data_type: Optional type filter

        Returns:
            List of documents
        """
        where = {"company": company_name.lower()}
        if data_type:
            where["data_type"] = data_type

        # Use a broad search to get all matching documents
        results = self._store.search("", k=100, where=where)
        return [r.document for r in results]

    def delete_company(self, company_name: str) -> int:
        """Delete all data for a company."""
        return self._store.delete_where({"company": company_name.lower()})

    def clear(self) -> int:
        """Clear all research data."""
        return self._store.clear()
