"""
Test Script for Phase 12: Context Engineering

Tests the four context strategies:
- WRITE: Scratchpad and working memory
- SELECT: RAG and memory retrieval
- COMPRESS: Summarization and distillation
- ISOLATE: Multi-agent context separation

Usage:
    python test_phase12_context.py
"""

from src.company_researcher.context.compress_strategy import (
    CompressionLevel,
    ContentType,
    KeyPointExtractor,
    TextCompressor,
)
from src.company_researcher.context.isolate_strategy import (
    AgentContextBuilder,
    ContextIsolationManager,
    ContextVisibility,
)
from src.company_researcher.context.select_strategy import (
    ContextSelector,
    QueryProcessor,
    RetrievalResult,
)
from src.company_researcher.context.write_strategy import NotePriority, Scratchpad


def test_scratchpad_basic():
    """Test basic scratchpad operations."""
    print("=" * 70)
    print("TEST 1: Scratchpad - Basic Operations")
    print("=" * 70)

    scratchpad = Scratchpad(company_name="Tesla")

    # Write various note types
    id1 = scratchpad.write_observation(
        "Tesla reported Q3 2024 revenue of $25.2B",
        agent_source="financial_agent",
        tags=["revenue", "q3_2024"],
    )

    id2 = scratchpad.write_finding(
        "Revenue grew 8% year-over-year",
        agent_source="financial_agent",
        priority=NotePriority.HIGH,
        tags=["growth"],
    )

    id3 = scratchpad.write_hypothesis(
        "EV market expansion driving growth", agent_source="market_agent", confidence=0.7
    )

    print(f"\n  Created {scratchpad.note_count} notes")
    print(f"  Note IDs: {id1}, {id2}, {id3}")

    # Read notes
    findings = scratchpad.read_findings()
    print(f"\n  Findings: {len(findings)}")
    for f in findings:
        print(f"    - [{f.priority.value}] {f.content}")

    # Read by agent
    financial_notes = scratchpad.read_by_agent("financial_agent")
    print(f"\n  Financial agent notes: {len(financial_notes)}")

    # Get summary
    summary = scratchpad.get_summary()
    print(f"\n  Summary: {summary}")

    assert scratchpad.note_count == 3
    assert len(findings) == 1

    print("\n[OK] Scratchpad basic test passed\n")


def test_working_memory():
    """Test working memory operations."""
    print("=" * 70)
    print("TEST 2: Working Memory")
    print("=" * 70)

    scratchpad = Scratchpad(company_name="Tesla")

    # Get working memory for an agent
    memory = scratchpad.get_working_memory("financial_agent")

    # Add thoughts
    memory.add_thought("Starting financial analysis")
    memory.add_thought("Found Q3 revenue data")
    memory.update_focus("Revenue growth analysis")

    # Set variables
    memory.set_variable("revenue_q3", 25.2)
    memory.set_variable("growth_rate", 0.08)

    print(f"\n  Agent: {memory.agent_name}")
    print(f"  Focus: {memory.current_focus}")
    print(f"  Thoughts: {len(memory.chain_of_thought)}")
    print(f"  Variables: {memory.variables}")

    assert memory.get_variable("revenue_q3") == 25.2
    assert len(memory.chain_of_thought) == 2

    print("\n[OK] Working memory test passed\n")


def test_scratchpad_format():
    """Test scratchpad formatting for context."""
    print("=" * 70)
    print("TEST 3: Scratchpad Context Formatting")
    print("=" * 70)

    scratchpad = Scratchpad(company_name="Tesla")

    # Add various notes
    scratchpad.write_finding("Revenue: $25.2B", "financial", NotePriority.HIGH)
    scratchpad.write_finding("Market share: 18%", "market", NotePriority.HIGH)
    scratchpad.write_observation("Competitor X launched new model", "competitive")
    scratchpad.write_question("What is the TAM?", "market")

    # Format for context
    context = scratchpad.format_for_context(max_length=2000)

    print(f"\n  Formatted context ({len(context)} chars):")
    print("  " + "-" * 50)
    print(context[:500])
    print("  ...")

    assert "Tesla" in context
    assert "FINDING" in context

    print("\n[OK] Scratchpad formatting test passed\n")


def test_query_processor():
    """Test query processing."""
    print("=" * 70)
    print("TEST 4: Query Processor")
    print("=" * 70)

    processor = QueryProcessor()

    # Test query expansion
    query = "Tesla revenue growth"
    expanded = processor.expand_query(query)
    print(f"\n  Original: {query}")
    print(f"  Expanded: {expanded}")

    # Test query decomposition
    complex_query = "Tesla revenue and market share analysis"
    decomposed = processor.decompose_query(complex_query)
    print(f"\n  Complex: {complex_query}")
    print(f"  Decomposed: {decomposed}")

    # Test entity extraction
    query = "Apple's revenue in 2024 was $400 billion"
    entities = processor.extract_entities(query)
    print(f"\n  Query: {query}")
    print(f"  Entities: {entities}")

    # Test intent classification
    queries = ["Tesla revenue growth 2024", "market size for EVs", "Tesla vs competitors"]
    print("\n  Intent classification:")
    for q in queries:
        intent = processor.classify_intent(q)
        print(f"    '{q}' -> {intent}")

    assert len(expanded) >= 1
    assert "financial" == processor.classify_intent("revenue growth")

    print("\n[OK] Query processor test passed\n")


