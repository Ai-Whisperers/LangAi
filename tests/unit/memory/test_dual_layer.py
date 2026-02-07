"""
Unit Tests for Phase 11: Dual-Layer Memory System.

Tests the memory system components:
- LRU cache (hot memory)
- Vector store (cold memory)
- Dual-layer coordination
- Research-specific operations
"""

import time
from unittest.mock import MagicMock, patch

import pytest

# Dual-layer imports
from src.company_researcher.memory.dual_layer import (
    DualLayerMemory,
    MemoryLayer,
    PromotionPolicy,
    create_research_memory,
)

# Hot layer imports
from src.company_researcher.memory.lru_cache import LRUCache, ResearchCache

# Cold layer imports
from src.company_researcher.memory.vector_store import (
    CHROMADB_AVAILABLE,
    EmbeddingGenerator,
    VectorDocument,
)

# ============================================================================
# LRU Cache Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestLRUCacheBasic:
    """Test basic LRU cache operations."""

    def test_put_and_get(self):
        """Test basic put and get operations."""
        cache = LRUCache(max_size=3)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("missing", "default") == "default"

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = LRUCache(max_size=3)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        # Access 'a' and 'b' to make 'c' the LRU
        cache.get("a")
        cache.get("b")

        # Adding 'd' should evict 'c' (least recently used)
        cache.put("d", 4)

        assert cache.get("c") is None  # Evicted
        assert cache.get("d") == 4
        assert cache.get("a") == 1
        assert cache.get("b") == 2

    def test_cache_size(self):
        """Test cache size tracking."""
        cache = LRUCache(max_size=5)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        assert cache.size == 3

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = LRUCache(max_size=5)

        cache.put("a", 1)
        cache.put("b", 2)

        cleared = cache.clear()

        assert cleared == 2
        assert cache.size == 0


@pytest.mark.unit
@pytest.mark.memory
class TestLRUCacheTTL:
    """Test LRU cache TTL expiration."""

    def test_ttl_expiration(self):
        """Test that items expire after TTL."""
        cache = LRUCache(max_size=10, default_ttl=1)  # 1 second TTL

        cache.put("expires_soon", "value")

        # Should be available immediately
        assert cache.get("expires_soon") == "value"

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired now
        assert cache.get("expires_soon") is None

    def test_custom_ttl(self):
        """Test custom TTL per item."""
        cache = LRUCache(max_size=10, default_ttl=10)  # 10 second default

        cache.put("short_lived", "value", ttl=1)  # Override with 1 second

        assert cache.get("short_lived") == "value"

        time.sleep(1.5)

        assert cache.get("short_lived") is None


# ============================================================================
# Research Cache Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestResearchCache:
    """Test research-specific cache operations."""

    def test_create_research_cache(self):
        """Test creating a research cache."""
        # Use correct parameter name: max_size_per_type
        cache = ResearchCache(max_size_per_type=50)
        assert cache is not None

    def test_cache_company_data(self):
        """Test caching company data."""
        cache = ResearchCache(max_size_per_type=50)

        # Cache different data types
        cache.cache_company("Tesla", {"overview": "EV company", "ticker": "TSLA"})
        cache.cache_financial("Tesla", {"revenue": 81.5, "profit": 15.0})

        # Retrieve data
        company_data = cache.get_company("Tesla")
        financial_data = cache.get_financial("Tesla")

        assert company_data is not None
        assert company_data["ticker"] == "TSLA"
        assert financial_data["revenue"] == 81.5

    def test_cache_market_data(self):
        """Test caching market data."""
        cache = ResearchCache(max_size_per_type=50)

        cache.put("market", "tesla", {"tam": 500, "sam": 200, "som": 50})
        market_data = cache.get("market", "tesla")

        assert market_data is not None
        assert market_data["tam"] == 500

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = ResearchCache(max_size_per_type=50)

        cache.cache_company("Tesla", {"name": "Tesla"})
        cache.get_company("Tesla")  # Hit
        cache.get_company("Apple")  # Miss

        stats = cache.get_stats()
        assert isinstance(stats, dict)


