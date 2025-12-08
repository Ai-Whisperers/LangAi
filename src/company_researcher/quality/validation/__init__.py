"""
Quality Validation Module.

Provides validation and contradiction detection:
- Cross-source validation
- Contradiction detection
- Quality checking
"""

from .cross_source_validator import (
    CrossSourceValidator,
    ValidationResult,
    SourceConsistencyScore,
)

from .contradiction_detector import (
    ContradictionDetector,
    Contradiction,
    ContradictionSeverity,
)

from .quality_checker import (
    QualityChecker,
    QualityCheckResult,
)

__all__ = [
    # Cross-source validation
    "CrossSourceValidator",
    "ValidationResult",
    "SourceConsistencyScore",
    # Contradiction detection
    "ContradictionDetector",
    "Contradiction",
    "ContradictionSeverity",
    # Quality checking
    "QualityChecker",
    "QualityCheckResult",
]
