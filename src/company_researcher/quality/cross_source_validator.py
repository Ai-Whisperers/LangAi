"""
Cross-Source Validation System

Enhanced contradiction detection with:
- Multi-source fact validation
- Confidence scoring by source reputation
- Automatic conflict resolution
- Evidence chain tracking

Usage:
    from company_researcher.quality.cross_source_validator import (
        CrossSourceValidator,
        ValidationResult
    )

    validator = CrossSourceValidator()
    result = validator.validate_facts(facts, sources)
"""

import re
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from ..utils import get_logger, utc_now

logger = get_logger(__name__)


class SourceTier(Enum):
    """Source credibility tiers."""
    OFFICIAL = "official"           # Company filings, official statements
    AUTHORITATIVE = "authoritative" # Major news, industry analysts
    REPUTABLE = "reputable"         # Known publications, databases
    STANDARD = "standard"           # General web sources
    LOW = "low"                     # Unknown or unreliable sources


class ConflictType(Enum):
    """Types of factual conflicts."""
    NUMERICAL = "numerical"         # Different numbers
    TEMPORAL = "temporal"           # Different dates/times
    CATEGORICAL = "categorical"     # Different categories
    DESCRIPTIVE = "descriptive"     # Different descriptions
    EXISTENCE = "existence"         # Fact exists vs doesn't exist


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    HIGHEST_AUTHORITY = "highest_authority"   # Trust most authoritative source
    MOST_RECENT = "most_recent"               # Trust most recent source
    CONSENSUS = "consensus"                   # Trust majority view
    WEIGHTED_AVERAGE = "weighted_average"     # For numerical conflicts
    MANUAL = "manual"                         # Requires human review


@dataclass
class SourceInfo:
    """Information about a data source."""
    url: str
    domain: str
    tier: SourceTier
    credibility_score: float  # 0.0 to 1.0
    publication_date: Optional[datetime] = None
    author: Optional[str] = None
    is_primary_source: bool = False

    @classmethod
    def from_url(cls, url: str, publication_date: Optional[datetime] = None) -> "SourceInfo":
        """Create SourceInfo from URL with automatic tier detection."""
        domain = cls._extract_domain(url)
        tier, score = cls._assess_source(domain, url)
        return cls(
            url=url,
            domain=domain,
            tier=tier,
            credibility_score=score,
            publication_date=publication_date
        )

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace("www.", "")
        except Exception:
            return url

    @staticmethod
    def _assess_source(domain: str, url: str) -> Tuple[SourceTier, float]:
        """Assess source credibility based on domain."""
        # Official sources
        official_patterns = [
            r"sec\.gov", r"edgar", r"investor\.", r"ir\.",
            r"\.gov$", r"\.edu$"
        ]
        for pattern in official_patterns:
            if re.search(pattern, domain):
                return SourceTier.OFFICIAL, 0.95

        # Authoritative sources
        authoritative_domains = {
            "reuters.com": 0.90,
            "bloomberg.com": 0.90,
            "wsj.com": 0.88,
            "ft.com": 0.88,
            "nytimes.com": 0.85,
            "forbes.com": 0.82,
            "techcrunch.com": 0.80,
            "crunchbase.com": 0.85,
            "pitchbook.com": 0.88,
            "statista.com": 0.85,
        }
        if domain in authoritative_domains:
            return SourceTier.AUTHORITATIVE, authoritative_domains[domain]

        # Reputable sources
        reputable_domains = {
            "wikipedia.org": 0.70,
            "linkedin.com": 0.72,
            "businessinsider.com": 0.75,
            "cnbc.com": 0.78,
            "marketwatch.com": 0.76,
            "yahoo.com": 0.70,
        }
        if domain in reputable_domains:
            return SourceTier.REPUTABLE, reputable_domains[domain]

        # Standard web sources
        return SourceTier.STANDARD, 0.50


@dataclass
class Fact:
    """A factual claim with source attribution."""
    id: str
    category: str              # e.g., "revenue", "employee_count", "founding_date"
    claim: str                 # The actual claim
    value: Any                 # Extracted value (number, date, string)
    source: SourceInfo
    confidence: float = 0.5
    extraction_method: str = "llm"
    timestamp: datetime = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conflict:
    """A detected conflict between facts."""
    id: str
    conflict_type: ConflictType
    category: str
    facts: List[Fact]
    severity: float            # 0.0 to 1.0
    description: str
    suggested_resolution: ResolutionStrategy
    resolved: bool = False
    resolved_value: Any = None
    resolution_reasoning: str = ""