# ============================================================================
# Embedding Generator Tests (Mocked)
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestEmbeddingGenerator:
    """Test embedding generation with mocked OpenAI."""

    @patch("src.company_researcher.memory.vector_store.OpenAI")
    @patch("src.company_researcher.memory.vector_store.OPENAI_AVAILABLE", True)
    def test_embedding_generator_with_mock(self, mock_openai_class):
        """Test embedding generator with mocked OpenAI client."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 384)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        generator = EmbeddingGenerator(api_key="test-key")

        text = "Tesla is an electric vehicle company"
        embedding = generator.embed(text)

        assert len(embedding) == 384
        assert all(isinstance(v, float) for v in embedding)

    @patch("src.company_researcher.memory.vector_store.OpenAI")
    @patch("src.company_researcher.memory.vector_store.OPENAI_AVAILABLE", True)
    def test_batch_embedding_with_mock(self, mock_openai_class):
        """Test batch embedding with mocked OpenAI client."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 384), MagicMock(embedding=[0.2] * 384)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        generator = EmbeddingGenerator(api_key="test-key")

        texts = ["Apple makes iPhones", "Google runs search engines"]
        embeddings = generator.embed_batch(texts)

        assert len(embeddings) == 2
        assert len(embeddings[0]) == 384

    def test_embedding_fallback(self):
        """Test embedding fallback without OpenAI."""
        # Create generator without API key to trigger fallback
        with patch("src.company_researcher.memory.vector_store.get_config", return_value=None):
            generator = EmbeddingGenerator(api_key=None)

            text = "Tesla is an electric vehicle company"
            embedding = generator.embed(text)

            assert len(embedding) == 384
            assert all(isinstance(v, float) for v in embedding)


# ============================================================================
# Vector Document Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestVectorDocument:
    """Test VectorDocument data class."""

    def test_id_generation(self):
        """Test document ID generation."""
        content1 = "Tesla revenue grew 25% in 2024"
        content2 = "Different content here"

        id1 = VectorDocument.generate_id(content1, "financial")
        id2 = VectorDocument.generate_id(content2, "market")

        assert id1 != id2
        assert id1.startswith("financial_")
        assert id2.startswith("market_")

    def test_same_content_same_id(self):
        """Test that same content generates same ID."""
        content = "Tesla revenue grew 25% in 2024"

        id1 = VectorDocument.generate_id(content, "financial")
        id2 = VectorDocument.generate_id(content, "financial")

        assert id1 == id2

    def test_document_creation(self):
        """Test creating a VectorDocument."""
        doc = VectorDocument(id="test_123", content="Test content", metadata={"company": "Tesla"})

        assert doc.id == "test_123"
        assert doc.content == "Test content"
        assert doc.metadata["company"] == "Tesla"


# ============================================================================
# Vector Store Tests (Mocked)
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="ChromaDB not installed")
class TestVectorStore:
    """Test vector store operations with mocked embeddings."""

    @patch("src.company_researcher.memory.vector_store.EmbeddingGenerator")
    def test_vector_store_operations(self, mock_embedding_class):
        """Test vector store with mocked embeddings."""
        # Setup mock embedding generator
        mock_generator = MagicMock()
        mock_generator.embed.return_value = [0.1] * 384
        mock_generator.embed_batch.return_value = [[0.1] * 384, [0.2] * 384]
        mock_embedding_class.return_value = mock_generator

        from src.company_researcher.memory.vector_store import VectorStore

        # Use in-memory store for testing
        store = VectorStore(collection_name="test_collection")

        # Add documents
        store.add("doc1", "Tesla is an electric vehicle manufacturer", {"company": "tesla"})
        store.add("doc2", "Apple designs and sells consumer electronics", {"company": "apple"})

        assert store.count >= 2

        # Get by ID
        doc = store.get("doc1")
        assert doc is not None

        # Clear
        cleared = store.clear()
        assert store.count == 0


# ============================================================================
# Dual-Layer Memory Tests (Mocked)
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestDualLayerBasic:
    """Test dual-layer memory basic operations."""

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", False)
    def test_dual_layer_hot_only(self, mock_vector_store):
        """Test dual-layer memory with hot layer only."""
        # Create memory without cold layer
        memory = DualLayerMemory(hot_max_size=100, hot_ttl=3600, cold_persist_dir=None)

        assert memory.cold_available == False

        # Store in hot layer only
        memory.remember(
            key="tesla_overview",
            content="Tesla Inc. is an American electric vehicle company.",
            metadata={"company": "tesla", "type": "overview"},
            layer=MemoryLayer.HOT,
        )

        # Recall by key
        item = memory.recall_key("tesla_overview")
        assert item is not None
        assert "Tesla" in item.content
        assert item.layer == MemoryLayer.HOT

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", True)
    def test_dual_layer_with_cold(self, mock_vector_store_class):
        """Test dual-layer memory with both layers."""
        # Setup mock cold layer
        mock_cold = MagicMock()
        mock_cold.count = 0
        mock_vector_store_class.return_value = mock_cold

        memory = DualLayerMemory(hot_max_size=100, hot_ttl=3600, cold_persist_dir="./test_data")

        assert memory.cold_available == True

        # Store in both layers
        memory.remember(
            key="tesla_overview",
            content="Tesla Inc. is an American electric vehicle company.",
            metadata={"company": "tesla", "type": "overview"},
            company_name="Tesla",
            data_type="overview",
        )

        # Recall by key should hit hot layer
        item = memory.recall_key("tesla_overview")
        assert item is not None
        assert item.layer == MemoryLayer.HOT


