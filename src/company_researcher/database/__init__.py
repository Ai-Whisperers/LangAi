"""
Database Package - PostgreSQL Integration.

Provides persistent storage for research data, including:
- Company records
- Research run history
- Agent outputs
- Cost tracking
- Source references

Usage:
    from company_researcher.database import ResearchRepository

    repo = ResearchRepository()
    run = repo.create_research_run("Tesla")
    repo.save_agent_output(run.id, "financial", analysis_text, cost)
"""

from .models import AgentOutput, Base, Company, CostLog, ResearchRun, Source
from .repository import ResearchRepository, get_repository

__all__ = [
    # Models
    "Base",
    "Company",
    "ResearchRun",
    "AgentOutput",
    "Source",
    "CostLog",
    # Repository
    "ResearchRepository",
    "get_repository",
]
