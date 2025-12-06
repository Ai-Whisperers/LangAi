"""
Test Script for Phase 11: Dual-Layer Memory System

Tests the memory system components:
- LRU cache (hot memory)
- Vector store (cold memory)
- Dual-layer coordination
- Research-specific operations

Usage:
    python test_phase11_memory.py
"""

import time
from datetime import datetime

# Hot layer imports
from src.company_researcher.memory.lru_cache import (
    LRUCache,
    TypedLRUCache,
    ResearchCache,
    CacheStats
)

# Cold layer imports
from src.company_researcher.memory.vector_store import (
    VectorDocument,
    EmbeddingGenerator,
    CHROMADB_AVAILABLE,
    OPENAI_AVAILABLE
)

# Dual-layer imports
from src.company_researcher.memory.dual_layer import (
    DualLayerMemory,
    MemoryLayer,
    PromotionPolicy,
    create_research_memory
)


def test_lru_cache_basic():
    """Test basic LRU cache operations."""
    print("=" * 70)
    print("TEST 1: LRU Cache - Basic Operations")
    print("=" * 70)

    cache = LRUCache(max_size=3)

    # Test put and get
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)

    print(f"\n  Added a=1, b=2, c=3")
    print(f"  Get 'a': {cache.get('a')}")
    print(f"  Get 'b': {cache.get('b')}")
    print(f"  Get 'missing': {cache.get('missing', 'default')}")

    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.get("missing", "default") == "default"

    # Test LRU eviction
    print("\n  Adding d=4 (should evict 'c' as LRU)")
    cache.put("d", 4)

    print(f"  Get 'c' (evicted): {cache.get('c')}")
    print(f"  Get 'd' (new): {cache.get('d')}")

    assert cache.get("c") is None  # Evicted
    assert cache.get("d") == 4

    print("\n[OK] LRU cache basic operations test passed\n")


def test_lru_cache_ttl():
    """Test LRU cache TTL expiration."""
    print("=" * 70)
    print("TEST 2: LRU Cache - TTL Expiration")
    print("=" * 70)

    cache = LRUCache(max_size=10, default_ttl=1)  # 1 second TTL

    cache.put("expires_soon", "value")
    print(f"\n  Added 'expires_soon' with 1 second TTL")
    print(f"  Immediate get: {cache.get('expires_soon')}")

    assert cache.get("expires_soon") == "value"

    print("  Waiting 1.5 seconds...")
    time.sleep(1.5)

    print(f"  After TTL: {cache.get('expires_soon')}")
    assert cache.get("expires_soon") is None

    print("\n[OK] LRU cache TTL test passed\n")


def test_research_cache():
    """Test research-specific cache operations."""
    print("=" * 70)
    print("TEST 3: Research Cache - Type-Aware Caching")
    print("=" * 70)

    cache = ResearchCache(max_size=50)

    # Cache different data types
    cache.cache_company("Tesla", {"overview": "EV company", "ticker": "TSLA"})
    cache.cache_financial("Tesla", {"revenue": 81.5, "profit": 15.0})
    cache.cache_market("Tesla", {"tam": 500, "sam": 200, "som": 50})

    print("\n  Cached Tesla company, financial, and market data")

    # Retrieve data
    company_data = cache.get_company("Tesla")
    financial_data = cache.get_financial("Tesla")
    market_data = cache.get_market("Tesla")

    print(f"  Company data: {company_data}")
    print(f"  Financial data: {financial_data}")
    print(f"  Market data: {market_data}")

    assert company_data is not None
    assert company_data["ticker"] == "TSLA"
    assert financial_data["revenue"] == 81.5

    # Test stats
    stats = cache.stats
    print(f"\n  Cache stats: {stats.hits} hits, {stats.misses} misses")

    print("\n[OK] Research cache test passed\n")


def test_embedding_generator():
    """Test embedding generation."""
    print("=" * 70)
    print("TEST 4: Embedding Generator")
    print("=" * 70)

    generator = EmbeddingGenerator()

    print(f"\n  OpenAI available: {OPENAI_AVAILABLE}")
    print(f"  Real embeddings available: {generator.is_available}")

    # Test embedding generation (fallback or real)
    text = "Tesla is an electric vehicle company"
    embedding = generator.embed(text)

    print(f"  Generated embedding for: '{text[:30]}...'")
    print(f"  Embedding dimensions: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")

    assert len(embedding) > 0
    assert all(isinstance(v, float) for v in embedding)

    # Test batch embedding
    texts = ["Apple makes iPhones", "Google runs search engines"]
    embeddings = generator.embed_batch(texts)

    print(f"\n  Batch embedded {len(texts)} texts")
    print(f"  Got {len(embeddings)} embeddings")

    assert len(embeddings) == 2

    print("\n[OK] Embedding generator test passed\n")


