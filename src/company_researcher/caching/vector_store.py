"""
ChromaDB Vector Store for Semantic Search.

Provides semantic search capabilities over research data:
- Search similar research across companies
- Find related sources
- Deduplicate content
- Context-aware retrieval

Usage:
    from company_researcher.caching import get_vector_store

    store = get_vector_store()

    # Add research output
    store.add_research_output(
        research_id="run_123",
        company_name="Tesla",
        agent_name="financial",
        content="Revenue increased to $96.8B..."
    )

    # Search similar research
    results = store.search_similar_research(
        query="electric vehicle market share",
        n_results=5
    )
"""

import hashlib
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, List, Optional

from ..utils import get_config, get_logger

logger = get_logger(__name__)

try:
    import chromadb
    from chromadb.config import Settings

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


@dataclass
class SearchResult:
    """Result from a vector search."""

    id: str
    content: str
    metadata: Dict[str, Any]
    distance: float
    similarity: float  # 1 - distance for cosine

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "distance": self.distance,
            "similarity": self.similarity,
        }


class ResearchVectorStore:
    """
    Vector store for research documents using ChromaDB.

    Provides semantic search and similarity matching for:
    - Research outputs from agents
    - Source content
    - Company information
    """

    def __init__(self, persist_directory: str = "./chroma_db", collection_prefix: str = "research"):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory for persistent storage
            collection_prefix: Prefix for collection names
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is required for vector store. " "Install with: pip install chromadb"
            )

        self.persist_directory = persist_directory
        self.collection_prefix = collection_prefix

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory, settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )

        # Get or create collections
        self.research_collection = self.client.get_or_create_collection(
            name=f"{collection_prefix}_outputs", metadata={"hnsw:space": "cosine"}
        )

        self.sources_collection = self.client.get_or_create_collection(
            name=f"{collection_prefix}_sources", metadata={"hnsw:space": "cosine"}
        )

        self.companies_collection = self.client.get_or_create_collection(
            name=f"{collection_prefix}_companies", metadata={"hnsw:space": "cosine"}
        )

    # =========================================================================
    # Research Output Operations
    # =========================================================================

    def add_research_output(
        self,
        research_id: str,
        company_name: str,
        agent_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add research output to vector store.

        Args:
            research_id: Unique research run ID
            company_name: Company name
            agent_name: Agent that produced the output
            content: Analysis content
            metadata: Additional metadata

        Returns:
            Document ID
        """
        doc_id = f"{research_id}_{agent_name}"

        full_metadata = {
            "company": company_name,
            "agent": agent_name,
            "research_id": research_id,
            **(metadata or {}),
        }

        self.research_collection.upsert(
            ids=[doc_id], documents=[content], metadatas=[full_metadata]
        )

        return doc_id

    def add_research_outputs_bulk(self, outputs: List[Dict[str, Any]]) -> int:
        """
        Add multiple research outputs efficiently.

        Args:
            outputs: List of output dictionaries with keys:
                     research_id, company_name, agent_name, content

        Returns:
            Number of documents added
        """
        if not outputs:
            return 0

        ids = []
        documents = []
        metadatas = []

        for output in outputs:
            doc_id = f"{output['research_id']}_{output['agent_name']}"
            ids.append(doc_id)
            documents.append(output["content"])
            metadatas.append(
                {
                    "company": output["company_name"],
                    "agent": output["agent_name"],
                    "research_id": output["research_id"],
                    **(output.get("metadata", {})),
                }
            )

        self.research_collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

        return len(ids)

    def search_similar_research(
        self,
        query: str,
        company_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        n_results: int = 5,
        min_similarity: float = 0.0,
    ) -> List[SearchResult]:
        """
        Search for similar research outputs.

        Args:
            query: Search query
            company_name: Filter by company
            agent_name: Filter by agent
            n_results: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of SearchResult objects
        """
        where_filter = {}
        if company_name:
            where_filter["company"] = company_name
        if agent_name:
            where_filter["agent"] = agent_name

        results = self.research_collection.query(
            query_texts=[query], n_results=n_results, where=where_filter if where_filter else None
        )

        search_results = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance  # For cosine distance

            if similarity >= min_similarity:
                search_results.append(
                    SearchResult(
                        id=results["ids"][0][i],
                        content=results["documents"][0][i],
                        metadata=results["metadatas"][0][i],
                        distance=distance,
                        similarity=similarity,
                    )
                )

        return search_results

    def get_research_by_company(self, company_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all research outputs for a company."""
        results = self.research_collection.get(where={"company": company_name}, limit=limit)

        outputs = []
        for i in range(len(results["ids"])):
            outputs.append(
                {
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
            )

        return outputs

    # =========================================================================
    # Source Operations
    # =========================================================================

    def add_source(
        self,
        source_id: str,
        url: str,
        title: str,
        content: str,
        company_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add source to vector store.

        Args:
            source_id: Unique source ID
            url: Source URL
            title: Source title
            content: Source content
            company_name: Related company
            metadata: Additional metadata

        Returns:
            Document ID
        """
        doc_id = source_id or self._hash_url(url)

        full_metadata = {"url": url, "title": title, "company": company_name, **(metadata or {})}

        self.sources_collection.upsert(ids=[doc_id], documents=[content], metadatas=[full_metadata])

        return doc_id

    def search_similar_sources(
        self,
        query: str,
        company_name: Optional[str] = None,
        n_results: int = 10,
        min_similarity: float = 0.5,
    ) -> List[SearchResult]:
        """
        Search for similar sources.

        Args:
            query: Search query
            company_name: Filter by company
            n_results: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of SearchResult objects
        """
        where_filter = {"company": company_name} if company_name else None

        results = self.sources_collection.query(
            query_texts=[query], n_results=n_results, where=where_filter
        )

        search_results = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance

            if similarity >= min_similarity:
                search_results.append(
                    SearchResult(
                        id=results["ids"][0][i],
                        content=results["documents"][0][i],
                        metadata=results["metadatas"][0][i],
                        distance=distance,
                        similarity=similarity,
                    )
                )

        return search_results

    def find_duplicate_sources(self, content: str, threshold: float = 0.95) -> List[SearchResult]:
        """
        Find potentially duplicate sources by content.

        Args:
            content: Content to check for duplicates
            threshold: Similarity threshold (0.95 = 95% similar)

        Returns:
            List of potential duplicates
        """
        results = self.sources_collection.query(query_texts=[content], n_results=10)

        duplicates = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance

            if similarity >= threshold:
                duplicates.append(
                    SearchResult(
                        id=results["ids"][0][i],
                        content=results["documents"][0][i],
                        metadata=results["metadatas"][0][i],
                        distance=distance,
                        similarity=similarity,
                    )
                )

        return duplicates

    # =========================================================================
    # Company Operations
    # =========================================================================

    def add_company_profile(
        self, company_name: str, profile: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add company profile for similarity matching.

        Args:
            company_name: Company name
            profile: Company profile/overview text
            metadata: Additional metadata

        Returns:
            Document ID
        """
        doc_id = f"company_{self._normalize_name(company_name)}"

        full_metadata = {"company": company_name, "type": "profile", **(metadata or {})}

        self.companies_collection.upsert(
            ids=[doc_id], documents=[profile], metadatas=[full_metadata]
        )

        return doc_id

    def find_similar_companies(
        self, query: str, n_results: int = 5, exclude_company: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Find companies similar to a query or description.

        Args:
            query: Search query or company description
            n_results: Maximum results
            exclude_company: Company to exclude from results

        Returns:
            List of similar companies
        """
        results = self.companies_collection.query(
            query_texts=[query], n_results=n_results + (1 if exclude_company else 0)
        )

        search_results = []
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]

            # Skip excluded company
            if exclude_company and metadata.get("company") == exclude_company:
                continue

            distance = results["distances"][0][i]
            search_results.append(
                SearchResult(
                    id=results["ids"][0][i],
                    content=results["documents"][0][i],
                    metadata=metadata,
                    distance=distance,
                    similarity=1 - distance,
                )
            )

        return search_results[:n_results]

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def delete_research(self, research_id: str) -> None:
        """Delete all data for a research run."""
        # Get all document IDs for this research
        results = self.research_collection.get(where={"research_id": research_id})

        if results["ids"]:
            self.research_collection.delete(ids=results["ids"])

    def delete_company_data(self, company_name: str) -> None:
        """Delete all data for a company."""
        # Delete from research collection
        research_results = self.research_collection.get(where={"company": company_name})
        if research_results["ids"]:
            self.research_collection.delete(ids=research_results["ids"])

        # Delete from sources collection
        source_results = self.sources_collection.get(where={"company": company_name})
        if source_results["ids"]:
            self.sources_collection.delete(ids=source_results["ids"])

        # Delete from companies collection
        company_id = f"company_{self._normalize_name(company_name)}"
        try:
            self.companies_collection.delete(ids=[company_id])
        except Exception as e:
            logger.debug(f"Company {company_name} not in collection (expected): {e}")

    def get_stats(self) -> Dict[str, int]:
        """Get collection statistics."""
        return {
            "research_outputs": self.research_collection.count(),
            "sources": self.sources_collection.count(),
            "companies": self.companies_collection.count(),
        }

    def reset(self) -> None:
        """Reset all collections (for testing)."""
        self.client.delete_collection(f"{self.collection_prefix}_outputs")
        self.client.delete_collection(f"{self.collection_prefix}_sources")
        self.client.delete_collection(f"{self.collection_prefix}_companies")

        # Recreate collections
        self.research_collection = self.client.get_or_create_collection(
            name=f"{self.collection_prefix}_outputs", metadata={"hnsw:space": "cosine"}
        )
        self.sources_collection = self.client.get_or_create_collection(
            name=f"{self.collection_prefix}_sources", metadata={"hnsw:space": "cosine"}
        )
        self.companies_collection = self.client.get_or_create_collection(
            name=f"{self.collection_prefix}_companies", metadata={"hnsw:space": "cosine"}
        )

    def _hash_url(self, url: str) -> str:
        """Generate hash for URL."""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _normalize_name(self, name: str) -> str:
        """Normalize name for ID generation."""
        import re

        normalized = name.lower()
        normalized = re.sub(r"[^\w\s]", "", normalized)
        normalized = re.sub(r"\s+", "_", normalized).strip("_")
        return normalized


# Singleton instance
_vector_store: Optional[ResearchVectorStore] = None
_store_lock = Lock()


def get_vector_store(persist_directory: Optional[str] = None) -> ResearchVectorStore:
    """
    Get singleton vector store instance.

    Args:
        persist_directory: Optional custom directory

    Returns:
        ResearchVectorStore instance
    """
    global _vector_store

    if not CHROMADB_AVAILABLE:
        raise ImportError(
            "ChromaDB is required for vector store. " "Install with: pip install chromadb"
        )

    if _vector_store is None:
        with _store_lock:
            if _vector_store is None:
                directory = persist_directory or get_config(
                    "CHROMA_PERSIST_DIR", default="./chroma_db"
                )
                _vector_store = ResearchVectorStore(directory)

    return _vector_store


def reset_vector_store() -> None:
    """Reset vector store instance (for testing)."""
    global _vector_store
    if _vector_store:
        _vector_store.reset()
    _vector_store = None
