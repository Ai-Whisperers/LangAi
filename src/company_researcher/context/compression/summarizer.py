"""
Progressive Summarizer Module.

Multi-level summarization for long documents.
"""

import re
from typing import Any, Dict, List, Optional

from .compressor import TextCompressor
from .models import CompressionLevel


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
        self, text: str, levels: int = 2, final_length: int = 500
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
        results = {"original_length": len(text), "levels": []}

        current_text = text

        for level in range(levels):
            # Calculate target for this level
            reduction_factor = 0.4 ** (level + 1)
            target_length = max(final_length, int(len(text) * reduction_factor))

            # Compress
            compression_level = (
                CompressionLevel.MODERATE if level == 0 else CompressionLevel.AGGRESSIVE
            )

            result = self._compressor.compress(
                current_text, level=compression_level, target_length=target_length
            )

            results["levels"].append(
                {
                    "level": level + 1,
                    "input_length": len(current_text),
                    "output_length": len(result.compressed_text),
                    "compression_ratio": result.compression_ratio,
                    "text": result.compressed_text,
                }
            )

            current_text = result.compressed_text

            # Stop if we've reached target
            if len(current_text) <= final_length:
                break

        results["final_summary"] = current_text
        results["final_length"] = len(current_text)

        return results

    def summarize_sections(
        self, text: str, section_headers: Optional[List[str]] = None
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
                r"^\d+\.\s+(.+)",  # Numbered sections
            ]

        # Split into sections
        sections = self._split_sections(text, section_headers)

        summaries = {}
        for section_name, section_text in sections.items():
            if len(section_text) > 100:
                result = self._compressor.compress(
                    section_text,
                    level=CompressionLevel.MODERATE,
                    target_length=min(500, len(section_text) // 2),
                )
                summaries[section_name] = result.compressed_text
            else:
                summaries[section_name] = section_text

        return summaries

    def _split_sections(self, text: str, patterns: List[str]) -> Dict[str, str]:
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
