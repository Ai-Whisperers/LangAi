"""
Confidence Scoring - Per-fact confidence.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ConfidenceLevel(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class SourceType(str, Enum):
    OFFICIAL = "official"
    NEWS = "news"
    RESEARCH = "research"
    UNKNOWN = "unknown"


@dataclass
class SourceInfo:
    url: str
    source_type: SourceType = SourceType.UNKNOWN
    authority_score: float = 0.5


@dataclass
class ConfidenceFactors:
    source_count: int = 1
    source_agreement: float = 1.0
    source_authority: float = 0.5
    recency: float = 1.0
    specificity: float = 0.5
    language_certainty: float = 0.5


@dataclass
class ScoredFact:
    claim: str
    confidence: float
    confidence_level: ConfidenceLevel
    factors: ConfidenceFactors
    sources: List[SourceInfo] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "confidence": self.confidence,
            "level": self.confidence_level.value,
        }


class ConfidenceScorer:
    HEDGING_WORDS = {"might", "could", "possibly", "estimated", "reportedly"}
    CONFIDENT_WORDS = {"confirmed", "official", "announced", "stated"}

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            "source_count": 0.2,
            "source_agreement": 0.25,
            "source_authority": 0.2,
            "recency": 0.15,
            "specificity": 0.1,
            "language_certainty": 0.1,
        }

    def score_fact(self, claim: str, sources: List[Dict] = None) -> ScoredFact:
        sources = sources or []
        source_infos = [self._parse_source(s) for s in sources]
        factors = ConfidenceFactors(
            source_count=len(sources),
            source_agreement=min(len(sources) / 5, 1.0),
            source_authority=self._calculate_authority(source_infos),
            recency=0.7,
            specificity=self._calculate_specificity(claim),
            language_certainty=self._calculate_language_certainty(claim),
        )
        confidence = self._calculate_overall(factors)
        level = self._classify_confidence(confidence)
        return ScoredFact(
            claim=claim,
            confidence=confidence,
            confidence_level=level,
            factors=factors,
            sources=source_infos,
            explanation=f"Confidence: {confidence:.0%}",
        )

    def _parse_source(self, source: Dict) -> SourceInfo:
        url = source.get("url", "")
        source_type = SourceType.UNKNOWN
        if any(d in url.lower() for d in ["gov", "sec.gov"]):
            source_type = SourceType.OFFICIAL
        elif any(d in url.lower() for d in ["reuters", "bloomberg"]):
            source_type = SourceType.NEWS
        authority = (
            0.8
            if source_type == SourceType.OFFICIAL
            else 0.6 if source_type == SourceType.NEWS else 0.4
        )
        return SourceInfo(url=url, source_type=source_type, authority_score=authority)

    def _calculate_authority(self, sources: List[SourceInfo]) -> float:
        if not sources:
            return 0.3
        return sum(s.authority_score for s in sources) / len(sources)

    def _calculate_specificity(self, claim: str) -> float:
        has_numbers = bool(re.search(r"\d", claim))
        has_dates = bool(re.search(r"\d{4}", claim))
        return 0.3 + (has_numbers * 0.3) + (has_dates * 0.4)

    def _calculate_language_certainty(self, claim: str) -> float:
        lower = claim.lower()
        hedging = sum(1 for w in self.HEDGING_WORDS if w in lower)
        confident = sum(1 for w in self.CONFIDENT_WORDS if w in lower)
        return max(0.2, min(0.8 + confident * 0.1 - hedging * 0.15, 1.0))

    def _calculate_overall(self, factors: ConfidenceFactors) -> float:
        sc_factor = min(factors.source_count / 3, 1.0)
        return max(
            0.0,
            min(
                self.weights["source_count"] * sc_factor
                + self.weights["source_agreement"] * factors.source_agreement
                + self.weights["source_authority"] * factors.source_authority
                + self.weights["recency"] * factors.recency
                + self.weights["specificity"] * factors.specificity
                + self.weights["language_certainty"] * factors.language_certainty,
                1.0,
            ),
        )

    def _classify_confidence(self, score: float) -> ConfidenceLevel:
        if score >= 0.85:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.7:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.3:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW


def score_facts(facts: List[Dict]) -> List[ScoredFact]:
    scorer = ConfidenceScorer()
    return [scorer.score_fact(f["claim"], f.get("sources", [])) for f in facts]


def create_confidence_scorer(weights: Dict[str, float] = None) -> ConfidenceScorer:
    return ConfidenceScorer(weights=weights)
