"""
Key Point Extractor Module.

Extracts key points from text content based on importance signals.
"""

import re
from typing import Any, Dict, List

from .models import ContentType, KeyPoint


class KeyPointExtractor:
    """
    Extract key points from text content.

    Identifies the most important sentences and facts
    based on various signals.
    """

    # Importance signals
    IMPORTANCE_KEYWORDS = {
        "high": [
            "revenue",
            "profit",
            "growth",
            "market share",
            "billion",
            "million",
            "percent",
            "increased",
            "decreased",
            "launched",
            "acquired",
            "partnership",
            "announced",
            "leading",
            "first",
            "largest",
            "significant",
            "major",
            "key",
            "critical",
        ],
        "medium": [
            "expected",
            "projected",
            "estimated",
            "approximately",
            "reported",
            "according",
            "stated",
            "mentioned",
            "noted",
        ],
        "low": ["may", "might", "could", "possibly", "potentially", "some", "various", "certain"],
    }

    # Numerical patterns
    NUMERICAL_PATTERNS = [
        r"\$[\d,.]+\s*(?:billion|million|B|M|trillion|T)?",
        r"[\d,.]+\s*(?:percent|%)",
        r"[\d,.]+x",
        r"Q[1-4]\s*20\d{2}",
        r"20\d{2}",
    ]

    def __init__(self):
        """Initialize extractor."""
        self._sentence_splitter = re.compile(r"(?<=[.!?])\s+")

    def extract(
        self, text: str, max_points: int = 10, content_type: ContentType = ContentType.GENERAL
    ) -> List[KeyPoint]:
        """
        Extract key points from text.

        Args:
            text: Source text
            max_points: Maximum key points to extract
            content_type: Type of content for targeted extraction

        Returns:
            List of KeyPoints sorted by importance
        """
        sentences = self._split_sentences(text)
        scored_sentences = []

        for sentence in sentences:
            score = self._score_sentence(sentence, content_type)
            if score > 0.2:  # Minimum threshold
                entities = self._extract_entities(sentence)
                category = self._categorize_sentence(sentence)

                scored_sentences.append(
                    KeyPoint(
                        content=sentence.strip(),
                        importance=score,
                        category=category,
                        source_sentence=sentence,
                        entities=entities,
                    )
                )

        # Sort by importance and return top N
        scored_sentences.sort(key=lambda x: x.importance, reverse=True)
        return scored_sentences[:max_points]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Clean text
        text = re.sub(r"\s+", " ", text)
        sentences = self._sentence_splitter.split(text)
        # Filter very short sentences
        return [s for s in sentences if len(s) > 20]

    def _score_sentence(self, sentence: str, content_type: ContentType) -> float:
        """Score sentence importance."""
        score = 0.0
        sentence_lower = sentence.lower()

        # Keyword-based scoring
        for keyword in self.IMPORTANCE_KEYWORDS["high"]:
            if keyword in sentence_lower:
                score += 0.15

        for keyword in self.IMPORTANCE_KEYWORDS["medium"]:
            if keyword in sentence_lower:
                score += 0.08

        for keyword in self.IMPORTANCE_KEYWORDS["low"]:
            if keyword in sentence_lower:
                score -= 0.05

        # Numerical content bonus
        for pattern in self.NUMERICAL_PATTERNS:
            if re.search(pattern, sentence):
                score += 0.2

        # Content type specific boosting
        type_keywords = {
            ContentType.FINANCIAL: ["revenue", "profit", "earnings", "cash", "debt", "margin"],
            ContentType.MARKET: ["market", "share", "tam", "sam", "som", "growth", "industry"],
            ContentType.COMPETITIVE: ["competitor", "competition", "rival", "vs", "against"],
            ContentType.PRODUCT: ["product", "feature", "technology", "innovation", "launch"],
        }

        if content_type in type_keywords:
            for kw in type_keywords[content_type]:
                if kw in sentence_lower:
                    score += 0.1

        # Length normalization (prefer medium-length sentences)
        length = len(sentence)
        if 50 < length < 200:
            score += 0.1
        elif length > 300:
            score -= 0.1

        return min(1.0, max(0.0, score))

    def _extract_entities(self, sentence: str) -> List[str]:
        """Extract named entities from sentence."""
        entities = []

        # Company/proper noun pattern
        proper_nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", sentence)
        entities.extend(proper_nouns[:3])

        # Money amounts
        money = re.findall(r"\$[\d,.]+\s*(?:billion|million|B|M)?", sentence)
        entities.extend(money)

        # Percentages
        percents = re.findall(r"[\d,.]+\s*(?:percent|%)", sentence)
        entities.extend(percents)

        return entities[:5]  # Limit entities

    def _categorize_sentence(self, sentence: str) -> str:
        """Categorize sentence by topic."""
        sentence_lower = sentence.lower()

        categories = {
            "financial": ["revenue", "profit", "earnings", "financial", "cash", "debt"],
            "market": ["market", "industry", "sector", "growth", "share"],
            "competitive": ["competitor", "competition", "rival"],
            "product": ["product", "feature", "technology", "service"],
            "operations": ["employee", "office", "headquarters", "facility"],
        }

        for category, keywords in categories.items():
            if any(kw in sentence_lower for kw in keywords):
                return category

        return "general"


# ============================================================================
# Factory Function
# ============================================================================


def extract_key_points(
    text: str, max_points: int = 10, content_type: str = "general"
) -> List[Dict[str, Any]]:
    """
    Extract key points from text.

    Args:
        text: Source text
        max_points: Maximum points
        content_type: Type of content

    Returns:
        List of key point dictionaries
    """
    extractor = KeyPointExtractor()
    points = extractor.extract(text, max_points=max_points, content_type=ContentType(content_type))
    return [p.to_dict() for p in points]
