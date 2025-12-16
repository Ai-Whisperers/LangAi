"""AI-powered quality assessment using LLM."""

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from ...llm.response_parser import parse_json_response
from ..base import AIComponent
from ..fallback import FallbackHandler
from ..utils import get_logger, normalize_confidence, truncate_text
from .models import (
    ConfidenceAssessment,
    ContentQualityAssessment,
    OverallQualityReport,
    QualityLevel,
    SourceQualityAssessment,
    SourceType,
)
from .prompts import (
    CONFIDENCE_ASSESSMENT_PROMPT,
    CONTENT_QUALITY_PROMPT,
    OVERALL_QUALITY_PROMPT,
    SOURCE_QUALITY_PROMPT,
)

logger = get_logger(__name__)


class AIQualityAssessor(AIComponent[OverallQualityReport]):
    """
    AI-driven quality assessment replacing rule-based scoring.

    Provides semantic quality assessment that understands content
    quality, source reliability, and information completeness.

    Example:
        assessor = get_quality_assessor()

        # Assess content quality
        content_quality = assessor.assess_content_quality(
            content="Tesla reported $81.5B revenue...",
            section_name="financial",
            company_name="Tesla"
        )

        # Generate overall report
        report = assessor.generate_overall_report(
            company_name="Tesla",
            section_assessments=[content_quality],
            source_assessments=[...]
        )

        if report.ready_for_delivery:
            print("Report is ready!")
    """

    component_name = "quality_assessment"
    default_task_type = "reflection"
    default_complexity = "medium"

    def __init__(self):
        super().__init__()
        self._fallback_handler = FallbackHandler("quality_assessment")

    def assess_content_quality(
        self,
        content: str,
        section_name: str,
        company_name: str,
        industry: str = "Unknown",
        company_type: str = "Unknown",
    ) -> ContentQualityAssessment:
        """
        Assess quality of a content section using LLM.

        Args:
            content: The content to assess
            section_name: Name of the section
            company_name: Target company
            industry: Company industry
            company_type: Type (public, private, startup, etc.)

        Returns:
            ContentQualityAssessment with detailed quality metrics
        """
        if not content or len(content.strip()) < 50:
            return ContentQualityAssessment(
                section_name=section_name,
                quality_level=QualityLevel.INSUFFICIENT,
                score=0.0,
                factual_density=0.0,
                specificity=0.0,
                completeness=0.0,
                issues=["Content is empty or too short"],
                missing_topics=["All expected content"],
            )

        prompt = CONTENT_QUALITY_PROMPT.format(
            section_name=section_name,
            content=truncate_text(content, 6000),
            company_name=company_name,
            industry=industry,
            company_type=company_type,
        )

        try:
            result = self._call_llm(prompt=prompt, task_type="reflection", complexity="medium")

            parsed = parse_json_response(result, default={})
            return self._parse_content_assessment(parsed, section_name)

        except Exception as e:
            logger.error(f"Content quality assessment failed: {e}")
            return self._fallback_content_assessment(content, section_name)

    def assess_source_quality(
        self, url: str, title: str, snippet: str, company_name: str
    ) -> SourceQualityAssessment:
        """
        Assess quality of a source using LLM.

        Args:
            url: Source URL
            title: Source title
            snippet: Content snippet
            company_name: Target company

        Returns:
            SourceQualityAssessment with quality metrics
        """
        domain = urlparse(url).netloc if url else "unknown"

        prompt = SOURCE_QUALITY_PROMPT.format(
            url=url,
            title=title,
            domain=domain,
            snippet=truncate_text(snippet, 1000),
            company_name=company_name,
        )

        try:
            result = self._call_llm(prompt=prompt, task_type="classification", complexity="low")

            parsed = parse_json_response(result, default={})
            return self._parse_source_assessment(parsed, url, domain, title)

        except Exception as e:
            logger.error(f"Source quality assessment failed: {e}")
            return self._fallback_source_assessment(url, domain, title)

    def assess_confidence(
        self, claim: str, evidence: List[Dict[str, Any]], company_name: str
    ) -> ConfidenceAssessment:
        """
        Assess confidence level for a claim.

        Args:
            claim: The claim to assess
            evidence: List of supporting/contradicting evidence
            company_name: Target company

        Returns:
            ConfidenceAssessment with confidence metrics
        """
        evidence_str = "\n".join(
            [
                f"- Source: {e.get('source', 'Unknown')}, "
                f"Supports: {e.get('supports', 'unknown')}, "
                f"Quote: {e.get('quote', '')[:200]}"
                for e in evidence[:10]
            ]
        )

        prompt = CONFIDENCE_ASSESSMENT_PROMPT.format(
            company_name=company_name, claim=claim, evidence=evidence_str
        )

        try:
            result = self._call_llm(prompt=prompt, task_type="reasoning", complexity="low")

            parsed = parse_json_response(result, default={})
            return self._parse_confidence_assessment(parsed, claim)

        except Exception as e:
            logger.error(f"Confidence assessment failed: {e}")
            return ConfidenceAssessment(
                claim=claim,
                confidence_level=QualityLevel.POOR,
                confidence_score=0.3,
                verification_status="uncertain",
                reasoning=f"Assessment failed: {str(e)}",
            )

    def generate_overall_report(
        self,
        company_name: str,
        section_assessments: List[ContentQualityAssessment],
        source_assessments: List[SourceQualityAssessment],
        industry: str = "Unknown",
        company_type: str = "Unknown",
        threshold: float = 75.0,
    ) -> OverallQualityReport:
        """
        Generate overall quality report using LLM.

        Args:
            company_name: Target company
            section_assessments: List of section quality assessments
            source_assessments: List of source quality assessments
            industry: Company industry
            company_type: Company type
            threshold: Quality threshold for passing

        Returns:
            OverallQualityReport with overall assessment
        """
        # Build section scores summary
        section_scores_str = "\n".join(
            [
                f"- {s.section_name}: {s.score:.0f}/100 ({s.quality_level})"
                f"\n  Issues: {', '.join(s.issues[:3]) if s.issues else 'None'}"
                for s in section_assessments
            ]
        )

        # Calculate source statistics
        total_sources = len(source_assessments)
        primary_sources = sum(1 for s in source_assessments if s.is_primary_source)
        avg_quality = (
            sum(s.authority_score for s in source_assessments) / total_sources
            if total_sources > 0
            else 0.0
        )

        prompt = OVERALL_QUALITY_PROMPT.format(
            company_name=company_name,
            industry=industry,
            company_type=company_type,
            threshold=threshold,
            section_scores=section_scores_str,
            total_sources=total_sources,
            primary_sources=primary_sources,
            avg_source_quality=f"{avg_quality:.2f}",
        )

        try:
            result = self._call_llm(prompt=prompt, task_type="reasoning", complexity="medium")

            parsed = parse_json_response(result, default={})
            return self._build_overall_report(
                parsed, section_assessments, source_assessments, company_type, threshold
            )

        except Exception as e:
            logger.error(f"Overall report generation failed: {e}")
            return self._fallback_overall_report(section_assessments, source_assessments, threshold)

    def assess_batch_sources(
        self, sources: List[Dict[str, str]], company_name: str
    ) -> List[SourceQualityAssessment]:
        """
        Assess multiple sources in a single LLM call for efficiency.

        Args:
            sources: List of source dicts with url, title, snippet
            company_name: Target company

        Returns:
            List of SourceQualityAssessment
        """
        assessments = []

        # Process in batches of 5 for efficiency
        batch_size = 5
        for i in range(0, len(sources), batch_size):
            batch = sources[i : i + batch_size]

            for source in batch:
                assessment = self.assess_source_quality(
                    url=source.get("url", ""),
                    title=source.get("title", ""),
                    snippet=source.get("snippet", ""),
                    company_name=company_name,
                )
                assessments.append(assessment)

        return assessments

    def _parse_content_assessment(
        self, data: Dict[str, Any], section_name: str
    ) -> ContentQualityAssessment:
        """Parse LLM response into ContentQualityAssessment."""
        quality = data.get("quality_level", "poor")
        try:
            quality_level = QualityLevel(quality)
        except ValueError:
            quality_level = QualityLevel.POOR

        return ContentQualityAssessment(
            section_name=section_name,
            quality_level=quality_level,
            score=float(data.get("score", 50.0)),
            factual_density=normalize_confidence(data.get("factual_density", 0.5)),
            specificity=normalize_confidence(data.get("specificity", 0.5)),
            completeness=normalize_confidence(data.get("completeness", 0.5)),
            accuracy_indicators=normalize_confidence(data.get("accuracy_indicators", 0.5)),
            recency=normalize_confidence(data.get("recency", 0.5)),
            issues=data.get("issues", []),
            strengths=data.get("strengths", []),
            improvement_suggestions=data.get("improvement_suggestions", []),
            missing_topics=data.get("missing_topics", []),
        )

    def _parse_source_assessment(
        self, data: Dict[str, Any], url: str, domain: str, title: str
    ) -> SourceQualityAssessment:
        """Parse LLM response into SourceQualityAssessment."""
        quality = data.get("quality_level", "acceptable")
        try:
            quality_level = QualityLevel(quality)
        except ValueError:
            quality_level = QualityLevel.ACCEPTABLE

        source_type = data.get("source_type", "unknown")
        try:
            source_type_enum = SourceType(source_type)
        except ValueError:
            source_type_enum = SourceType.UNKNOWN

        return SourceQualityAssessment(
            url=url,
            domain=domain,
            title=title,
            quality_level=quality_level,
            source_type=source_type_enum,
            authority_score=normalize_confidence(data.get("authority_score", 0.5)),
            recency_score=normalize_confidence(data.get("recency_score", 0.5)),
            relevance_score=normalize_confidence(data.get("relevance_score", 0.5)),
            depth_score=normalize_confidence(data.get("depth_score", 0.5)),
            is_primary_source=data.get("is_primary_source", False),
            is_paywalled=data.get("is_paywalled", False),
            reasoning=data.get("reasoning", ""),
        )

    def _parse_confidence_assessment(
        self, data: Dict[str, Any], claim: str
    ) -> ConfidenceAssessment:
        """Parse LLM response into ConfidenceAssessment."""
        quality = data.get("confidence_level", "poor")
        try:
            quality_level = QualityLevel(quality)
        except ValueError:
            quality_level = QualityLevel.POOR

        return ConfidenceAssessment(
            claim=claim,
            confidence_level=quality_level,
            confidence_score=normalize_confidence(data.get("confidence_score", 0.3)),
            supporting_sources=int(data.get("supporting_sources", 0)),
            contradicting_sources=int(data.get("contradicting_sources", 0)),
            source_quality_avg=normalize_confidence(data.get("source_quality_avg", 0.5)),
            uncertainty_indicators=data.get("uncertainty_indicators", []),
            verification_status=data.get("verification_status", "unverified"),
            reasoning=data.get("reasoning", ""),
        )

    def _build_overall_report(
        self,
        data: Dict[str, Any],
        section_assessments: List[ContentQualityAssessment],
        source_assessments: List[SourceQualityAssessment],
        company_type: str,
        threshold: float,
    ) -> OverallQualityReport:
        """Build OverallQualityReport from LLM response."""
        overall_score = float(data.get("overall_score", 50.0))
        quality = data.get("overall_level", "acceptable")
        try:
            quality_level = QualityLevel(quality)
        except ValueError:
            quality_level = QualityLevel.from_score(overall_score)

        section_scores = {s.section_name: s.score for s in section_assessments}
        total_sources = len(source_assessments)
        primary_sources = sum(1 for s in source_assessments if s.is_primary_source)
        avg_quality = (
            sum(s.authority_score for s in source_assessments) / total_sources
            if total_sources > 0
            else 0.0
        )

        return OverallQualityReport(
            overall_score=overall_score,
            overall_level=quality_level,
            section_assessments=section_assessments,
            source_assessments=source_assessments,
            section_scores=section_scores,
            avg_source_quality=avg_quality,
            primary_source_count=primary_sources,
            total_source_count=total_sources,
            key_gaps=data.get("key_gaps", []),
            critical_issues=data.get("critical_issues", []),
            recommendations=data.get("recommendations", []),
            ready_for_delivery=data.get("ready_for_delivery", overall_score >= threshold),
            iteration_needed=data.get("iteration_needed", overall_score < threshold),
            focus_areas_for_iteration=data.get("focus_areas_for_iteration", []),
            company_type=company_type,
            quality_threshold=threshold,
        )

    def _fallback_content_assessment(
        self, content: str, section_name: str
    ) -> ContentQualityAssessment:
        """Fallback content assessment using simple heuristics."""
        content_length = len(content)

        # Simple heuristics
        if content_length < 100:
            score = 20.0
        elif content_length < 500:
            score = 50.0
        elif content_length < 1000:
            score = 65.0
        else:
            score = 75.0

        return ContentQualityAssessment(
            section_name=section_name,
            quality_level=QualityLevel.from_score(score),
            score=score,
            factual_density=0.5,
            specificity=0.5,
            completeness=min(1.0, content_length / 2000),
            issues=["AI assessment failed, using fallback heuristics"],
            strengths=[],
        )

    def _fallback_source_assessment(
        self, url: str, domain: str, title: str
    ) -> SourceQualityAssessment:
        """Fallback source assessment using domain heuristics."""
        # Simple domain-based scoring
        high_quality_domains = [
            "bloomberg.com",
            "reuters.com",
            "wsj.com",
            "ft.com",
            "sec.gov",
            "investor.",
            ".gov",
            ".edu",
        ]
        medium_quality = ["news", "finance", "business", "market"]

        authority = 0.5
        is_primary = False

        domain_lower = domain.lower()

        for hq in high_quality_domains:
            if hq in domain_lower:
                authority = 0.85
                if ".gov" in hq or "investor" in hq:
                    is_primary = True
                break
        else:
            for mq in medium_quality:
                if mq in domain_lower:
                    authority = 0.65
                    break

        return SourceQualityAssessment(
            url=url,
            domain=domain,
            title=title,
            quality_level=QualityLevel.ACCEPTABLE,
            source_type=SourceType.UNKNOWN,
            authority_score=authority,
            recency_score=0.5,
            relevance_score=0.5,
            is_primary_source=is_primary,
            reasoning="Fallback assessment based on domain patterns",
        )

    def _fallback_overall_report(
        self,
        section_assessments: List[ContentQualityAssessment],
        source_assessments: List[SourceQualityAssessment],
        threshold: float,
    ) -> OverallQualityReport:
        """Fallback overall report using averages."""
        if section_assessments:
            overall_score = sum(s.score for s in section_assessments) / len(section_assessments)
        else:
            overall_score = 0.0

        total_sources = len(source_assessments)
        primary_sources = sum(1 for s in source_assessments if s.is_primary_source)
        avg_quality = (
            sum(s.authority_score for s in source_assessments) / total_sources
            if total_sources > 0
            else 0.0
        )

        return OverallQualityReport(
            overall_score=overall_score,
            overall_level=QualityLevel.from_score(overall_score),
            section_assessments=section_assessments,
            source_assessments=source_assessments,
            section_scores={s.section_name: s.score for s in section_assessments},
            avg_source_quality=avg_quality,
            primary_source_count=primary_sources,
            total_source_count=total_sources,
            key_gaps=["AI assessment failed"],
            critical_issues=[],
            recommendations=["Re-run quality assessment"],
            ready_for_delivery=overall_score >= threshold,
            iteration_needed=overall_score < threshold,
            quality_threshold=threshold,
        )

    def process(
        self, company_name: str, sections: Dict[str, str], sources: List[Dict]
    ) -> OverallQualityReport:
        """Main processing method (implements AIComponent interface)."""
        # Assess each section
        section_assessments = []
        for name, content in sections.items():
            assessment = self.assess_content_quality(content, name, company_name)
            section_assessments.append(assessment)

        # Assess sources
        source_assessments = []
        for source in sources[:20]:  # Limit to 20 sources
            assessment = self.assess_source_quality(
                url=source.get("url", ""),
                title=source.get("title", ""),
                snippet=source.get("snippet", ""),
                company_name=company_name,
            )
            source_assessments.append(assessment)

        # Generate overall report
        return self.generate_overall_report(
            company_name=company_name,
            section_assessments=section_assessments,
            source_assessments=source_assessments,
        )


# Singleton instance
_assessor_instance: Optional[AIQualityAssessor] = None


def get_quality_assessor() -> AIQualityAssessor:
    """Get singleton quality assessor instance."""
    global _assessor_instance
    if _assessor_instance is None:
        _assessor_instance = AIQualityAssessor()
    return _assessor_instance


def reset_quality_assessor():
    """Reset the singleton instance (useful for testing)."""
    global _assessor_instance
    _assessor_instance = None