@dataclass
class ValidationResult:
    """Result of cross-source validation."""
    is_valid: bool
    confidence_score: float
    validated_facts: List[Fact]
    conflicts: List[Conflict]
    unverified_facts: List[Fact]
    source_coverage: Dict[str, int]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=utc_now)


class CrossSourceValidator:
    """
    Validates facts across multiple sources.

    Detects contradictions, resolves conflicts, and provides
    confidence scores based on source agreement.
    """

    # Numerical tolerance for different categories
    NUMERICAL_TOLERANCES = {
        "revenue": 0.05,           # 5% tolerance
        "employee_count": 0.10,    # 10% tolerance
        "market_cap": 0.05,
        "funding": 0.02,
        "stock_price": 0.01,
        "default": 0.10
    }

    def __init__(
        self,
        min_sources_for_validation: int = 2,
        conflict_threshold: float = 0.15,
        auto_resolve: bool = True
    ):
        self.min_sources = min_sources_for_validation
        self.conflict_threshold = conflict_threshold
        self.auto_resolve = auto_resolve
        self.fact_index: Dict[str, List[Fact]] = defaultdict(list)

    def validate_facts(
        self,
        facts: List[Fact],
        require_consensus: bool = False
    ) -> ValidationResult:
        """
        Validate a list of facts through cross-source checking.

        Args:
            facts: List of facts to validate
            require_consensus: If True, require multiple sources to agree

        Returns:
            ValidationResult with validated facts and detected conflicts
        """
        # Index facts by category
        self._index_facts(facts)

        validated = []
        conflicts = []
        unverified = []
        recommendations = []

        # Process each category
        for category, category_facts in self.fact_index.items():
            if len(category_facts) == 1:
                # Single source - mark as unverified
                fact = category_facts[0]
                if require_consensus:
                    unverified.append(fact)
                    recommendations.append(
                        f"'{category}' has only one source. Consider finding additional sources."
                    )
                else:
                    fact.confidence = fact.source.credibility_score * 0.7
                    validated.append(fact)
            else:
                # Multiple sources - check for conflicts
                category_conflicts = self._detect_conflicts(category, category_facts)

                if category_conflicts:
                    conflicts.extend(category_conflicts)

                    # Try to resolve conflicts
                    if self.auto_resolve:
                        for conflict in category_conflicts:
                            resolved_fact = self._resolve_conflict(conflict)
                            if resolved_fact:
                                validated.append(resolved_fact)
                else:
                    # No conflicts - boost confidence
                    best_fact = self._select_best_fact(category_facts)
                    best_fact.confidence = self._calculate_consensus_confidence(category_facts)
                    validated.append(best_fact)

        # Calculate source coverage
        source_coverage = self._calculate_source_coverage(facts)

        # Calculate overall confidence
        if validated:
            overall_confidence = sum(f.confidence for f in validated) / len(validated)
        else:
            overall_confidence = 0.0

        # Generate recommendations
        if len(conflicts) > 3:
            recommendations.append(
                f"High conflict rate ({len(conflicts)} conflicts). Consider manual review."
            )

        low_confidence_facts = [f for f in validated if f.confidence < 0.6]
        if low_confidence_facts:
            recommendations.append(
                f"{len(low_confidence_facts)} facts have low confidence. Seek additional sources."
            )

        return ValidationResult(
            is_valid=len(conflicts) == 0 or all(c.resolved for c in conflicts),
            confidence_score=overall_confidence,
            validated_facts=validated,
            conflicts=conflicts,
            unverified_facts=unverified,
            source_coverage=source_coverage,
            recommendations=recommendations
        )

    def _index_facts(self, facts: List[Fact]):
        """Index facts by category for comparison."""
        self.fact_index.clear()
        for fact in facts:
            self.fact_index[fact.category].append(fact)

    def _detect_conflicts(self, category: str, facts: List[Fact]) -> List[Conflict]:
        """Detect conflicts within a category."""
        conflicts = []

        # Compare all pairs
        for i, fact1 in enumerate(facts):
            for fact2 in facts[i+1:]:
                conflict = self._compare_facts(fact1, fact2)
                if conflict:
                    # Check if already in conflicts list
                    existing = next(
                        (c for c in conflicts if c.category == category),
                        None
                    )
                    if existing:
                        if fact2 not in existing.facts:
                            existing.facts.append(fact2)
                    else:
                        conflicts.append(conflict)

        return conflicts

    def _compare_facts(self, fact1: Fact, fact2: Fact) -> Optional[Conflict]:
        """Compare two facts for conflict."""
        # Determine conflict type based on value types
        val1, val2 = fact1.value, fact2.value

        # Numerical comparison
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            tolerance = self.NUMERICAL_TOLERANCES.get(
                fact1.category,
                self.NUMERICAL_TOLERANCES["default"]
            )

            if val1 == 0 and val2 == 0:
                return None

            diff = abs(val1 - val2) / max(abs(val1), abs(val2), 1)

            if diff > tolerance:
                severity = min(diff / tolerance, 1.0)
                return Conflict(
                    id=f"conflict_{fact1.id}_{fact2.id}",
                    conflict_type=ConflictType.NUMERICAL,
                    category=fact1.category,
                    facts=[fact1, fact2],
                    severity=severity,
                    description=f"Numerical conflict: {val1} vs {val2} ({diff:.1%} difference)",
                    suggested_resolution=ResolutionStrategy.WEIGHTED_AVERAGE
                )

        # Date comparison
        elif isinstance(val1, datetime) and isinstance(val2, datetime):
            if val1 != val2:
                days_diff = abs((val1 - val2).days)
                severity = min(days_diff / 365, 1.0)
                return Conflict(
                    id=f"conflict_{fact1.id}_{fact2.id}",
                    conflict_type=ConflictType.TEMPORAL,
                    category=fact1.category,
                    facts=[fact1, fact2],
                    severity=severity,
                    description=f"Date conflict: {val1.date()} vs {val2.date()}",
                    suggested_resolution=ResolutionStrategy.HIGHEST_AUTHORITY
                )

        # String comparison
        elif isinstance(val1, str) and isinstance(val2, str):
            if val1.lower().strip() != val2.lower().strip():
                # Calculate similarity
                similarity = self._string_similarity(val1, val2)
                if similarity < 0.8:  # Less than 80% similar
                    return Conflict(
                        id=f"conflict_{fact1.id}_{fact2.id}",
                        conflict_type=ConflictType.DESCRIPTIVE,
                        category=fact1.category,
                        facts=[fact1, fact2],
                        severity=1 - similarity,
                        description=f"Descriptive conflict: '{val1[:50]}' vs '{val2[:50]}'",
                        suggested_resolution=ResolutionStrategy.HIGHEST_AUTHORITY
                    )

        return None

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using simple ratio."""
        s1, s2 = s1.lower(), s2.lower()
        if s1 == s2:
            return 1.0

        # Simple character overlap
        set1, set2 = set(s1.split()), set(s2.split())
        intersection = set1 & set2
        union = set1 | set2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _resolve_conflict(self, conflict: Conflict) -> Optional[Fact]:
        """Attempt to resolve a conflict."""
        if conflict.suggested_resolution == ResolutionStrategy.WEIGHTED_AVERAGE:
            return self._resolve_by_weighted_average(conflict)
        elif conflict.suggested_resolution == ResolutionStrategy.HIGHEST_AUTHORITY:
            return self._resolve_by_authority(conflict)
        elif conflict.suggested_resolution == ResolutionStrategy.CONSENSUS:
            return self._resolve_by_consensus(conflict)
        elif conflict.suggested_resolution == ResolutionStrategy.MOST_RECENT:
            return self._resolve_by_recency(conflict)

        return None

    def _resolve_by_weighted_average(self, conflict: Conflict) -> Optional[Fact]:
        """Resolve numerical conflict by weighted average."""
        if conflict.conflict_type != ConflictType.NUMERICAL:
            return self._resolve_by_authority(conflict)

        total_weight = 0
        weighted_sum = 0

        for fact in conflict.facts:
            weight = fact.source.credibility_score
            weighted_sum += fact.value * weight
            total_weight += weight

        if total_weight == 0:
            return None

        resolved_value = weighted_sum / total_weight

        # Create resolved fact
        best_source_fact = max(conflict.facts, key=lambda f: f.source.credibility_score)
        resolved_fact = Fact(
            id=f"resolved_{conflict.id}",
            category=conflict.category,
            claim=f"Resolved: {best_source_fact.claim}",
            value=resolved_value,
            source=best_source_fact.source,
            confidence=0.75,
            metadata={
                "resolution": "weighted_average",
                "original_values": [f.value for f in conflict.facts]
            }
        )

        conflict.resolved = True
        conflict.resolved_value = resolved_value
        conflict.resolution_reasoning = f"Weighted average of {len(conflict.facts)} sources"

        return resolved_fact

    def _resolve_by_authority(self, conflict: Conflict) -> Optional[Fact]:
        """Resolve by selecting highest authority source."""
        best_fact = max(conflict.facts, key=lambda f: f.source.credibility_score)

        # Adjust confidence based on conflict severity
        best_fact.confidence = best_fact.source.credibility_score * (1 - conflict.severity * 0.3)

        conflict.resolved = True
        conflict.resolved_value = best_fact.value
        conflict.resolution_reasoning = f"Selected highest authority source: {best_fact.source.domain}"

        return best_fact

    def _resolve_by_consensus(self, conflict: Conflict) -> Optional[Fact]:
        """Resolve by majority agreement."""
        # Group by value
        value_counts: Dict[Any, List[Fact]] = defaultdict(list)
        for fact in conflict.facts:
            value_counts[str(fact.value)].append(fact)

        # Find majority
        majority_value = max(value_counts.keys(), key=lambda v: len(value_counts[v]))
        majority_facts = value_counts[majority_value]

        if len(majority_facts) > len(conflict.facts) / 2:
            best_fact = max(majority_facts, key=lambda f: f.source.credibility_score)
            best_fact.confidence = len(majority_facts) / len(conflict.facts)

            conflict.resolved = True
            conflict.resolved_value = best_fact.value
            conflict.resolution_reasoning = f"Consensus: {len(majority_facts)}/{len(conflict.facts)} sources agree"

            return best_fact

        # No clear majority - fall back to authority
        return self._resolve_by_authority(conflict)

    def _resolve_by_recency(self, conflict: Conflict) -> Optional[Fact]:
        """Resolve by selecting most recent source."""
        facts_with_dates = [
            f for f in conflict.facts
            if f.source.publication_date is not None
        ]

        if not facts_with_dates:
            return self._resolve_by_authority(conflict)

        most_recent = max(facts_with_dates, key=lambda f: f.source.publication_date)
        most_recent.confidence = most_recent.source.credibility_score * 0.9

        conflict.resolved = True
        conflict.resolved_value = most_recent.value
        conflict.resolution_reasoning = f"Selected most recent source: {most_recent.source.publication_date}"

        return most_recent

    def _select_best_fact(self, facts: List[Fact]) -> Fact:
        """Select best fact when no conflicts."""
        return max(facts, key=lambda f: f.source.credibility_score)

    def _calculate_consensus_confidence(self, facts: List[Fact]) -> float:
        """Calculate confidence based on source agreement."""
        # Base confidence on number of agreeing sources
        source_bonus = min(len(facts) * 0.1, 0.3)

        # Average source credibility
        avg_credibility = sum(f.source.credibility_score for f in facts) / len(facts)

        return min(avg_credibility + source_bonus, 0.99)

    def _calculate_source_coverage(self, facts: List[Fact]) -> Dict[str, int]:
        """Calculate coverage by source tier."""
        coverage = {tier.value: 0 for tier in SourceTier}
        seen_urls: Set[str] = set()

        for fact in facts:
            if fact.source.url not in seen_urls:
                coverage[fact.source.tier.value] += 1
                seen_urls.add(fact.source.url)

        return coverage


def validate_research_data(
    data: Dict[str, Any],
    sources: List[Dict[str, Any]]
) -> ValidationResult:
    """
    Convenience function to validate research data.

    Args:
        data: Extracted research data
        sources: List of source information

    Returns:
        ValidationResult
    """
    validator = CrossSourceValidator()
    facts = []

    # Convert data to facts
    for i, (key, value) in enumerate(data.items()):
        if value is not None and sources:
            source_info = sources[i % len(sources)] if i < len(sources) else sources[0]
            source = SourceInfo.from_url(source_info.get("url", "unknown"))

            facts.append(Fact(
                id=f"fact_{i}",
                category=key,
                claim=f"{key}: {value}",
                value=value,
                source=source
            ))

    return validator.validate_facts(facts)
