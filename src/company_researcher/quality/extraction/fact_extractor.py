"""
Fact Extraction Module (Phase 10).

Extracts verifiable facts from agent outputs for quality validation.

Features:
- Entity extraction (companies, people, products, numbers)
- Claim detection (statements that can be verified)
- Source linking (associate facts with sources)
- Fact categorization (financial, market, product, etc.)
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .models import Source, ResearchFact, SourceQuality, ConfidenceLevel


# ============================================================================
# Enumerations
# ============================================================================

class FactCategory(str, Enum):
    """Categories for extracted facts."""
    FINANCIAL = "financial"       # Revenue, profit, funding, valuation
    MARKET = "market"             # Market size, share, trends
    PRODUCT = "product"           # Products, features, technology
    COMPETITIVE = "competitive"   # Competitors, positioning
    COMPANY = "company"           # General company info
    LEADERSHIP = "leadership"     # Executives, team
    TEMPORAL = "temporal"         # Dates, timelines, events
    QUANTITATIVE = "quantitative" # Numbers, metrics, statistics
    UNKNOWN = "unknown"


class ClaimType(str, Enum):
    """Types of verifiable claims."""
    NUMERICAL = "numerical"        # Contains specific numbers
    COMPARATIVE = "comparative"    # Comparisons (larger than, better than)
    TEMPORAL = "temporal"          # Time-based claims (founded in, since)
    ATTRIBUTIVE = "attributive"    # Attributes to entity (CEO of, makes)
    EXISTENTIAL = "existential"    # Existence claims (has, offers)
    CAUSAL = "causal"              # Cause-effect (because, leads to)


# ============================================================================
# Extraction Patterns
# ============================================================================

# Numerical patterns
NUMERICAL_PATTERNS = [
    r'\$[\d,]+(?:\.\d+)?[BMK]?',                      # Currency ($1.5B)
    r'[\d,]+(?:\.\d+)?%',                             # Percentages
    r'[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand)', # Written numbers
    r'(?:FY|Q[1-4])\s*\d{4}',                         # Fiscal periods
    r'\d{4}(?:-\d{2}(?:-\d{2})?)?',                   # Dates
    r'[\d,]+\s*(?:employees|users|customers)',        # Counts
]

# Comparative keywords
COMPARATIVE_KEYWORDS = [
    'larger than', 'smaller than', 'more than', 'less than',
    'better than', 'worse than', 'higher than', 'lower than',
    'leading', 'trailing', 'outperforms', 'underperforms',
    'exceeds', 'surpasses', 'lags behind'
]

# Temporal keywords
TEMPORAL_KEYWORDS = [
    'founded in', 'established in', 'since', 'as of',
    'in Q[1-4]', 'in FY', 'year-over-year', 'YoY',
    'annually', 'quarterly', 'monthly', 'recently',
    'launched', 'released', 'introduced'
]

# Financial keywords
FINANCIAL_KEYWORDS = [
    'revenue', 'profit', 'margin', 'EBITDA', 'cash flow',
    'funding', 'valuation', 'market cap', 'stock', 'IPO',
    'debt', 'equity', 'assets', 'liabilities', 'ROI', 'ROE'
]

# Market keywords
MARKET_KEYWORDS = [
    'market size', 'TAM', 'SAM', 'SOM', 'market share',
    'industry', 'sector', 'segment', 'trend', 'growth rate',
    'CAGR', 'penetration', 'addressable market'
]


# ============================================================================
# Data Models
# ============================================================================

class ExtractedEntity(BaseModel):
    """An entity extracted from text."""
    name: str
    entity_type: str  # company, person, product, number, date
    context: str      # Surrounding text
    start_pos: int
    end_pos: int


class ExtractedFact(BaseModel):
    """A fact extracted for verification."""
    content: str
    category: FactCategory = FactCategory.UNKNOWN
    claim_type: ClaimType = ClaimType.ATTRIBUTIVE
    entities: List[ExtractedEntity] = Field(default_factory=list)
    source_agent: str = "unknown"
    source_url: Optional[str] = None
    confidence_hint: float = Field(ge=0, le=1, default=0.5)
    needs_verification: bool = True
    extracted_at: datetime = Field(default_factory=datetime.now)

    def to_research_fact(self, source: Source) -> ResearchFact:
        """Convert to ResearchFact model."""
        confidence = ConfidenceLevel.HIGH if self.confidence_hint > 0.7 else \
                     ConfidenceLevel.MEDIUM if self.confidence_hint > 0.4 else \
                     ConfidenceLevel.LOW

        return ResearchFact(
            content=self.content,
            source=source,
            extracted_by=self.source_agent,
            confidence=confidence,
            verified=not self.needs_verification
        )


class ExtractionResult(BaseModel):
    """Result of fact extraction from text."""
    facts: List[ExtractedFact] = Field(default_factory=list)
    entities: List[ExtractedEntity] = Field(default_factory=list)
    total_sentences: int = 0
    total_facts: int = 0
    extraction_time_ms: float = 0.0

    @property
    def facts_by_category(self) -> Dict[str, List[ExtractedFact]]:
        """Group facts by category."""
        result = {}
        for fact in self.facts:
            cat = fact.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(fact)
        return result


# ============================================================================
# Fact Extractor
# ============================================================================

class FactExtractor:
    """
    Extract verifiable facts from agent outputs.

    Process:
    1. Split text into sentences
    2. Identify sentences with verifiable claims
    3. Extract entities (companies, numbers, dates)
    4. Categorize facts
    5. Assess verification need

    Usage:
        extractor = FactExtractor()
        result = extractor.extract(text, agent_name="financial")
    """

    def __init__(self):
        """Initialize fact extractor."""
        self._numerical_patterns = [re.compile(p) for p in NUMERICAL_PATTERNS]

    def extract(
        self,
        text: str,
        agent_name: str = "unknown",
        source_url: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract facts from text.

        Args:
            text: Text to extract facts from
            agent_name: Name of the agent that produced the text
            source_url: URL of the source (if known)

        Returns:
            ExtractionResult with facts and entities
        """
        start_time = datetime.now()

        # Split into sentences
        sentences = self._split_sentences(text)

        # Extract facts
        facts = []
        all_entities = []

        for sentence in sentences:
            # Skip short sentences
            if len(sentence) < 20:
                continue

            # Check if sentence contains verifiable claim
            if self._is_verifiable_claim(sentence):
                # Extract entities from sentence
                entities = self._extract_entities(sentence)
                all_entities.extend(entities)

                # Categorize and create fact
                category = self._categorize_fact(sentence)
                claim_type = self._detect_claim_type(sentence)
                confidence = self._assess_confidence(sentence, entities)

                fact = ExtractedFact(
                    content=sentence.strip(),
                    category=category,
                    claim_type=claim_type,
                    entities=entities,
                    source_agent=agent_name,
                    source_url=source_url,
                    confidence_hint=confidence,
                    needs_verification=confidence < 0.8
                )
                facts.append(fact)

        extraction_time = (datetime.now() - start_time).total_seconds() * 1000

        return ExtractionResult(
            facts=facts,
            entities=all_entities,
            total_sentences=len(sentences),
            total_facts=len(facts),
            extraction_time_ms=extraction_time
        )

    def extract_from_agent_output(
        self,
        agent_output: Dict[str, Any],
        agent_name: str
    ) -> ExtractionResult:
        """
        Extract facts from structured agent output.

        Args:
            agent_output: Agent's output dictionary
            agent_name: Name of the agent

        Returns:
            ExtractionResult
        """
        # Combine relevant text fields
        text_parts = []

        # Common text fields in agent outputs
        text_keys = [
            'analysis', 'content', 'company_overview', 'financial_analysis',
            'market_analysis', 'product_analysis', 'competitor_analysis'
        ]

        for key in text_keys:
            if key in agent_output and isinstance(agent_output[key], str):
                text_parts.append(agent_output[key])

        combined_text = "\n\n".join(text_parts)

        return self.extract(combined_text, agent_name)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        # Handle common abbreviations
        text = re.sub(r'(\d)\.\s*(\d)', r'\1<DOT>\2', text)  # Preserve decimals
        text = re.sub(r'(Mr|Mrs|Ms|Dr|Inc|Ltd|Corp|vs|etc)\.\s*', r'\1<DOT> ', text)

        # Split on sentence boundaries
        sentences = re.split(r'[.!?]\s+', text)

        # Restore dots
        sentences = [s.replace('<DOT>', '.').strip() for s in sentences]

        return [s for s in sentences if s]

    def _is_verifiable_claim(self, sentence: str) -> bool:
        """Check if sentence contains a verifiable claim."""
        sentence_lower = sentence.lower()

        # Check for numerical content
        for pattern in self._numerical_patterns:
            if pattern.search(sentence):
                return True

        # Check for comparative claims
        for keyword in COMPARATIVE_KEYWORDS:
            if keyword in sentence_lower:
                return True

        # Check for temporal claims
        for keyword in TEMPORAL_KEYWORDS:
            if re.search(keyword, sentence_lower, re.IGNORECASE):
                return True

        # Check for specific assertion keywords
        assertion_keywords = [
            'is', 'was', 'has', 'have', 'are', 'were',
            'will be', 'became', 'reported', 'announced'
        ]

        return any(f' {kw} ' in f' {sentence_lower} ' for kw in assertion_keywords)

    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities from text."""
        entities = []

        # Extract numbers/currencies
        for pattern in self._numerical_patterns:
            for match in pattern.finditer(text):
                entities.append(ExtractedEntity(
                    name=match.group(),
                    entity_type="number",
                    context=text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        # Extract potential company names (capitalized words)
        company_pattern = r'(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|Ltd|LLC|Co)\.?)?)'
        for match in re.finditer(company_pattern, text):
            name = match.group()
            if len(name) > 2 and name not in ['The', 'This', 'That', 'These']:
                entities.append(ExtractedEntity(
                    name=name,
                    entity_type="company",
                    context=text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        return entities

    def _categorize_fact(self, sentence: str) -> FactCategory:
        """Categorize a fact based on content."""
        sentence_lower = sentence.lower()

        # Check financial keywords
        if any(kw in sentence_lower for kw in FINANCIAL_KEYWORDS):
            return FactCategory.FINANCIAL

        # Check market keywords
        if any(kw in sentence_lower for kw in MARKET_KEYWORDS):
            return FactCategory.MARKET

        # Check product keywords
        product_keywords = ['product', 'feature', 'technology', 'software', 'platform', 'service']
        if any(kw in sentence_lower for kw in product_keywords):
            return FactCategory.PRODUCT

        # Check competitive keywords
        competitive_keywords = ['competitor', 'competition', 'rival', 'versus', 'market leader']
        if any(kw in sentence_lower for kw in competitive_keywords):
            return FactCategory.COMPETITIVE

        # Check leadership keywords
        leadership_keywords = ['CEO', 'founder', 'executive', 'CTO', 'CFO', 'president', 'board']
        if any(kw in sentence_lower for kw in leadership_keywords):
            return FactCategory.LEADERSHIP

        # Check for numbers (quantitative)
        if any(p.search(sentence) for p in self._numerical_patterns):
            return FactCategory.QUANTITATIVE

        return FactCategory.COMPANY

    def _detect_claim_type(self, sentence: str) -> ClaimType:
        """Detect the type of claim in a sentence."""
        sentence_lower = sentence.lower()

        # Check for numerical claims
        if any(p.search(sentence) for p in self._numerical_patterns):
            return ClaimType.NUMERICAL

        # Check for comparative claims
        if any(kw in sentence_lower for kw in COMPARATIVE_KEYWORDS):
            return ClaimType.COMPARATIVE

        # Check for temporal claims
        if any(re.search(kw, sentence_lower, re.IGNORECASE) for kw in TEMPORAL_KEYWORDS):
            return ClaimType.TEMPORAL

        # Check for causal claims
        causal_keywords = ['because', 'due to', 'leads to', 'results in', 'caused by']
        if any(kw in sentence_lower for kw in causal_keywords):
            return ClaimType.CAUSAL

        # Check for existential claims
        existential_keywords = ['has', 'have', 'offers', 'provides', 'includes']
        if any(kw in sentence_lower for kw in existential_keywords):
            return ClaimType.EXISTENTIAL

        return ClaimType.ATTRIBUTIVE

    def _assess_confidence(
        self,
        sentence: str,
        entities: List[ExtractedEntity]
    ) -> float:
        """
        Assess confidence in the fact.

        Higher confidence for:
        - Specific numbers
        - Named entities
        - Attribution to source
        """
        confidence = 0.5  # Base confidence

        # Boost for numerical entities
        numerical_entities = [e for e in entities if e.entity_type == "number"]
        if numerical_entities:
            confidence += 0.15

        # Boost for company mentions
        company_entities = [e for e in entities if e.entity_type == "company"]
        if company_entities:
            confidence += 0.1

        # Boost for specific attribution
        attribution_keywords = ['according to', 'reported by', 'stated', 'announced']
        if any(kw in sentence.lower() for kw in attribution_keywords):
            confidence += 0.15

        # Penalty for hedging language
        hedging_keywords = ['may', 'might', 'could', 'possibly', 'perhaps', 'approximately']
        if any(kw in sentence.lower() for kw in hedging_keywords):
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))


# ============================================================================
# Convenience Functions
# ============================================================================

def extract_facts(text: str, agent_name: str = "unknown") -> List[ExtractedFact]:
    """
    Extract facts from text.

    Args:
        text: Text to extract from
        agent_name: Agent that produced the text

    Returns:
        List of extracted facts
    """
    extractor = FactExtractor()
    result = extractor.extract(text, agent_name)
    return result.facts


def extract_from_all_agents(
    agent_outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, ExtractionResult]:
    """
    Extract facts from all agent outputs.

    Args:
        agent_outputs: Dict mapping agent names to their outputs

    Returns:
        Dict mapping agent names to extraction results
    """
    extractor = FactExtractor()
    results = {}

    for agent_name, output in agent_outputs.items():
        results[agent_name] = extractor.extract_from_agent_output(output, agent_name)

    return results
