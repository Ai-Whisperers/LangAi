"""
API Routes (Phase 18.4).

REST API endpoints for company research:
- Research endpoints
- Batch processing
- Task management
- Health checks
"""

import asyncio
import time
from typing import Any, Dict, Optional

from ..utils import get_config, get_logger, utc_now

try:
    from fastapi import APIRouter, BackgroundTasks, HTTPException, Path, Query

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Stub
    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            def decorator(f):
                return f

            return decorator

        def post(self, *args, **kwargs):
            def decorator(f):
                return f

            return decorator

        def delete(self, *args, **kwargs):
            def decorator(f):
                return f

            return decorator


from ..executors import get_orchestrator
from .models import (
    BatchRequest,
    BatchResponse,
    HealthResponse,
    ResearchDepthEnum,
    ResearchRequest,
    ResearchResponse,
    TaskStatusEnum,
)
from .task_storage import TaskStorage, get_task_storage

logger = get_logger(__name__)


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/v1", tags=["research"])


def _get_storage() -> TaskStorage:
    """Get the task storage instance."""
    return get_task_storage()


def _use_disk_backend() -> bool:
    """
    Select API execution backend.

    - disk (default): Disk-first orchestrator (Ray-style, local-first)
    - task_storage: Legacy FastAPI BackgroundTasks + TaskStorage
    """
    backend = (get_config("COMPANY_RESEARCH_API_BACKEND", default="disk") or "disk").strip().lower()
    return backend != "task_storage"


# ============================================================================
# Research Endpoints
# ============================================================================

