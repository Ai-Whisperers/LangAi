"""
API Routes (Phase 18.4).

REST API endpoints for company research:
- Research endpoints
- Batch processing
- Task management
- Health checks
"""

from typing import Dict, Any, Optional
import time
from ..utils import get_config, get_logger, utc_now

try:
    from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
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

from .models import (
    ResearchRequest,
    ResearchResponse,
    BatchRequest,
    BatchResponse,
    HealthResponse,
    TaskStatusEnum,
    ResearchDepthEnum,
)
from .task_storage import get_task_storage, TaskStorage

logger = get_logger(__name__)


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/v1", tags=["research"])


def _get_storage() -> TaskStorage:
    """Get the task storage instance."""
    return get_task_storage()


# ============================================================================
# Research Endpoints
# ============================================================================

if FASTAPI_AVAILABLE:
    @router.post(
        "/research",
        response_model=ResearchResponse,
        summary="Start company research",
        description="Initiate research for a single company"
    )
    async def start_research(
        request: ResearchRequest,
        background_tasks: BackgroundTasks
    ) -> ResearchResponse:
        """
        Start research for a company.

        Returns task ID to track progress.
        """
        storage = _get_storage()
        task_id = f"task_{int(time.time() * 1000)}"

        # Create task data
        task_data = {
            "task_id": task_id,
            "company_name": request.company_name,
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
            "error": None
        }

        # Store task persistently
        await storage.save_task(task_id, task_data)

        # Start background task
        background_tasks.add_task(
            _execute_research,
            task_id,
            request
        )

        # Estimate duration based on depth
        duration_map = {
            "quick": 30,
            "standard": 120,
            "comprehensive": 300
        }

        return ResearchResponse(
            task_id=task_id,
            company_name=request.company_name,
            status=TaskStatusEnum.PENDING,
            depth=request.depth,
            created_at=utc_now(),
            estimated_duration_seconds=duration_map.get(request.depth.value, 120),
            message="Research task created successfully"
        )


    @router.get(
        "/research/{task_id}",
        summary="Get research task status",
        description="Get status and results of a research task"
    )
    async def get_research_status(
        task_id: str = Path(..., description="Task ID")
    ) -> Dict[str, Any]:
        """Get status of a research task."""
        storage = _get_storage()
        task = await storage.get_task(task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )

        return task


    @router.get(
        "/research/{task_id}/result",
        summary="Get research results",
        description="Get complete results of a finished research task"
    )
    async def get_research_result(
        task_id: str = Path(..., description="Task ID")
    ) -> Dict[str, Any]:
        """Get results of a completed research task."""
        storage = _get_storage()
        task = await storage.get_task(task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )

        if task["status"] != TaskStatusEnum.COMPLETED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Task not completed. Current status: {task['status']}"
            )

        return {
            "task_id": task_id,
            "company_name": task["company_name"],
            "status": task["status"],
            "result": task.get("result", {}),
            "completed_at": task.get("completed_at")
        }


    @router.delete(
        "/research/{task_id}",
        summary="Cancel research task",
        description="Cancel a pending or running research task"
    )
    async def cancel_research(
        task_id: str = Path(..., description="Task ID")
    ) -> Dict[str, str]:
        """Cancel a research task."""
        storage = _get_storage()
        task = await storage.get_task(task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )

        if task["status"] in [TaskStatusEnum.COMPLETED.value, TaskStatusEnum.FAILED.value]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel task with status: {task['status']}"
            )

        await storage.update_task(task_id, {
            "status": TaskStatusEnum.CANCELLED.value,
            "cancelled_at": utc_now()
        })

        return {"message": f"Task {task_id} cancelled"}


    # ==========================================================================
    # Batch Endpoints
    # ==========================================================================

    @router.post(
        "/research/batch",
        response_model=BatchResponse,
        summary="Start batch research",
        description="Start research for multiple companies"
    )
    async def start_batch_research(
        request: BatchRequest,
        background_tasks: BackgroundTasks
    ) -> BatchResponse:
        """Start batch research for multiple companies."""
        storage = _get_storage()
        batch_id = f"batch_{int(time.time() * 1000)}"
        task_ids = []

        # Create individual tasks
        for company in request.companies:
            task_id = f"task_{int(time.time() * 1000)}_{len(task_ids)}"
            task_ids.append(task_id)

            task_data = {
                "task_id": task_id,
                "company_name": company,
                "batch_id": batch_id,
                "depth": request.depth.value,
                "status": TaskStatusEnum.PENDING.value,
                "created_at": utc_now(),
                "result": None,
                "error": None
            }
            await storage.save_task(task_id, task_data)

        # Store batch
        batch_data = {
            "batch_id": batch_id,
            "companies": request.companies,
            "task_ids": task_ids,
            "status": TaskStatusEnum.PENDING.value,
            "created_at": utc_now(),
            "completed": 0,
            "failed": 0
        }
        await storage.save_batch(batch_id, batch_data)

        # Start background processing
        background_tasks.add_task(
            _execute_batch,
            batch_id,
            request
        )

        return BatchResponse(
            batch_id=batch_id,
            total_companies=len(request.companies),
            status=TaskStatusEnum.PENDING,
            created_at=utc_now(),
            task_ids=task_ids,
            message="Batch research started"
        )


    @router.get(
        "/research/batch/{batch_id}",
        summary="Get batch status",
        description="Get status of a batch research job"
    )
    async def get_batch_status(
        batch_id: str = Path(..., description="Batch ID")
    ) -> Dict[str, Any]:
        """Get status of a batch research job."""
        storage = _get_storage()
        batch = await storage.get_batch(batch_id)

        if not batch:
            raise HTTPException(
                status_code=404,
                detail=f"Batch {batch_id} not found"
            )

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
            "progress": completed / len(batch["task_ids"]) if batch["task_ids"] else 0
        }


    # ==========================================================================
    # List and Search
    # ==========================================================================

    @router.get(
        "/research",
        summary="List research tasks",
        description="List all research tasks with optional filtering"
    )
    async def list_research_tasks(
        status: Optional[str] = Query(None, description="Filter by status"),
        company: Optional[str] = Query(None, description="Filter by company name"),
        limit: int = Query(50, ge=1, le=200, description="Maximum results"),
        offset: int = Query(0, ge=0, description="Offset for pagination")
    ) -> Dict[str, Any]:
        """List research tasks."""
        storage = _get_storage()
        tasks = await storage.list_tasks(
            status=status,
            company=company,
            limit=limit,
            offset=offset
        )

        # Get total count for pagination
        total = await storage.count_tasks(status=status)

        return {
            "tasks": tasks,
            "total": total,
            "limit": limit,
            "offset": offset
        }


    # ==========================================================================
    # Health Check
    # ==========================================================================

    @router.get(
        "/health",
        response_model=HealthResponse,
        summary="Health check",
        description="Check API health status"
    )
    async def health_check() -> HealthResponse:
        """Check API health."""
        storage = _get_storage()
        total_tasks = await storage.count_tasks()

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=utc_now(),
            services={
                "api": "running",
                "storage": type(storage).__name__,
                "tasks": f"{total_tasks} total"
            }
        )


    @router.get(
        "/stats",
        summary="Get API statistics",
        description="Get usage statistics"
    )
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
            "timestamp": utc_now().isoformat()
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
    await storage.update_task(task_id, {
        "status": TaskStatusEnum.RUNNING.value,
        "started_at": utc_now()
    })

    try:
        # Import and execute workflow
        from ..orchestration.research_workflow import execute_research, ResearchDepth

        depth_map = {
            "quick": ResearchDepth.QUICK,
            "standard": ResearchDepth.STANDARD,
            "comprehensive": ResearchDepth.COMPREHENSIVE
        }

        result = execute_research(
            company_name=request.company_name,
            depth=depth_map.get(request.depth.value, ResearchDepth.STANDARD)
        )

        # Update to completed
        await storage.update_task(task_id, {
            "status": TaskStatusEnum.COMPLETED.value,
            "completed_at": utc_now(),
            "result": {
                "agent_outputs": result.data.get("agent_outputs", {}),
                "synthesis": result.data.get("synthesis"),
                "total_cost": result.total_cost,
                "duration_seconds": result.duration_seconds
            }
        })

        # Send webhook if configured
        if request.webhook_url:
            updated_task = await storage.get_task(task_id)
            if updated_task:
                await _send_webhook(request.webhook_url, updated_task)

    except Exception as e:
        logger.error(f"Research task {task_id} failed: {e}")
        await storage.update_task(task_id, {
            "status": TaskStatusEnum.FAILED.value,
            "error": str(e),
            "failed_at": utc_now()
        })


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
            individual_request = ResearchRequest(
                company_name=task["company_name"],
                depth=ResearchDepthEnum(task["depth"])
            )
            await _execute_research(task_id, individual_request)

            # Check updated status
            updated_task = await storage.get_task(task_id)
            if updated_task:
                if updated_task["status"] == TaskStatusEnum.COMPLETED.value:
                    completed_count += 1
                elif updated_task["status"] == TaskStatusEnum.FAILED.value:
                    failed_count += 1

    await storage.update_batch(batch_id, {
        "status": TaskStatusEnum.COMPLETED.value,
        "completed_at": utc_now(),
        "completed": completed_count,
        "failed": failed_count
    })


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
                url,
                json=payload,
                timeout=10.0,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code >= 400:
                logger.warning(f"Webhook returned {response.status_code}: {url}")
    except Exception as e:
        logger.error(f"Webhook failed for {url}: {e}")
