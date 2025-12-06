"""
COMPRESS Strategy (Phase 12.3).

Summarization and context distillation:
- Progressive summarization
- Key point extraction
- Redundancy elimination
- Context window optimization

The COMPRESS strategy reduces information while preserving
essential content to fit within context limits.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


# ============================================================================
# Enums and Data Models
# ============================================================================

class CompressionLevel(str, Enum):
    """Levels of compression."""
    MINIMAL = "minimal"      # Light summarization, keep details
    MODERATE = "moderate"    # Balanced summarization
    AGGRESSIVE = "aggressive"  # Heavy summarization, key points only
    EXTREME = "extreme"      # Maximum compression, essentials only


class ContentType(str, Enum):
    """Types of content for targeted compression."""
    FINANCIAL = "financial"
    MARKET = "market"
    COMPETITIVE = "competitive"
    PRODUCT = "product"
    GENERAL = "general"


@dataclass
class CompressionResult:
    """Result of compression operation."""
    original_text: str
    compressed_text: str
    original_length: int
    compressed_length: int
    compression_ratio: float
    key_points: List[str] = field(default_factory=list)
    preserved_entities: List[str] = field(default_factory=list)
    compression_level: CompressionLevel = CompressionLevel.MODERATE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_length": self.original_length,
            "compressed_length": self.compressed_length,
            "compression_ratio": round(self.compression_ratio, 3),
            "key_points_count": len(self.key_points),
            "level": self.compression_level.value
        }


@dataclass
class KeyPoint:
    """An extracted key point."""
    content: str
    importance: float  # 0-1
    category: str
    source_sentence: str = ""
    entities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "importance": round(self.importance, 2),
            "category": self.category,
            "entities": self.entities
        }


# ============================================================================
# Key Point Extractor
# ============================================================================

class KeyPointExtractor:
    """
    Extract key points from text content.

    Identifies the most important sentences and facts
    based on various signals.
    """

    # Importance signals
    IMPORTANCE_KEYWORDS = {
        "high": [
            "revenue", "profit", "growth", "market share", "billion",
            "million", "percent", "increased", "decreased", "launched",
            "acquired", "partnership", "announced", "leading", "first",
            "largest", "significant", "major", "key", "critical"
        ],
        "medium": [
            "expected", "projected", "estimated", "approximately",
            "reported", "according", "stated", "mentioned", "noted"
        ],
        "low": [
            "may", "might", "could", "possibly", "potentially",
            "some", "various", "certain"
        ]
    }

    # Numerical patterns
    NUMERICAL_PATTERNS = [
        r'\$[\d,.]+\s*(?:billion|million|B|M|trillion|T)?',
        r'[\d,.]+\s*(?:percent|%)',
        r'[\d,.]+x',
        r'Q[1-4]\s*20\d{2}',
        r'20\d{2}'
    ]

    def __init__(self):
        self._sentence_splitter = re.compile(r'(?<=[.!?])\s+')

    def extract(
        self,
        text: str,
        max_points: int = 10,
        content_type: ContentType = ContentType.GENERAL
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

                scored_sentences.append(KeyPoint(
                    content=sentence.strip(),
                    importance=score,
                    category=category,
                    source_sentence=sentence,
                    entities=entities
                ))

        # Sort by importance and return top N
        scored_sentences.sort(key=lambda x: x.importance, reverse=True)
        return scored_sentences[:max_points]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        sentences = self._sentence_splitter.split(text)
        # Filter very short sentences
        return [s for s in sentences if len(s) > 20]

    def _score_sentence(
        self,
        sentence: str,
        content_type: ContentType
    ) -> float:
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
            ContentType.PRODUCT: ["product", "feature", "technology", "innovation", "launch"]
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
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence)
        entities.extend(proper_nouns[:3])

        # Money amounts
        money = re.findall(r'\$[\d,.]+\s*(?:billion|million|B|M)?', sentence)
        entities.extend(money)

        # Percentages
        percents = re.findall(r'[\d,.]+\s*(?:percent|%)', sentence)
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
            "operations": ["employee", "office", "headquarters", "facility"]
        }

        for category, keywords in categories.items():
            if any(kw in sentence_lower for kw in keywords):
                return category

        return "general"


# ============================================================================
# Text Compressor
# ============================================================================

class TextCompressor:
    """
    Compress text while preserving essential information.

    Strategies:
    - Sentence extraction (keep important sentences)
    - Redundancy removal
    - Entity preservation
    - Progressive summarization
    """

    def __init__(self):
        self._key_extractor = KeyPointExtractor()

    def compress(
        self,
        text: str,
        level: CompressionLevel = CompressionLevel.MODERATE,
        target_length: Optional[int] = None,
        content_type: ContentType = ContentType.GENERAL,
        preserve_entities: Optional[List[str]] = None
    ) -> CompressionResult:
        """
        Compress text to target length or compression level.

        Args:
            text: Text to compress
            level: Compression level
            target_length: Target character length (optional)
            content_type: Type of content
            preserve_entities: Entities that must be preserved

        Returns:
            CompressionResult
        """
        original_length = len(text)

        # Calculate target based on level if not specified
        if target_length is None:
            target_ratios = {
                CompressionLevel.MINIMAL: 0.7,
                CompressionLevel.MODERATE: 0.4,
                CompressionLevel.AGGRESSIVE: 0.2,
                CompressionLevel.EXTREME: 0.1
            }
            target_length = int(original_length * target_ratios[level])

        # If already under target, return as-is
        if original_length <= target_length:
            return CompressionResult(
                original_text=text,
                compressed_text=text,
                original_length=original_length,
                compressed_length=original_length,
                compression_ratio=1.0,
                compression_level=level
            )

        # Extract key points
        key_points = self._key_extractor.extract(
            text,
            max_points=20,
            content_type=content_type
        )

        # Build compressed text from key points
        compressed_parts = []
        current_length = 0
        preserved = set()

        for point in key_points:
            if current_length + len(point.content) + 2 <= target_length:
                compressed_parts.append(point.content)
                current_length += len(point.content) + 2  # +2 for spacing
                preserved.update(point.entities)

                # Check if we've met target
                if current_length >= target_length * 0.8:
                    break

        compressed_text = " ".join(compressed_parts)

        # Ensure preserved entities are included
        if preserve_entities:
            for entity in preserve_entities:
                if entity.lower() not in compressed_text.lower():
                    # Find sentence with entity
                    for point in key_points:
                        if entity.lower() in point.content.lower():
                            if len(compressed_text) + len(point.content) + 2 <= target_length * 1.2:
                                compressed_text += " " + point.content
                            break

        return CompressionResult(
            original_text=text,
            compressed_text=compressed_text,
            original_length=original_length,
            compressed_length=len(compressed_text),
            compression_ratio=len(compressed_text) / original_length if original_length > 0 else 0,
            key_points=[p.content for p in key_points[:10]],
            preserved_entities=list(preserved),
            compression_level=level
        )

    def compress_to_bullets(
        self,
        text: str,
        max_bullets: int = 10,
        content_type: ContentType = ContentType.GENERAL
    ) -> List[str]:
        """
        Compress text to bullet points.

        Args:
            text: Text to compress
            max_bullets: Maximum bullet points
            content_type: Content type

        Returns:
            List of bullet point strings
        """
        key_points = self._key_extractor.extract(
            text,
            max_points=max_bullets,
            content_type=content_type
        )

        bullets = []
        for point in key_points:
            # Trim to reasonable length
            content = point.content[:200]
            if len(point.content) > 200:
                content += "..."

            # Format as bullet
            bullets.append(f"• {content}")

        return bullets

    def remove_redundancy(self, texts: List[str]) -> List[str]:
        """
        Remove redundant content from multiple texts.

        Args:
            texts: List of text segments

        Returns:
            Deduplicated list
        """
        if not texts:
            return []

        # Track seen content (fuzzy matching)
        seen_signatures = set()
        unique_texts = []

        for text in texts:
            # Create signature from key terms
            words = text.lower().split()
            # Take every 5th word as signature
            signature = tuple(words[::5][:10])

            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_texts.append(text)

        return unique_texts


# ============================================================================
# Progressive Summarizer
# ============================================================================

class ProgressiveSummarizer:
    """
    Progressive summarization for long documents.

    Implements multi-level summarization:
    1. Full text -> Section summaries
    2. Section summaries -> Document summary
    3. Document summary -> Abstract
    """

    def __init__(self, llm_client=None):
        """
        Initialize summarizer.

        Args:
            llm_client: Optional LLM client for advanced summarization
        """
        self._llm_client = llm_client
        self._compressor = TextCompressor()

    def summarize_progressive(
        self,
        text: str,
        levels: int = 2,
        final_length: int = 500
    ) -> Dict[str, Any]:
        """
        Progressively summarize text through multiple levels.

        Args:
            text: Text to summarize
            levels: Number of summarization levels
            final_length: Target final length

        Returns:
            Dictionary with summaries at each level
        """
        results = {
            "original_length": len(text),
            "levels": []
        }

        current_text = text

        for level in range(levels):
            # Calculate target for this level
            reduction_factor = 0.4 ** (level + 1)
            target_length = max(
                final_length,
                int(len(text) * reduction_factor)
            )

            # Compress
            compression_level = CompressionLevel.MODERATE if level == 0 else CompressionLevel.AGGRESSIVE

            result = self._compressor.compress(
                current_text,
                level=compression_level,
                target_length=target_length
            )

            results["levels"].append({
                "level": level + 1,
                "input_length": len(current_text),
                "output_length": len(result.compressed_text),
                "compression_ratio": result.compression_ratio,
                "text": result.compressed_text
            })

            current_text = result.compressed_text

            # Stop if we've reached target
            if len(current_text) <= final_length:
                break

        results["final_summary"] = current_text
        results["final_length"] = len(current_text)

        return results

    def summarize_sections(
        self,
        text: str,
        section_headers: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Summarize text by sections.

        Args:
            text: Text with sections
            section_headers: Optional list of section markers

        Returns:
            Dictionary mapping section names to summaries
        """
        # Default section patterns
        if section_headers is None:
            section_headers = [
                r"#{1,3}\s+(.+)",  # Markdown headers
                r"^([A-Z][A-Za-z\s]+):\s*$",  # Title: format
                r"^\d+\.\s+(.+)"  # Numbered sections
            ]

        # Split into sections
        sections = self._split_sections(text, section_headers)

        summaries = {}
        for section_name, section_text in sections.items():
            if len(section_text) > 100:
                result = self._compressor.compress(
                    section_text,
                    level=CompressionLevel.MODERATE,
                    target_length=min(500, len(section_text) // 2)
                )
                summaries[section_name] = result.compressed_text
            else:
                summaries[section_name] = section_text

        return summaries

    def _split_sections(
        self,
        text: str,
        patterns: List[str]
    ) -> Dict[str, str]:
        """Split text into sections."""
        sections = {}
        current_section = "Introduction"
        current_text = []

        lines = text.split("\n")

        for line in lines:
            is_header = False

            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    # Save previous section
                    if current_text:
                        sections[current_section] = "\n".join(current_text)

                    current_section = match.group(1).strip()
                    current_text = []
                    is_header = True
                    break

            if not is_header:
                current_text.append(line)

        # Save last section
        if current_text:
            sections[current_section] = "\n".join(current_text)

        return sections


# ============================================================================
# Context Window Optimizer
# ============================================================================

class ContextWindowOptimizer:
    """
    Optimize content to fit within context window limits.

    Intelligently compresses and prioritizes content to maximize
    information density within token limits.
    """

    # Approximate chars per token (varies by model)
    CHARS_PER_TOKEN = 4

    def __init__(self, max_tokens: int = 8000):
        """
        Initialize optimizer.

        Args:
            max_tokens: Maximum context window tokens
        """
        self._max_tokens = max_tokens
        self._max_chars = max_tokens * self.CHARS_PER_TOKEN
        self._compressor = TextCompressor()

    def optimize(
        self,
        contents: List[Dict[str, Any]],
        priorities: Optional[List[float]] = None
    ) -> str:
        """
        Optimize multiple content pieces for context window.

        Args:
            contents: List of {"text": str, "type": str} dicts
            priorities: Optional priority scores (0-1) for each piece

        Returns:
            Optimized combined content
        """
        if not contents:
            return ""

        # Assign default priorities if not provided
        if priorities is None:
            priorities = [1.0] * len(contents)

        # Calculate space allocation
        total_priority = sum(priorities)
        allocations = [
            int(self._max_chars * (p / total_priority))
            for p in priorities
        ]

        # Compress each piece to allocation
        optimized_parts = []

        for content, allocation in zip(contents, allocations):
            text = content.get("text", "")
            content_type = ContentType(content.get("type", "general"))

            if len(text) <= allocation:
                optimized_parts.append(text)
            else:
                result = self._compressor.compress(
                    text,
                    target_length=allocation,
                    content_type=content_type
                )
                optimized_parts.append(result.compressed_text)

        # Combine with separators
        combined = "\n\n---\n\n".join(optimized_parts)

        # Final check and trim if needed
        if len(combined) > self._max_chars:
            combined = combined[:self._max_chars - 100] + "\n\n[Content truncated]"

        return combined

    def fit_to_window(
        self,
        text: str,
        reserved_tokens: int = 1000
    ) -> str:
        """
        Fit text to available context window.

        Args:
            text: Text to fit
            reserved_tokens: Tokens to reserve for other content

        Returns:
            Fitted text
        """
        available_chars = (self._max_tokens - reserved_tokens) * self.CHARS_PER_TOKEN

        if len(text) <= available_chars:
            return text

        result = self._compressor.compress(
            text,
            target_length=available_chars
        )

        return result.compressed_text


# ============================================================================
# Factory Functions
# ============================================================================

def compress_text(
    text: str,
    level: str = "moderate",
    target_length: Optional[int] = None
) -> CompressionResult:
    """
    Compress text with specified level.

    Args:
        text: Text to compress
        level: "minimal", "moderate", "aggressive", "extreme"
        target_length: Optional target length

    Returns:
        CompressionResult
    """
    compressor = TextCompressor()
    return compressor.compress(
        text,
        level=CompressionLevel(level),
        target_length=target_length
    )


def extract_key_points(
    text: str,
    max_points: int = 10,
    content_type: str = "general"
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
    points = extractor.extract(
        text,
        max_points=max_points,
        content_type=ContentType(content_type)
    )
    return [p.to_dict() for p in points]


def optimize_for_context(
    contents: List[str],
    max_tokens: int = 8000
) -> str:
    """
    Optimize multiple texts for context window.

    Args:
        contents: List of text strings
        max_tokens: Maximum tokens

    Returns:
        Optimized combined text
    """
    optimizer = ContextWindowOptimizer(max_tokens=max_tokens)
    content_dicts = [{"text": c, "type": "general"} for c in contents]
    return optimizer.optimize(content_dicts)
