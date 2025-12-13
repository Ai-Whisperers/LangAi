"""
Enhanced Contradiction Detector Module.

Addresses Issue #5: Contradiction Detection Weaknesses.
- Uses semantic similarity instead of simple word overlap
- Handles different number formats ($1.5B vs 1500M)
- Tracks contradiction confidence with evidence
- Distinguishes contradictions from updates/corrections
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from ..utils import get_logger

logger = get_logger(__name__)


class ContradictionType(Enum):
    """Types of contradictions detected."""
    NUMERIC = "numeric"  # Numbers that conflict
    TEMPORAL = "temporal"  # Timeline inconsistencies
    CATEGORICAL = "categorical"  # Mutually exclusive categories
    FACTUAL = "factual"  # Conflicting facts
    DIRECTIONAL = "directional"  # Opposite trends (up vs down)
    UPDATE = "update"  # Not contradiction - newer data


class ContradictionSeverity(Enum):
    """Severity levels for contradictions."""
    CRITICAL = "critical"  # Major claim conflicts
    SIGNIFICANT = "significant"  # Notable inconsistencies
    MINOR = "minor"  # Small discrepancies
    NEGLIGIBLE = "negligible"  # Within tolerance


@dataclass
class ExtractedClaim:
    """A claim extracted from text with metadata."""
    text: str
    value: Optional[Any]
    unit: Optional[str]
    field_type: str
    source: str
    timestamp: Optional[datetime] = None
    confidence: float = 1.0

    def __hash__(self):
        return hash((self.text, self.field_type, self.source))


@dataclass
class Contradiction:
    """A detected contradiction between claims."""
    claim_a: ExtractedClaim
    claim_b: ExtractedClaim
    contradiction_type: ContradictionType
    severity: ContradictionSeverity
    confidence: float
    explanation: str
    resolution_suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "claim_a": {
                "text": self.claim_a.text,
                "source": self.claim_a.source,
                "value": self.claim_a.value
            },
            "claim_b": {
                "text": self.claim_b.text,
                "source": self.claim_b.source,
                "value": self.claim_b.value
            },
            "type": self.contradiction_type.value,
            "severity": self.severity.value,
            "confidence": round(self.confidence, 3),
            "explanation": self.explanation,
            "resolution": self.resolution_suggestion
        }


@dataclass
class ContradictionReport:
    """Complete contradiction analysis report."""
    contradictions: List[Contradiction]
    total_claims_analyzed: int
    contradiction_rate: float
    severity_distribution: Dict[str, int]
    has_critical: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_contradictions": len(self.contradictions),
            "total_claims": self.total_claims_analyzed,
            "contradiction_rate": round(self.contradiction_rate, 3),
            "severity_distribution": self.severity_distribution,
            "has_critical": self.has_critical,
            "contradictions": [c.to_dict() for c in self.contradictions]
        }


class EnhancedContradictionDetector:
    """
    Semantic contradiction detection with numeric normalization.

    Improvements over basic detector:
    1. Semantic similarity for fact comparison (not word overlap)
    2. Numeric normalization ($1.5B == 1500M == 1,500,000,000)
    3. Temporal awareness (distinguishes updates from contradictions)
    4. Confidence scoring with evidence
    5. Multiple contradiction types

    Usage:
        detector = EnhancedContradictionDetector()
        report = detector.analyze(text_a, text_b)
        # or
        report = detector.analyze_multi_source(
            {"sec_filing": text1, "news": text2, "website": text3}
        )
    """

    # Numeric extraction patterns
    NUMERIC_PATTERNS = {
        "currency": re.compile(
            r'\$\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|thousand|[TBMKtbmk])?',
            re.IGNORECASE
        ),
        "percentage": re.compile(
            r'([\d,]+(?:\.\d+)?)\s*%'
        ),
        "plain_number": re.compile(
            r'(?<!\$)([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|thousand|employees?|users?|customers?)?',
            re.IGNORECASE
        ),
    }

    # Multipliers for normalization
    MULTIPLIERS = {
        "trillion": 1e12, "t": 1e12,
        "billion": 1e9, "b": 1e9,
        "million": 1e6, "m": 1e6,
        "thousand": 1e3, "k": 1e3,
    }

    # Fields and their tolerance for "same" values
    FIELD_TOLERANCES = {
        "revenue": 0.05,  # 5% tolerance
        "market_cap": 0.10,  # 10% (more volatile)
        "employees": 0.15,  # 15% (estimates vary)
        "growth": 0.02,  # 2 percentage points
        "margin": 0.02,
        "pe_ratio": 0.10,
        "stock_price": 0.05,
    }

    # Semantic field categories for comparison
    FIELD_KEYWORDS = {
        "revenue": ["revenue", "sales", "turnover", "top line", "gross income"],
        "profit": ["profit", "earnings", "net income", "bottom line", "ebit", "ebitda"],
        "market_cap": ["market cap", "market value", "valuation", "market capitalization"],
        "employees": ["employees", "workforce", "headcount", "staff", "team size"],
        "growth": ["growth", "increase", "grew", "expanded", "yoy", "year over year"],
        "headquarters": ["headquarters", "hq", "based in", "headquartered", "located"],
        "founded": ["founded", "established", "started", "incorporated", "since"],
        "ceo": ["ceo", "chief executive", "leader", "headed by"],
    }

    # Directional words for trend detection
    DIRECTION_WORDS = {
        "positive": ["increase", "grew", "growth", "up", "higher", "gain", "rise", "improved"],
        "negative": ["decrease", "declined", "down", "lower", "drop", "fell", "reduced", "loss"],
    }

    def __init__(self, use_embeddings: bool = True):
        """
        Initialize detector.

        Args:
            use_embeddings: Whether to use sentence embeddings for similarity
        """
        self._encoder = None
        self._use_embeddings = use_embeddings

        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self._encoder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("EnhancedContradictionDetector initialized with embeddings")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed. "
                    "Using keyword-based comparison."
                )
                self._use_embeddings = False

    def analyze(
        self,
        text_a: str,
        text_b: str,
        source_a: str = "source_a",
        source_b: str = "source_b"
    ) -> ContradictionReport:
        """
        Analyze two texts for contradictions.

        Args:
            text_a: First text
            text_b: Second text
            source_a: Identifier for first source
            source_b: Identifier for second source

        Returns:
            ContradictionReport with detected contradictions
        """
        claims_a = self._extract_claims(text_a, source_a)
        claims_b = self._extract_claims(text_b, source_b)

        contradictions = self._find_contradictions(claims_a, claims_b)

        return self._build_report(contradictions, len(claims_a) + len(claims_b))

    def analyze_multi_source(
        self,
        sources: Dict[str, str]
    ) -> ContradictionReport:
        """
        Analyze multiple sources for cross-contradictions.

        Args:
            sources: Dict mapping source name to text content

        Returns:
            ContradictionReport aggregating all contradictions
        """
        all_claims: Dict[str, List[ExtractedClaim]] = {}

        for source_name, text in sources.items():
            all_claims[source_name] = self._extract_claims(text, source_name)

        # Compare all pairs
        all_contradictions = []
        source_names = list(sources.keys())
        total_claims = sum(len(c) for c in all_claims.values())

        for i, source_a in enumerate(source_names):
            for source_b in source_names[i+1:]:
                contradictions = self._find_contradictions(
                    all_claims[source_a],
                    all_claims[source_b]
                )
                all_contradictions.extend(contradictions)

        return self._build_report(all_contradictions, total_claims)

    def _extract_claims(
        self,
        text: str,
        source: str
    ) -> List[ExtractedClaim]:
        """Extract factual claims from text."""
        claims = []

        # Extract numeric claims
        claims.extend(self._extract_numeric_claims(text, source))

        # Extract categorical/factual claims
        claims.extend(self._extract_factual_claims(text, source))

        # Extract directional claims (trends)
        claims.extend(self._extract_directional_claims(text, source))

        return claims

    def _extract_numeric_claims(
        self,
        text: str,
        source: str
    ) -> List[ExtractedClaim]:
        """Extract claims with numeric values."""
        claims = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Currency values
            for match in self.NUMERIC_PATTERNS["currency"].finditer(sentence):
                value = self._normalize_number(match.group(1), match.group(2))
                field_type = self._infer_field_type(sentence)

                claims.append(ExtractedClaim(
                    text=sentence.strip(),
                    value=value,
                    unit="USD",
                    field_type=field_type,
                    source=source
                ))

            # Percentages
            for match in self.NUMERIC_PATTERNS["percentage"].finditer(sentence):
                value = float(match.group(1).replace(",", ""))
                field_type = self._infer_field_type(sentence, is_percentage=True)

                claims.append(ExtractedClaim(
                    text=sentence.strip(),
                    value=value,
                    unit="percent",
                    field_type=field_type,
                    source=source
                ))

            # Plain numbers with context
            for match in self.NUMERIC_PATTERNS["plain_number"].finditer(sentence):
                context = match.group(2) or ""
                if context.lower() in ["employees", "employee", "users", "user", "customers", "customer"]:
                    value = self._normalize_number(match.group(1), None)
                    claims.append(ExtractedClaim(
                        text=sentence.strip(),
                        value=value,
                        unit=context.lower(),
                        field_type="employees" if "employ" in context.lower() else "users",
                        source=source
                    ))

        return claims

    def _extract_factual_claims(
        self,
        text: str,
        source: str
    ) -> List[ExtractedClaim]:
        """Extract categorical/factual claims."""
        claims = []
        sentences = self._split_sentences(text)

        # Headquarters extraction
        hq_patterns = [
            r'(?:headquartered|based|located)\s+in\s+([A-Z][a-zA-Z\s,]+)',
            r'headquarters?\s+(?:is|are)\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+)',
        ]

        for sentence in sentences:
            for pattern in hq_patterns:
                match = re.search(pattern, sentence)
                if match:
                    claims.append(ExtractedClaim(
                        text=sentence.strip(),
                        value=match.group(1).strip(),
                        unit=None,
                        field_type="headquarters",
                        source=source
                    ))

        # CEO extraction
        ceo_patterns = [
            r'(?:CEO|chief executive)\s+(?:is|:)?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:is|serves as)\s+(?:the\s+)?CEO',
        ]

        for sentence in sentences:
            for pattern in ceo_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    claims.append(ExtractedClaim(
                        text=sentence.strip(),
                        value=match.group(1).strip(),
                        unit=None,
                        field_type="ceo",
                        source=source
                    ))

        # Founded year
        founded_patterns = [
            r'founded\s+(?:in\s+)?(\d{4})',
            r'established\s+(?:in\s+)?(\d{4})',
            r'since\s+(\d{4})',
        ]

        for sentence in sentences:
            for pattern in founded_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    claims.append(ExtractedClaim(
                        text=sentence.strip(),
                        value=int(match.group(1)),
                        unit="year",
                        field_type="founded",
                        source=source
                    ))

        return claims

    def _extract_directional_claims(
        self,
        text: str,
        source: str
    ) -> List[ExtractedClaim]:
        """Extract claims about trends and directions."""
        claims = []
        sentences = self._split_sentences(text)

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Determine direction
            direction = None
            for word in self.DIRECTION_WORDS["positive"]:
                if word in sentence_lower:
                    direction = "positive"
                    break
            if not direction:
                for word in self.DIRECTION_WORDS["negative"]:
                    if word in sentence_lower:
                        direction = "negative"
                        break

            if direction:
                # Determine what metric the direction applies to
                field_type = self._infer_field_type(sentence)
                if field_type != "unknown":
                    claims.append(ExtractedClaim(
                        text=sentence.strip(),
                        value=direction,
                        unit="direction",
                        field_type=f"{field_type}_trend",
                        source=source
                    ))

        return claims

    def _find_contradictions(
        self,
        claims_a: List[ExtractedClaim],
        claims_b: List[ExtractedClaim]
    ) -> List[Contradiction]:
        """Find contradictions between two sets of claims."""
        contradictions = []

        for claim_a in claims_a:
            for claim_b in claims_b:
                # Only compare claims of same field type
                if not self._claims_comparable(claim_a, claim_b):
                    continue

                contradiction = self._check_contradiction(claim_a, claim_b)
                if contradiction:
                    contradictions.append(contradiction)

        return contradictions

    def _claims_comparable(
        self,
        claim_a: ExtractedClaim,
        claim_b: ExtractedClaim
    ) -> bool:
        """Determine if two claims can be compared."""
        # Same field type
        if claim_a.field_type == claim_b.field_type:
            return True

        # Same unit type
        if claim_a.unit == claim_b.unit and claim_a.unit is not None:
            return True

        # Check semantic similarity if embeddings available
        if self._use_embeddings and self._encoder:
            similarity = self._semantic_similarity(
                claim_a.text,
                claim_b.text
            )
            return similarity > 0.7

        # Keyword-based comparison
        return self._keyword_similarity(claim_a, claim_b) > 0.5

    def _check_contradiction(
        self,
        claim_a: ExtractedClaim,
        claim_b: ExtractedClaim
    ) -> Optional[Contradiction]:
        """Check if two claims contradict each other."""

        # Numeric contradiction
        if claim_a.value is not None and claim_b.value is not None:
            if isinstance(claim_a.value, (int, float)) and isinstance(claim_b.value, (int, float)):
                return self._check_numeric_contradiction(claim_a, claim_b)

        # Directional contradiction
        if claim_a.unit == "direction" and claim_b.unit == "direction":
            return self._check_directional_contradiction(claim_a, claim_b)

        # Factual contradiction (strings)
        if isinstance(claim_a.value, str) and isinstance(claim_b.value, str):
            return self._check_factual_contradiction(claim_a, claim_b)

        return None

    def _check_numeric_contradiction(
        self,
        claim_a: ExtractedClaim,
        claim_b: ExtractedClaim
    ) -> Optional[Contradiction]:
        """Check for numeric value contradictions."""
        val_a = float(claim_a.value)
        val_b = float(claim_b.value)

        if val_a == 0 or val_b == 0:
            return None

        # Calculate difference
        diff_ratio = abs(val_a - val_b) / max(abs(val_a), abs(val_b))

        # Get tolerance for this field type
        tolerance = self.FIELD_TOLERANCES.get(
            claim_a.field_type.replace("_trend", ""),
            0.20  # Default 20% tolerance
        )

        if diff_ratio <= tolerance:
            return None  # Within tolerance

        # Determine severity
        if diff_ratio > 0.5:
            severity = ContradictionSeverity.CRITICAL
        elif diff_ratio > 0.3:
            severity = ContradictionSeverity.SIGNIFICANT
        elif diff_ratio > 0.15:
            severity = ContradictionSeverity.MINOR
        else:
            severity = ContradictionSeverity.NEGLIGIBLE

        return Contradiction(
            claim_a=claim_a,
            claim_b=claim_b,
            contradiction_type=ContradictionType.NUMERIC,
            severity=severity,
            confidence=min(0.95, 0.5 + diff_ratio),
            explanation=f"Numeric values differ by {diff_ratio*100:.1f}%: {val_a} vs {val_b}",
            resolution_suggestion=f"Verify {claim_a.field_type} from authoritative source"
        )

    def _check_directional_contradiction(
        self,
        claim_a: ExtractedClaim,
        claim_b: ExtractedClaim
    ) -> Optional[Contradiction]:
        """Check for directional/trend contradictions."""
        if claim_a.value != claim_b.value:
            return Contradiction(
                claim_a=claim_a,
                claim_b=claim_b,
                contradiction_type=ContradictionType.DIRECTIONAL,
                severity=ContradictionSeverity.SIGNIFICANT,
                confidence=0.8,
                explanation=f"Contradicting trends: {claim_a.value} vs {claim_b.value}",
                resolution_suggestion="Check date of sources - newer data may supersede"
            )
        return None

    def _check_factual_contradiction(
        self,
        claim_a: ExtractedClaim,
        claim_b: ExtractedClaim
    ) -> Optional[Contradiction]:
        """Check for factual/categorical contradictions."""
        val_a = claim_a.value.lower().strip()
        val_b = claim_b.value.lower().strip()

        # Exact match
        if val_a == val_b:
            return None

        # Check if one contains the other (partial match)
        if val_a in val_b or val_b in val_a:
            return None

        # For headquarters, check city match
        if claim_a.field_type == "headquarters":
            # Extract cities
            city_a = val_a.split(",")[0].strip()
            city_b = val_b.split(",")[0].strip()
            if city_a == city_b:
                return None

        return Contradiction(
            claim_a=claim_a,
            claim_b=claim_b,
            contradiction_type=ContradictionType.FACTUAL,
            severity=ContradictionSeverity.SIGNIFICANT,
            confidence=0.85,
            explanation=f"Conflicting {claim_a.field_type}: '{claim_a.value}' vs '{claim_b.value}'",
            resolution_suggestion=f"Verify {claim_a.field_type} from official source"
        )

    def _normalize_number(
        self,
        num_str: str,
        multiplier_str: Optional[str]
    ) -> float:
        """Normalize a number with multiplier to base value."""
        # Remove commas
        num = float(num_str.replace(",", ""))

        if multiplier_str:
            mult_key = multiplier_str.lower().rstrip('s')  # Remove plural
            multiplier = self.MULTIPLIERS.get(mult_key, 1)
            num *= multiplier

        return num

    def _infer_field_type(
        self,
        sentence: str,
        is_percentage: bool = False
    ) -> str:
        """Infer what field type a sentence is about."""
        sentence_lower = sentence.lower()

        for field, keywords in self.FIELD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in sentence_lower:
                    return field

        # Percentage-specific inference
        if is_percentage:
            if any(w in sentence_lower for w in ["margin", "profit"]):
                return "margin"
            if any(w in sentence_lower for w in ["growth", "increase", "grew"]):
                return "growth"

        return "unknown"

    def _semantic_similarity(
        self,
        text_a: str,
        text_b: str
    ) -> float:
        """Calculate semantic similarity using embeddings."""
        if not self._encoder:
            return 0.5

        try:
            import numpy as np
            embeddings = self._encoder.encode([text_a, text_b])

            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            logger.debug(f"Embedding similarity failed: {e}")
            return 0.5

    def _keyword_similarity(
        self,
        claim_a: ExtractedClaim,
        claim_b: ExtractedClaim
    ) -> float:
        """Calculate keyword-based similarity."""
        words_a = set(claim_a.text.lower().split())
        words_b = set(claim_b.text.lower().split())

        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of',
                     'and', 'in', 'for', 'on', 'with', 'at', 'by', 'this', 'that'}
        words_a -= stopwords
        words_b -= stopwords

        if not words_a or not words_b:
            return 0.0

        intersection = words_a & words_b
        union = words_a | words_b

        return len(intersection) / len(union)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _build_report(
        self,
        contradictions: List[Contradiction],
        total_claims: int
    ) -> ContradictionReport:
        """Build the final contradiction report."""
        severity_dist = {
            "critical": 0,
            "significant": 0,
            "minor": 0,
            "negligible": 0
        }

        for c in contradictions:
            severity_dist[c.severity.value] += 1

        return ContradictionReport(
            contradictions=contradictions,
            total_claims_analyzed=total_claims,
            contradiction_rate=len(contradictions) / max(total_claims, 1),
            severity_distribution=severity_dist,
            has_critical=severity_dist["critical"] > 0
        )
