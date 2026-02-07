"""
Compression Data Models.

Enums and dataclasses for compression operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class CompressionLevel(str, Enum):
    """Levels of compression."""

    MINIMAL = "minimal"  # Light summarization, keep details
    MODERATE = "moderate"  # Balanced summarization
    AGGRESSIVE = "aggressive"  # Heavy summarization, key points only
    EXTREME = "extreme"  # Maximum compression, essentials only


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
        """Convert to dictionary representation."""
        return {
            "original_length": self.original_length,
            "compressed_length": self.compressed_length,
            "compression_ratio": round(self.compression_ratio, 3),
            "key_points_count": len(self.key_points),
            "level": self.compression_level.value,
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
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "importance": round(self.importance, 2),
            "category": self.category,
            "entities": self.entities,
        }
