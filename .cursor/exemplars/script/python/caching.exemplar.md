# Python Smart Caching Pattern Exemplar

## Overview

Smart caching using file hashing and `@lru_cache` skips analysis of unchanged items, providing 50-80% performance improvement.

## When to Use

- **Use for**: Advanced quality level scripts, repeated analysis, large datasets
- **Skip for**: Always-changing data, single-run scripts

## Good Pattern ✅

```python
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Dict, Optional

class CoverageCache:
    """Smart caching for coverage results."""
    
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache: Dict = self._load()
    
    def _load(self) -> Dict:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Cache file corrupted, starting fresh")
                return {}
        return {}
    
    def save(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self.cache, indent=2))
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _compute_project_hash(project_path: str) -> str:
        """Compute hash of all source files in project."""
        path = Path(project_path)
        files = sorted(path.rglob("*.cs"))
        
        hasher = hashlib.sha256()
        for file in files:
            hasher.update(file.read_bytes())
        
        return hasher.hexdigest()
    
    def should_analyze(self, project_name: str, project_path: Path) -> bool:
        """Check if project needs analysis."""
        current_hash = self._compute_project_hash(str(project_path))
        
        if project_name in self.cache:
            if self.cache[project_name].get('hash') == current_hash:
                logger.info(f"⚡ Skipping {project_name} (unchanged)")
                return False
        return True
    
    def store_result(self, project_name: str, project_path: Path, result: Dict):
        """Store analysis result in cache."""
        self.cache[project_name] = {
            'hash': self._compute_project_hash(str(project_path)),
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

# Usage:
cache = CoverageCache(output_path / "coverage-cache.json")

for project in projects:
    if not cache.should_analyze(project.name, project.path):
        result = cache.get_cached_result(project.name)
        results.append(result)
        continue
    
    result = analyze_project(project)
    cache.store_result(project.name, project.path, result)
    results.append(result)

cache.save()
```

**Why this is good:**
- Content-based hashing (SHA256)
- @lru_cache for method-level caching
- JSON persistence
- Fast skip logic

## Performance Characteristics

- **Speedup**: 50-80% on unchanged codebases
- **Storage**: ~1-10KB per cached item

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