def test_vector_document():
    """Test VectorDocument data class."""
    print("=" * 70)
    print("TEST 5: Vector Document")
    print("=" * 70)

    # Test ID generation
    content1 = "Tesla revenue grew 25% in 2024"
    content2 = "Different content here"

    id1 = VectorDocument.generate_id(content1, "financial")
    id2 = VectorDocument.generate_id(content2, "market")

    print(f"\n  Generated ID for content1: {id1}")
    print(f"  Generated ID for content2: {id2}")

    assert id1 != id2
    assert id1.startswith("financial_")
    assert id2.startswith("market_")

    # Same content generates same ID
    id1_repeat = VectorDocument.generate_id(content1, "financial")
    assert id1 == id1_repeat
    print(f"  Same content generates same ID: {id1 == id1_repeat}")

    print("\n[OK] Vector document test passed\n")


def test_vector_store():
    """Test vector store operations."""
    print("=" * 70)
    print("TEST 6: Vector Store (ChromaDB)")
    print("=" * 70)

    if not CHROMADB_AVAILABLE:
        print("\n  [SKIP] ChromaDB not installed")
        print("  Install with: pip install chromadb")
        print("\n[OK] Test skipped (ChromaDB not available)\n")
        return

    from src.company_researcher.memory.vector_store import VectorStore

    # Use in-memory store for testing
    store = VectorStore(collection_name="test_collection")

    print(f"\n  Created test collection")
    print(f"  Initial count: {store.count}")

    # Add documents
    store.add("doc1", "Tesla is an electric vehicle manufacturer", {"company": "tesla"})
    store.add("doc2", "Apple designs and sells consumer electronics", {"company": "apple"})
    store.add("doc3", "Microsoft develops software products", {"company": "microsoft"})

    print(f"  Added 3 documents, count: {store.count}")
    assert store.count == 3

    # Search
    results = store.search("electric cars", k=2)
    print(f"\n  Search 'electric cars': {len(results)} results")

    if results:
        print(f"  Top result: {results[0].document.content[:50]}...")
        print(f"  Score: {results[0].score:.3f}")

    # Get by ID
    doc = store.get("doc1")
    print(f"\n  Get 'doc1': {doc.content[:30] if doc else 'Not found'}...")

    # Clear
    cleared = store.clear()
    print(f"\n  Cleared {cleared} documents")
    assert store.count == 0

    print("\n[OK] Vector store test passed\n")


def test_dual_layer_basic():
    """Test dual-layer memory basic operations."""
    print("=" * 70)
    print("TEST 7: Dual-Layer Memory - Basic Operations")
    print("=" * 70)

    # Create memory with in-memory cold layer
    memory = DualLayerMemory(
        hot_max_size=100,
        hot_ttl=3600,
        cold_persist_dir=None  # In-memory
    )

    print(f"\n  Cold layer available: {memory.cold_available}")

    # Store in both layers
    memory.remember(
        key="tesla_overview",
        content="Tesla Inc. is an American electric vehicle and clean energy company.",
        metadata={"company": "tesla", "type": "overview"},
        company_name="Tesla",
        data_type="overview"
    )

    print("  Stored 'tesla_overview' in both layers")

    # Recall by key
    item = memory.recall_key("tesla_overview")
    print(f"\n  Recalled by key: {item is not None}")
    if item:
        print(f"  Content preview: {item.content[:40]}...")
        print(f"  Layer: {item.layer.value}")

    assert item is not None
    assert "Tesla" in item.content

    print("\n[OK] Dual-layer basic test passed\n")