if FASTAPI_AVAILABLE:

    @router.post(
        "/research",
        response_model=ResearchResponse,
        summary="Start company research",
        description="Initiate research for a single company",
    )
    async def start_research(
        request: ResearchRequest, background_tasks: BackgroundTasks
    ) -> ResearchResponse:
        """
        Start research for a company.

        Returns task ID to track progress.
        """
        if _use_disk_backend():
            orchestrator = get_orchestrator()
            research_type = request.research_type.value
            subject = request.company_name if research_type == "company" else request.topic
            subject = (subject or "").strip()
            job = orchestrator.start_batch(
                [subject],
                depth=request.depth.value,
                force=False,
                metadata=request.metadata,
                research_type=research_type,
            )
            task_id = job["task_ids"][0]
        else:
            storage = _get_storage()
            task_id = f"task_{int(time.time() * 1000)}"

            # Create task data
            task_data = {
                "task_id": task_id,
                "research_type": request.research_type.value,
                "company_name": request.company_name,
                "topic": request.topic,
                "subject": (
                    request.company_name
                    if request.research_type.value == "company"
                    else request.topic
                ),
                "depth": request.depth.value,
                "status": TaskStatusEnum.PENDING.value,
                "created_at": utc_now(),
                "config": {
                    "include_financial": request.include_financial,
                    "include_market": request.include_market,
                    "include_competitive": request.include_competitive,
                    "include_news": request.include_news,
                    "include_brand": request.include_brand,
                    "include_social": request.include_social,
                    "include_sales": request.include_sales,
                    "include_investment": request.include_investment,
                },
                "webhook_url": request.webhook_url,
                "metadata": request.metadata,
                "result": None,
                "error": None,
            }

            # Store task persistently
            await storage.save_task(task_id, task_data)

            # Start background task (legacy mode only)
            background_tasks.add_task(_execute_research, task_id, request)

        # Estimate duration based on depth
        duration_map = {"quick": 30, "standard": 120, "comprehensive": 300}

        return ResearchResponse(
            task_id=task_id,
            research_type=request.research_type,
            subject=(
                request.company_name
                if request.research_type.value == "company"
                else (request.topic or "")
            ),
            company_name=request.company_name,
            topic=request.topic,
            status=TaskStatusEnum.PENDING,
            depth=request.depth,
            created_at=utc_now(),
            estimated_duration_seconds=duration_map.get(request.depth.value, 120),
            message=(
                "Research task created successfully"
                if not _use_disk_backend()
                else "Research task submitted (disk-first runner). Check /research/{task_id} for output paths."
            ),
        )

    @router.get(
        "/research/{task_id}",
        summary="Get research task status",
        description="Get status and results of a research task",
    )
    async def get_research_status(
        task_id: str = Path(..., description="Task ID")
    ) -> Dict[str, Any]:
        """Get status of a research task."""
        if _use_disk_backend():
            task = get_orchestrator().get_task_status(task_id)
        else:
            storage = _get_storage()
            task = await storage.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return task

    @router.get(
        "/research/{task_id}/result",
        summary="Get research results",
        description="Get complete results of a finished research task",
    )
    async def get_research_result(
        task_id: str = Path(..., description="Task ID")
    ) -> Dict[str, Any]:
        """Get results of a completed research task."""
        if _use_disk_backend():
            task = get_orchestrator().get_task_result(task_id)
        else:
            storage = _get_storage()
            task = await storage.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if task["status"] != TaskStatusEnum.COMPLETED.value:
            raise HTTPException(
                status_code=400, detail=f"Task not completed. Current status: {task['status']}"
            )

        return {
            "task_id": task_id,
            "research_type": task.get("research_type")
            or ("topic" if task.get("topic") else "company"),
            "subject": task.get("subject") or task.get("company_name") or task.get("topic"),
            "company_name": task.get("company_name"),
            "topic": task.get("topic"),
            "status": task["status"],
            "result": (
                task.get("result", {}) if not _use_disk_backend() else task.get("result") or task
            ),
            "completed_at": task.get("completed_at"),
        }

    @router.delete(
        "/research/{task_id}",
        summary="Cancel research task",
        description="Cancel a pending or running research task",
    )
    async def cancel_research(task_id: str = Path(..., description="Task ID")) -> Dict[str, str]:
        """Cancel a research task."""
        if _use_disk_backend():
            cancelled = get_orchestrator().cancel_task(task_id)
            if not cancelled:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Cannot cancel task. "
                        "Only tasks that have not started yet can be cancelled in disk-first mode."
                    ),
                )
            return {"message": f"Task {task_id} cancelled"}

        storage = _get_storage()
        task = await storage.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if task["status"] in [TaskStatusEnum.COMPLETED.value, TaskStatusEnum.FAILED.value]:
            raise HTTPException(
                status_code=400, detail=f"Cannot cancel task with status: {task['status']}"
            )

        await storage.update_task(
            task_id, {"status": TaskStatusEnum.CANCELLED.value, "cancelled_at": utc_now()}
        )

        return {"message": f"Task {task_id} cancelled"}

    # ==========================================================================
    # Batch Endpoints
    # ==========================================================================

    @router.post(
        "/research/batch",
        response_model=BatchResponse,
        summary="Start batch research",
        description="Start research for multiple companies",
    )
    async def start_batch_research(
        request: BatchRequest, background_tasks: BackgroundTasks
    ) -> BatchResponse:
        """Start batch research for multiple companies."""
        if _use_disk_backend():
            orchestrator = get_orchestrator()
            research_type = request.research_type.value
            items = request.companies if research_type == "company" else request.topics
            job = orchestrator.start_batch(
                items,
                depth=request.depth.value,
                force=False,
                metadata=request.metadata,
                research_type=research_type,
            )
            batch_id = job["batch_id"]
            task_ids = job["task_ids"]
        else:
            storage = _get_storage()
            batch_id = f"batch_{int(time.time() * 1000)}"
            task_ids = []

            # Create individual tasks
            items = (
                request.companies if request.research_type.value == "company" else request.topics
            )
            for item in items:
                task_id = f"task_{int(time.time() * 1000)}_{len(task_ids)}"
                task_ids.append(task_id)

                task_data = {
                    "task_id": task_id,
                    "research_type": request.research_type.value,
                    "company_name": item if request.research_type.value == "company" else None,
                    "topic": item if request.research_type.value == "topic" else None,
                    "subject": item,
                    "batch_id": batch_id,
                    "depth": request.depth.value,
                    "status": TaskStatusEnum.PENDING.value,
                    "created_at": utc_now(),
                    "result": None,
                    "error": None,
                }
                await storage.save_task(task_id, task_data)

            # Store batch
            batch_data = {
                "batch_id": batch_id,
                "research_type": request.research_type.value,
                "items": items,
                "task_ids": task_ids,
                "status": TaskStatusEnum.PENDING.value,
                "created_at": utc_now(),
                "completed": 0,
                "failed": 0,
            }
            await storage.save_batch(batch_id, batch_data)

            # Start background processing
            background_tasks.add_task(_execute_batch, batch_id, request)

        return BatchResponse(
            batch_id=batch_id,
            research_type=request.research_type,
            total_items=len(
                request.companies if request.research_type.value == "company" else request.topics
            ),
            status=TaskStatusEnum.PENDING,
            created_at=utc_now(),
            task_ids=task_ids,
            message=(
                "Batch research started"
                if not _use_disk_backend()
                else "Batch submitted (disk-first runner). See outputs/ or poll /research/batch/{batch_id}."
            ),
        )

    @router.get(
        "/research/batch/{batch_id}",
        summary="Get batch status",
        description="Get status of a batch research job",
    )
    async def get_batch_status(batch_id: str = Path(..., description="Batch ID")) -> Dict[str, Any]:
        """Get status of a batch research job."""
        if _use_disk_backend():
            batch = get_orchestrator().get_batch_status(batch_id)
        else:
            storage = _get_storage()
            batch = await storage.get_batch(batch_id)

        if not batch:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")

        if _use_disk_backend():
            return batch

        # Calculate progress
        completed = 0
        failed = 0
        running = 0
        for tid in batch["task_ids"]:
            task = await storage.get_task(tid)
            if task:
                if task["status"] == TaskStatusEnum.COMPLETED.value:
                    completed += 1
                elif task["status"] == TaskStatusEnum.FAILED.value:
                    failed += 1
                elif task["status"] == TaskStatusEnum.RUNNING.value:
                    running += 1

        return {
            **batch,
            "completed": completed,
            "failed": failed,
            "running": running,
            "progress": completed / len(batch["task_ids"]) if batch["task_ids"] else 0,
        }

    # ==========================================================================
    # List and Search
    # ==========================================================================

    @router.get(
        "/research",
        summary="List research tasks",
        description="List all research tasks with optional filtering",
    )
    async def list_research_tasks(
        status: Optional[str] = Query(None, description="Filter by status"),
        company: Optional[str] = Query(None, description="Filter by company name"),
        limit: int = Query(50, ge=1, le=200, description="Maximum results"),
        offset: int = Query(0, ge=0, description="Offset for pagination"),
    ) -> Dict[str, Any]:
        """List research tasks."""
        if _use_disk_backend():
            tasks = get_orchestrator().list_tasks(
                status=status, company=company, limit=limit, offset=offset
            )
            return {"tasks": tasks, "total": len(tasks), "limit": limit, "offset": offset}
        else:
            storage = _get_storage()
            tasks = await storage.list_tasks(
                status=status, company=company, limit=limit, offset=offset
            )
            total = await storage.count_tasks(status=status)
            return {"tasks": tasks, "total": total, "limit": limit, "offset": offset}

    # ==========================================================================
    # Health Check
    # ==========================================================================

    @router.get(
        "/health",
        response_model=HealthResponse,
        summary="Health check",
        description="Check API health status",
    )
    async def health_check() -> HealthResponse:
        """Check API health."""
        services: Dict[str, str] = {"api": "running"}

        if _use_disk_backend():
            services["execution_backend"] = "disk"
        else:
            services["execution_backend"] = "task_storage"
            storage = _get_storage()
            total_tasks = await storage.count_tasks()
            services["tasks"] = f"{total_tasks} total"

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=utc_now(),
            services=services,
        )

    @router.get("/stats", summary="Get API statistics", description="Get usage statistics")
    async def get_stats() -> Dict[str, Any]:
        """Get API statistics."""
        storage = _get_storage()

        total = await storage.count_tasks()
        completed = await storage.count_tasks(status=TaskStatusEnum.COMPLETED.value)
        failed = await storage.count_tasks(status=TaskStatusEnum.FAILED.value)
        running = await storage.count_tasks(status=TaskStatusEnum.RUNNING.value)
        pending = await storage.count_tasks(status=TaskStatusEnum.PENDING.value)

        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
            "storage_backend": type(storage).__name__,
            "timestamp": utc_now().isoformat(),
        }


