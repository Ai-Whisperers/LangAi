"""
COMPRESS Strategy (Phase 12.3) - Backward Compatibility Module.

This module re-exports all components from the modular compression/ package
for backward compatibility. New code should import directly from:

    from company_researcher.context.compression import (
        TextCompressor,
        KeyPointExtractor,
        compress_text,
        ...
    )

This file maintains backward compatibility with existing imports:
    from company_researcher.context.compress_strategy import TextCompressor
"""

# Re-export all components from modular structure
from .compression import (  # Enums; Data Models; Classes; Factory Functions
    CompressionLevel,
    CompressionResult,
    ContentType,
    ContextWindowOptimizer,
    KeyPoint,
    KeyPointExtractor,
    ProgressiveSummarizer,
    TextCompressor,
    compress_text,
    extract_key_points,
    optimize_for_context,
)

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
