"""
Fact Extractor Module for Quality Assurance.

Extracts structured facts from agent outputs for contradiction detection
and quality assessment. Provides pattern-based extraction for common
fact types including numerical, temporal, and comparative claims.

Phase 10 Implementation - restored for backward compatibility.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class FactCategory(str, Enum):
    """Category of extracted facts."""
    FINANCIAL = "financial"
    MARKET = "market"
    COMPANY = "company"
    PRODUCT = "product"
    LEADERSHIP = "leadership"
    OPERATIONAL = "operational"
    UNKNOWN = "unknown"


class ClaimType(str, Enum):
    """Type of claim being made."""
    NUMERICAL = "numerical"  # Contains specific numbers
    TEMPORAL = "temporal"  # Contains dates/time references
    COMPARATIVE = "comparative"  # Compares entities
    ATTRIBUTIVE = "attributive"  # Assigns attributes/properties


@dataclass
class ExtractedFact:
    """A fact extracted from text content."""
    content: str
    category: FactCategory = FactCategory.UNKNOWN
    claim_type: ClaimType = ClaimType.ATTRIBUTIVE
    source_agent: str = "unknown"
    confidence_hint: float = 0.5
    needs_verification: bool = True
    entities: List[str] = field(default_factory=list)

    def to_research_fact(self, source: Any) -> Any:
        """Convert to ResearchFact model for compatibility."""
        from .models import ResearchFact, ConfidenceLevel

        # Map confidence hint to confidence level
        if self.confidence_hint >= 0.7:
            confidence = ConfidenceLevel.HIGH
        elif self.confidence_hint >= 0.4:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW

        return ResearchFact(
            content=self.content,
            source=source,
            confidence=confidence,
            extracted_by=self.source_agent
        )


@dataclass
class ExtractedEntity:
    """An entity extracted from text."""
    text: str
    entity_type: str  # "number", "company", "date", "person", etc.
    start_pos: int = 0
    end_pos: int = 0


@dataclass
class ExtractionResult:
    """Result of fact extraction from text."""
    facts: List[ExtractedFact] = field(default_factory=list)
    entities: List[ExtractedEntity] = field(default_factory=list)
    total_facts: int = 0
    total_sentences: int = 0

    @property
    def facts_by_category(self) -> Dict[FactCategory, List[ExtractedFact]]:
        """Group facts by category."""
        result: Dict[FactCategory, List[ExtractedFact]] = {}
        for fact in self.facts:
            if fact.category not in result:
                result[fact.category] = []
            result[fact.category].append(fact)
        return result


class FactExtractor:
    """
    Extract structured facts from text content.

    Identifies numerical claims, temporal references, comparisons,
    and attributive statements from agent outputs.

    Usage:
        extractor = FactExtractor()
        result = extractor.extract(text, agent_name="researcher")
        for fact in result.facts:
            print(f"{fact.claim_type}: {fact.content}")
    """

    def __init__(self):
        """Initialize the fact extractor with compiled patterns."""
        # Numerical patterns (money, percentages, counts)
        self._numerical_patterns = [
            # Currency amounts
            re.compile(r'\$[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|trillion|[BMT]))?', re.IGNORECASE),
            re.compile(r'[\d,]+(?:\.\d+)?\s*(?:USD|EUR|GBP|BRL|MXN)', re.IGNORECASE),
            # Percentages
            re.compile(r'[\d,]+(?:\.\d+)?\s*%'),
            # Employee counts and general numbers with units
            re.compile(r'[\d,]+\s+(?:employees|workers|staff|people)', re.IGNORECASE),
            # Large numbers with multipliers
            re.compile(r'[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand|[BMKbmk])\b', re.IGNORECASE),
        ]

        # Temporal patterns
        self._temporal_patterns = [
            re.compile(r'\b(?:19|20)\d{2}\b'),  # Years
            re.compile(r'\b(?:Q[1-4]|FY)\s*(?:19|20)?\d{2}\b', re.IGNORECASE),  # Quarters
            re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', re.IGNORECASE),
            re.compile(r'\bfounded\s+(?:in\s+)?(?:19|20)\d{2}\b', re.IGNORECASE),
            re.compile(r'\b(?:since|from|in)\s+(?:19|20)\d{2}\b', re.IGNORECASE),
        ]

        # Comparative patterns
        self._comparative_patterns = [
            re.compile(r'\b(?:larger|smaller|bigger|better|worse|higher|lower|more|less|greater)\s+than\b', re.IGNORECASE),
            re.compile(r'\b(?:outperform|underperform|exceed|surpass|lag)\w*\b', re.IGNORECASE),
            re.compile(r'\b(?:compared\s+to|versus|vs\.?)\b', re.IGNORECASE),
            re.compile(r'\b(?:leading|trailing|ahead|behind)\b', re.IGNORECASE),
        ]

        # Category keywords
        self._category_keywords = {
            FactCategory.FINANCIAL: [
                'revenue', 'profit', 'income', 'ebitda', 'earnings', 'sales',
                'margin', 'cash flow', 'dividend', 'eps', 'market cap',
                'valuation', 'funding', 'investment', 'debt', 'assets'
            ],
            FactCategory.MARKET: [
                'market share', 'tam', 'sam', 'cagr', 'growth rate',
                'market size', 'industry', 'sector', 'competition'
            ],
            FactCategory.COMPANY: [
                'founded', 'headquarters', 'headquartered', 'employees',
                'established', 'incorporated', 'based in', 'located'
            ],
            FactCategory.LEADERSHIP: [
                'ceo', 'cfo', 'cto', 'founder', 'chairman', 'president',
                'executive', 'board', 'director', 'chief'
            ],
            FactCategory.PRODUCT: [
                'product', 'service', 'platform', 'solution', 'offering',
                'launch', 'release', 'feature'
            ],
        }

        # Confidence modifiers
        self._high_confidence_indicators = [
            'according to', 'reported', 'announced', 'confirmed',
            'sec filing', 'official', 'stated', 'disclosed'
        ]
        self._low_confidence_indicators = [
            'approximately', 'about', 'around', 'estimated', 'roughly',
            'may', 'might', 'could', 'possibly', 'potentially'
        ]

    def extract(self, text: str, agent_name: str = "unknown") -> ExtractionResult:
        """
        Extract facts from text content.

        Args:
            text: Text to extract facts from
            agent_name: Name of the agent that produced this text

        Returns:
            ExtractionResult with extracted facts and entities
        """
        if not text or not text.strip():
            return ExtractionResult()

        sentences = self._split_sentences(text)
        facts = []
        all_entities = []

        for sentence in sentences:
            # Skip very short sentences
            if len(sentence.strip()) < 15:
                continue

            # Determine claim type
            claim_type = self._determine_claim_type(sentence)

            # Determine category
            category = self._determine_category(sentence, agent_name)

            # Calculate confidence hint
            confidence = self._calculate_confidence(sentence)

            # Extract entities
            entities = self._extract_entities(sentence)
            all_entities.extend(entities)

            # Create fact if it has extractable content
            if claim_type in (ClaimType.NUMERICAL, ClaimType.TEMPORAL, ClaimType.COMPARATIVE) or entities:
                fact = ExtractedFact(
                    content=sentence.strip(),
                    category=category,
                    claim_type=claim_type,
                    source_agent=agent_name,
                    confidence_hint=confidence,
                    needs_verification=confidence < 0.7,
                    entities=[e.text for e in entities]
                )
                facts.append(fact)

        return ExtractionResult(
            facts=facts,
            entities=all_entities,
            total_facts=len(facts),
            total_sentences=len(sentences)
        )

    def extract_from_agent_output(
        self,
        agent_output: Dict[str, Any],
        agent_name: str
    ) -> ExtractionResult:
        """
        Extract facts from structured agent output.

        Args:
            agent_output: Dictionary output from an agent
            agent_name: Name of the agent

        Returns:
            ExtractionResult with extracted facts
        """
        all_facts = []
        all_entities = []
        total_sentences = 0

        # Collect text from string fields
        for key, value in agent_output.items():
            if isinstance(value, str) and len(value) > 20:
                result = self.extract(value, agent_name)
                all_facts.extend(result.facts)
                all_entities.extend(result.entities)
                total_sentences += result.total_sentences

        return ExtractionResult(
            facts=all_facts,
            entities=all_entities,
            total_facts=len(all_facts),
            total_sentences=total_sentences
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences, preserving decimals and abbreviations."""
        # Protect common abbreviations
        protected = text
        abbreviations = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'Inc.', 'Ltd.', 'Corp.', 'vs.', 'etc.']
        for abbr in abbreviations:
            protected = protected.replace(abbr, abbr.replace('.', '<DOT>'))

        # Protect decimal numbers
        protected = re.sub(r'(\d)\.(\d)', r'\1<DOT>\2', protected)

        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', protected)

        # Restore protected characters
        sentences = [s.replace('<DOT>', '.') for s in sentences]

        return sentences

    def _determine_claim_type(self, text: str) -> ClaimType:
        """Determine the type of claim in the text."""
        text_lower = text.lower()

        # Check for comparative language
        for pattern in self._comparative_patterns:
            if pattern.search(text):
                return ClaimType.COMPARATIVE

        # Check for numerical content
        for pattern in self._numerical_patterns:
            if pattern.search(text):
                return ClaimType.NUMERICAL

        # Check for temporal content
        for pattern in self._temporal_patterns:
            if pattern.search(text):
                return ClaimType.TEMPORAL

        return ClaimType.ATTRIBUTIVE

    def _determine_category(self, text: str, agent_name: str) -> FactCategory:
        """Determine the category based on text content and agent name."""
        text_lower = text.lower()

        # Agent name hints
        agent_hints = {
            'financial': FactCategory.FINANCIAL,
            'market': FactCategory.MARKET,
            'researcher': FactCategory.COMPANY,
        }

        # Check keywords for each category
        category_scores: Dict[FactCategory, int] = {}
        for category, keywords in self._category_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                category_scores[category] = score

        # Return highest scoring category
        if category_scores:
            return max(category_scores, key=category_scores.get)

        # Fall back to agent hint
        for hint, category in agent_hints.items():
            if hint in agent_name.lower():
                return category

        return FactCategory.UNKNOWN

    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence hint based on language patterns."""
        text_lower = text.lower()
        confidence = 0.5  # Base confidence

        # High confidence indicators
        for indicator in self._high_confidence_indicators:
            if indicator in text_lower:
                confidence += 0.15
                break

        # Low confidence indicators
        for indicator in self._low_confidence_indicators:
            if indicator in text_lower:
                confidence -= 0.15
                break

        # Numerical specificity boost
        if re.search(r'\d+\.\d+', text):  # Decimal numbers
            confidence += 0.1

        # Cap confidence
        return max(0.1, min(0.95, confidence))

    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities from text."""
        entities = []

        # Extract numbers
        for pattern in self._numerical_patterns:
            for match in pattern.finditer(text):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    entity_type="number",
                    start_pos=match.start(),
                    end_pos=match.end()
                ))

        # Extract years
        year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        for match in year_pattern.finditer(text):
            entities.append(ExtractedEntity(
                text=match.group(),
                entity_type="date",
                start_pos=match.start(),
                end_pos=match.end()
            ))

        return entities


# Convenience functions

def extract_facts(text: str, agent_name: str) -> List[ExtractedFact]:
    """
    Convenience function to extract facts from text.

    Args:
        text: Text to extract from
        agent_name: Name of source agent

    Returns:
        List of ExtractedFact objects
    """
    extractor = FactExtractor()
    result = extractor.extract(text, agent_name)
    return result.facts


def extract_from_all_agents(
    agent_outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, ExtractionResult]:
    """
    Extract facts from multiple agent outputs.

    Args:
        agent_outputs: Dict mapping agent names to their outputs

    Returns:
        Dict mapping agent names to ExtractionResult
    """
    extractor = FactExtractor()
    results = {}

    for agent_name, output in agent_outputs.items():
        if isinstance(output, dict):
            results[agent_name] = extractor.extract_from_agent_output(output, agent_name)
        elif isinstance(output, str):
            results[agent_name] = extractor.extract(output, agent_name)
        else:
            results[agent_name] = ExtractionResult()

    return results
