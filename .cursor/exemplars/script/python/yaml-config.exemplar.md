# Python YAML Configuration Pattern Exemplar

## Overview

YAML configuration files with Pydantic validation provide readable, validated configuration management.

## When to Use

- **Use for**: Standard quality level scripts with 5+ parameters
- **Critical for**: Multiple environments, complex configuration

## Good Pattern ✅

```python
import yaml
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict

class CoverageConfigFile(BaseModel):
    """Configuration loaded from YAML file."""
    
    class Thresholds(BaseModel):
        line: int = Field(ge=0, le=100)
        branch: int = Field(ge=0, le=100)
        public_api: int = Field(ge=0, le=100)
    
    class Report(BaseModel):
        formats: List[str] = Field(default=["html", "cobertura"])
        output_dir: str = "./coverage-reports"
    
    thresholds: Thresholds
    excluded_projects: List[str] = Field(default_factory=list)
    report: Report = Field(default_factory=Report)
    enable_parallel: bool = True
    
    @validator('excluded_projects')
    def validate_patterns(cls, v):
        for pattern in v:
            if not pattern.strip():
                raise ValueError("Empty pattern not allowed")
        return v

def load_configuration(config_file: Path) -> CoverageConfigFile:
    """Load and validate configuration from YAML file."""
    if not config_file.exists():
        logger.info(f"Config file not found, using defaults")
        return CoverageConfigFile(
            thresholds={'line': 80, 'branch': 70, 'public_api': 90}
        )
    
    try:
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        config = CoverageConfigFile(**data)
        logger.info(f"Loaded configuration from: {config_file}")
        return config
    
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {e}")
        raise
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

# Example YAML file:
# thresholds:
#   line: 85
#   branch: 75
#   public_api: 90
# 
# excluded_projects:
#   - "*.Tests"
#   - "*.Benchmarks"
# 
# report:
#   formats: ["html", "cobertura", "json"]
#   output_dir: "./coverage-reports"
```

**Why this is good:**
- Pydantic validation
- Nested models
- Clear schema
- Readable YAML format

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

