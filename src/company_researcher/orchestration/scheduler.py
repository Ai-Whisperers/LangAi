"""
Workflow Scheduler (Phase 17.2).

Batch and scheduled workflow execution:
- Batch processing of multiple companies
- Rate limiting and throttling
- Priority queue management
- Progress tracking
- Result aggregation

Designed for large-scale research operations.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from .workflow_engine import WorkflowEngine, WorkflowState, ExecutionStatus


# ============================================================================
# Data Models
# ============================================================================

class Priority(int, Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(str, Enum):
    """Scheduled task status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduleConfig:
    """Configuration for scheduled execution."""
    max_concurrent: int = 3
    rate_limit: float = 1.0  # requests per second
    retry_failed: bool = True
    max_retries: int = 2
    timeout_seconds: int = 600
    cooldown_seconds: float = 0.5


@dataclass
class ScheduledTask:
    """A scheduled workflow task."""
    task_id: str
    company_name: str
    priority: Priority = Priority.NORMAL
    status: TaskStatus = TaskStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0
    result: Optional[WorkflowState] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """Enable priority queue comparison."""
        return self.priority.value < other.priority.value


@dataclass
class BatchResult:
    """Result of batch execution."""
    batch_id: str
    total_tasks: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    results: Dict[str, WorkflowState] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_cost: float = 0.0

    @property
    def duration_seconds(self) -> float:
        if not self.start_time:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed / self.total_tasks

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "total_tasks": self.total_tasks,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "success_rate": round(self.success_rate, 2),
            "duration_seconds": round(self.duration_seconds, 2),
            "total_cost": round(self.total_cost, 4)
        }


# ============================================================================
# Workflow Scheduler
# ============================================================================

