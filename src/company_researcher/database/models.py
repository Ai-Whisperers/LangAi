"""
SQLAlchemy Models for Research Data.

Defines the database schema for storing research data including:
- Companies being researched
- Research runs with configuration
- Agent outputs and analysis
- Sources and references
- Cost logging

The schema supports:
- Historical tracking of all research
- Cost analysis per agent/company
- Source deduplication
- Incremental research updates
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ..utils import utc_now

Base = declarative_base()


class Company(Base):
    """
    Company research target.

    Stores basic company information and provides a foreign key
    for research runs. Supports both public and private companies.
    """

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    normalized_name = Column(String(255), index=True)  # Lowercase, no punctuation
    ticker = Column(String(20), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    company_type = Column(String(50), default="unknown")  # public, private, startup
    website = Column(String(500), nullable=True)
    headquarters = Column(String(255), nullable=True)
    founded_year = Column(Integer, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    last_researched_at = Column(DateTime, nullable=True)

    # Relationships
    research_runs = relationship(
        "ResearchRun", back_populates="company", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Company(name='{self.name}', ticker='{self.ticker}')>"

    @classmethod
    def normalize_name(cls, name: str) -> str:
        """Normalize company name for matching."""
        import re

        # Lowercase, remove punctuation, collapse whitespace
        normalized = name.lower()
        normalized = re.sub(r"[^\w\s]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized


class ResearchRun(Base):
    """
    Individual research execution.

    Tracks a complete research workflow including configuration,
    status, timing, and costs.
    """

    __tablename__ = "research_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Run identification
    run_id = Column(String(50), unique=True, index=True)  # UUID or timestamp-based

    # Status tracking
    status = Column(
        String(50), default="pending", index=True
    )  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)
    total_cached_tokens = Column(Integer, default=0)

    # Configuration snapshot
    config_snapshot = Column(JSON, nullable=True)  # Store config at time of run
    workflow_type = Column(String(50), default="parallel")  # parallel, sequential, custom

    # Quality metrics
    quality_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    source_count = Column(Integer, default=0)

    # Metadata
    triggered_by = Column(String(100), nullable=True)  # api, cli, scheduled
    notes = Column(Text, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="research_runs")
    agent_outputs = relationship(
        "AgentOutput", back_populates="research_run", cascade="all, delete-orphan"
    )
    sources = relationship("Source", back_populates="research_run", cascade="all, delete-orphan")
    cost_logs = relationship("CostLog", back_populates="research_run", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_research_runs_company_status", "company_id", "status"),
        Index("ix_research_runs_started_at", "started_at"),
    )

    def __repr__(self):
        return f"<ResearchRun(id={self.id}, company_id={self.company_id}, status='{self.status}')>"

    def mark_completed(self) -> None:
        """Mark run as completed with timing."""
        from datetime import timezone

        self.status = "completed"
        self.completed_at = utc_now()
        if self.started_at:
            # Handle timezone-naive started_at for duration calculation
            started = self.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            self.duration_seconds = (self.completed_at - started).total_seconds()

    def mark_failed(self, error: str) -> None:
        """Mark run as failed with error."""
        from datetime import timezone

        self.status = "failed"
        self.completed_at = utc_now()
        self.error_message = error
        if self.started_at:
            # Handle timezone-naive started_at for duration calculation
            started = self.started_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            self.duration_seconds = (self.completed_at - started).total_seconds()


class AgentOutput(Base):
    """
    Output from individual agents.

    Stores the analysis produced by each agent in a research run,
    along with cost and token metrics.
    """

    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    research_run_id = Column(Integer, ForeignKey("research_runs.id"), nullable=False, index=True)

    # Agent identification
    agent_name = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(50), nullable=True)  # core, financial, market, specialized

    # Output content
    analysis = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=True)  # Extracted structured data

    # Metrics
    cost = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cached_tokens = Column(Integer, default=0)
    execution_time_ms = Column(Integer, nullable=True)

    # Quality
    confidence_score = Column(Float, nullable=True)
    data_freshness = Column(String(50), nullable=True)  # recent, stale, unknown

    # Metadata
    created_at = Column(DateTime, default=utc_now)
    model_used = Column(String(100), nullable=True)
    extra_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved by SQLAlchemy)

    # Relationships
    research_run = relationship("ResearchRun", back_populates="agent_outputs")

    # Indexes
    __table_args__ = (Index("ix_agent_outputs_run_agent", "research_run_id", "agent_name"),)

    def __repr__(self):
        return f"<AgentOutput(agent='{self.agent_name}', run_id={self.research_run_id})>"


class Source(Base):
    """
    Research source/reference.

    Stores sources discovered during research, enabling:
    - Source attribution
    - Deduplication across runs
    - Quality assessment
    """

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    research_run_id = Column(Integer, ForeignKey("research_runs.id"), nullable=False, index=True)

    # Source identification
    url = Column(String(2000), nullable=False)
    url_hash = Column(String(64))  # SHA256 hash for deduplication (indexed below)
    title = Column(String(500), nullable=True)
    domain = Column(String(255), nullable=True)  # Indexed below

    # Content
    content_snippet = Column(Text, nullable=True)
    full_content_hash = Column(String(64), nullable=True)  # For deduplication

    # Quality metrics
    relevance_score = Column(Float, nullable=True)
    credibility_score = Column(Float, nullable=True)
    freshness_date = Column(DateTime, nullable=True)

    # Metadata
    discovered_at = Column(DateTime, default=utc_now)
    discovered_by_agent = Column(String(100), nullable=True)
    source_type = Column(String(50), nullable=True)  # news, official, social, financial

    # Relationships
    research_run = relationship("ResearchRun", back_populates="sources")

    # Indexes
    __table_args__ = (
        Index("ix_sources_url_hash", "url_hash"),
        Index("ix_sources_domain", "domain"),
    )

    def __repr__(self):
        return f"<Source(url='{self.url[:50]}...', run_id={self.research_run_id})>"

    @classmethod
    def compute_url_hash(cls, url: str) -> str:
        """Compute hash of URL for deduplication."""
        import hashlib

        return hashlib.sha256(url.encode()).hexdigest()


class CostLog(Base):
    """
    Detailed API cost logging.

    Provides granular tracking of every API call for
    cost analysis and optimization.
    """

    __tablename__ = "cost_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    research_run_id = Column(Integer, ForeignKey("research_runs.id"), nullable=True, index=True)

    # Call identification (indexed via composite index below)
    model = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=True)

    # Token counts
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cached_tokens = Column(Integer, default=0)

    # Cost
    cost = Column(Float, nullable=False)
    cache_savings = Column(Float, default=0.0)

    # Metadata (indexed below)
    created_at = Column(DateTime, default=utc_now)
    is_batch = Column(Boolean, default=False)
    extra_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved by SQLAlchemy)

    # Relationships
    research_run = relationship("ResearchRun", back_populates="cost_logs")

    # Indexes
    __table_args__ = (
        Index("ix_cost_logs_created_at", "created_at"),
        Index("ix_cost_logs_model_agent", "model", "agent_name"),
    )

    def __repr__(self):
        return f"<CostLog(model='{self.model}', cost=${self.cost:.4f})>"


# Additional utility models


class ResearchCache(Base):
    """
    Cache for research results.

    Enables quick retrieval of recent research without
    re-running the full workflow.
    """

    __tablename__ = "research_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    cache_key = Column(String(100), unique=True, index=True)

    # Cached data
    cached_data = Column(JSON, nullable=False)
    data_version = Column(String(20), default="1.0")

    # Validity
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)

    # Source tracking
    source_run_id = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<ResearchCache(company='{self.company_name}', valid={self.is_valid})>"

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return utc_now() > self.expires_at


class ScheduledResearch(Base):
    """
    Scheduled research tasks.

    Supports periodic research updates for tracked companies.
    """

    __tablename__ = "scheduled_research"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    # Schedule configuration
    schedule_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    cron_expression = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)

    # Execution tracking
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_run_status = Column(String(50), nullable=True)

    # Configuration
    config_override = Column(JSON, nullable=True)
    notification_email = Column(String(255), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=utc_now)
    created_by = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<ScheduledResearch(company_id={self.company_id}, type='{self.schedule_type}')>"
