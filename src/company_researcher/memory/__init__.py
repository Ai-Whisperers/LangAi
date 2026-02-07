"""
Memory System for Company Researcher (Phase 11).

Dual-layer memory architecture:
- Hot layer: Fast in-memory LRU cache with TTL
- Cold layer: Persistent vector store with semantic search
- Unified API for research memory operations

Components:
- LRUCache: Generic LRU cache with TTL support
- ResearchCache: Type-aware cache for research data
- VectorStore: ChromaDB wrapper for semantic search
- ResearchVectorStore: Research-specific vector operations
- DualLayerMemory: Coordinated hot/cold storage

Usage:
    from src.company_researcher.memory import DualLayerMemory, create_research_memory

    # Quick setup
    memory = create_research_memory()

    # Store research
    memory.remember_research(
        company_name="Tesla",
        data_type="financial",
        content="Tesla Q3 2024 revenue was $25.2B..."
    )

    # Semantic search
    results = memory.recall_similar("electric vehicle revenue", k=5)

    # Company-specific recall
    items = memory.recall_company("Tesla", data_type="financial")
"""

# Conversation memory
from .conversation import (
    BufferedConversationMemory,
    ConversationMemory,
    ConversationSummary,
    Message,
    MessageRole,
    WindowedConversationMemory,
    create_conversation_memory,
)

# Dual-layer system
from .dual_layer import (
    AsyncDualLayerMemory,
    DualLayerMemory,
    DualLayerStats,
    MemoryItem,
    MemoryLayer,
    PromotionPolicy,
    create_research_memory,
)

# Entity memory
from .entity import (
    Entity,
    EntityMemory,
    EntityType,
    Relationship,
    RelationType,
    create_entity_memory,
)

# Hot layer (LRU cache)
from .lru_cache import CacheEntry, CacheStats, LRUCache, ResearchCache, TypedLRUCache

# Cold layer (vector store)
from .vector_store import (
    CHROMADB_AVAILABLE,
    OPENAI_AVAILABLE,
    EmbeddingGenerator,
    EmbeddingModel,
    ResearchVectorStore,
    SearchResult,
    VectorDocument,
    VectorStore,
)

# Working memory
from .working import (
    ScratchpadMemory,
    WorkingMemory,
    WorkingMemoryItem,
    create_scratchpad,
    create_working_memory,
)

__all__ = [
    # Hot layer
    "LRUCache",
    "TypedLRUCache",
    "ResearchCache",
    "CacheEntry",
    "CacheStats",
    # Cold layer
    "VectorStore",
    "ResearchVectorStore",
    "VectorDocument",
    "SearchResult",
    "EmbeddingGenerator",
    "EmbeddingModel",
    "CHROMADB_AVAILABLE",
    "OPENAI_AVAILABLE",
    # Dual-layer
    "DualLayerMemory",
    "AsyncDualLayerMemory",
    "MemoryItem",
    "MemoryLayer",
    "PromotionPolicy",
    "DualLayerStats",
    "create_research_memory",
    # Conversation memory
    "ConversationMemory",
    "WindowedConversationMemory",
    "BufferedConversationMemory",
    "Message",
    "MessageRole",
    "ConversationSummary",
    "create_conversation_memory",
    # Entity memory
    "EntityMemory",
    "Entity",
    "EntityType",
    "Relationship",
    "RelationType",
    "create_entity_memory",
    # Working memory
    "WorkingMemory",
    "WorkingMemoryItem",
    "ScratchpadMemory",
    "create_working_memory",
    "create_scratchpad",
]