class WorkflowScheduler:
    """
    Scheduler for batch and queued workflow execution.

    Features:
    - Priority queue for task ordering
    - Rate limiting to avoid API throttling
    - Concurrent execution with limits
    - Progress callbacks
    - Result aggregation

    Usage:
        scheduler = WorkflowScheduler(config)

        # Schedule batch
        batch_result = scheduler.schedule_batch(
            companies=["Tesla", "Apple", "Microsoft"],
            workflow_factory=create_research_workflow
        )

        # Or schedule individual tasks
        scheduler.schedule(
            company_name="Tesla",
            priority=Priority.HIGH
        )

        # Process queue
        scheduler.process_all()
    """

    def __init__(
        self,
        config: Optional[ScheduleConfig] = None,
        workflow_factory: Optional[Callable] = None
    ):
        """
        Initialize scheduler.

        Args:
            config: Scheduling configuration
            workflow_factory: Factory function to create workflows
        """
        self._config = config or ScheduleConfig()
        self._workflow_factory = workflow_factory

        # Task management
        self._task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._active_tasks: Dict[str, ScheduledTask] = {}
        self._completed_tasks: Dict[str, ScheduledTask] = {}

        # Threading
        self._executor = ThreadPoolExecutor(max_workers=self._config.max_concurrent)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # Callbacks
        self._on_task_start: List[Callable] = []
        self._on_task_complete: List[Callable] = []
        self._on_task_error: List[Callable] = []
        self._on_batch_complete: List[Callable] = []

        # Rate limiting
        self._last_request_time = 0.0
        self._task_counter = 0

    # ==========================================================================
    # Task Scheduling
    # ==========================================================================

    def schedule(
        self,
        company_name: str,
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a single company for research.

        Args:
            company_name: Company to research
            priority: Task priority
            metadata: Additional task metadata

        Returns:
            Task ID
        """
        self._task_counter += 1
        task_id = f"task_{int(time.time())}_{self._task_counter}"

        task = ScheduledTask(
            task_id=task_id,
            company_name=company_name,
            priority=priority,
            metadata=metadata or {}
        )

        self._task_queue.put((priority.value, task))
        return task_id

    def schedule_batch(
        self,
        companies: List[str],
        priority: Priority = Priority.NORMAL,
        workflow_factory: Optional[Callable] = None
    ) -> BatchResult:
        """
        Schedule and execute a batch of companies.

        Args:
            companies: List of company names
            priority: Priority for all tasks
            workflow_factory: Optional workflow factory override

        Returns:
            Batch execution result
        """
        batch_id = f"batch_{int(time.time())}"
        batch_result = BatchResult(
            batch_id=batch_id,
            total_tasks=len(companies),
            start_time=datetime.now()
        )

        factory = workflow_factory or self._workflow_factory
        if not factory:
            raise ValueError("No workflow factory provided")

        # Schedule all tasks
        task_ids = []
        for company in companies:
            task_id = self.schedule(
                company_name=company,
                priority=priority,
                metadata={"batch_id": batch_id}
            )
            task_ids.append(task_id)

        # Process all tasks
        results = self._process_batch(factory)

        # Aggregate results
        for task_id, task in self._completed_tasks.items():
            if task.metadata.get("batch_id") == batch_id:
                if task.status == TaskStatus.COMPLETED:
                    batch_result.completed += 1
                    if task.result:
                        batch_result.results[task.company_name] = task.result
                        batch_result.total_cost += task.result.total_cost
                elif task.status == TaskStatus.FAILED:
                    batch_result.failed += 1
                    if task.error:
                        batch_result.errors[task.company_name] = task.error
                elif task.status == TaskStatus.CANCELLED:
                    batch_result.cancelled += 1

        batch_result.end_time = datetime.now()

        for callback in self._on_batch_complete:
            callback(batch_result)

        return batch_result

    def _process_batch(
        self,
        workflow_factory: Callable
    ) -> Dict[str, WorkflowState]:
        """Process all queued tasks."""
        results = {}
        futures = {}

        while not self._task_queue.empty() or self._active_tasks:
            # Start new tasks if under limit
            while (
                not self._task_queue.empty() and
                len(self._active_tasks) < self._config.max_concurrent
            ):
                try:
                    _, task = self._task_queue.get_nowait()
                    future = self._executor.submit(
                        self._execute_task,
                        task,
                        workflow_factory
                    )
                    futures[future] = task.task_id
                    self._active_tasks[task.task_id] = task
                except queue.Empty:
                    break

            # Check completed futures
            completed_futures = []
            for future in futures:
                if future.done():
                    completed_futures.append(future)
                    task_id = futures[future]
                    try:
                        task = future.result()
                        if task.result:
                            results[task.company_name] = task.result
                    except Exception as e:
                        print(f"[Scheduler] Task {task_id} error: {e}")

            # Remove completed from active
            for future in completed_futures:
                task_id = futures.pop(future)
                if task_id in self._active_tasks:
                    task = self._active_tasks.pop(task_id)
                    self._completed_tasks[task_id] = task

            # Brief sleep to prevent busy loop
            time.sleep(0.1)

        return results

    def _execute_task(
        self,
        task: ScheduledTask,
        workflow_factory: Callable
    ) -> ScheduledTask:
        """Execute a single scheduled task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        for callback in self._on_task_start:
            callback(task)

        # Rate limiting
        self._apply_rate_limit()

        try:
            # Create workflow
            workflow = workflow_factory()

            # Execute
            result = workflow.execute(
                initial_data={"company_name": task.company_name}
            )

            task.result = result
            task.status = TaskStatus.COMPLETED

            for callback in self._on_task_complete:
                callback(task)

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED

            # Retry if enabled
            if self._config.retry_failed and task.retries < self._config.max_retries:
                task.retries += 1
                task.status = TaskStatus.QUEUED
                self._task_queue.put((task.priority.value, task))
            else:
                for callback in self._on_task_error:
                    callback(task, task.error)

        task.completed_at = datetime.now()
        return task

    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        with self._lock:
            min_interval = 1.0 / self._config.rate_limit
            elapsed = time.time() - self._last_request_time

            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

            self._last_request_time = time.time()

    # ==========================================================================
    # Task Management
    # ==========================================================================

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a task."""
        if task_id in self._active_tasks:
            return self._active_tasks[task_id].status
        if task_id in self._completed_tasks:
            return self._completed_tasks[task_id].status
        return None

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued task."""
        if task_id in self._active_tasks:
            task = self._active_tasks[task_id]
            if task.status == TaskStatus.QUEUED:
                task.status = TaskStatus.CANCELLED
                return True
        return False

    def cancel_all(self):
        """Cancel all queued tasks."""
        self._stop_event.set()
        while not self._task_queue.empty():
            try:
                _, task = self._task_queue.get_nowait()
                task.status = TaskStatus.CANCELLED
                self._completed_tasks[task.task_id] = task
            except queue.Empty:
                break

    def get_queue_size(self) -> int:
        """Get number of queued tasks."""
        return self._task_queue.qsize()

    def get_active_count(self) -> int:
        """Get number of active tasks."""
        return len(self._active_tasks)

    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        completed = sum(
            1 for t in self._completed_tasks.values()
            if t.status == TaskStatus.COMPLETED
        )
        failed = sum(
            1 for t in self._completed_tasks.values()
            if t.status == TaskStatus.FAILED
        )

        total_cost = sum(
            t.result.total_cost
            for t in self._completed_tasks.values()
            if t.result
        )

        return {
            "queued": self.get_queue_size(),
            "active": self.get_active_count(),
            "completed": completed,
            "failed": failed,
            "total_processed": len(self._completed_tasks),
            "total_cost": round(total_cost, 4)
        }

    # ==========================================================================
    # Callbacks
    # ==========================================================================

    def on_task_start(self, callback: Callable) -> "WorkflowScheduler":
        """Register callback for task start."""
        self._on_task_start.append(callback)
        return self

    def on_task_complete(self, callback: Callable) -> "WorkflowScheduler":
        """Register callback for task completion."""
        self._on_task_complete.append(callback)
        return self

    def on_task_error(self, callback: Callable) -> "WorkflowScheduler":
        """Register callback for task errors."""
        self._on_task_error.append(callback)
        return self

    def on_batch_complete(self, callback: Callable) -> "WorkflowScheduler":
        """Register callback for batch completion."""
        self._on_batch_complete.append(callback)
        return self

    # ==========================================================================
    # Cleanup
    # ==========================================================================

    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler."""
        self._stop_event.set()
        self._executor.shutdown(wait=wait)


# ============================================================================
# Factory Functions
# ============================================================================

def create_scheduler(
    max_concurrent: int = 3,
    rate_limit: float = 1.0,
    workflow_factory: Optional[Callable] = None
) -> WorkflowScheduler:
    """Create a workflow scheduler."""
    config = ScheduleConfig(
        max_concurrent=max_concurrent,
        rate_limit=rate_limit
    )
    return WorkflowScheduler(config, workflow_factory)
