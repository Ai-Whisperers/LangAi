"""
API Routes (Phase 18.4).

REST API endpoints for company research:
- Research endpoints
- Batch processing
- Task management
- Health checks
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import time

try:
    from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, Path
    from fastapi.responses import JSONResponse
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


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/v1", tags=["research"])

# In-memory task storage (replace with database in production)
_tasks: Dict[str, Dict[str, Any]] = {}
_batches: Dict[str, Dict[str, Any]] = {}


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
        task_id = f"task_{int(time.time() * 1000)}"

        # Store task
        _tasks[task_id] = {
            "task_id": task_id,
            "company_name": request.company_name,
            "depth": request.depth.value,
            "status": TaskStatusEnum.PENDING.value,
            "created_at": datetime.now(),
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
            created_at=datetime.now(),
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
        task = _tasks.get(task_id)

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
        task = _tasks.get(task_id)

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
        task = _tasks.get(task_id)

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

        task["status"] = TaskStatusEnum.CANCELLED.value
        task["cancelled_at"] = datetime.now()

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
        batch_id = f"batch_{int(time.time() * 1000)}"
        task_ids = []

        # Create individual tasks
        for company in request.companies:
            task_id = f"task_{int(time.time() * 1000)}_{len(task_ids)}"
            task_ids.append(task_id)

            _tasks[task_id] = {
                "task_id": task_id,
                "company_name": company,
                "batch_id": batch_id,
                "depth": request.depth.value,
                "status": TaskStatusEnum.PENDING.value,
                "created_at": datetime.now(),
                "result": None,
                "error": None
            }

        # Store batch
        _batches[batch_id] = {
            "batch_id": batch_id,
            "companies": request.companies,
            "task_ids": task_ids,
            "status": TaskStatusEnum.PENDING.value,
            "created_at": datetime.now(),
            "completed": 0,
            "failed": 0
        }

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
            created_at=datetime.now(),
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
        batch = _batches.get(batch_id)

        if not batch:
            raise HTTPException(
                status_code=404,
                detail=f"Batch {batch_id} not found"
            )

        # Calculate progress
        tasks = [_tasks.get(tid) for tid in batch["task_ids"]]
        completed = sum(1 for t in tasks if t and t["status"] == TaskStatusEnum.COMPLETED.value)
        failed = sum(1 for t in tasks if t and t["status"] == TaskStatusEnum.FAILED.value)
        running = sum(1 for t in tasks if t and t["status"] == TaskStatusEnum.RUNNING.value)

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
        tasks = list(_tasks.values())

        # Filter by status
        if status:
            tasks = [t for t in tasks if t["status"] == status]

        # Filter by company
        if company:
            company_lower = company.lower()
            tasks = [t for t in tasks if company_lower in t["company_name"].lower()]

        # Sort by created_at descending
        tasks.sort(key=lambda t: t["created_at"], reverse=True)

        # Paginate
        total = len(tasks)
        tasks = tasks[offset:offset + limit]

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
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now(),
            services={
                "api": "running",
                "tasks": f"{len(_tasks)} active",
                "batches": f"{len(_batches)} active"
            }
        )


    @router.get(
        "/stats",
        summary="Get API statistics",
        description="Get usage statistics"
    )
    async def get_stats() -> Dict[str, Any]:
        """Get API statistics."""
        completed = sum(1 for t in _tasks.values() if t["status"] == TaskStatusEnum.COMPLETED.value)
        failed = sum(1 for t in _tasks.values() if t["status"] == TaskStatusEnum.FAILED.value)
        running = sum(1 for t in _tasks.values() if t["status"] == TaskStatusEnum.RUNNING.value)

        return {
            "total_tasks": len(_tasks),
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": len(_tasks) - completed - failed - running,
            "batches": len(_batches),
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# Background Task Functions
# ============================================================================

async def _execute_research(task_id: str, request: ResearchRequest):
    """Execute research in background."""
    task = _tasks.get(task_id)
    if not task:
        return

    task["status"] = TaskStatusEnum.RUNNING.value
    task["started_at"] = datetime.now()

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

        task["status"] = TaskStatusEnum.COMPLETED.value
        task["completed_at"] = datetime.now()
        task["result"] = {
            "agent_outputs": result.data.get("agent_outputs", {}),
            "synthesis": result.data.get("synthesis"),
            "total_cost": result.total_cost,
            "duration_seconds": result.duration_seconds
        }

        # Send webhook if configured
        if request.webhook_url:
            await _send_webhook(request.webhook_url, task)

    except Exception as e:
        task["status"] = TaskStatusEnum.FAILED.value
        task["error"] = str(e)
        task["failed_at"] = datetime.now()


async def _execute_batch(batch_id: str, request: BatchRequest):
    """Execute batch research in background."""
    batch = _batches.get(batch_id)
    if not batch:
        return

    batch["status"] = TaskStatusEnum.RUNNING.value

    for task_id in batch["task_ids"]:
        task = _tasks.get(task_id)
        if task:
            # Create individual request
            individual_request = ResearchRequest(
                company_name=task["company_name"],
                depth=ResearchDepthEnum(task["depth"])
            )
            await _execute_research(task_id, individual_request)

            # Update batch counts
            if task["status"] == TaskStatusEnum.COMPLETED.value:
                batch["completed"] += 1
            elif task["status"] == TaskStatusEnum.FAILED.value:
                batch["failed"] += 1

    batch["status"] = TaskStatusEnum.COMPLETED.value
    batch["completed_at"] = datetime.now()


async def _send_webhook(url: str, payload: Dict[str, Any]):
    """Send webhook notification."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                url,
                json=payload,
                timeout=10.0
            )
    except Exception as e:
        print(f"Webhook failed: {e}")
