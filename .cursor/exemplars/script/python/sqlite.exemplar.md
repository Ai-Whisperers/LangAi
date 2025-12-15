# Python SQLite for Historical Tracking Pattern Exemplar

## Overview

SQLite provides lightweight, serverless persistence for tracking metrics over time (Production quality level feature).

## When to Use

- **Use for**: Historical trend analysis, metric tracking, audit logs
- **Skip for**: Simple one-time scripts, minimal data persistence needs

## Good Pattern ✅

```python
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class CoverageHistory:
    """Track coverage metrics over time using SQLite."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Create database schema if not exists."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS coverage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                commit_hash TEXT,
                branch TEXT,
                line_coverage REAL NOT NULL,
                branch_coverage REAL NOT NULL,
                build_number TEXT,
                duration_seconds REAL
            );
            CREATE INDEX IF NOT EXISTS idx_timestamp ON coverage_history(timestamp);
        """)
        self.conn.commit()
    
    def record(self, metrics: Dict) -> int:
        """Record coverage metrics."""
        cursor = self.conn.execute("""
            INSERT INTO coverage_history 
            (timestamp, commit_hash, branch, line_coverage, branch_coverage, build_number, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            metrics.get('commit_hash'),
            metrics.get('branch'),
            metrics['line_coverage'],
            metrics['branch_coverage'],
            metrics.get('build_number'),
            metrics.get('duration_seconds')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_trend(self, days: int = 30) -> List[Dict]:
        """Get coverage trend for analysis."""
        cursor = self.conn.execute("""
            SELECT * FROM coverage_history 
            WHERE datetime(timestamp) > datetime('now', '-{} days')
            ORDER BY timestamp ASC
        """.format(days))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        self.conn.close()

# Usage:
history = CoverageHistory(Path("coverage-history.db"))
history.record({
    'commit_hash': get_commit_hash(),
    'line_coverage': 85.5,
    'branch_coverage': 78.2
})
trend = history.get_trend(days=30)
history.close()
```

**Why this is good:**
- Lightweight (no server setup)
- SQL for querying trends
- Automatic schema creation
- Context manager compatible

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

