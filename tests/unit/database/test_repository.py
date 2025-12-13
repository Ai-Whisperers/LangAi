"""
Tests for Database Repository.

Tests the ResearchRepository class including:
- Company CRUD operations
- Research run management
- Agent output storage
- Source bulk operations (N+1 fix verification)
- Cost logging
- Connection pooling
"""

import pytest

from company_researcher.database.models import (
    Company,
    ResearchRun,
    AgentOutput,
    Source,
)
from company_researcher.database.repository import ResearchRepository


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def in_memory_repo():
    """Create repository with in-memory SQLite database."""
    # Tables are created automatically in __init__ via Base.metadata.create_all()
    repo = ResearchRepository(database_url="sqlite:///:memory:")
    return repo


@pytest.fixture
def sample_company():
    """Sample company data."""
    return {
        "name": "TestCorp Inc.",
        "ticker": "TEST",
        "industry": "Technology",
        "company_type": "public",
        "website": "https://testcorp.com",
        "headquarters": "San Francisco, CA",
        "founded_year": 2010
    }


@pytest.fixture
def sample_sources():
    """Sample source data for bulk operations."""
    return [
        {
            "url": "https://example.com/article1",
            "title": "Article 1",
            "content": "Content about the company",
            "score": 0.95
        },
        {
            "url": "https://example.com/article2",
            "title": "Article 2",
            "content": "More content about the company",
            "score": 0.85
        },
        {
            "url": "https://example.com/article3",
            "title": "Article 3",
            "content": "Additional information",
            "score": 0.75
        }
    ]


@pytest.fixture
def sample_agent_output():
    """Sample agent output data."""
    return {
        "agent_name": "researcher",
        "agent_type": "core",
        "analysis": "Test analysis content",
        "structured_data": {"key": "value"},
        "cost": 0.001,
        "input_tokens": 100,
        "output_tokens": 50,
        "model": "gpt-4"
    }


# ============================================================================
# Company Tests
# ============================================================================

class TestCompanyOperations:
    """Tests for company CRUD operations."""

    def test_create_company(self, in_memory_repo, sample_company):
        """Test company creation."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])

        assert company is not None
        assert company.name == sample_company["name"]
        assert company.id is not None

    def test_get_existing_company(self, in_memory_repo, sample_company):
        """Test retrieving existing company."""
        # Create company first
        company1 = in_memory_repo.get_or_create_company(sample_company["name"])

        # Get same company again
        company2 = in_memory_repo.get_or_create_company(sample_company["name"])

        assert company1.id == company2.id
        assert company1.name == company2.name

    def test_company_name_normalization(self, in_memory_repo):
        """Test company name normalization."""
        # Create with different case
        company1 = in_memory_repo.get_or_create_company("TestCorp Inc.")
        company2 = in_memory_repo.get_or_create_company("testcorp inc.")

        # Should be same company due to normalization
        assert company1.id == company2.id

    def test_company_with_ticker(self, in_memory_repo):
        """Test company creation with ticker."""
        company = in_memory_repo.get_or_create_company(
            "Apple Inc.",
            ticker="AAPL"
        )

        assert company.ticker == "AAPL"


# ============================================================================
# Research Run Tests
# ============================================================================

class TestResearchRunOperations:
    """Tests for research run management."""

    def test_create_research_run(self, in_memory_repo, sample_company):
        """Test research run creation."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        assert run is not None
        assert run.company_id == company.id
        assert run.status == "running"
        assert run.run_id is not None

    def test_update_research_run_status(self, in_memory_repo, sample_company):
        """Test updating research run status."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Update status
        in_memory_repo.update_run_status(run.id, "completed")

        # Verify status updated
        updated_run = in_memory_repo.get_research_run(run.id)
        assert updated_run.status == "completed"

    def test_update_research_run_metrics(self, in_memory_repo, sample_company):
        """Test updating research run metrics."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Update metrics
        in_memory_repo.update_run_metrics(
            run.id,
            total_cost=0.05,
            total_input_tokens=1000,
            total_output_tokens=500,
            quality_score=85.5
        )

        # Verify metrics
        updated_run = in_memory_repo.get_research_run(run.id)
        assert updated_run.total_cost == 0.05
        assert updated_run.total_input_tokens == 1000
        assert updated_run.total_output_tokens == 500
        assert updated_run.quality_score == 85.5

    def test_get_latest_run_for_company(self, in_memory_repo, sample_company):
        """Test getting latest research run for company."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])

        # Create multiple runs
        run1 = in_memory_repo.create_research_run(sample_company["name"])
        run2 = in_memory_repo.create_research_run(sample_company["name"])
        run3 = in_memory_repo.create_research_run(sample_company["name"])

        # Get latest
        latest = in_memory_repo.get_latest_run(company.id)

        assert latest.id == run3.id


# ============================================================================
# Agent Output Tests
# ============================================================================

class TestAgentOutputOperations:
    """Tests for agent output storage."""

    def test_save_agent_output(self, in_memory_repo, sample_company, sample_agent_output):
        """Test saving agent output."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        output_id = in_memory_repo.save_agent_output(
            research_run_id=run.id,
            agent_name=sample_agent_output["agent_name"],
            agent_type=sample_agent_output["agent_type"],
            analysis=sample_agent_output["analysis"],
            structured_data=sample_agent_output["structured_data"],
            cost=sample_agent_output["cost"],
            input_tokens=sample_agent_output["input_tokens"],
            output_tokens=sample_agent_output["output_tokens"],
            model=sample_agent_output["model"]
        )

        assert output_id is not None

    def test_save_agent_output_with_metadata(self, in_memory_repo, sample_company):
        """Test saving agent output with extra_metadata (renamed from metadata)."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        metadata = {"custom_field": "custom_value", "version": "1.0"}

        output_id = in_memory_repo.save_agent_output(
            research_run_id=run.id,
            agent_name="test_agent",
            agent_type="test",
            analysis="Test analysis",
            metadata=metadata  # Should be stored in extra_metadata column
        )

        assert output_id is not None

    def test_get_agent_outputs_for_run(self, in_memory_repo, sample_company):
        """Test retrieving all agent outputs for a run."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Save multiple outputs
        for agent in ["researcher", "financial", "market"]:
            in_memory_repo.save_agent_output(
                research_run_id=run.id,
                agent_name=agent,
                analysis=f"Analysis from {agent}"
            )

        # Get all outputs
        outputs = in_memory_repo.get_agent_outputs(run.id)

        assert len(outputs) == 3
        agent_names = [o.agent_name for o in outputs]
        assert "researcher" in agent_names
        assert "financial" in agent_names
        assert "market" in agent_names