# ============================================================================
# Background Task Functions
# ============================================================================


async def _execute_research(task_id: str, request: ResearchRequest):
    """Execute research in background."""
    storage = _get_storage()
    task = await storage.get_task(task_id)
    if not task:
        return

    # Update to running
    await storage.update_task(
        task_id, {"status": TaskStatusEnum.RUNNING.value, "started_at": utc_now()}
    )

    try:
        from ..runner import run_with_state

        research_type = request.research_type.value
        subject = request.company_name if research_type == "company" else request.topic
        subject = (subject or "").strip()

        if research_type == "topic":
            output, final_state = await asyncio.to_thread(
                run_with_state, research_type="topic", subject=subject, force=False, output_dir=None
            )
            await storage.update_task(
                task_id,
                {
                    "status": TaskStatusEnum.COMPLETED.value,
                    "completed_at": utc_now(),
                    "result": {
                        "output": output,
                        "report_path": output.get("report_path"),
                        "sources_count": len(final_state.get("sources") or []),
                    },
                },
            )
        else:
            output, final_state = await asyncio.to_thread(
                run_with_state,
                research_type="company",
                subject=subject,
                force=False,
                output_dir=None,
            )

            # Update to completed
            await storage.update_task(
                task_id,
                {
                    "status": TaskStatusEnum.COMPLETED.value,
                    "completed_at": utc_now(),
                    "result": {
                        "output": output,
                        "report_path": output.get("report_path"),
                        "sources_count": len(final_state.get("sources") or []),
                    },
                },
            )

        # Send webhook if configured
        if request.webhook_url:
            updated_task = await storage.get_task(task_id)
            if updated_task:
                await _send_webhook(request.webhook_url, updated_task)

    except Exception as e:
        logger.error(f"Research task {task_id} failed: {e}")
        await storage.update_task(
            task_id,
            {"status": TaskStatusEnum.FAILED.value, "error": str(e), "failed_at": utc_now()},
        )