def test_context_selector():
    """Test context selector."""
    print("=" * 70)
    print("TEST 5: Context Selector")
    print("=" * 70)

    selector = ContextSelector()  # No memory backend

    print("\n  Created selector without memory backend")
    print("  (Full test requires DualLayerMemory)")

    # Test retrieve (should return empty without memory)
    result = selector.retrieve("Tesla revenue", k=5)
    print(f"\n  Query: 'Tesla revenue'")
    print(f"  Results: {len(result.chunks)}")
    print(f"  Mode: {result.retrieval_mode.value}")

    assert isinstance(result, RetrievalResult)

    print("\n[OK] Context selector test passed\n")


def test_key_point_extractor():
    """Test key point extraction."""
    print("=" * 70)
    print("TEST 6: Key Point Extractor")
    print("=" * 70)

    extractor = KeyPointExtractor()

    text = """
    Tesla reported Q3 2024 revenue of $25.2 billion, representing an 8% increase
    year-over-year. The automotive segment generated $20.1 billion in revenue.
    Energy generation and storage revenue grew 52% to $2.4 billion.
    The company delivered 462,890 vehicles during the quarter.
    Operating margin was 10.8%, down from 17.2% in the prior year.
    Cash and investments totaled $33.6 billion at quarter end.
    """

    key_points = extractor.extract(text, max_points=5, content_type=ContentType.FINANCIAL)

    print(f"\n  Extracted {len(key_points)} key points:")
    for i, point in enumerate(key_points, 1):
        print(f"  {i}. [{point.importance:.2f}] {point.content[:60]}...")
        print(f"     Category: {point.category}, Entities: {point.entities}")

    assert len(key_points) > 0
    assert key_points[0].importance > 0

    print("\n[OK] Key point extractor test passed\n")


def test_text_compressor():
    """Test text compression."""
    print("=" * 70)
    print("TEST 7: Text Compressor")
    print("=" * 70)

    compressor = TextCompressor()

    text = """
    Tesla, Inc. is an American multinational automotive and clean energy company
    headquartered in Austin, Texas. Tesla designs and manufactures electric vehicles,
    battery energy storage, and solar panels. The company was founded in 2003 by
    Martin Eberhard and Marc Tarpenning, and Elon Musk became CEO in 2008. Tesla's
    mission is to accelerate the world's transition to sustainable energy. The company
    reported revenue of $96.8 billion in 2023, with automotive sales comprising the
    majority. Tesla operates Gigafactories in California, Nevada, Texas, Shanghai,
    Berlin, and is constructing one in Mexico. The company has delivered over 5 million
    vehicles worldwide. Tesla's market capitalization makes it one of the most valuable
    automakers globally. The company continues to invest in autonomous driving technology
    and artificial intelligence for its Full Self-Driving feature.
    """

    # Test different compression levels
    for level in [CompressionLevel.MINIMAL, CompressionLevel.MODERATE, CompressionLevel.AGGRESSIVE]:
        result = compressor.compress(text, level=level)
        print(f"\n  {level.value.upper()}:")
        print(f"    Original: {result.original_length} chars")
        print(f"    Compressed: {result.compressed_length} chars")
        print(f"    Ratio: {result.compression_ratio:.2f}")
        print(f"    Preview: {result.compressed_text[:100]}...")

    # Test bullet point compression
    bullets = compressor.compress_to_bullets(text, max_bullets=5)
    print(f"\n  Bullet points ({len(bullets)}):")
    for bullet in bullets[:3]:
        print(f"    {bullet[:70]}...")

    assert result.compressed_length < result.original_length

    print("\n[OK] Text compressor test passed\n")


def test_progressive_summarizer():
    """Test progressive summarization."""
    print("=" * 70)
    print("TEST 8: Progressive Summarizer")
    print("=" * 70)

    from src.company_researcher.context.compress_strategy import ProgressiveSummarizer

    summarizer = ProgressiveSummarizer()

    text = """
    Tesla's Q3 2024 earnings report showed strong performance in several areas.
    Total revenue reached $25.2 billion, an 8% increase from the previous year.
    The automotive segment remained the primary revenue driver at $20.1 billion.
    Energy storage deployment hit record levels with 6.9 GWh deployed.
    Vehicle deliveries totaled 462,890 units for the quarter.
    The company maintained positive free cash flow of $2.7 billion.
    Operating expenses were managed effectively despite increased R&D spending.
    The Cybertruck production ramped up during the quarter.
    Tesla's market position in the EV space remains strong globally.
    The company continues to lead in battery technology and efficiency.
    """

    result = summarizer.summarize_progressive(text, levels=2, final_length=200)

    print(f"\n  Original length: {result['original_length']}")
    print(f"  Levels processed: {len(result['levels'])}")

    for level_info in result["levels"]:
        print(f"\n  Level {level_info['level']}:")
        print(f"    Input: {level_info['input_length']} -> Output: {level_info['output_length']}")
        print(f"    Ratio: {level_info['compression_ratio']:.2f}")

    print(f"\n  Final summary ({result['final_length']} chars):")
    print(f"    {result['final_summary'][:150]}...")

    assert result["final_length"] <= result["original_length"]

    print("\n[OK] Progressive summarizer test passed\n")


