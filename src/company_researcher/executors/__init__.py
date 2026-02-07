"""
Execution backends for running research jobs.

This package provides a Ray-style orchestration layer (local-first) that:
- Starts batch jobs via API
- Tracks progress per task and batch
- Writes all artifacts to the outputs folder for later inspection/sharing
"""

from .orchestrator import DiskBatchOrchestrator, get_orchestrator

__all__ = [
    "DiskBatchOrchestrator",
    "get_orchestrator",
]
