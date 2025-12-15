# Python Async/Await Pattern Exemplar

## Overview

`async/await` enables concurrent execution for I/O-bound operations, providing 3-10x performance improvement over sequential code.

## When to Use

- **Use for**: I/O-bound operations (file reading, API calls, database queries)
- **Skip for**: CPU-bound operations (use multiprocessing instead)

## Good Pattern ✅

```python
import asyncio
import aiohttp
from typing import List, Dict

async def analyze_package_async(package: Package) -> Dict:
    """Analyze single package asynchronously."""
    await asyncio.sleep(0.1)  # Simulate I/O
    
    return {
        'name': package.name,
        'line_coverage': calculate_line_coverage(package),
        'branch_coverage': calculate_branch_coverage(package)
    }

async def analyze_all_packages_async(packages: List[Package]) -> List[Dict]:
    """Analyze all packages concurrently."""
    tasks = [analyze_package_async(pkg) for pkg in packages]
    results = await asyncio.gather(*tasks)
    return results

def analyze_packages(packages: List[Package]) -> List[Dict]:
    """Wrapper for sync code."""
    return asyncio.run(analyze_all_packages_async(packages))

# 🚀 3-10x faster for I/O-bound operations
```

**Why this is good:**
- Concurrent I/O operations
- Non-blocking execution
- asyncio.gather for parallel awaits
- Clean sync/async boundary

## Performance Characteristics

- **Speedup**: 3-10x for I/O-bound operations
- **Best for**: Network calls, file I/O, database queries
- **Memory efficient**: Single-threaded with event loop

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