# ============================================================================
# Source Bulk Operations Tests (N+1 Fix Verification)
# ============================================================================

class TestSourceBulkOperations:
    """Tests for source bulk operations including N+1 fix verification."""

    def test_save_sources_bulk_basic(self, in_memory_repo, sample_company, sample_sources):
        """Test basic bulk source saving."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        saved_count = in_memory_repo.save_sources_bulk(run.id, sample_sources)

        assert saved_count == 3

    def test_save_sources_bulk_deduplication(self, in_memory_repo, sample_company, sample_sources):
        """Test that duplicate sources are not saved twice."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Save sources first time
        first_count = in_memory_repo.save_sources_bulk(run.id, sample_sources)

        # Save same sources again
        second_count = in_memory_repo.save_sources_bulk(run.id, sample_sources)

        # First save should add all, second should add none (duplicates)
        assert first_count == 3
        assert second_count == 0

    def test_save_sources_bulk_partial_duplicates(self, in_memory_repo, sample_company, sample_sources):
        """Test saving sources with some duplicates."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Save first batch
        in_memory_repo.save_sources_bulk(run.id, sample_sources[:2])

        # Save batch with 1 duplicate and 1 new
        new_sources = [
            sample_sources[1],  # Duplicate
            {"url": "https://example.com/article4", "title": "New Article"}
        ]

        second_count = in_memory_repo.save_sources_bulk(run.id, new_sources)

        # Should only add the new one
        assert second_count == 1

    def test_save_sources_bulk_empty_list(self, in_memory_repo, sample_company):
        """Test saving empty source list."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        saved_count = in_memory_repo.save_sources_bulk(run.id, [])

        assert saved_count == 0

    def test_save_sources_bulk_updates_run_count(self, in_memory_repo, sample_company, sample_sources):
        """Test that bulk save updates research run source count."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Save sources
        in_memory_repo.save_sources_bulk(run.id, sample_sources)

        # Verify run source count updated
        updated_run = in_memory_repo.get_research_run(run.id)
        assert updated_run.source_count == 3

    def test_save_sources_bulk_no_url(self, in_memory_repo, sample_company):
        """Test handling sources without URLs."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        sources = [
            {"title": "No URL"},
            {"url": "", "title": "Empty URL"},
            {"url": "https://valid.com", "title": "Valid URL"}
        ]

        saved_count = in_memory_repo.save_sources_bulk(run.id, sources)

        # Should only save the one with valid URL
        assert saved_count == 1

    @pytest.mark.parametrize("source_count", [10, 50, 100])
    def test_save_sources_bulk_performance(self, in_memory_repo, sample_company, source_count):
        """Test bulk saving with various source counts."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        sources = [
            {
                "url": f"https://example.com/article{i}",
                "title": f"Article {i}",
                "content": f"Content for article {i}"
            }
            for i in range(source_count)
        ]

        saved_count = in_memory_repo.save_sources_bulk(run.id, sources)

        assert saved_count == source_count


# ============================================================================
# Cost Logging Tests
# ============================================================================

class TestCostLogging:
    """Tests for cost logging operations."""

    def test_log_cost(self, in_memory_repo, sample_company):
        """Test logging API cost."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        in_memory_repo.log_cost(
            research_run_id=run.id,
            model="gpt-4",
            agent_name="researcher",
            input_tokens=100,
            output_tokens=50,
            cost=0.005
        )

        # Verify cost logged
        costs = in_memory_repo.get_cost_logs(run.id)
        assert len(costs) == 1
        assert costs[0].model == "gpt-4"
        assert costs[0].cost == 0.005

    def test_get_total_cost_for_run(self, in_memory_repo, sample_company):
        """Test getting total cost for a research run."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Log multiple costs
        costs = [0.005, 0.003, 0.002]
        for i, cost in enumerate(costs):
            in_memory_repo.log_cost(
                research_run_id=run.id,
                model="gpt-4",
                agent_name=f"agent_{i}",
                input_tokens=100,
                output_tokens=50,
                cost=cost
            )

        total = in_memory_repo.get_total_cost(run.id)

        assert abs(total - sum(costs)) < 0.0001


# ============================================================================
# Connection Pool Tests
# ============================================================================

class TestConnectionPooling:
    """Tests for connection pooling configuration."""

    def test_repository_uses_connection_pool(self):
        """Verify repository uses connection pooling."""
        repo = ResearchRepository(database_url="sqlite:///:memory:")

        # Check engine pool configuration
        pool = repo.engine.pool
        assert pool is not None

    def test_session_context_manager(self, in_memory_repo):
        """Test session context manager properly releases connections."""
        with in_memory_repo.get_session() as session:
            # Session should be active
            assert session is not None

            # Perform a simple query (SQLAlchemy 2.x requires text())
            from sqlalchemy import text
            result = session.execute(text("SELECT 1"))
            assert result is not None


# ============================================================================
# Model Tests
# ============================================================================

class TestModels:
    """Tests for SQLAlchemy models."""

    def test_company_normalize_name(self):
        """Test Company.normalize_name method."""
        assert Company.normalize_name("TestCorp Inc.") == "testcorp inc"
        assert Company.normalize_name("Test Corp!") == "test corp"
        assert Company.normalize_name("Test  Corp") == "test corp"

    def test_source_compute_url_hash(self):
        """Test Source.compute_url_hash method."""
        url = "https://example.com/article"
        hash1 = Source.compute_url_hash(url)
        hash2 = Source.compute_url_hash(url)

        # Same URL should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_research_run_mark_completed(self, in_memory_repo, sample_company):
        """Test ResearchRun.mark_completed method."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Complete the run
        with in_memory_repo.get_session() as session:
            db_run = session.query(ResearchRun).filter_by(id=run.id).first()
            db_run.mark_completed()
            session.commit()

        # Verify completion
        updated_run = in_memory_repo.get_research_run(run.id)
        assert updated_run.status == "completed"
        assert updated_run.completed_at is not None
        assert updated_run.duration_seconds is not None

    def test_research_run_mark_failed(self, in_memory_repo, sample_company):
        """Test ResearchRun.mark_failed method."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Fail the run
        error_msg = "Test error message"
        with in_memory_repo.get_session() as session:
            db_run = session.query(ResearchRun).filter_by(id=run.id).first()
            db_run.mark_failed(error_msg)
            session.commit()

        # Verify failure
        updated_run = in_memory_repo.get_research_run(run.id)
        assert updated_run.status == "failed"
        assert updated_run.error_message == error_msg

    def test_agent_output_extra_metadata_column(self, in_memory_repo, sample_company):
        """Test AgentOutput uses extra_metadata instead of metadata."""
        company = in_memory_repo.get_or_create_company(sample_company["name"])
        run = in_memory_repo.create_research_run(sample_company["name"])

        # Create agent output with metadata
        with in_memory_repo.get_session() as session:
            output = AgentOutput(
                research_run_id=run.id,
                agent_name="test",
                analysis="Test",
                extra_metadata={"test": "value"}  # Using renamed column
            )
            session.add(output)
            session.commit()
            output_id = output.id

        # Verify metadata stored correctly
        with in_memory_repo.get_session() as session:
            retrieved = session.query(AgentOutput).filter_by(id=output_id).first()
            assert retrieved.extra_metadata == {"test": "value"}
