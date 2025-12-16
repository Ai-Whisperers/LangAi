"""
Text Compressor Module.

Compresses text while preserving essential information.
"""

from typing import List, Optional

from .extractor import KeyPointExtractor
from .models import CompressionLevel, CompressionResult, ContentType


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
        """Initialize compressor."""
        self._key_extractor = KeyPointExtractor()

    def compress(
        self,
        text: str,
        level: CompressionLevel = CompressionLevel.MODERATE,
        target_length: Optional[int] = None,
        content_type: ContentType = ContentType.GENERAL,
        preserve_entities: Optional[List[str]] = None,
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
                CompressionLevel.EXTREME: 0.1,
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
                compression_level=level,
            )

        # Extract key points
        key_points = self._key_extractor.extract(text, max_points=20, content_type=content_type)

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
            compression_level=level,
        )

    def compress_to_bullets(
        self, text: str, max_bullets: int = 10, content_type: ContentType = ContentType.GENERAL
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
            text, max_points=max_bullets, content_type=content_type
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
# Factory Function
# ============================================================================


def compress_text(
    text: str, level: str = "moderate", target_length: Optional[int] = None
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
    return compressor.compress(text, level=CompressionLevel(level), target_length=target_length)
