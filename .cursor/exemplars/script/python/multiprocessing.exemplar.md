# Python Multiprocessing Pattern Exemplar

## Overview

`multiprocessing.Pool` uses all CPU cores for CPU-bound operations, providing 4-8x performance improvement.

## When to Use

- **Use for**: CPU-bound computations, data processing, calculations
- **Skip for**: I/O-bound operations (use async instead)

## Good Pattern ✅

```python
from multiprocessing import Pool, cpu_count
from functools import partial
from typing import List, Dict

def analyze_single_package(package: Package, config: CoverageConfig) -> Dict:
    """Analyze single package (CPU-bound work)."""
    return {
        'name': package.name,
        'line_coverage': calculate_coverage(package),
        'complexity': calculate_complexity(package)
    }

def analyze_packages_parallel(packages: List[Package], config: CoverageConfig) -> List[Dict]:
    """Analyze packages in parallel using all CPU cores."""
    analyze_func = partial(analyze_single_package, config=config)
    num_processes = cpu_count()

    logger.info(f"Analyzing {len(packages)} packages using {num_processes} cores")

    with Pool(processes=num_processes) as pool:
        results = pool.map(analyze_func, packages)

    return results

# 🚀 4-8x faster for CPU-intensive operations
```

**Why this is good:**
- Uses all CPU cores
- functools.partial for parameter binding
- Context manager for cleanup
- Proper logging

## Performance Characteristics

- **Speedup**: 4-8x for CPU-bound operations
- **Best for**: Calculations, data transformation, parsing
- **Overhead**: Process spawning cost (~100ms per process)

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z
