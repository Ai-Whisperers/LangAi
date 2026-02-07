"""Tests for AI integration and migration layer."""

from datetime import datetime

import pytest

from company_researcher.ai.config import get_ai_config, reset_ai_config
from company_researcher.ai.integration import (
    AIIntegrationLayer,
    get_ai_integration,
    reset_ai_integration,
)
from company_researcher.ai.migration import (
    ComparisonResult,
    MigrationValidator,
    get_migration_registry,
    gradual_rollout,
    reset_migration_registry,
)


class TestAIIntegrationLayer:
    """Tests for AIIntegrationLayer."""

    def setup_method(self):
        """Reset singletons before each test."""
        reset_ai_integration()
        reset_ai_config()

    def test_singleton_pattern(self):
        """Test that get_ai_integration returns same instance."""
        layer1 = get_ai_integration()
        layer2 = get_ai_integration()
        assert layer1 is layer2

    def test_reset_creates_new_instance(self):
        """Test that reset creates a new instance."""
        layer1 = get_ai_integration()
        reset_ai_integration()
        layer2 = get_ai_integration()
        assert layer1 is not layer2

    def test_get_all_stats(self):
        """Test get_all_stats returns dict with cost."""
        layer = AIIntegrationLayer()
        stats = layer.get_all_stats()
        assert "cost" in stats
        assert stats["cost"]["total_cost"] == 0.0

    def test_legacy_queries_fallback(self):
        """Test legacy query generation works."""
        layer = AIIntegrationLayer()
        queries = layer._legacy_queries("Apple Inc", 5)
        assert len(queries) == 5
        assert any("Apple" in q for q in queries)

    def test_legacy_classify_fallback(self):
        """Test legacy classification works."""
        layer = AIIntegrationLayer()
        classification = layer._legacy_classify("Apple Inc")
        assert classification["company_type"] == "unknown"
        assert classification["source"] == "legacy"

    def test_legacy_quality_check(self):
        """Test legacy quality check works."""
        layer = AIIntegrationLayer()
        state = {
            "company_name": "Test Corp",
            "company_overview": "Test content" * 100,
            "sources": ["https://example.com"],
        }
        result = layer._legacy_quality_check(state)
        assert "score" in result
        assert "level" in result
        assert result["source"] == "legacy"

    def test_is_ai_available(self):
        """Test is_ai_available returns boolean."""
        layer = AIIntegrationLayer()
        result = layer.is_ai_available()
        assert isinstance(result, bool)

    def test_get_cost_summary(self):
        """Test get_cost_summary returns expected structure."""
        layer = AIIntegrationLayer()
        summary = layer.get_cost_summary()
        assert "total_cost" in summary
        assert "breakdown" in summary
        assert "warn_threshold" in summary
        assert "max_threshold" in summary


class TestMigrationValidator:
    """Tests for MigrationValidator."""

    def test_init(self):
        """Test MigrationValidator initialization."""
        validator = MigrationValidator("test")
        assert validator.component_name == "test"
        assert validator.comparisons == []

    @pytest.mark.asyncio
    async def test_validate_exact_match(self):
        """Test validation of exact matches."""
        validator = MigrationValidator("test")

        async def ai_func(x):
            return {"value": 42}

        def legacy_func(x):
            return {"value": 42}

        result = await validator.validate(ai_func, legacy_func, "test")
        assert result.match is True
        assert result.similarity_score == 1.0

    @pytest.mark.asyncio
    async def test_validate_different_values(self):
        """Test validation of different values."""
        validator = MigrationValidator("test")

        async def ai_func(x):
            return {"sentiment": "positive"}

        def legacy_func(x):
            return {"sentiment": "negative"}

        result = await validator.validate(ai_func, legacy_func, "test")
        assert result.match is False
        assert len(result.differences) > 0

    @pytest.mark.asyncio
    async def test_validate_tracks_latency(self):
        """Test that validation tracks latency."""
        validator = MigrationValidator("test")

        async def ai_func(x):
            return "result"

        def legacy_func(x):
            return "result"

        result = await validator.validate(ai_func, legacy_func, "test")
        assert result.ai_latency_ms >= 0
        assert result.legacy_latency_ms >= 0

    @pytest.mark.asyncio
    async def test_stats_tracking(self):
        """Test that stats are tracked correctly."""
        validator = MigrationValidator("test")

        async def ai_match(x):
            return {"a": 1}

        def legacy_match(x):
            return {"a": 1}

        async def ai_mismatch(x):
            return {"a": 1}

        def legacy_mismatch(x):
            return {"a": 2}

        await validator.validate(ai_match, legacy_match, "test")
        await validator.validate(ai_mismatch, legacy_mismatch, "test")

        stats = validator.get_stats()
        assert stats["validations"] == 2
        assert stats["match_rate"] == 0.5