async def _execute_batch(batch_id: str, request: BatchRequest):
    """Execute batch research in background."""
    storage = _get_storage()
    batch = await storage.get_batch(batch_id)
    if not batch:
        return

    await storage.update_batch(batch_id, {"status": TaskStatusEnum.RUNNING.value})

    completed_count = 0
    failed_count = 0

    for task_id in batch["task_ids"]:
        task = await storage.get_task(task_id)
        if task:
            # Create individual request
            research_type = task.get("research_type") or request.research_type.value
            individual_request = ResearchRequest(
                research_type=research_type,
                company_name=task.get("company_name"),
                topic=task.get("topic"),
                depth=ResearchDepthEnum(task["depth"]),
            )
            await _execute_research(task_id, individual_request)

            # Check updated status
            updated_task = await storage.get_task(task_id)
            if updated_task:
                if updated_task["status"] == TaskStatusEnum.COMPLETED.value:
                    completed_count += 1
                elif updated_task["status"] == TaskStatusEnum.FAILED.value:
                    failed_count += 1

    await storage.update_batch(
        batch_id,
        {
            "status": TaskStatusEnum.COMPLETED.value,
            "completed_at": utc_now(),
            "completed": completed_count,
            "failed": failed_count,
        },
    )


async def _send_webhook(url: str, payload: Dict[str, Any]):
    """
    Send webhook notification with SSL verification.

    Args:
        url: Webhook URL (must be HTTPS in production)
        payload: Data to send
    """

    # Validate URL scheme
    if not url.startswith(("http://", "https://")):
        logger.warning(f"Invalid webhook URL scheme: {url}")
        return

    # Require HTTPS in production
    is_production = get_config("ENVIRONMENT", default="development") == "production"
    if is_production and not url.startswith("https://"):
        logger.warning(f"Webhook URL must use HTTPS in production: {url}")
        return

    try:
        import httpx

        # Always verify SSL certificates (default behavior)
        async with httpx.AsyncClient(verify=True) as client:
            response = await client.post(
                url, json=payload, timeout=10.0, headers={"Content-Type": "application/json"}
            )
            if response.status_code >= 400:
                logger.warning(f"Webhook returned {response.status_code}: {url}")
    except Exception as e:
        logger.error(f"Webhook failed for {url}: {e}")
