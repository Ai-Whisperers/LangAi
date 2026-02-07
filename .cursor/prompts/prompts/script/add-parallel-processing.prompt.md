---
name: Add Parallel Processing
description: "Add parallel/concurrent processing to improve script performance"
category: script
tags: [parallel, performance, concurrency, enhancement]
---

# Add Parallel/Concurrent Processing

## Context

Add parallel processing for independent operations on multiple items to achieve 3-10x performance improvement.

## Instructions

### PowerShell (PowerShell 7+)

Use `ForEach-Object -Parallel` from [parallel exemplar](../../exemplars/script/powershell/parallel.exemplar.md):
```powershell
$results = $items | ForEach-Object -Parallel {
    param($item = $_)
    # Process item
} -ThrottleLimit 10
```

### Python (CPU-Bound)

Use `multiprocessing.Pool` from [multiprocessing exemplar](../../exemplars/script/python/multiprocessing.exemplar.md):
```python
from multiprocessing import Pool, cpu_count
from functools import partial

with Pool(processes=cpu_count()) as pool:
    results = pool.map(process_func, items)
```

### Python (I/O-Bound)

Use `async/await` from [async exemplar](../../exemplars/script/python/async.exemplar.md):
```python
async def process_all():
    tasks = [process_item_async(item) for item in items]
    return await asyncio.gather(*tasks)
```

## Quality Checklist

- [ ] Items are independent (no shared state)
- [ ] Appropriate concurrency limit (10 for PowerShell, cpu_count() for Python)
- [ ] Error handling within parallel blocks
- [ ] Performance improvement measured (should be 3x+ for 10+ items)

---
Produced-by: prompt.scripts.add-parallel.v1 | ts=2025-12-07T00:00:00Z