def test_dual_layer_semantic_search():
    """Test dual-layer semantic search."""
    print("=" * 70)
    print("TEST 8: Dual-Layer Memory - Semantic Search")
    print("=" * 70)

    if not CHROMADB_AVAILABLE:
        print("\n  [SKIP] ChromaDB not installed")
        print("\n[OK] Test skipped\n")
        return

    memory = DualLayerMemory(hot_max_size=100)

    # Store multiple research items
    memory.remember_research(
        company_name="Tesla",
        data_type="financial",
        content="Tesla reported Q3 2024 revenue of $25.2 billion, up 8% year-over-year."
    )

    memory.remember_research(
        company_name="Tesla",
        data_type="market",
        content="The global EV market is expected to reach $1.3 trillion by 2030."
    )

    memory.remember_research(
        company_name="Apple",
        data_type="financial",
        content="Apple's services revenue exceeded $24 billion in the quarter."
    )

    print("\n  Stored 3 research items")

    # Semantic search
    results = memory.recall_similar("electric vehicle revenue growth", k=3)
    print(f"\n  Search 'electric vehicle revenue growth': {len(results)} results")

    for i, item in enumerate(results):
        print(f"  {i+1}. Score: {item.score:.3f} - {item.content[:50]}...")

    # Company-specific recall
    tesla_items = memory.recall_company("Tesla")
    print(f"\n  Tesla items: {len(tesla_items)}")

    # Stats
    stats = memory.get_stats()
    print(f"\n  Hot hits: {stats['hot_hits']}")
    print(f"  Cold hits: {stats['cold_hits']}")

    print("\n[OK] Dual-layer semantic search test passed\n")


def test_promotion_policy():
    """Test promotion from cold to hot layer."""
    print("=" * 70)
    print("TEST 9: Promotion Policy")
    print("=" * 70)

    memory = DualLayerMemory(
        hot_max_size=100,
        promotion_policy=PromotionPolicy.MODERATE,
        promotion_threshold=2
    )

    print(f"\n  Policy: MODERATE (threshold=2)")

    # Store in cold only
    if memory.cold_available:
        memory.remember(
            key="test_promotion",
            content="Content that might get promoted",
            layer=MemoryLayer.COLD
        )

        # Access multiple times
        for i in range(3):
            item = memory.recall_key("test_promotion")
            if item:
                print(f"  Access {i+1}: Layer={item.layer.value}, Count={item.access_count}")

        stats = memory.get_stats()
        print(f"\n  Promotions: {stats['promotions']}")
    else:
        print("  [SKIP] Cold layer not available")

    print("\n[OK] Promotion policy test passed\n")


def test_factory_function():
    """Test factory function for creating memory."""
    print("=" * 70)
    print("TEST 10: Factory Function")
    print("=" * 70)

    memory = create_research_memory(
        persist_dir="./test_data/memory",
        hot_size=200,
        hot_ttl=3600,
        promotion_policy="aggressive"
    )

    print(f"\n  Created memory with factory function")
    print(f"  Hot max size: {memory._hot._max_size}")
    print(f"  Cold available: {memory.cold_available}")
    print(f"  Promotion policy: {memory._promotion_policy.value}")

    assert memory._hot._max_size == 200

    print("\n[OK] Factory function test passed\n")


def run_all_tests():
    """Run all Phase 11 tests."""
    print("\n")
    print("*" * 70)
    print("PHASE 11: DUAL-LAYER MEMORY SYSTEM - TEST SUITE")
    print("*" * 70)
    print()

    tests = [
        ("LRU Cache - Basic", test_lru_cache_basic),
        ("LRU Cache - TTL", test_lru_cache_ttl),
        ("Research Cache", test_research_cache),
        ("Embedding Generator", test_embedding_generator),
        ("Vector Document", test_vector_document),
        ("Vector Store", test_vector_store),
        ("Dual-Layer - Basic", test_dual_layer_basic),
        ("Dual-Layer - Semantic Search", test_dual_layer_semantic_search),
        ("Promotion Policy", test_promotion_policy),
        ("Factory Function", test_factory_function),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "PASSED", None))
        except Exception as e:
            results.append((test_name, "FAILED", str(e)))
            import traceback
            traceback.print_exc()

    # Print summary
    print("\n")
    print("*" * 70)
    print("TEST SUMMARY")
    print("*" * 70)
    print()

    passed = sum(1 for _, status, _ in results if status == "PASSED")
    failed = sum(1 for _, status, _ in results if status == "FAILED")

    for test_name, status, error in results:
        symbol = "[PASS]" if status == "PASSED" else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")
        if error:
            print(f"  Error: {error}")

    print()
    print(f"Tests Passed: {passed}/{len(results)}")
    print(f"Tests Failed: {failed}/{len(results)}")

    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED")
    else:
        print(f"\n[FAILURE] {failed} TEST(S) FAILED")

    print("\n")


if __name__ == "__main__":
    run_all_tests()
