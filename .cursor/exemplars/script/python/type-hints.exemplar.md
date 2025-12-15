# Python Type Hints and Pydantic Validation Pattern Exemplar

## Overview

Type hints with Pydantic provide strong typing, automatic validation, and excellent IDE support for Python scripts.

## When to Use

- **Use for**: Standard quality level and above, complex configuration, data validation
- **Critical for**: Production scripts, API clients, configuration management
- **Skip for**: Simple throwaway scripts, minimal configuration

## Good Pattern ✅

```python
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator, root_validator
from pathlib import Path

class CoverageThresholds(BaseModel):
    """Coverage threshold configuration with validation."""
    
    line: int = Field(default=80, ge=0, le=100, description="Minimum line coverage percentage")
    branch: int = Field(default=70, ge=0, le=100, description="Minimum branch coverage percentage")
    public_api: int = Field(default=90, ge=0, le=100, description="Minimum public API coverage")
    
    @validator('*')
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError(f'Coverage must be 0-100, got {v}')
        return v
    
    @root_validator
    def validate_threshold_logic(cls, values):
        if values.get('branch', 0) > values.get('line', 100):
            raise ValueError('Branch coverage cannot exceed line coverage')
        return values


class CoverageConfig(BaseModel):
    """Complete coverage configuration."""
    
    configuration: str = Field(default="Release", pattern="^(Debug|Release)$")
    output_path: Optional[Path] = None
    thresholds: CoverageThresholds = Field(default_factory=CoverageThresholds)
    excluded_projects: List[str] = Field(default_factory=lambda: ["*.Tests", "*.Benchmarks"])
    enable_parallel: bool = Field(default=True)
    
    class Config:
        validate_assignment = True
        extra = "forbid"  # Reject unknown fields


# Usage with automatic validation:
try:
    config = CoverageConfig(
        thresholds={"line": 85, "branch": 75},
        enable_parallel=True
    )
except ValidationError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(2)
```

**Why this is good:**
- **Type safety**: Types checked at assignment time
- **Field validation**: `ge`, `le`, `pattern` constrain values
- **Custom validators**: `@validator` for complex logic
- **Root validators**: Cross-field validation
- **Default factories**: Clean default values
- **IDE support**: Excellent autocomplete and type checking

## Bad Pattern ❌

```python
# ❌ No validation, just dictionaries
config = {
    "configuration": "Release",
    "threshold": 80,
    # ❌ Typo goes undetected
    "enable_paralel": True  # Should be "enable_parallel"
}

# ❌ No type hints
def analyze_coverage(threshold, output):
    # What types are these? IDE doesn't know
    pass
```

**Why this is bad:**
- **No validation**: Invalid values accepted silently
- **Typos undetected**: Extra fields ignored
- **No IDE support**: No autocomplete or type checking
- **Runtime errors**: Problems discovered late in execution

## Type Hints Best Practices

### Function Type Hints

```python
def analyze_coverage(
    coverage_file: Path,
    threshold: int,
    enable_caching: bool = True
) -> Dict[str, float]:
    """
    Analyze coverage from file.
    
    Args:
        coverage_file: Path to coverage XML file
        threshold: Minimum coverage percentage (0-100)
        enable_caching: Whether to use cached results
    
    Returns:
        Dictionary with coverage metrics
    """
    # Implementation
    return {"line": 85.5, "branch": 72.3}
```

### Optional and Union Types

```python
from typing import Optional, Union

def load_config(
    config_file: Optional[Path] = None
) -> Union[Dict, None]:
    """Load config from file if provided."""
    if config_file is None:
        return None
    
    return load_yaml(config_file)
```

### Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Cache(Generic[T]):
    """Generic cache for any type."""
    
    def __init__(self):
        self._cache: Dict[str, T] = {}
    
    def get(self, key: str) -> Optional[T]:
        return self._cache.get(key)
    
    def set(self, key: str, value: T) -> None:
        self._cache[key] = value
```

## Performance Characteristics

- **Validation overhead**: 1-5ms for typical config objects
- **Runtime cost**: Negligible after initial validation
- **Developer productivity**: Significant improvement with IDE support

## Related Patterns

- [YAML Config](./yaml-config.exemplar.md) - Load YAML into Pydantic models
- [Exceptions](./exceptions.exemplar.md) - Handle Pydantic validation errors
- See also: `rule.scripts.python-standards.v1` section "Type Hints with Pydantic"

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