@pytest.mark.unit
@pytest.mark.memory
class TestDualLayerSemanticSearch:
    """Test dual-layer semantic search."""

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", True)
    def test_semantic_search_cold_layer(self, mock_vector_store_class):
        """Test semantic search through cold layer."""
        # Setup mock cold layer with search results
        mock_cold = MagicMock()
        mock_cold.count = 3
        mock_doc = MagicMock()
        mock_doc.content = "Tesla Q3 revenue was $25.2 billion"
        mock_doc.metadata = {"company": "tesla", "data_type": "financial"}
        mock_doc.id = "tesla_fin_001"
        mock_result = MagicMock()
        mock_result.document = mock_doc
        mock_result.score = 0.95
        mock_cold.search_all.return_value = [mock_result]
        mock_cold.search_company.return_value = [mock_result]
        mock_vector_store_class.return_value = mock_cold

        memory = DualLayerMemory(hot_max_size=100)

        # Semantic search
        results = memory.recall_similar("electric vehicle revenue growth", k=3)

        assert len(results) >= 1
        assert results[0].score > 0


# ============================================================================
# Promotion Policy Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestPromotionPolicy:
    """Test promotion from cold to hot layer."""

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", True)
    def test_promotion_policy_aggressive(self, mock_vector_store_class):
        """Test aggressive promotion policy."""
        mock_cold = MagicMock()
        mock_cold.count = 0
        mock_vector_store_class.return_value = mock_cold

        memory = DualLayerMemory(
            hot_max_size=100, promotion_policy=PromotionPolicy.AGGRESSIVE, promotion_threshold=1
        )

        assert memory._promotion_policy == PromotionPolicy.AGGRESSIVE

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", True)
    def test_promotion_policy_moderate(self, mock_vector_store_class):
        """Test moderate promotion policy."""
        mock_cold = MagicMock()
        mock_cold.count = 0
        mock_vector_store_class.return_value = mock_cold

        memory = DualLayerMemory(
            hot_max_size=100, promotion_policy=PromotionPolicy.MODERATE, promotion_threshold=2
        )

        assert memory._promotion_policy == PromotionPolicy.MODERATE


# ============================================================================
# Factory Function Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestFactoryFunction:
    """Test factory function for creating memory."""

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", True)
    def test_create_research_memory(self, mock_vector_store_class):
        """Test factory function creates memory correctly."""
        mock_cold = MagicMock()
        mock_cold.count = 0
        mock_vector_store_class.return_value = mock_cold

        memory = create_research_memory(
            persist_dir="./test_data/memory",
            hot_size=200,
            hot_ttl=3600,
            promotion_policy="aggressive",
        )

        assert memory._hot._max_size == 200
        assert memory._promotion_policy == PromotionPolicy.AGGRESSIVE

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", False)
    def test_create_research_memory_no_cold(self, mock_vector_store_class):
        """Test factory function without cold layer."""
        memory = create_research_memory(
            persist_dir="./test_data/memory",
            hot_size=100,
            hot_ttl=1800,
            promotion_policy="conservative",
        )

        assert memory._hot._max_size == 100
        assert memory._promotion_policy == PromotionPolicy.CONSERVATIVE
        assert memory.cold_available == False


# ============================================================================
# Memory Stats Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.memory
class TestMemoryStats:
    """Test memory statistics tracking."""

    @patch("src.company_researcher.memory.dual_layer.ResearchVectorStore")
    @patch("src.company_researcher.memory.dual_layer.CHROMADB_AVAILABLE", False)
    def test_get_stats(self, mock_vector_store):
        """Test getting memory statistics."""
        memory = DualLayerMemory(hot_max_size=100)

        # Do some operations
        memory.remember("key1", "content1", layer=MemoryLayer.HOT)
        memory.recall_key("key1")  # Hit
        memory.recall_key("missing")  # Miss

        stats = memory.get_stats()

        assert "hot_layer" in stats
        assert "total_recalls" in stats
        assert "hot_hits" in stats
        assert stats["total_recalls"] >= 2
