"""
Agent Self-Reflection Mixin - Meta-cognitive capabilities for agents.

Provides:
- Confidence self-assessment
- Output quality evaluation
- Re-research triggers
- Reasoning chain validation
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ConfidenceLevel(str, Enum):
    """Confidence level classifications."""
    VERY_HIGH = "very_high"  # >90%
    HIGH = "high"  # 75-90%
    MEDIUM = "medium"  # 50-75%
    LOW = "low"  # 25-50%
    VERY_LOW = "very_low"  # <25%


class ReflectionAspect(str, Enum):
    """Aspects to reflect on."""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    RECENCY = "recency"
    SOURCE_QUALITY = "source_quality"
    REASONING = "reasoning"


@dataclass
class ReflectionScore:
    """Score for a reflection aspect."""
    aspect: ReflectionAspect
    score: float  # 0-1
    confidence: float  # 0-1
    reasoning: str
    improvements: List[str] = field(default_factory=list)


@dataclass
class SelfReflectionResult:
    """Result of agent self-reflection."""
    overall_confidence: float
    confidence_level: ConfidenceLevel
    aspect_scores: List[ReflectionScore]
    needs_re_research: bool
    re_research_reasons: List[str]
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    reflection_reasoning: str
    reflected_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def average_aspect_score(self) -> float:
        """Calculate average aspect score."""
        if not self.aspect_scores:
            return 0.0
        return sum(s.score for s in self.aspect_scores) / len(self.aspect_scores)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_confidence": self.overall_confidence,
            "confidence_level": self.confidence_level.value,
            "average_aspect_score": self.average_aspect_score,
            "aspect_scores": [
                {
                    "aspect": s.aspect.value,
                    "score": s.score,
                    "confidence": s.confidence,
                    "reasoning": s.reasoning
                }
                for s in self.aspect_scores
            ],
            "needs_re_research": self.needs_re_research,
            "re_research_reasons": self.re_research_reasons,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "improvement_suggestions": self.improvement_suggestions,
            "reflected_at": self.reflected_at.isoformat()
        }


class SelfReflectionMixin:
    """
    Mixin that adds self-reflection capabilities to agents.

    Usage:
        class MyAgent(SelfReflectionMixin, BaseAgent):
            async def research(self, query):
                result = await self._do_research(query)

                # Reflect on output
                reflection = await self.reflect_on_output(result)

                if reflection.needs_re_research:
                    result = await self._do_research(query, enhanced=True)

                return result, reflection.overall_confidence
    """

    # Configurable thresholds
    RE_RESEARCH_THRESHOLD: float = 0.5
    MIN_ACCEPTABLE_CONFIDENCE: float = 0.6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reflection_history: List[SelfReflectionResult] = []
        self._llm_client = kwargs.get('llm_client')

    async def reflect_on_output(
        self,
        output: Dict[str, Any],
        query: str = "",
        sources: List[Dict] = None
    ) -> SelfReflectionResult:
        """
        Perform self-reflection on agent output.

        Args:
            output: The output to reflect on
            query: Original query/task
            sources: Sources used

        Returns:
            SelfReflectionResult
        """
        # Evaluate each aspect
        aspect_scores = []

        for aspect in ReflectionAspect:
            score = await self._evaluate_aspect(aspect, output, query, sources)
            aspect_scores.append(score)

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(aspect_scores)
        confidence_level = self._classify_confidence(overall_confidence)

        # Identify strengths and weaknesses
        strengths = [
            s.aspect.value for s in aspect_scores
            if s.score >= 0.7
        ]
        weaknesses = [
            s.aspect.value for s in aspect_scores
            if s.score < 0.5
        ]

        # Determine if re-research needed
        needs_re_research = overall_confidence < self.RE_RESEARCH_THRESHOLD
        re_research_reasons = []

        if needs_re_research:
            for score in aspect_scores:
                if score.score < 0.4:
                    re_research_reasons.append(
                        f"Low {score.aspect.value} score: {score.score:.2f}"
                    )

        # Collect improvement suggestions
        improvements = []
        for score in aspect_scores:
            improvements.extend(score.improvements)

        # Generate reflection reasoning
        reasoning = await self._generate_reflection_reasoning(
            output, aspect_scores, overall_confidence
        )

        result = SelfReflectionResult(
            overall_confidence=overall_confidence,
            confidence_level=confidence_level,
            aspect_scores=aspect_scores,
            needs_re_research=needs_re_research,
            re_research_reasons=re_research_reasons,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=improvements[:5],
            reflection_reasoning=reasoning
        )

        self._reflection_history.append(result)
        return result

    async def _evaluate_aspect(
        self,
        aspect: ReflectionAspect,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate a specific aspect."""
        evaluators = {
            ReflectionAspect.COMPLETENESS: self._evaluate_completeness,
            ReflectionAspect.ACCURACY: self._evaluate_accuracy,
            ReflectionAspect.RELEVANCE: self._evaluate_relevance,
            ReflectionAspect.RECENCY: self._evaluate_recency,
            ReflectionAspect.SOURCE_QUALITY: self._evaluate_source_quality,
            ReflectionAspect.REASONING: self._evaluate_reasoning,
        }

        evaluator = evaluators.get(aspect, self._evaluate_generic)
        return await evaluator(output, query, sources)

    async def _evaluate_completeness(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate output completeness."""
        score = 0.5
        improvements = []
        reasoning = ""

        # Check if key fields are present
        expected_fields = self._get_expected_fields()
        present_fields = set(output.keys())
        missing = expected_fields - present_fields

        if not missing:
            score = 0.9
            reasoning = "All expected fields present"
        else:
            score = len(present_fields) / (len(expected_fields) + 1)
            improvements.append(f"Missing fields: {', '.join(missing)}")
            reasoning = f"Missing {len(missing)} expected fields"

        # Check for empty values
        empty_count = sum(1 for v in output.values() if not v)
        if empty_count > 0:
            score *= 0.9
            improvements.append(f"{empty_count} fields have empty values")

        return ReflectionScore(
            aspect=ReflectionAspect.COMPLETENESS,
            score=min(score, 1.0),
            confidence=0.8,
            reasoning=reasoning,
            improvements=improvements
        )

    async def _evaluate_accuracy(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate potential accuracy."""
        score = 0.7  # Default to moderate confidence
        improvements = []
        reasoning = "Accuracy estimated based on source corroboration"

        if sources:
            # More sources generally means higher accuracy
            source_count = len(sources)
            if source_count >= 5:
                score = 0.85
            elif source_count >= 3:
                score = 0.75
            elif source_count >= 1:
                score = 0.6
            else:
                score = 0.4
                improvements.append("No sources to verify accuracy")

        # Check for hedging language
        output_text = str(output)
        hedging_words = ["might", "could", "possibly", "approximately", "estimated"]
        hedging_count = sum(1 for w in hedging_words if w in output_text.lower())
        if hedging_count > 3:
            score *= 0.9
            reasoning = "Contains hedging language indicating uncertainty"

        return ReflectionScore(
            aspect=ReflectionAspect.ACCURACY,
            score=score,
            confidence=0.6,  # Lower confidence in accuracy assessment
            reasoning=reasoning,
            improvements=improvements
        )

    async def _evaluate_relevance(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate relevance to query."""
        score = 0.7
        improvements = []
        reasoning = ""

        if not query:
            return ReflectionScore(
                aspect=ReflectionAspect.RELEVANCE,
                score=0.7,
                confidence=0.5,
                reasoning="No query to evaluate relevance against",
                improvements=[]
            )

        # Check if query terms appear in output
        query_terms = set(query.lower().split())
        output_text = str(output).lower()
        matching_terms = sum(1 for term in query_terms if term in output_text and len(term) > 3)

        if matching_terms >= len(query_terms) * 0.8:
            score = 0.9
            reasoning = "Output strongly relevant to query"
        elif matching_terms >= len(query_terms) * 0.5:
            score = 0.7
            reasoning = "Output moderately relevant to query"
        else:
            score = 0.5
            reasoning = "Output may not fully address query"
            improvements.append("Consider addressing more aspects of the query")

        return ReflectionScore(
            aspect=ReflectionAspect.RELEVANCE,
            score=score,
            confidence=0.7,
            reasoning=reasoning,
            improvements=improvements
        )

    async def _evaluate_recency(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate data recency."""
        score = 0.7
        improvements = []
        reasoning = ""

        # Check sources for dates
        recent_sources = 0
        if sources:
            for source in sources:
                # Check for recent publication date
                pub_date = source.get("published_date") or source.get("date")
                if pub_date:
                    # Simplified check - in real implementation parse dates
                    if "2024" in str(pub_date) or "2025" in str(pub_date):
                        recent_sources += 1

            if recent_sources >= len(sources) * 0.7:
                score = 0.9
                reasoning = "Data sources are recent"
            elif recent_sources >= len(sources) * 0.3:
                score = 0.6
                reasoning = "Mixed recency of sources"
            else:
                score = 0.4
                reasoning = "Data may be outdated"
                improvements.append("Consider finding more recent sources")
        else:
            score = 0.5
            reasoning = "Cannot assess recency without source information"
            improvements.append("Include source dates for recency evaluation")

        return ReflectionScore(
            aspect=ReflectionAspect.RECENCY,
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            improvements=improvements
        )

    async def _evaluate_source_quality(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate source quality."""
        score = 0.7
        improvements = []
        reasoning = ""

        if not sources:
            return ReflectionScore(
                aspect=ReflectionAspect.SOURCE_QUALITY,
                score=0.4,
                confidence=0.5,
                reasoning="No sources provided for quality assessment",
                improvements=["Include source information"]
            )

        # Check for high-quality domains
        high_quality_domains = {
            "gov", "edu", "reuters", "bloomberg", "wsj", "ft.com",
            "sec.gov", "nytimes", "bbc", "official"
        }

        quality_sources = 0
        for source in sources:
            url = source.get("url", "").lower()
            if any(domain in url for domain in high_quality_domains):
                quality_sources += 1

        ratio = quality_sources / len(sources) if sources else 0
        if ratio >= 0.5:
            score = 0.85
            reasoning = "Good proportion of high-quality sources"
        elif ratio >= 0.2:
            score = 0.65
            reasoning = "Mixed source quality"
        else:
            score = 0.5
            reasoning = "Could use higher quality sources"
            improvements.append("Consider official or authoritative sources")

        return ReflectionScore(
            aspect=ReflectionAspect.SOURCE_QUALITY,
            score=score,
            confidence=0.7,
            reasoning=reasoning,
            improvements=improvements
        )

    async def _evaluate_reasoning(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Evaluate reasoning quality."""
        score = 0.7
        improvements = []
        reasoning = ""

        # Check for reasoning indicators
        output_text = str(output)
        reasoning_indicators = [
            "because", "therefore", "indicates", "suggests",
            "based on", "according to", "analysis shows"
        ]

        indicator_count = sum(
            1 for indicator in reasoning_indicators
            if indicator in output_text.lower()
        )

        if indicator_count >= 5:
            score = 0.9
            reasoning = "Strong reasoning chain present"
        elif indicator_count >= 2:
            score = 0.7
            reasoning = "Moderate reasoning present"
        else:
            score = 0.5
            reasoning = "Limited explicit reasoning"
            improvements.append("Include more explicit reasoning for conclusions")

        return ReflectionScore(
            aspect=ReflectionAspect.REASONING,
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            improvements=improvements
        )

    async def _evaluate_generic(
        self,
        output: Dict[str, Any],
        query: str,
        sources: List[Dict]
    ) -> ReflectionScore:
        """Generic aspect evaluation."""
        return ReflectionScore(
            aspect=ReflectionAspect.COMPLETENESS,
            score=0.5,
            confidence=0.5,
            reasoning="Generic evaluation",
            improvements=[]
        )

    def _calculate_overall_confidence(
        self,
        aspect_scores: List[ReflectionScore]
    ) -> float:
        """Calculate weighted overall confidence."""
        if not aspect_scores:
            return 0.5

        # Weights for different aspects
        weights = {
            ReflectionAspect.ACCURACY: 1.5,
            ReflectionAspect.COMPLETENESS: 1.2,
            ReflectionAspect.RELEVANCE: 1.3,
            ReflectionAspect.SOURCE_QUALITY: 1.0,
            ReflectionAspect.RECENCY: 0.8,
            ReflectionAspect.REASONING: 1.0
        }

        weighted_sum = sum(
            s.score * s.confidence * weights.get(s.aspect, 1.0)
            for s in aspect_scores
        )
        total_weight = sum(
            s.confidence * weights.get(s.aspect, 1.0)
            for s in aspect_scores
        )

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _classify_confidence(self, confidence: float) -> ConfidenceLevel:
        """Classify confidence level."""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    async def _generate_reflection_reasoning(
        self,
        output: Dict[str, Any],
        aspect_scores: List[ReflectionScore],
        overall_confidence: float
    ) -> str:
        """Generate reasoning for reflection."""
        # Build reasoning text
        strongest = max(aspect_scores, key=lambda s: s.score)
        weakest = min(aspect_scores, key=lambda s: s.score)

        return (
            f"Overall confidence: {overall_confidence:.2%}. "
            f"Strongest aspect: {strongest.aspect.value} ({strongest.score:.2f}). "
            f"Weakest aspect: {weakest.aspect.value} ({weakest.score:.2f}). "
            f"{strongest.reasoning}. {weakest.reasoning}."
        )

    def _get_expected_fields(self) -> set:
        """Get expected output fields. Override in subclasses."""
        return {"findings", "summary", "sources"}

    def get_reflection_history(self) -> List[SelfReflectionResult]:
        """Get reflection history."""
        return self._reflection_history

    def get_average_confidence(self) -> float:
        """Get average confidence across all reflections."""
        if not self._reflection_history:
            return 0.0
        return sum(r.overall_confidence for r in self._reflection_history) / len(self._reflection_history)


# Convenience function
def create_reflective_agent(agent_class, **kwargs):
    """Create an agent with self-reflection capabilities."""
    class ReflectiveAgent(SelfReflectionMixin, agent_class):
        pass
    return ReflectiveAgent(**kwargs)
