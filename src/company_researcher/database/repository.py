"""
Database Repository for Research Operations.

Provides a high-level interface for database operations with:
- Connection pooling
- Transaction management
- Query helpers
- Singleton pattern for shared access

Usage:
    from company_researcher.database import get_repository

    repo = get_repository()

    # Create a research run
    run = repo.create_research_run("Tesla")

    # Save agent output
    repo.save_agent_output(
        research_run_id=run.id,
        agent_name="financial",
        analysis="...",
        cost=0.05
    )

    # Get recent research
    recent = repo.get_recent_research("Tesla", limit=5)
"""

import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from ..utils import utc_now
from .models import AgentOutput, Base, Company, CostLog, ResearchCache, ResearchRun, Source


class ResearchRepository:
    """
    Repository for research data operations.

    Provides a clean interface for database operations with
    automatic session management and connection pooling.
    """

    def __init__(
        self, database_url: Optional[str] = None, pool_size: int = 5, max_overflow: int = 10
    ):
        """
        Initialize the repository.

        Args:
            database_url: Database connection URL. If None, uses config.
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
        """
        if database_url is None:
            from ..config import get_config

            config = get_config()
            database_url = getattr(config, "database_url", None)

            if database_url is None:
                # Default to SQLite if no PostgreSQL configured
                database_url = "sqlite:///./research_data.db"

        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Verify connections before use
        )

        self.SessionFactory = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session context manager.

        Automatically handles commit/rollback and session cleanup.

        Yields:
            SQLAlchemy Session

        Example:
            with repo.get_session() as session:
                company = session.query(Company).first()
        """
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # =========================================================================
    # Company Operations
    # =========================================================================

    def get_or_create_company(
        self,
        name: str,
        ticker: Optional[str] = None,
        industry: Optional[str] = None,
        company_type: str = "unknown",
    ) -> Company:
        """
        Get existing company or create new one.

        Args:
            name: Company name
            ticker: Stock ticker (if public)
            industry: Industry classification
            company_type: Type (public, private, startup)

        Returns:
            Company instance
        """
        normalized = Company.normalize_name(name)

        with self.get_session() as session:
            company = session.query(Company).filter(Company.normalized_name == normalized).first()

            if company is None:
                company = Company(
                    name=name,
                    normalized_name=normalized,
                    ticker=ticker,
                    industry=industry,
                    company_type=company_type,
                )
                session.add(company)
                session.flush()

            # Refresh to get updated values
            session.refresh(company)
            # Detach from session
            session.expunge(company)

            return company

    def get_company(self, name: str) -> Optional[Company]:
        """Get company by name."""
        normalized = Company.normalize_name(name)
        with self.get_session() as session:
            company = session.query(Company).filter(Company.normalized_name == normalized).first()
            if company:
                session.expunge(company)
            return company

    def get_company_by_ticker(self, ticker: str) -> Optional[Company]:
        """Get company by stock ticker."""
        with self.get_session() as session:
            company = session.query(Company).filter(Company.ticker == ticker.upper()).first()
            if company:
                session.expunge(company)
            return company

    def update_company(self, name: str, **updates) -> Optional[Company]:
        """Update company attributes."""
        normalized = Company.normalize_name(name)
        with self.get_session() as session:
            company = session.query(Company).filter(Company.normalized_name == normalized).first()

            if company:
                for key, value in updates.items():
                    if hasattr(company, key):
                        setattr(company, key, value)
                session.flush()
                session.refresh(company)
                session.expunge(company)

            return company

    # =========================================================================
    # Research Run Operations
    # =========================================================================

    def create_research_run(
        self,
        company_name: str,
        config_snapshot: Optional[Dict] = None,
        workflow_type: str = "parallel",
        triggered_by: str = "api",
    ) -> ResearchRun:
        """
        Create a new research run.

        Args:
            company_name: Company to research
            config_snapshot: Configuration at time of run
            workflow_type: Type of workflow
            triggered_by: How the run was triggered

        Returns:
            ResearchRun instance
        """
        company = self.get_or_create_company(company_name)

        run_id = f"{utc_now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        with self.get_session() as session:
            run = ResearchRun(
                company_id=company.id,
                run_id=run_id,
                status="running",
                config_snapshot=config_snapshot,
                workflow_type=workflow_type,
                triggered_by=triggered_by,
            )
            session.add(run)
            session.flush()
            session.refresh(run)
            session.expunge(run)

            # Update company last researched
            session.query(Company).filter(Company.id == company.id).update(
                {"last_researched_at": utc_now()}
            )

            return run

    def get_research_run(self, run_id) -> Optional[ResearchRun]:
        """Get research run by ID (integer) or run_id (string).

        Args:
            run_id: Either the integer primary key or the string run_id.

        Returns:
            ResearchRun instance if found, None otherwise.
        """
        with self.get_session() as session:
            if isinstance(run_id, int):
                run = session.query(ResearchRun).filter(ResearchRun.id == run_id).first()
            else:
                run = session.query(ResearchRun).filter(ResearchRun.run_id == run_id).first()
            if run:
                session.expunge(run)
            return run

    def update_run_status(self, run_id: int, status: str) -> Optional[ResearchRun]:
        """Update research run status by integer ID.

        Args:
            run_id: The integer primary key of the research run.
            status: New status value (e.g., 'running', 'completed', 'failed').

        Returns:
            Updated ResearchRun instance if found, None otherwise.
        """
        with self.get_session() as session:
            run = session.query(ResearchRun).filter(ResearchRun.id == run_id).first()

            if run:
                run.status = status
                if status == "completed":
                    run.completed_at = utc_now()
                    if run.started_at:
                        # Handle timezone-naive started_at for duration calculation
                        started = run.started_at
                        if started.tzinfo is None:
                            from datetime import timezone

                            started = started.replace(tzinfo=timezone.utc)
                        run.duration_seconds = (run.completed_at - started).total_seconds()
                session.flush()
                session.refresh(run)
                session.expunge(run)

            return run

    def update_run_metrics(
        self,
        run_id: int,
        total_cost: Optional[float] = None,
        total_input_tokens: Optional[int] = None,
        total_output_tokens: Optional[int] = None,
        quality_score: Optional[float] = None,
    ) -> Optional[ResearchRun]:
        """Update research run metrics by integer ID.

        Args:
            run_id: The integer primary key of the research run.
            total_cost: Total API cost.
            total_input_tokens: Total input tokens used.
            total_output_tokens: Total output tokens used.
            quality_score: Quality score (0-100).

        Returns:
            Updated ResearchRun instance if found, None otherwise.
        """
        with self.get_session() as session:
            run = session.query(ResearchRun).filter(ResearchRun.id == run_id).first()

            if run:
                if total_cost is not None:
                    run.total_cost = total_cost
                if total_input_tokens is not None:
                    run.total_input_tokens = total_input_tokens
                if total_output_tokens is not None:
                    run.total_output_tokens = total_output_tokens
                if quality_score is not None:
                    run.quality_score = quality_score
                session.flush()
                session.refresh(run)
                session.expunge(run)

            return run

    def get_latest_run(self, company_id: int) -> Optional[ResearchRun]:
        """Get the most recent research run for a company.

        Args:
            company_id: The integer primary key of the company.

        Returns:
            Most recent ResearchRun instance if found, None otherwise.
        """
        with self.get_session() as session:
            run = (
                session.query(ResearchRun)
                .filter(ResearchRun.company_id == company_id)
                .order_by(desc(ResearchRun.started_at))
                .first()
            )

            if run:
                session.expunge(run)

            return run

    def complete_research_run(
        self,
        run_id: str,
        total_cost: float = 0.0,
        total_input_tokens: int = 0,
        total_output_tokens: int = 0,
        quality_score: Optional[float] = None,
    ) -> Optional[ResearchRun]:
        """Mark research run as completed."""
        with self.get_session() as session:
            run = session.query(ResearchRun).filter(ResearchRun.run_id == run_id).first()

            if run:
                run.mark_completed()
                run.total_cost = total_cost
                run.total_input_tokens = total_input_tokens
                run.total_output_tokens = total_output_tokens
                run.quality_score = quality_score
                session.flush()
                session.refresh(run)
                session.expunge(run)

            return run

    def fail_research_run(self, run_id: str, error: str) -> Optional[ResearchRun]:
        """Mark research run as failed."""
        with self.get_session() as session:
            run = session.query(ResearchRun).filter(ResearchRun.run_id == run_id).first()

            if run:
                run.mark_failed(error)
                session.flush()
                session.refresh(run)
                session.expunge(run)

            return run

    def get_recent_research(
        self, company_name: str, limit: int = 5, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent research runs for a company.

        Args:
            company_name: Company name
            limit: Maximum results
            status: Filter by status

        Returns:
            List of research run dictionaries
        """
        company = self.get_company(company_name)
        if not company:
            return []

        with self.get_session() as session:
            query = session.query(ResearchRun).filter(ResearchRun.company_id == company.id)

            if status:
                query = query.filter(ResearchRun.status == status)

            runs = query.order_by(desc(ResearchRun.started_at)).limit(limit).all()

            return [
                {
                    "run_id": r.run_id,
                    "status": r.status,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    "total_cost": r.total_cost,
                    "quality_score": r.quality_score,
                }
                for r in runs
            ]

    # =========================================================================
    # Agent Output Operations
    # =========================================================================

    def save_agent_output(
        self,
        research_run_id: int,
        agent_name: str,
        analysis: str = "",
        cost: float = 0.0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_tokens: int = 0,
        model_used: Optional[str] = None,
        model: Optional[str] = None,  # Alias for model_used
        agent_type: Optional[str] = None,
        structured_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> AgentOutput:
        """
        Save agent output to database.

        Args:
            research_run_id: ID of research run
            agent_name: Name of agent
            analysis: Analysis text
            cost: API cost
            input_tokens: Input token count
            output_tokens: Output token count
            cached_tokens: Cached token count
            model_used: Model used (preferred parameter name)
            model: Alias for model_used (for backwards compatibility)
            agent_type: Type of agent (e.g., 'core', 'specialist')
            structured_data: Extracted structured data
            metadata: Additional metadata

        Returns:
            AgentOutput instance
        """
        # Handle model alias
        actual_model = model_used or model

        # Build extra_metadata including agent_type if provided
        extra_meta = metadata.copy() if metadata else {}
        if agent_type:
            extra_meta["agent_type"] = agent_type

        with self.get_session() as session:
            output = AgentOutput(
                research_run_id=research_run_id,
                agent_name=agent_name,
                analysis=analysis,
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                model_used=actual_model,
                structured_data=structured_data,
                extra_metadata=extra_meta if extra_meta else None,
            )
            session.add(output)
            session.flush()
            session.refresh(output)
            session.expunge(output)

            # Update research run totals
            session.query(ResearchRun).filter(ResearchRun.id == research_run_id).update(
                {
                    "total_cost": ResearchRun.total_cost + cost,
                    "total_input_tokens": ResearchRun.total_input_tokens + input_tokens,
                    "total_output_tokens": ResearchRun.total_output_tokens + output_tokens,
                }
            )

            return output

    def get_agent_outputs(self, research_run_id: int) -> List[AgentOutput]:
        """Get all agent outputs for a research run."""
        with self.get_session() as session:
            outputs = (
                session.query(AgentOutput)
                .filter(AgentOutput.research_run_id == research_run_id)
                .all()
            )

            for output in outputs:
                session.expunge(output)

            return outputs

    # =========================================================================
    # Source Operations
    # =========================================================================

    def save_source(
        self,
        research_run_id: int,
        url: str,
        title: Optional[str] = None,
        content_snippet: Optional[str] = None,
        relevance_score: Optional[float] = None,
        discovered_by_agent: Optional[str] = None,
    ) -> Source:
        """Save a source reference."""
        from urllib.parse import urlparse

        url_hash = Source.compute_url_hash(url)
        domain = urlparse(url).netloc

        with self.get_session() as session:
            # Check for existing source in this run
            existing = (
                session.query(Source)
                .filter(Source.research_run_id == research_run_id, Source.url_hash == url_hash)
                .first()
            )

            if existing:
                session.expunge(existing)
                return existing

            source = Source(
                research_run_id=research_run_id,
                url=url,
                url_hash=url_hash,
                domain=domain,
                title=title,
                content_snippet=content_snippet,
                relevance_score=relevance_score,
                discovered_by_agent=discovered_by_agent,
            )
            session.add(source)
            session.flush()
            session.refresh(source)
            session.expunge(source)

            # Update source count
            session.query(ResearchRun).filter(ResearchRun.id == research_run_id).update(
                {"source_count": ResearchRun.source_count + 1}
            )

            return source

    def save_sources_bulk(self, research_run_id: int, sources: List[Dict[str, Any]]) -> int:
        """
        Save multiple sources efficiently.

        Args:
            research_run_id: Research run ID
            sources: List of source dictionaries

        Returns:
            Number of sources saved
        """
        from urllib.parse import urlparse

        if not sources:
            return 0

        saved_count = 0

        with self.get_session() as session:
            # Compute all url_hashes first
            url_hashes = {}
            for source_data in sources:
                url = source_data.get("url", "")
                if url:
                    url_hashes[Source.compute_url_hash(url)] = source_data

            if not url_hashes:
                return 0

            # Single query to get ALL existing hashes (fixes N+1 pattern)
            existing_hashes = {
                row[0]
                for row in session.query(Source.url_hash)
                .filter(
                    Source.research_run_id == research_run_id,
                    Source.url_hash.in_(list(url_hashes.keys())),
                )
                .all()
            }

            # Process only new sources
            for url_hash, source_data in url_hashes.items():
                if url_hash in existing_hashes:
                    continue

                url = source_data.get("url", "")
                source = Source(
                    research_run_id=research_run_id,
                    url=url,
                    url_hash=url_hash,
                    domain=urlparse(url).netloc,
                    title=source_data.get("title"),
                    content_snippet=source_data.get("content", "")[:1000],
                    relevance_score=source_data.get("score"),
                )
                session.add(source)
                saved_count += 1

            if saved_count > 0:
                session.query(ResearchRun).filter(ResearchRun.id == research_run_id).update(
                    {"source_count": ResearchRun.source_count + saved_count}
                )

        return saved_count

    # =========================================================================
    # Cost Log Operations
    # =========================================================================

    def log_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        agent_name: Optional[str] = None,
        research_run_id: Optional[int] = None,
        cached_tokens: int = 0,
        is_batch: bool = False,
    ) -> CostLog:
        """Log an API call cost."""
        with self.get_session() as session:
            log = CostLog(
                research_run_id=research_run_id,
                model=model,
                agent_name=agent_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                cost=cost,
                is_batch=is_batch,
            )
            session.add(log)
            session.flush()
            session.refresh(log)
            session.expunge(log)

            return log

    def get_cost_summary(
        self, since: Optional[datetime] = None, until: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost summary for a time period."""
        with self.get_session() as session:
            query = session.query(
                func.sum(CostLog.cost).label("total_cost"),
                func.sum(CostLog.input_tokens).label("total_input"),
                func.sum(CostLog.output_tokens).label("total_output"),
                func.count(CostLog.id).label("total_calls"),
            )

            if since:
                query = query.filter(CostLog.created_at >= since)
            if until:
                query = query.filter(CostLog.created_at <= until)

            result = query.first()

            return {
                "total_cost": float(result.total_cost or 0),
                "total_input_tokens": int(result.total_input or 0),
                "total_output_tokens": int(result.total_output or 0),
                "total_calls": int(result.total_calls or 0),
            }

    def get_cost_logs(self, research_run_id: int) -> List[CostLog]:
        """Get all cost logs for a research run.

        Args:
            research_run_id: The integer primary key of the research run.

        Returns:
            List of CostLog instances.
        """
        with self.get_session() as session:
            logs = (
                session.query(CostLog)
                .filter(CostLog.research_run_id == research_run_id)
                .order_by(CostLog.created_at)
                .all()
            )

            for log in logs:
                session.expunge(log)

            return logs

    def get_total_cost(self, research_run_id: int) -> float:
        """Get total cost for a research run.

        Args:
            research_run_id: The integer primary key of the research run.

        Returns:
            Total cost as float.
        """
        with self.get_session() as session:
            result = (
                session.query(func.sum(CostLog.cost).label("total"))
                .filter(CostLog.research_run_id == research_run_id)
                .first()
            )

            return float(result.total or 0.0)

    # =========================================================================
    # Cache Operations
    # =========================================================================

    def cache_research(
        self,
        company_name: str,
        data: Dict[str, Any],
        ttl_hours: int = 24,
        source_run_id: Optional[int] = None,
    ) -> ResearchCache:
        """Cache research results."""
        cache_key = f"research_{Company.normalize_name(company_name)}"

        with self.get_session() as session:
            # Remove existing cache
            session.query(ResearchCache).filter(ResearchCache.cache_key == cache_key).delete()

            cache = ResearchCache(
                company_name=company_name,
                cache_key=cache_key,
                cached_data=data,
                expires_at=utc_now() + timedelta(hours=ttl_hours),
                source_run_id=source_run_id,
            )
            session.add(cache)
            session.flush()
            session.refresh(cache)
            session.expunge(cache)

            return cache

    def get_cached_research(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get cached research if valid."""
        cache_key = f"research_{Company.normalize_name(company_name)}"

        with self.get_session() as session:
            cache = (
                session.query(ResearchCache)
                .filter(
                    ResearchCache.cache_key == cache_key,
                    ResearchCache.is_valid == True,
                    ResearchCache.expires_at > utc_now(),
                )
                .first()
            )

            if cache:
                return cache.cached_data

            return None

    def invalidate_cache(self, company_name: str) -> None:
        """Invalidate cached research for a company."""
        cache_key = f"research_{Company.normalize_name(company_name)}"

        with self.get_session() as session:
            session.query(ResearchCache).filter(ResearchCache.cache_key == cache_key).update(
                {"is_valid": False}
            )


# Singleton instance
_repository: Optional[ResearchRepository] = None
_repo_lock = Lock()


def get_repository(database_url: Optional[str] = None) -> ResearchRepository:
    """
    Get singleton repository instance.

    Args:
        database_url: Optional database URL override

    Returns:
        ResearchRepository instance
    """
    global _repository

    if _repository is None:
        with _repo_lock:
            if _repository is None:
                _repository = ResearchRepository(database_url)

    return _repository


def reset_repository() -> None:
    """Reset repository instance (for testing)."""
    global _repository
    _repository = None
