---
name: Add Smart Caching
description: "Add smart caching using file hashing to skip analysis of unchanged items"
category: script
tags: [caching, performance, optimization, enhancement]
---

# Add Smart Caching for Unchanged Items

## Context

Add smart caching using file hashing to skip analysis of unchanged projects/files, providing 50-80% performance improvement for repeated executions.

## Instructions

See [PowerShell caching exemplar](../../exemplars/script/powershell/caching.exemplar.md) or [Python caching exemplar](../../exemplars/script/python/caching.exemplar.md) for complete implementation.

### Key Steps

1. Add hash computation function (SHA256 of source files)
2. Load cache from JSON file
3. For each item:
   - Compute current hash
   - Compare with cached hash
   - Skip if unchanged, process if changed
   - Update cache with new hash and results
4. Save updated cache

## Quality Checklist

- [ ] Content-based hashing (SHA256)
- [ ] Cache persisted to JSON file
- [ ] Cache invalidation on file changes
- [ ] Skip logic logs skipped items
- [ ] Performance improvement measured (50%+ expected)

---
Produced-by: prompt.scripts.add-caching.v1 | ts=2025-12-07T00:00:00Z

