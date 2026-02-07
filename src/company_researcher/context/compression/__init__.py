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

# Factory functions
from .compressor import TextCompressor, compress_text
from .extractor import KeyPointExtractor, extract_key_points
from .models import CompressionLevel, CompressionResult, ContentType, KeyPoint
from .optimizer import ContextWindowOptimizer, optimize_for_context
from .summarizer import ProgressiveSummarizer

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
