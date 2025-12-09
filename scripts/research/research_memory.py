"""
Research Memory Module.

Manages previous research data to enable reuse and token savings.
- Loads existing research reports from the unified output folder
- Verifies if content is still valid based on age and quality
- Provides data to the researcher to avoid redundant API calls
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PreviousResearch:
    """Previous research data for a company."""
    company_name: str
    research_date: datetime
    report_path: Path
    sources_path: Optional[Path] = None
    metrics_path: Optional[Path] = None
    quality_score: float = 0.0
    sources_count: int = 0
    summary: str = ""
    sources: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    needs_refresh: bool = False

    @property
    def age_days(self) -> float:
        """Get the age of this research in days."""
        return (datetime.now() - self.research_date).total_seconds() / 86400


class ResearchMemory:
    """
    Manages previous research data for reuse.

    Features:
    - Scans output folder for existing research
    - Loads reports, sources, and metrics
    - Validates content based on age and quality
    - Provides data to researcher for token savings
    """

    def __init__(
        self,
        output_base: Path,
        max_age_days: int = 30,
        min_quality_score: float = 70.0,
        verify_content: bool = True
    ):
        """
        Initialize research memory.

        Args:
            output_base: Base directory for research outputs
            max_age_days: Maximum age (in days) for previous research to be valid
            min_quality_score: Minimum quality score to consider research valid
            verify_content: Whether to verify content validity
        """
        self.output_base = Path(output_base)
        self.max_age_days = max_age_days
        self.min_quality_score = min_quality_score
        self.verify_content = verify_content

        # Cache of loaded previous research
        self._cache: Dict[str, PreviousResearch] = {}

        # Scan for existing research
        self._scan_existing_research()

    def _scan_existing_research(self) -> None:
        """Scan output folder for existing research."""
        if not self.output_base.exists():
            return

        # Look for company folders (each subfolder is a company)
        for company_dir in self.output_base.iterdir():
            if not company_dir.is_dir():
                continue

            # Skip hidden/system folders
            if company_dir.name.startswith("."):
                continue

            # Look for the full report
            full_report = company_dir / "00_full_report.md"
            if not full_report.exists():
                continue

            # Load previous research data
            company_name = company_dir.name
            self._load_previous_research(company_name, company_dir)

    def _load_previous_research(self, company_name: str, company_dir: Path) -> None:
        """Load previous research data for a company."""
        full_report = company_dir / "00_full_report.md"
        sources_file = company_dir / "07_sources.md"
        metrics_file = company_dir / "metrics.json"

        # Get modification time as research date
        research_date = datetime.fromtimestamp(full_report.stat().st_mtime)

        # Load metrics if available
        metrics = {}
        quality_score = 0.0
        sources_count = 0
        if metrics_file.exists():
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
                quality_score = metrics.get("research", {}).get("quality_score", 0.0)
                sources_count = metrics.get("research", {}).get("sources_count", 0)
            except Exception:
                pass

        # Load sources if available
        sources = []
        if sources_file.exists():
            # Parse sources from markdown (simple extraction)
            sources = self._extract_sources_from_markdown(sources_file)
            if not sources_count:
                sources_count = len(sources)

        # Load summary (first 500 chars of report)
        summary = ""
        try:
            with open(full_report, "r", encoding="utf-8") as f:
                summary = f.read()[:500]
        except Exception:
            pass

        # Create previous research object
        prev_research = PreviousResearch(
            company_name=company_name,
            research_date=research_date,
            report_path=full_report,
            sources_path=sources_file if sources_file.exists() else None,
            metrics_path=metrics_file if metrics_file.exists() else None,
            quality_score=quality_score,
            sources_count=sources_count,
            summary=summary,
            sources=sources,
            metrics=metrics,
        )

        # Validate the research
        prev_research.is_valid = self._validate_research(prev_research)
        prev_research.needs_refresh = self._check_needs_refresh(prev_research)

        # Store in cache
        self._cache[company_name.lower()] = prev_research

    def _extract_sources_from_markdown(self, sources_file: Path) -> List[Dict[str, Any]]:
        """Extract sources from the sources markdown file."""
        sources = []
        try:
            with open(sources_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple extraction: look for markdown links [title](url)
            import re
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                title, url = match.groups()
                if url.startswith("http"):
                    sources.append({
                        "title": title,
                        "url": url,
                    })
        except Exception:
            pass

        return sources

    def _validate_research(self, research: PreviousResearch) -> bool:
        """Validate if previous research is still usable."""
        # Check age
        if research.age_days > self.max_age_days:
            return False

        # Check quality score
        if research.quality_score < self.min_quality_score:
            return False

        # Check sources count (at least some sources)
        if research.sources_count < 5:
            return False

        return True

    def _check_needs_refresh(self, research: PreviousResearch) -> bool:
        """Check if research needs a refresh (partial update)."""
        # Needs refresh if older than half the max age
        if research.age_days > self.max_age_days / 2:
            return True

        # Needs refresh if quality is borderline
        if research.quality_score < self.min_quality_score + 10:
            return True

        # Needs refresh if low sources
        if research.sources_count < 50:
            return True

        return False

    def has_previous_research(self, company_name: str) -> bool:
        """Check if we have previous research for a company."""
        return company_name.lower() in self._cache

    def get_previous_research(self, company_name: str) -> Optional[PreviousResearch]:
        """Get previous research for a company."""
        return self._cache.get(company_name.lower())

    def get_all_previous_research(self) -> Dict[str, PreviousResearch]:
        """Get all previous research."""
        return self._cache.copy()

    def get_valid_previous_research(self) -> Dict[str, PreviousResearch]:
        """Get only valid previous research."""
        return {k: v for k, v in self._cache.items() if v.is_valid}

    def get_previous_sources(self, company_name: str) -> List[Dict[str, Any]]:
        """Get previous sources for a company."""
        research = self.get_previous_research(company_name)
        if research and research.is_valid:
            return research.sources
        return []

    def get_reusable_data(self, company_name: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get reusable data from previous research.

        Returns:
            Tuple of (can_reuse, data_dict)
            - can_reuse: Whether the previous research can be reused
            - data_dict: Dictionary with reusable data (sources, summary, metrics)
        """
        research = self.get_previous_research(company_name)

        if not research:
            return False, {}

        if not research.is_valid:
            return False, {
                "reason": "Previous research is too old or low quality",
                "age_days": research.age_days,
                "quality_score": research.quality_score,
            }

        # Can reuse - return the data
        return True, {
            "sources": research.sources,
            "sources_count": research.sources_count,
            "quality_score": research.quality_score,
            "research_date": research.research_date.isoformat(),
            "age_days": research.age_days,
            "needs_refresh": research.needs_refresh,
            "report_path": str(research.report_path),
            "summary_preview": research.summary[:200] + "..." if len(research.summary) > 200 else research.summary,
        }

    def print_status(self) -> None:
        """Print status of previous research."""
        print("\n[RESEARCH MEMORY] Previous Research Status:")
        print("=" * 60)

        if not self._cache:
            print("  No previous research found")
            return

        valid_count = sum(1 for r in self._cache.values() if r.is_valid)
        print(f"  Total companies: {len(self._cache)}")
        print(f"  Valid (reusable): {valid_count}")
        print(f"  Max age: {self.max_age_days} days")
        print()

        for name, research in sorted(self._cache.items()):
            status = "[OK]" if research.is_valid else "[OLD]"
            refresh = " (needs refresh)" if research.needs_refresh else ""
            print(f"  {status} {name}: {research.sources_count} sources, "
                  f"Q={research.quality_score:.1f}, "
                  f"{research.age_days:.1f} days old{refresh}")

        print("=" * 60)


def create_research_memory(
    output_base: str = "outputs/research",
    max_age_days: int = 30,
    min_quality_score: float = 70.0,
    verify_content: bool = True
) -> ResearchMemory:
    """
    Create a research memory instance.

    Args:
        output_base: Base directory for research outputs
        max_age_days: Maximum age for previous research to be valid
        min_quality_score: Minimum quality score for validity
        verify_content: Whether to verify content validity

    Returns:
        ResearchMemory instance
    """
    return ResearchMemory(
        output_base=Path(output_base),
        max_age_days=max_age_days,
        min_quality_score=min_quality_score,
        verify_content=verify_content,
    )
