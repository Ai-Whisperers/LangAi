"""
Integration Module - Unified Entry Point for Enhanced Research.

This module provides the integration layer between the new enhanced modules
and the existing research workflow. It serves as the primary interface for
using all the improvements without modifying existing code.

Key Integrations:
1. Quality Assessment Pipeline (UnifiedQualityScorer + GroundTruthValidator)
2. Gap Detection Pipeline (SemanticGapDetector)
3. Contradiction Resolution Pipeline (EnhancedContradictionDetector)
4. Search Optimization Pipeline (QueryDiversifier + SemanticSourceSelector)
5. State Management (TypedResearchState conversion)
6. Prompt Management (PromptRegistry integration)

Usage:
    from company_researcher.shared.integration import (
        EnhancedResearchPipeline,
        run_quality_pipeline,
        run_gap_detection,
        run_contradiction_analysis
    )

    # Full pipeline
    pipeline = EnhancedResearchPipeline("Apple Inc.")
    result = await pipeline.run_full_analysis(research_data)

    # Individual components
    quality = run_quality_pipeline(research_output)
    gaps = run_gap_detection(research_output)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


# ============================================================================
# Import Enhanced Modules
# ============================================================================

# Quality modules
from .quality import UnifiedQualityScorer, QualityResult
from .gaps import SemanticGapDetector, GapAssessment
from .search import QueryDiversifier

# Validation
from ..validation.ground_truth import GroundTruthValidator, ValidationReport

# Contradiction detection
from ..quality.enhanced_contradiction_detector import (
    EnhancedContradictionDetector,
    ContradictionReport
)

# Source selection
from ..retrieval.source_selector import SemanticSourceSelector

# Prompts

# State (typed models)


# ============================================================================
# Result Models
# ============================================================================

@dataclass
class EnhancedAnalysisResult:
    """Complete result from enhanced analysis pipeline."""
    company_name: str

    # Quality Assessment
    quality_result: Optional[QualityResult] = None
    quality_score: float = 0.0

    # Gap Analysis
    gap_assessment: Optional[GapAssessment] = None
    critical_gaps: List[str] = field(default_factory=list)

    # Ground Truth Validation
    validation_report: Optional[ValidationReport] = None
    verified_claims: int = 0
    contradicted_claims: int = 0

    # Contradiction Analysis
    contradiction_report: Optional[ContradictionReport] = None
    has_critical_contradictions: bool = False

    # Processing metadata
    processing_time_seconds: float = 0.0
    timestamp: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "quality_score": round(self.quality_score, 2),
            "critical_gaps": self.critical_gaps,
            "verified_claims": self.verified_claims,
            "contradicted_claims": self.contradicted_claims,
            "has_critical_contradictions": self.has_critical_contradictions,
            "processing_time_seconds": round(self.processing_time_seconds, 2),
            "timestamp": self.timestamp.isoformat()
        }

    @property
    def overall_confidence(self) -> str:
        """Calculate overall confidence level."""
        if self.contradicted_claims > 2 or self.has_critical_contradictions:
            return "low"
        if self.quality_score >= 70 and len(self.critical_gaps) == 0:
            return "high"
        if self.quality_score >= 50:
            return "medium"
        return "low"


# ============================================================================
# Pipeline Components
# ============================================================================

class QualityPipeline:
    """
    Quality assessment pipeline combining multiple validators.

    Runs:
    1. UnifiedQualityScorer for multi-dimensional scoring
    2. GroundTruthValidator for claim verification
    3. Returns combined quality assessment
    """

    def __init__(self):
        self.scorer = UnifiedQualityScorer()
        self.validator = GroundTruthValidator()

    def assess(
        self,
        research_output: Dict[str, Any],
        company_name: str,
        ticker: Optional[str] = None
    ) -> Tuple[QualityResult, Optional[ValidationReport]]:
        """
        Run full quality assessment.

        Args:
            research_output: Research data to assess
            company_name: Company being researched
            ticker: Optional stock ticker for ground truth

        Returns:
            Tuple of (QualityResult, ValidationReport or None)
        """
        # Run unified quality scoring
        quality_result = self.scorer.score_comprehensive(
            research_output,
            company_name
        )

        # Run ground truth validation if ticker available
        validation_report = None
        if ticker:
            try:
                ground_truth = self.validator.fetch_ground_truth(ticker)
                if ground_truth:
                    validation_report = self.validator.validate_claims(
                        research_output,
                        ground_truth
                    )
            except Exception as e:
                logger.warning(f"Ground truth validation failed: {e}")

        return quality_result, validation_report


class GapDetectionPipeline:
    """
    Gap detection pipeline for comprehensive coverage analysis.
    """

    def __init__(self):
        self.detector = SemanticGapDetector()

    def detect(
        self,
        research_output: Dict[str, Any],
        company_name: str
    ) -> GapAssessment:
        """
        Detect gaps in research coverage.

        Args:
            research_output: Research data to analyze
            company_name: Company being researched

        Returns:
            GapAssessment with detailed gap analysis
        """
        # Convert research output to analyzable format
        content = self._extract_content(research_output)
        sources = self._extract_sources(research_output)
        agent_gaps = self._extract_agent_gaps(research_output)

        return self.detector.detect_gaps(
            content=content,
            sources=sources,
            company_name=company_name,
            agent_reported_gaps=agent_gaps
        )

    def _extract_content(self, research_output: Dict) -> str:
        """Extract text content from research output."""
        parts = []

        # Extract from agent outputs
        agent_outputs = research_output.get("agent_outputs", {})
        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                parts.append(output.get("summary", ""))
                parts.append(output.get("analysis", ""))

        # Extract from other fields
        parts.append(research_output.get("company_overview", ""))
        parts.append(str(research_output.get("key_metrics", {})))
        parts.append(str(research_output.get("key_insights", [])))

        return "\n".join(str(p) for p in parts if p)

    def _extract_sources(self, research_output: Dict) -> List[Dict]:
        """Extract sources from research output."""
        sources = research_output.get("sources", [])
        if isinstance(sources, list):
            return sources
        return []

    def _extract_agent_gaps(self, research_output: Dict) -> List[str]:
        """Extract gaps reported by agents."""
        gaps = []
        agent_outputs = research_output.get("agent_outputs", {})

        for output in agent_outputs.values():
            if isinstance(output, dict):
                agent_gaps = output.get("data_gaps", [])
                if isinstance(agent_gaps, list):
                    gaps.extend(agent_gaps)

        return gaps


class ContradictionPipeline:
    """
    Contradiction detection pipeline for multi-source analysis.
    """

    def __init__(self, use_embeddings: bool = True):
        self.detector = EnhancedContradictionDetector(use_embeddings=use_embeddings)

    def analyze(
        self,
        research_output: Dict[str, Any]
    ) -> ContradictionReport:
        """
        Analyze research output for contradictions.

        Args:
            research_output: Research data from multiple agents

        Returns:
            ContradictionReport with detected contradictions
        """
        # Extract content from each agent
        sources = {}
        agent_outputs = research_output.get("agent_outputs", {})

        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                content = output.get("summary", "") + " " + output.get("analysis", "")
                if content.strip():
                    sources[agent_name] = content

        # Add synthesized content if available
        if research_output.get("company_overview"):
            sources["synthesis"] = research_output["company_overview"]

        if len(sources) < 2:
            # Not enough sources to compare
            return ContradictionReport(
                contradictions=[],
                total_claims_analyzed=0,
                contradiction_rate=0.0,
                severity_distribution={
                    "critical": 0, "significant": 0, "minor": 0, "negligible": 0
                },
                has_critical=False
            )

        return self.detector.analyze_multi_source(sources)


class SearchOptimizationPipeline:
    """
    Search optimization pipeline for better coverage.
    """

    def __init__(self):
        self.diversifier = QueryDiversifier()
        self.source_selector = SemanticSourceSelector()

    def generate_queries(
        self,
        company_name: str,
        focus_areas: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate diversified search queries.

        Args:
            company_name: Company to research
            focus_areas: Optional list of focus areas

        Returns:
            List of diversified search queries
        """
        return self.diversifier.generate_queries(
            company_name,
            focus_areas or ["financial", "market", "product", "competitive"]
        )

    def select_sources(
        self,
        query: str,
        sources: List[Dict],
        max_sources: int = 5
    ) -> List[Dict]:
        """
        Select most relevant and diverse sources.

        Args:
            query: The research query
            sources: All available sources
            max_sources: Maximum sources to select

        Returns:
            Selected sources optimized for relevance and diversity
        """
        return self.source_selector.select_sources(
            query=query,
            sources=sources,
            max_sources=max_sources
        )


