"""
Dual-Layer Memory System (Phase 11).

Coordinates hot (LRU cache) and cold (vector store) memory layers:
- Hot layer: Fast, in-memory, LRU-evicted
- Cold layer: Persistent, semantic search enabled
- Automatic promotion/demotion between layers
- Unified API for research memory operations

Usage:
    memory = DualLayerMemory()

    # Store research
    memory.remember("tesla_overview", content, metadata)

    # Recall by key (checks hot first)
    result = memory.recall_key("tesla_overview")

    # Semantic search (uses cold layer)
    results = memory.recall_similar("electric vehicle market share", k=5)
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .lru_cache import ResearchCache, CacheStats
from .vector_store import (
    ResearchVectorStore,
    VectorDocument,
    SearchResult,
    CHROMADB_AVAILABLE
)


# ============================================================================
# Enums and Data Models
# ============================================================================

class MemoryLayer(str, Enum):
    """Memory layer identifiers."""
    HOT = "hot"
    COLD = "cold"
    BOTH = "both"


class PromotionPolicy(str, Enum):
    """Policies for promoting cold items to hot."""
    AGGRESSIVE = "aggressive"  # Promote on first access
    MODERATE = "moderate"      # Promote after 2+ accesses
    CONSERVATIVE = "conservative"  # Promote only frequently accessed


@dataclass
class MemoryItem:
    """A unified memory item across layers."""
    key: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    layer: MemoryLayer = MemoryLayer.COLD
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    score: float = 0.0  # Relevance score for search results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "content": self.content,
            "metadata": self.metadata,
            "layer": self.layer.value,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "score": self.score
        }


@dataclass
class DualLayerStats:
    """Statistics for dual-layer memory."""
    hot_stats: CacheStats
    cold_count: int
    total_recalls: int = 0
    hot_hits: int = 0
    cold_hits: int = 0
    promotions: int = 0
    demotions: int = 0

    @property
    def hit_rate(self) -> float:
        if self.total_recalls == 0:
            return 0.0
        return (self.hot_hits + self.cold_hits) / self.total_recalls

    @property
    def hot_hit_rate(self) -> float:
        if self.total_recalls == 0:
            return 0.0
        return self.hot_hits / self.total_recalls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hot_layer": self.hot_stats.to_dict(),
            "cold_count": self.cold_count,
            "total_recalls": self.total_recalls,
            "hot_hits": self.hot_hits,
            "cold_hits": self.cold_hits,
            "hit_rate": round(self.hit_rate, 3),
            "hot_hit_rate": round(self.hot_hit_rate, 3),
            "promotions": self.promotions,
            "demotions": self.demotions
        }


# ============================================================================
# Dual-Layer Memory System
# ============================================================================

class DualLayerMemory:
    """
    Dual-layer memory system combining hot (cache) and cold (vector) storage.

    Features:
    - Unified API for memory operations
    - Automatic hot/cold layer management
    - Semantic search through cold layer
    - Fast key-based lookup through hot layer
    - Configurable promotion/demotion policies

    Usage:
        # Initialize
        memory = DualLayerMemory(
            hot_max_size=500,
            hot_ttl=7200,
            cold_persist_dir="./data/memory"
        )

        # Store research data
        memory.remember(
            key="tesla_financials_2024",
            content="Tesla Q3 2024 revenue was $25.2B...",
            metadata={"company": "tesla", "type": "financial"}
        )

        # Recall by exact key
        item = memory.recall_key("tesla_financials_2024")

        # Semantic search
        results = memory.recall_similar("Tesla revenue growth", k=5)
    """

    def __init__(
        self,
        hot_max_size: int = 500,
        hot_ttl: int = 7200,  # 2 hours
        cold_persist_dir: str = "./data/vector_memory",
        cold_collection: str = "research_memory",
        promotion_policy: PromotionPolicy = PromotionPolicy.MODERATE,
        promotion_threshold: int = 2
    ):
        """
        Initialize dual-layer memory.

        Args:
            hot_max_size: Maximum items in hot layer
            hot_ttl: Default TTL for hot layer items (seconds)
            cold_persist_dir: Directory for cold layer persistence
            cold_collection: Collection name for vector store
            promotion_policy: Policy for promoting cold to hot
            promotion_threshold: Access count threshold for promotion
        """
        # Initialize hot layer (always available)
        self._hot = ResearchCache(max_size=hot_max_size, default_ttl=hot_ttl)

        # Initialize cold layer (requires ChromaDB)
        self._cold: Optional[ResearchVectorStore] = None
        self._cold_available = False

        if CHROMADB_AVAILABLE:
            try:
                self._cold = ResearchVectorStore(
                    persist_directory=cold_persist_dir,
                    collection_name=cold_collection
                )
                self._cold_available = True
            except Exception as e:
                print(f"[Memory] Cold layer initialization failed: {e}")

        # Configuration
        self._promotion_policy = promotion_policy
        self._promotion_threshold = promotion_threshold

        # Statistics
        self._total_recalls = 0
        self._hot_hits = 0
        self._cold_hits = 0
        self._promotions = 0
        self._demotions = 0

        # Access tracking for promotion decisions
        self._access_counts: Dict[str, int] = {}

    @property
    def cold_available(self) -> bool:
        """Check if cold layer is available."""
        return self._cold_available

    @property
    def stats(self) -> DualLayerStats:
        """Get memory statistics."""
        return DualLayerStats(
            hot_stats=self._hot.stats,
            cold_count=self._cold.count if self._cold else 0,
            total_recalls=self._total_recalls,
            hot_hits=self._hot_hits,
            cold_hits=self._cold_hits,
            promotions=self._promotions,
            demotions=self._demotions
        )

    # ==========================================================================
    # Core Operations
    # ==========================================================================

    def remember(
        self,
        key: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        layer: MemoryLayer = MemoryLayer.BOTH,
        company_name: Optional[str] = None,
        data_type: Optional[str] = None,
        hot_ttl: Optional[int] = None
    ) -> None:
        """
        Store content in memory.

        Args:
            key: Unique identifier for the content
            content: Text content to store
            metadata: Optional metadata
            layer: Which layer(s) to store in
            company_name: Company name for cold layer organization
            data_type: Data type for cold layer organization
            hot_ttl: Override TTL for hot layer
        """
        meta = metadata or {}

        # Store in hot layer
        if layer in (MemoryLayer.HOT, MemoryLayer.BOTH):
            hot_data = {
                "content": content,
                "metadata": meta,
                "stored_at": datetime.now().isoformat()
            }
            self._hot.put(key, hot_data, ttl=hot_ttl)

        # Store in cold layer
        if layer in (MemoryLayer.COLD, MemoryLayer.BOTH) and self._cold_available:
            # Determine company and type
            comp = company_name or meta.get("company", "unknown")
            dtype = data_type or meta.get("data_type", "general")

            self._cold.store_research(
                company_name=comp,
                data_type=dtype,
                content=content,
                source_url=meta.get("source_url"),
                extra_metadata={**meta, "memory_key": key}
            )

    def recall_key(self, key: str) -> Optional[MemoryItem]:
        """
        Recall content by exact key.

        Checks hot layer first, then cold layer.
        Promotes from cold to hot based on policy.

        Args:
            key: The key to look up

        Returns:
            MemoryItem if found, None otherwise
        """
        self._total_recalls += 1
        self._access_counts[key] = self._access_counts.get(key, 0) + 1

        # Check hot layer first
        hot_data = self._hot.get(key)
        if hot_data is not None:
            self._hot_hits += 1
            return MemoryItem(
                key=key,
                content=hot_data["content"],
                metadata=hot_data.get("metadata", {}),
                layer=MemoryLayer.HOT,
                access_count=self._access_counts[key]
            )

        # Check cold layer
        if self._cold_available:
            # Search for exact key in metadata
            results = self._cold.search_all(
                query=key,  # Use key as query
                k=1
            )

            for result in results:
                if result.document.metadata.get("memory_key") == key:
                    self._cold_hits += 1

                    # Create memory item
                    item = MemoryItem(
                        key=key,
                        content=result.document.content,
                        metadata=result.document.metadata,
                        layer=MemoryLayer.COLD,
                        access_count=self._access_counts[key],
                        score=result.score
                    )

                    # Consider promotion
                    if self._should_promote(key):
                        self._promote(item)

                    return item

        return None

    def recall_similar(
        self,
        query: str,
        k: int = 5,
        company_name: Optional[str] = None,
        data_type: Optional[str] = None,
        promote_top: bool = False
    ) -> List[MemoryItem]:
        """
        Recall similar content using semantic search.

        Uses cold layer for semantic search.

        Args:
            query: Search query
            k: Number of results
            company_name: Filter by company
            data_type: Filter by data type
            promote_top: Whether to promote top result to hot

        Returns:
            List of MemoryItems sorted by relevance
        """
        self._total_recalls += 1

        if not self._cold_available:
            return []

        # Perform semantic search
        if company_name:
            results = self._cold.search_company(
                company_name=company_name,
                query=query,
                k=k,
                data_type=data_type
            )
        else:
            results = self._cold.search_all(
                query=query,
                k=k,
                data_type=data_type
            )

        # Convert to MemoryItems
        items = []
        for result in results:
            key = result.document.metadata.get("memory_key", result.document.id)
            self._access_counts[key] = self._access_counts.get(key, 0) + 1

            item = MemoryItem(
                key=key,
                content=result.document.content,
                metadata=result.document.metadata,
                layer=MemoryLayer.COLD,
                access_count=self._access_counts[key],
                score=result.score
            )
            items.append(item)

        if items:
            self._cold_hits += 1

            # Optionally promote top result
            if promote_top and items[0].score > 0.8:
                self._promote(items[0])

        return items

    def forget(self, key: str, layer: MemoryLayer = MemoryLayer.BOTH) -> bool:
        """
        Remove content from memory.

        Args:
            key: Key to remove
            layer: Which layer(s) to remove from

        Returns:
            True if anything was removed
        """
        removed = False

        if layer in (MemoryLayer.HOT, MemoryLayer.BOTH):
            if self._hot.get(key) is not None:
                # Hot layer doesn't have explicit delete, but we can track
                removed = True

        if layer in (MemoryLayer.COLD, MemoryLayer.BOTH) and self._cold_available:
            # Cold layer deletion by metadata key
            deleted = self._cold._store.delete_where({"memory_key": key})
            if deleted > 0:
                removed = True

        if key in self._access_counts:
            del self._access_counts[key]

        return removed

    def forget_company(self, company_name: str) -> int:
        """
        Remove all memory for a company.

        Args:
            company_name: Company to forget

        Returns:
            Number of items removed
        """
        count = 0

        # Clear from hot layer
        company_key = f"company:{company_name.lower()}"
        hot_data = self._hot.get_company(company_name)
        if hot_data:
            count += 1

        # Clear from cold layer
        if self._cold_available:
            deleted = self._cold.delete_company(company_name)
            count += deleted

        return count

    # ==========================================================================
    # Research-Specific Operations
    # ==========================================================================

    def remember_research(
        self,
        company_name: str,
        data_type: str,
        content: str,
        source_url: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store research data with company context.

        Args:
            company_name: Company being researched
            data_type: Type (overview, financial, market, etc.)
            content: Research content
            source_url: Source URL
            extra_metadata: Additional metadata

        Returns:
            Generated key for the content
        """
        # Generate key
        key = f"{company_name.lower()}_{data_type}_{hash(content[:50]) % 10000}"

        metadata = {
            "company": company_name.lower(),
            "data_type": data_type,
            "source_url": source_url or "",
            **(extra_metadata or {})
        }

        self.remember(
            key=key,
            content=content,
            metadata=metadata,
            company_name=company_name,
            data_type=data_type
        )

        return key

    def recall_company(
        self,
        company_name: str,
        query: Optional[str] = None,
        data_type: Optional[str] = None,
        k: int = 10
    ) -> List[MemoryItem]:
        """
        Recall all memory for a company.

        Args:
            company_name: Company to recall
            query: Optional semantic query
            data_type: Optional type filter
            k: Max results

        Returns:
            List of MemoryItems
        """
        # Check hot cache first
        hot_data = self._hot.get_company(company_name)
        items = []

        if hot_data:
            items.append(MemoryItem(
                key=f"company:{company_name.lower()}",
                content=str(hot_data),
                metadata={"company": company_name, "source": "hot_cache"},
                layer=MemoryLayer.HOT
            ))

        # Search cold layer
        if self._cold_available:
            if query:
                results = self._cold.search_company(
                    company_name=company_name,
                    query=query,
                    k=k,
                    data_type=data_type
                )
            else:
                # Get all company data
                docs = self._cold.get_company_data(
                    company_name=company_name,
                    data_type=data_type
                )
                results = [
                    type('SearchResult', (), {
                        'document': doc,
                        'score': 1.0,
                        'distance': 0.0
                    })()
                    for doc in docs[:k]
                ]

            for result in results:
                items.append(MemoryItem(
                    key=result.document.metadata.get("memory_key", result.document.id),
                    content=result.document.content,
                    metadata=result.document.metadata,
                    layer=MemoryLayer.COLD,
                    score=getattr(result, 'score', 1.0)
                ))

        return items

    # ==========================================================================
    # Layer Management
    # ==========================================================================

    def _should_promote(self, key: str) -> bool:
        """Determine if an item should be promoted to hot layer."""
        access_count = self._access_counts.get(key, 0)

        if self._promotion_policy == PromotionPolicy.AGGRESSIVE:
            return True
        elif self._promotion_policy == PromotionPolicy.MODERATE:
            return access_count >= self._promotion_threshold
        elif self._promotion_policy == PromotionPolicy.CONSERVATIVE:
            return access_count >= self._promotion_threshold * 2

        return False

    def _promote(self, item: MemoryItem) -> None:
        """Promote an item from cold to hot layer."""
        hot_data = {
            "content": item.content,
            "metadata": item.metadata,
            "promoted_at": datetime.now().isoformat(),
            "original_layer": "cold"
        }

        self._hot.put(item.key, hot_data)
        self._promotions += 1
        item.layer = MemoryLayer.BOTH

    def _demote(self, key: str) -> None:
        """Record demotion (hot items naturally expire via TTL)."""
        self._demotions += 1

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    def clear(self, layer: MemoryLayer = MemoryLayer.BOTH) -> Dict[str, int]:
        """
        Clear memory layers.

        Args:
            layer: Which layer(s) to clear

        Returns:
            Count of items cleared per layer
        """
        cleared = {"hot": 0, "cold": 0}

        if layer in (MemoryLayer.HOT, MemoryLayer.BOTH):
            cleared["hot"] = self._hot.clear()

        if layer in (MemoryLayer.COLD, MemoryLayer.BOTH) and self._cold_available:
            cleared["cold"] = self._cold.clear()

        self._access_counts.clear()

        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return self.stats.to_dict()