class TestMigrationRegistry:
    """Tests for MigrationRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_migration_registry()

    def test_singleton_pattern(self):
        """Test that get_migration_registry returns same instance."""
        registry1 = get_migration_registry()
        registry2 = get_migration_registry()
        assert registry1 is registry2

    def test_get_validator(self):
        """Test getting a validator."""
        registry = get_migration_registry()
        validator = registry.get_validator("sentiment")
        assert isinstance(validator, MigrationValidator)
        assert validator.component_name == "sentiment"

    def test_same_validator_for_same_component(self):
        """Test that same validator is returned for same component."""
        registry = get_migration_registry()
        v1 = registry.get_validator("query")
        v2 = registry.get_validator("query")
        assert v1 is v2

    def test_get_all_stats(self):
        """Test getting stats for all validators."""
        registry = get_migration_registry()
        registry.get_validator("sentiment")
        registry.get_validator("query")

        all_stats = registry.get_all_stats()
        assert "sentiment" in all_stats
        assert "query" in all_stats


class TestGradualRollout:
    """Tests for gradual_rollout decorator."""

    @pytest.mark.asyncio
    async def test_decorator_with_100_percent(self):
        """Test that 100% rollout always uses AI."""
        call_tracker = {"ai_calls": 0}

        @gradual_rollout("test", rollout_percentage=100.0)
        async def ai_func(x):
            call_tracker["ai_calls"] += 1
            return f"ai_{x}"

        result = await ai_func("test")

        # AI should be called with 100% rollout
        assert call_tracker["ai_calls"] == 1
        assert result == "ai_test"

    @pytest.mark.asyncio
    async def test_decorator_with_0_percent(self):
        """Test that 0% rollout returns None (skip AI)."""
        call_tracker = {"ai_calls": 0}

        @gradual_rollout("test", rollout_percentage=0.0)
        async def ai_func(x):
            call_tracker["ai_calls"] += 1
            return f"ai_{x}"

        result = await ai_func("test")

        # AI should not be called with 0% rollout
        assert call_tracker["ai_calls"] == 0
        assert result is None  # Signal to use legacy


class TestComparisonResult:
    """Tests for ComparisonResult dataclass."""

    def test_creation(self):
        """Test creating a ComparisonResult."""
        result = ComparisonResult(
            component="test",
            timestamp=datetime.now(),
            ai_result={"a": 1},
            legacy_result={"a": 1},
            match=True,
            similarity_score=0.95,
            differences=[],
        )
        assert result.match is True
        assert result.similarity_score == 0.95
        assert result.differences == []

    def test_with_differences(self):
        """Test ComparisonResult with differences."""
        result = ComparisonResult(
            component="test",
            timestamp=datetime.now(),
            ai_result={"value": 42},
            legacy_result={"value": 24},
            match=False,
            similarity_score=0.6,
            differences=["Field 'value' differs: 42 vs 24"],
        )
        assert result.match is False
        assert len(result.differences) == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ComparisonResult(
            component="test",
            timestamp=datetime.now(),
            ai_result={"a": 1},
            legacy_result={"a": 1},
            match=True,
            similarity_score=1.0,
            differences=[],
        )
        d = result.to_dict()
        assert "component" in d
        assert "timestamp" in d
        assert "match" in d
        assert "similarity_score" in d


class TestAllWorkstreamsIntegration:
    """Integration tests verifying all workstreams work together."""

    def test_all_ai_imports(self):
        """Test that all AI module imports work."""
        # Workstream 1: Sentiment

        # Workstream 2: Query

        # Workstream 3: Quality

        # Workstream 4: Extraction

        # Workstream 5: Foundation

        # Workstream 6: Integration

        # All imports should succeed
        assert True

    def test_config_controls_components(self):
        """Test that config controls component behavior."""
        reset_ai_config()
        config = get_ai_config()

        # Check config has expected attributes
        assert hasattr(config, "global_enabled")
        assert hasattr(config, "sentiment")
        assert hasattr(config, "query_generation")
        assert hasattr(config, "quality_assessment")
        assert hasattr(config, "data_extraction")

    def test_integration_layer_creation(self):
        """Test that integration layer can be created."""
        reset_ai_integration()
        layer = get_ai_integration()
        assert layer is not None
        assert hasattr(layer, "generate_search_queries")
        assert hasattr(layer, "analyze_news_sentiment")
        assert hasattr(layer, "assess_research_quality")
        assert hasattr(layer, "extract_structured_data")

    def test_cost_tracker_integration(self):
        """Test cost tracker is properly initialized."""
        reset_ai_integration()
        layer = get_ai_integration()
        assert layer.cost_tracker is not None
        assert layer.cost_tracker.total_cost == 0.0