# ============================================================================
# Main Pipeline
# ============================================================================

class EnhancedResearchPipeline:
    """
    Unified pipeline integrating all enhanced research capabilities.

    This is the main entry point for using all the improvements together.
    """

    def __init__(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        use_embeddings: bool = True
    ):
        self.company_name = company_name
        self.ticker = ticker

        # Initialize pipelines
        self.quality_pipeline = QualityPipeline()
        self.gap_pipeline = GapDetectionPipeline()
        self.contradiction_pipeline = ContradictionPipeline(use_embeddings)
        self.search_pipeline = SearchOptimizationPipeline()

    def run_full_analysis(
        self,
        research_output: Dict[str, Any]
    ) -> EnhancedAnalysisResult:
        """
        Run complete enhanced analysis on research output.

        Args:
            research_output: The research data to analyze

        Returns:
            EnhancedAnalysisResult with all assessments
        """
        start_time = utc_now()

        result = EnhancedAnalysisResult(company_name=self.company_name)

        # 1. Quality Assessment
        try:
            quality_result, validation_report = self.quality_pipeline.assess(
                research_output,
                self.company_name,
                self.ticker
            )
            result.quality_result = quality_result
            result.quality_score = quality_result.overall_score
            result.validation_report = validation_report

            if validation_report:
                result.verified_claims = validation_report.verified_count
                result.contradicted_claims = validation_report.contradicted_count

        except Exception as e:
            logger.error(f"Quality pipeline failed: {e}")

        # 2. Gap Detection
        try:
            gap_assessment = self.gap_pipeline.detect(
                research_output,
                self.company_name
            )
            result.gap_assessment = gap_assessment
            result.critical_gaps = [
                g.field for g in gap_assessment.gaps
                if g.confidence.value in ["confirmed", "likely"]
            ]

        except Exception as e:
            logger.error(f"Gap detection failed: {e}")

        # 3. Contradiction Analysis
        try:
            contradiction_report = self.contradiction_pipeline.analyze(
                research_output
            )
            result.contradiction_report = contradiction_report
            result.has_critical_contradictions = contradiction_report.has_critical

        except Exception as e:
            logger.error(f"Contradiction analysis failed: {e}")

        # Calculate processing time
        result.processing_time_seconds = (
            utc_now() - start_time
        ).total_seconds()

        return result

    def get_quality_improvements(
        self,
        result: EnhancedAnalysisResult
    ) -> List[str]:
        """
        Get actionable suggestions to improve research quality.

        Args:
            result: Analysis result

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Gap-based suggestions
        for gap in result.critical_gaps:
            suggestions.append(f"Fill data gap: {gap}")

        # Contradiction-based suggestions
        if result.contradiction_report:
            for c in result.contradiction_report.contradictions:
                if c.severity.value in ["critical", "significant"]:
                    suggestions.append(
                        f"Resolve contradiction: {c.explanation}"
                    )

        # Quality-based suggestions
        if result.quality_result:
            for dim, score in result.quality_result.dimension_scores.items():
                if score.score < 0.5:
                    suggestions.append(
                        f"Improve {dim.value}: {score.details}"
                    )

        return suggestions[:10]  # Limit to top 10 suggestions


# ============================================================================
# Convenience Functions
# ============================================================================

def run_quality_pipeline(
    research_output: Dict[str, Any],
    company_name: str,
    ticker: Optional[str] = None
) -> Tuple[QualityResult, Optional[ValidationReport]]:
    """
    Convenience function to run quality assessment.

    Args:
        research_output: Research data to assess
        company_name: Company being researched
        ticker: Optional stock ticker

    Returns:
        Tuple of (QualityResult, ValidationReport or None)
    """
    pipeline = QualityPipeline()
    return pipeline.assess(research_output, company_name, ticker)


def run_gap_detection(
    research_output: Dict[str, Any],
    company_name: str
) -> GapAssessment:
    """
    Convenience function to run gap detection.

    Args:
        research_output: Research data to analyze
        company_name: Company being researched

    Returns:
        GapAssessment with detected gaps
    """
    pipeline = GapDetectionPipeline()
    return pipeline.detect(research_output, company_name)


def run_contradiction_analysis(
    research_output: Dict[str, Any],
    use_embeddings: bool = True
) -> ContradictionReport:
    """
    Convenience function to run contradiction analysis.

    Args:
        research_output: Research data with multiple sources
        use_embeddings: Whether to use semantic embeddings

    Returns:
        ContradictionReport with detected contradictions
    """
    pipeline = ContradictionPipeline(use_embeddings)
    return pipeline.analyze(research_output)


def get_optimized_queries(
    company_name: str,
    focus_areas: Optional[List[str]] = None
) -> List[str]:
    """
    Get diversified search queries for a company.

    Args:
        company_name: Company to research
        focus_areas: Optional focus areas

    Returns:
        List of optimized search queries
    """
    pipeline = SearchOptimizationPipeline()
    return pipeline.generate_queries(company_name, focus_areas)


def select_best_sources(
    query: str,
    sources: List[Dict],
    max_sources: int = 5
) -> List[Dict]:
    """
    Select best sources using semantic relevance and diversity.

    Args:
        query: Research query
        sources: Available sources
        max_sources: Maximum to select

    Returns:
        Selected sources
    """
    pipeline = SearchOptimizationPipeline()
    return pipeline.select_sources(query, sources, max_sources)
