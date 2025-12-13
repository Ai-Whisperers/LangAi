"""
Source and fact tracking system (Phase 5).

Tracks all research facts with source attribution, calculates multi-factor
quality scores, and generates comprehensive quality reports.
"""

from typing import List, Dict
from datetime import timedelta
from collections import defaultdict

from .models import (
    Source,
    ResearchFact,
    QualityReport,
    SourceQuality,
    ConfidenceLevel
)
from .source_assessor import SourceQualityAssessor
from ..utils import utc_now


class SourceTracker:
    """
    Track all sources and facts throughout research.

    Provides comprehensive source tracking, fact attribution,
    and multi-factor quality scoring.
    """

    def __init__(self):
        """Initialize source tracker."""
        self.assessor = SourceQualityAssessor()
        self.sources: List[Source] = []
        self.facts: List[ResearchFact] = []
        self.facts_by_agent: Dict[str, List[ResearchFact]] = defaultdict(list)

    def add_fact(
        self,
        content: str,
        url: str,
        title: str,
        agent_name: str,
        verified: bool = False
    ) -> ResearchFact:
        """
        Add a fact with automatic source assessment.

        Args:
            content: Fact content
            url: Source URL
            title: Source title
            agent_name: Agent that extracted this fact
            verified: Whether fact is verified

        Returns:
            ResearchFact object with quality assessed
        """
        # Create source
        source = Source(url=url, title=title)

        # Assess source quality
        self.assessor.assess_source(source)

        # Create fact
        fact = ResearchFact(
            content=content,
            source=source,
            extracted_by=agent_name,
            verified=verified
        )

        # Assess fact (adds confidence)
        self.assessor.assess_fact(fact)

        # Track
        self.facts.append(fact)
        self.facts_by_agent[agent_name].append(fact)

        # Track source if new
        if not any(s.url == source.url for s in self.sources):
            self.sources.append(source)

        return fact

    def verify_fact(self, fact: ResearchFact, verifier: str):
        """
        Mark a fact as verified by an agent.

        Args:
            fact: Fact to verify
            verifier: Agent name that verified
        """
        fact.verified = True
        fact.verified_by = verifier

    def calculate_quality_score(self) -> QualityReport:
        """
        Calculate comprehensive multi-factor quality score.

        Quality Formula (weighted):
        - Source Quality: 40% (average source quality score)
        - Verification Rate: 30% (% of facts verified)
        - Recency: 20% (how recent are sources)
        - Completeness: 10% (diversity of sources/agents)

        Returns:
            QualityReport with detailed scores
        """
        if not self.facts:
            return QualityReport(
                overall_score=0.0,
                source_quality_score=0.0,
                verification_rate=0.0,
                recency_score=0.0,
                completeness_score=0.0
            )

        # 1. Source Quality Score (40% weight)
        source_quality = sum(f.source.quality_score for f in self.facts) / len(self.facts)

        # 2. Verification Rate (30% weight)
        verified_count = sum(1 for f in self.facts if f.verified)
        verification_rate = (verified_count / len(self.facts)) * 100

        # 3. Recency Score (20% weight)
        recency_score = self._calculate_recency_score()

        # 4. Completeness Score (10% weight)
        completeness_score = self._calculate_completeness_score()

        # Overall Score (weighted average)
        overall = (
            source_quality * 0.4 +
            verification_rate * 0.3 +
            recency_score * 0.2 +
            completeness_score * 0.1
        )

        # Count source quality distribution
        high_quality = sum(1 for s in self.sources if s.quality_score >= 80)
        medium_quality = sum(1 for s in self.sources if 65 <= s.quality_score < 80)
        low_quality = sum(1 for s in self.sources if s.quality_score < 65)

        return QualityReport(
            overall_score=overall,
            source_quality_score=source_quality,
            verification_rate=verification_rate,
            recency_score=recency_score,
            completeness_score=completeness_score,
            total_facts=len(self.facts),
            verified_facts=verified_count,
            high_quality_sources=high_quality,
            medium_quality_sources=medium_quality,
            low_quality_sources=low_quality
        )

    def _calculate_recency_score(self) -> float:
        """
        Calculate recency score based on source timestamps.

        Scoring:
        - < 1 week: 100 points
        - < 1 month: 90 points
        - < 3 months: 75 points
        - < 6 months: 60 points
        - < 1 year: 40 points
        - >= 1 year: 20 points

        Returns:
            Average recency score (0-100)
        """
        if not self.sources:
            return 50.0  # Neutral score

        now = utc_now()
        scores = []

        for source in self.sources:
            age = now - source.retrieved_at

            if age < timedelta(weeks=1):
                scores.append(100.0)
            elif age < timedelta(days=30):
                scores.append(90.0)
            elif age < timedelta(days=90):
                scores.append(75.0)
            elif age < timedelta(days=180):
                scores.append(60.0)
            elif age < timedelta(days=365):
                scores.append(40.0)
            else:
                scores.append(20.0)

        return sum(scores) / len(scores)

    def _calculate_completeness_score(self) -> float:
        """
        Calculate completeness score based on source/agent diversity.

        Factors:
        - Number of unique sources (50%)
        - Number of agents contributing (50%)

        Returns:
            Completeness score (0-100)
        """
        # Source diversity (more sources = better)
        source_count = len(self.sources)
        source_score = min(source_count * 10, 100)  # Cap at 100

        # Agent diversity (more agents = better)
        agent_count = len(self.facts_by_agent)
        agent_score = min(agent_count * 20, 100)  # 5 agents = 100

        return (source_score * 0.5) + (agent_score * 0.5)

    def get_facts_by_confidence(self, level: ConfidenceLevel) -> List[ResearchFact]:
        """Get all facts with specific confidence level."""
        return [f for f in self.facts if f.confidence == level]

    def get_facts_by_agent(self, agent_name: str) -> List[ResearchFact]:
        """Get all facts extracted by a specific agent."""
        return self.facts_by_agent.get(agent_name, [])

    def get_unverified_facts(self) -> List[ResearchFact]:
        """Get all facts that haven't been verified."""
        return [f for f in self.facts if not f.verified]

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        return {
            "total_sources": len(self.sources),
            "total_facts": len(self.facts),
            "verified_facts": sum(1 for f in self.facts if f.verified),
            "agents_contributing": len(self.facts_by_agent),
            "confidence_distribution": {
                "high": len(self.get_facts_by_confidence(ConfidenceLevel.HIGH)),
                "medium": len(self.get_facts_by_confidence(ConfidenceLevel.MEDIUM)),
                "low": len(self.get_facts_by_confidence(ConfidenceLevel.LOW)),
            },
            "quality_distribution": {
                "official": sum(1 for s in self.sources if s.quality == SourceQuality.OFFICIAL),
                "authoritative": sum(1 for s in self.sources if s.quality == SourceQuality.AUTHORITATIVE),
                "reputable": sum(1 for s in self.sources if s.quality == SourceQuality.REPUTABLE),
                "community": sum(1 for s in self.sources if s.quality == SourceQuality.COMMUNITY),
                "unknown": sum(1 for s in self.sources if s.quality == SourceQuality.UNKNOWN),
            }
        }

    def generate_citations(self, format: str = "markdown") -> str:
        """
        Generate citations for all sources.

        Args:
            format: Citation format ("markdown", "apa", "mla")

        Returns:
            Formatted citations string
        """
        if format == "markdown":
            return "\n".join(s.to_markdown() for s in self.sources)
        else:
            # For other formats, use markdown as fallback
            return "\n".join(s.to_markdown() for s in self.sources)
