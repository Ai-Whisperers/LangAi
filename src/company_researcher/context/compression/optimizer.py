"""
Context Window Optimizer Module.

Optimizes content to fit within context window limits.
"""

from typing import Any, Dict, List, Optional

from .compressor import TextCompressor
from .models import ContentType


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
        self, contents: List[Dict[str, Any]], priorities: Optional[List[float]] = None
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
        allocations = [int(self._max_chars * (p / total_priority)) for p in priorities]

        # Compress each piece to allocation
        optimized_parts = []

        for content, allocation in zip(contents, allocations):
            text = content.get("text", "")
            content_type = ContentType(content.get("type", "general"))

            if len(text) <= allocation:
                optimized_parts.append(text)
            else:
                result = self._compressor.compress(
                    text, target_length=allocation, content_type=content_type
                )
                optimized_parts.append(result.compressed_text)

        # Combine with separators
        combined = "\n\n---\n\n".join(optimized_parts)

        # Final check and trim if needed
        if len(combined) > self._max_chars:
            combined = combined[: self._max_chars - 100] + "\n\n[Content truncated]"

        return combined

    def fit_to_window(self, text: str, reserved_tokens: int = 1000) -> str:
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

        result = self._compressor.compress(text, target_length=available_chars)

        return result.compressed_text

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // self.CHARS_PER_TOKEN

    def get_available_space(self, reserved: int = 0) -> int:
        """
        Get available character space.

        Args:
            reserved: Characters already reserved

        Returns:
            Available characters
        """
        return self._max_chars - reserved


# ============================================================================
# Factory Function
# ============================================================================


def optimize_for_context(contents: List[str], max_tokens: int = 8000) -> str:
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
