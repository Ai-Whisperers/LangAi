"""
Context Compression Module.

Provides summarization and context distillation:
- Progressive summarization
- Key point extraction
- Redundancy elimination
- Context window optimization

Usage:
    from company_researcher.context.compression import (
        TextCompressor,
        KeyPointExtractor,
        ProgressiveSummarizer,
        compress_text,
        extract_key_points
    )
"""

from .models import (
    CompressionLevel,
    ContentType,
    CompressionResult,
    KeyPoint,
)

from .extractor import KeyPointExtractor

from .compressor import TextCompressor

from .summarizer import ProgressiveSummarizer

from .optimizer import ContextWindowOptimizer

# Factory functions
from .compressor import compress_text
from .extractor import extract_key_points
from .optimizer import optimize_for_context

__all__ = [
    # Enums
    "CompressionLevel",
    "ContentType",
    # Data Models
    "CompressionResult",
    "KeyPoint",
    # Classes
    "KeyPointExtractor",
    "TextCompressor",
    "ProgressiveSummarizer",
    "ContextWindowOptimizer",
    # Factory Functions
    "compress_text",
    "extract_key_points",
    "optimize_for_context",
]