# ============================================================================
# Async Wrapper for Concurrent Operations
# ============================================================================

class AsyncDualLayerMemory:
    """
    Async wrapper for DualLayerMemory.

    Provides async interface for concurrent operations.
    """

    def __init__(self, memory: Optional[DualLayerMemory] = None, **kwargs):
        """
        Initialize async memory wrapper.

        Args:
            memory: Existing DualLayerMemory instance
            **kwargs: Arguments for new DualLayerMemory
        """
        self._memory = memory or DualLayerMemory(**kwargs)
        self._lock = asyncio.Lock()

    async def remember(
        self,
        key: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """Async remember operation."""
        async with self._lock:
            self._memory.remember(key, content, metadata, **kwargs)

    async def recall_key(self, key: str) -> Optional[MemoryItem]:
        """Async recall by key."""
        async with self._lock:
            return self._memory.recall_key(key)

    async def recall_similar(
        self,
        query: str,
        k: int = 5,
        **kwargs
    ) -> List[MemoryItem]:
        """Async semantic search."""
        async with self._lock:
            return self._memory.recall_similar(query, k, **kwargs)

    async def forget(self, key: str, **kwargs) -> bool:
        """Async forget operation."""
        async with self._lock:
            return self._memory.forget(key, **kwargs)

    @property
    def stats(self) -> DualLayerStats:
        return self._memory.stats


# ============================================================================
# Factory Function
# ============================================================================

def create_research_memory(
    persist_dir: str = "./data/research_memory",
    hot_size: int = 500,
    hot_ttl: int = 7200,
    promotion_policy: str = "moderate"
) -> DualLayerMemory:
    """
    Create a configured research memory system.

    Args:
        persist_dir: Directory for persistent storage
        hot_size: Max hot layer size
        hot_ttl: Hot layer TTL in seconds
        promotion_policy: "aggressive", "moderate", or "conservative"

    Returns:
        Configured DualLayerMemory instance
    """
    policy_map = {
        "aggressive": PromotionPolicy.AGGRESSIVE,
        "moderate": PromotionPolicy.MODERATE,
        "conservative": PromotionPolicy.CONSERVATIVE
    }

    return DualLayerMemory(
        hot_max_size=hot_size,
        hot_ttl=hot_ttl,
        cold_persist_dir=persist_dir,
        promotion_policy=policy_map.get(promotion_policy, PromotionPolicy.MODERATE)
    )