def test_context_isolation():
    """Test context isolation manager."""
    print("=" * 70)
    print("TEST 9: Context Isolation Manager")
    print("=" * 70)

    manager = ContextIsolationManager()

    # Create agent contexts
    fin_ctx = manager.create_context("financial_agent", "financial")
    mkt_ctx = manager.create_context("market_agent", "market")

    print("\n  Created financial_agent and market_agent contexts")

    # Add items
    fin_ctx.add("revenue_data", {"q3": 25.2}, visibility=ContextVisibility.TEAM)
    fin_ctx.add("internal_notes", "sensitive", visibility=ContextVisibility.PRIVATE)

    mkt_ctx.add("market_size", {"tam": 500}, visibility=ContextVisibility.TEAM)

    print(f"\n  Financial agent items: {len(fin_ctx.items)}")
    print(f"  Market agent items: {len(mkt_ctx.items)}")

    # Get context for market agent (should see shared items)
    market_context = manager.get_context_for_agent("market_agent")
    print(f"\n  Market agent visible context: {list(market_context.keys())}")

    # Private items should not be visible
    assert "internal_notes" not in market_context

    print("\n[OK] Context isolation test passed\n")


def test_global_context():
    """Test global context management."""
    print("=" * 70)
    print("TEST 10: Global Context")
    print("=" * 70)

    manager = ContextIsolationManager()

    # Add global context
    manager.add_global("company_name", "Tesla", tags=["config"])
    manager.add_global("research_date", "2024-11-01", tags=["config"])

    # Create agents
    manager.create_context("agent1", "financial")
    manager.create_context("agent2", "market")

    # Both should see global
    ctx1 = manager.get_context_for_agent("agent1")
    ctx2 = manager.get_context_for_agent("agent2")

    print(f"\n  Agent1 sees company_name: {'company_name' in ctx1}")
    print(f"  Agent2 sees company_name: {'company_name' in ctx2}")

    assert "company_name" in ctx1
    assert "company_name" in ctx2

    print("\n[OK] Global context test passed\n")


def test_cross_agent_communication():
    """Test cross-agent messaging."""
    print("=" * 70)
    print("TEST 11: Cross-Agent Communication")
    print("=" * 70)

    manager = ContextIsolationManager()

    manager.create_context("financial_agent", "financial")
    manager.create_context("market_agent", "market")
    manager.create_context("synthesizer", "synthesizer")

    # Send message
    msg_id = manager.send_message(
        from_agent="financial_agent",
        to_agent="market_agent",
        message="Revenue data is ready for analysis",
        message_type="notification",
    )

    print(f"\n  Sent message: {msg_id}")

    # Broadcast
    count = manager.broadcast(
        from_agent="synthesizer", message="Starting final synthesis", message_type="broadcast"
    )

    print(f"  Broadcast reached {count} agents")

    # Check stats
    stats = manager.get_stats()
    print(f"\n  Manager stats: {stats['agent_count']} agents")

    assert count > 0

    print("\n[OK] Cross-agent communication test passed\n")


def test_agent_context_builder():
    """Test agent context builder."""
    print("=" * 70)
    print("TEST 12: Agent Context Builder")
    print("=" * 70)

    builder = AgentContextBuilder()

    context = builder.build_for_agent(
        agent_name="financial_agent",
        agent_type="financial",
        company_name="Tesla",
        task_description="Analyze Q3 2024 financial performance",
        max_tokens=2000,
    )

    print(f"\n  Built context ({len(context)} chars):")
    print("  " + "-" * 50)
    print(context[:300])
    print("  ...")

    assert "Tesla" in context
    assert "financial" in context.lower()

    print("\n[OK] Agent context builder test passed\n")


def run_all_tests():
    """Run all Phase 12 tests."""
    print("\n")
    print("*" * 70)
    print("PHASE 12: CONTEXT ENGINEERING - TEST SUITE")
    print("*" * 70)
    print()

    tests = [
        ("Scratchpad - Basic", test_scratchpad_basic),
        ("Working Memory", test_working_memory),
        ("Scratchpad Formatting", test_scratchpad_format),
        ("Query Processor", test_query_processor),
        ("Context Selector", test_context_selector),
        ("Key Point Extractor", test_key_point_extractor),
        ("Text Compressor", test_text_compressor),
        ("Progressive Summarizer", test_progressive_summarizer),
        ("Context Isolation", test_context_isolation),
        ("Global Context", test_global_context),
        ("Cross-Agent Communication", test_cross_agent_communication),
        ("Agent Context Builder", test_agent_context_builder),
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
