"""
Workflow Engine (Phase 17.1).

Advanced workflow orchestration:
- Dynamic routing based on data
- Parallel and sequential execution
- Conditional branching
- Error handling and retries
- State management

Core engine for orchestrating multi-agent research workflows.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================================
# Enums and Data Models
# ============================================================================

class NodeType(str, Enum):
    """Types of workflow nodes."""
    AGENT = "agent"            # Agent execution node
    ROUTER = "router"          # Conditional routing
    PARALLEL = "parallel"      # Parallel execution
    SEQUENCE = "sequence"      # Sequential execution
    TRANSFORM = "transform"    # Data transformation
    CHECKPOINT = "checkpoint"  # State checkpoint
    END = "end"               # End node


class ExecutionStatus(str, Enum):
    """Execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class RouteCondition(str, Enum):
    """Route condition types."""
    ALWAYS = "always"
    IF_DATA_PRESENT = "if_data_present"
    IF_QUALITY_HIGH = "if_quality_high"
    IF_COST_UNDER = "if_cost_under"
    CUSTOM = "custom"


@dataclass
class NodeConfig:
    """Configuration for a workflow node."""
    name: str
    node_type: NodeType
    handler: Optional[Callable] = None
    children: List[str] = field(default_factory=list)
    retry_count: int = 2
    timeout: int = 300  # seconds
    condition: Optional[RouteCondition] = None
    condition_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of node execution."""
    node_name: str
    status: ExecutionStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    retries: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node": self.node_name,
            "status": self.status.value,
            "output_type": type(self.output).__name__ if self.output else None,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
            "retries": self.retries
        }


@dataclass
class WorkflowState:
    """State of workflow execution."""
    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_node: Optional[str] = None
    completed_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    results: Dict[str, ExecutionResult] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_cost: float = 0.0

    @property
    def duration_seconds(self) -> float:
        if not self.start_time:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "current_node": self.current_node,
            "completed": len(self.completed_nodes),
            "failed": len(self.failed_nodes),
            "duration_seconds": round(self.duration_seconds, 2),
            "total_cost": round(self.total_cost, 4)
        }


# ============================================================================
# Workflow Engine
# ============================================================================

class WorkflowEngine:
    """
    Core workflow execution engine.

    Supports:
    - Sequential and parallel node execution
    - Conditional routing
    - Error handling and retries
    - State persistence
    - Real-time monitoring

    Usage:
        engine = WorkflowEngine()

        # Define workflow
        engine.add_node(NodeConfig(
            name="research",
            node_type=NodeType.AGENT,
            handler=researcher_agent_node,
            children=["financial", "market"]
        ))

        # Execute workflow
        state = engine.execute(
            initial_data={"company_name": "Tesla"}
        )
    """

    def __init__(
        self,
        max_parallel: int = 4,
        default_timeout: int = 300,
        enable_retries: bool = True
    ):
        """
        Initialize workflow engine.

        Args:
            max_parallel: Maximum parallel executions
            default_timeout: Default node timeout (seconds)
            enable_retries: Enable automatic retries
        """
        self._nodes: Dict[str, NodeConfig] = {}
        self._start_node: Optional[str] = None
        self._max_parallel = max_parallel
        self._default_timeout = default_timeout
        self._enable_retries = enable_retries
        self._executor = ThreadPoolExecutor(max_workers=max_parallel)

        # Callbacks
        self._on_node_start: List[Callable] = []
        self._on_node_complete: List[Callable] = []
        self._on_node_error: List[Callable] = []

    # ==========================================================================
    # Workflow Definition
    # ==========================================================================

    def add_node(self, config: NodeConfig) -> "WorkflowEngine":
        """Add a node to the workflow."""
        self._nodes[config.name] = config

        # First node becomes start node
        if self._start_node is None:
            self._start_node = config.name

        return self

    def set_start_node(self, name: str) -> "WorkflowEngine":
        """Set the starting node."""
        if name not in self._nodes:
            raise ValueError(f"Node '{name}' not found")
        self._start_node = name
        return self

    def connect(self, from_node: str, to_node: str) -> "WorkflowEngine":
        """Connect two nodes."""
        if from_node not in self._nodes:
            raise ValueError(f"Node '{from_node}' not found")
        if to_node not in self._nodes:
            raise ValueError(f"Node '{to_node}' not found")

        self._nodes[from_node].children.append(to_node)
        return self

    def add_conditional_route(
        self,
        from_node: str,
        to_node: str,
        condition: RouteCondition,
        condition_value: Any = None
    ) -> "WorkflowEngine":
        """Add conditional routing."""
        self.connect(from_node, to_node)

        # Store condition on the destination node
        self._nodes[to_node].condition = condition
        self._nodes[to_node].condition_value = condition_value

        return self

    # ==========================================================================
    # Workflow Execution
    # ==========================================================================

    def execute(
        self,
        initial_data: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> WorkflowState:
        """
        Execute the workflow synchronously.

        Args:
            initial_data: Initial state data
            workflow_id: Optional workflow ID

        Returns:
            Final workflow state
        """
        state = WorkflowState(
            workflow_id=workflow_id or f"wf_{int(time.time())}",
            data=initial_data.copy(),
            start_time=datetime.now()
        )

        state.status = ExecutionStatus.RUNNING

        try:
            self._execute_from_node(self._start_node, state)
            state.status = ExecutionStatus.COMPLETED
        except Exception as e:
            state.status = ExecutionStatus.FAILED
            print(f"[Workflow] Execution failed: {e}")

        state.end_time = datetime.now()
        return state

    async def execute_async(
        self,
        initial_data: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> WorkflowState:
        """Execute workflow asynchronously."""
        state = WorkflowState(
            workflow_id=workflow_id or f"wf_{int(time.time())}",
            data=initial_data.copy(),
            start_time=datetime.now()
        )

        state.status = ExecutionStatus.RUNNING

        try:
            await self._execute_from_node_async(self._start_node, state)
            state.status = ExecutionStatus.COMPLETED
        except Exception as e:
            state.status = ExecutionStatus.FAILED
            print(f"[Workflow] Async execution failed: {e}")

        state.end_time = datetime.now()
        return state

    def _execute_from_node(self, node_name: str, state: WorkflowState):
        """Execute workflow starting from a specific node."""
        if not node_name or node_name not in self._nodes:
            return

        node = self._nodes[node_name]
        state.current_node = node_name

        # Check condition
        if not self._check_condition(node, state):
            state.results[node_name] = ExecutionResult(
                node_name=node_name,
                status=ExecutionStatus.SKIPPED
            )
            return

        # Execute based on node type
        if node.node_type == NodeType.AGENT:
            result = self._execute_agent_node(node, state)
        elif node.node_type == NodeType.PARALLEL:
            result = self._execute_parallel_nodes(node, state)
        elif node.node_type == NodeType.SEQUENCE:
            result = self._execute_sequence_nodes(node, state)
        elif node.node_type == NodeType.ROUTER:
            result = self._execute_router_node(node, state)
        elif node.node_type == NodeType.TRANSFORM:
            result = self._execute_transform_node(node, state)
        elif node.node_type == NodeType.CHECKPOINT:
            result = self._execute_checkpoint_node(node, state)
        elif node.node_type == NodeType.END:
            result = ExecutionResult(
                node_name=node_name,
                status=ExecutionStatus.COMPLETED
            )
        else:
            result = self._execute_agent_node(node, state)

        state.results[node_name] = result

        if result.status == ExecutionStatus.COMPLETED:
            state.completed_nodes.append(node_name)
            # Execute children (if not parallel/sequence which handle their own)
            if node.node_type not in (NodeType.PARALLEL, NodeType.SEQUENCE):
                for child in node.children:
                    self._execute_from_node(child, state)
        else:
            state.failed_nodes.append(node_name)

    def _execute_agent_node(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute an agent node."""
        start_time = time.time()
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        for callback in self._on_node_start:
            callback(node.name, state)

        retries = 0
        last_error = None

        while retries <= node.retry_count:
            try:
                if node.handler:
                    # Execute handler with current state data
                    output = node.handler(state.data)

                    # Merge output into state
                    if isinstance(output, dict):
                        if "agent_outputs" in output:
                            if "agent_outputs" not in state.data:
                                state.data["agent_outputs"] = {}
                            state.data["agent_outputs"].update(output["agent_outputs"])

                        if "total_cost" in output:
                            state.total_cost += output["total_cost"]

                        state.data.update(output)

                    result.output = output
                    result.status = ExecutionStatus.COMPLETED
                    break

            except Exception as e:
                last_error = str(e)
                retries += 1
                result.status = ExecutionStatus.RETRYING

                if self._enable_retries and retries <= node.retry_count:
                    print(f"[Workflow] Retrying {node.name} ({retries}/{node.retry_count})")
                    time.sleep(1)  # Brief delay before retry
                else:
                    result.status = ExecutionStatus.FAILED
                    result.error = last_error

                    for callback in self._on_node_error:
                        callback(node.name, last_error, state)

        result.duration_ms = (time.time() - start_time) * 1000
        result.retries = retries

        if result.status == ExecutionStatus.COMPLETED:
            for callback in self._on_node_complete:
                callback(node.name, result, state)

        return result

    def _execute_parallel_nodes(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute child nodes in parallel."""
        start_time = time.time()
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        futures = {}
        for child_name in node.children:
            child_node = self._nodes.get(child_name)
            if child_node and child_node.handler:
                future = self._executor.submit(
                    self._execute_agent_node,
                    child_node,
                    state
                )
                futures[future] = child_name

        # Wait for all to complete
        child_results = {}
        for future in as_completed(futures):
            child_name = futures[future]
            try:
                child_result = future.result()
                child_results[child_name] = child_result
                state.results[child_name] = child_result

                if child_result.status == ExecutionStatus.COMPLETED:
                    state.completed_nodes.append(child_name)
                else:
                    state.failed_nodes.append(child_name)
            except Exception as e:
                child_results[child_name] = ExecutionResult(
                    node_name=child_name,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
                state.failed_nodes.append(child_name)

        result.output = child_results
        result.status = ExecutionStatus.COMPLETED
        result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _execute_sequence_nodes(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute child nodes in sequence."""
        start_time = time.time()
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        for child_name in node.children:
            self._execute_from_node(child_name, state)

        result.status = ExecutionStatus.COMPLETED
        result.duration_ms = (time.time() - start_time) * 1000

        return result

    def _execute_router_node(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute router node (selects path based on conditions)."""
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        # Find first matching route
        selected_child = None
        for child_name in node.children:
            child_node = self._nodes.get(child_name)
            if child_node and self._check_condition(child_node, state):
                selected_child = child_name
                break

        if selected_child:
            self._execute_from_node(selected_child, state)
            result.output = {"selected_route": selected_child}
            result.status = ExecutionStatus.COMPLETED
        else:
            result.status = ExecutionStatus.SKIPPED

        return result

    def _execute_transform_node(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute data transformation node."""
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        try:
            if node.handler:
                transformed = node.handler(state.data)
                if isinstance(transformed, dict):
                    state.data.update(transformed)
                result.output = transformed
            result.status = ExecutionStatus.COMPLETED
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)

        return result

    def _execute_checkpoint_node(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute checkpoint node (state snapshot)."""
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        # Create state snapshot
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "completed_nodes": state.completed_nodes.copy(),
            "data_keys": list(state.data.keys()),
            "total_cost": state.total_cost
        }

        result.output = checkpoint
        result.status = ExecutionStatus.COMPLETED

        return result

    def _check_condition(self, node: NodeConfig, state: WorkflowState) -> bool:
        """Check if node condition is met."""
        if node.condition is None or node.condition == RouteCondition.ALWAYS:
            return True

        if node.condition == RouteCondition.IF_DATA_PRESENT:
            key = node.condition_value
            return key in state.data

        if node.condition == RouteCondition.IF_QUALITY_HIGH:
            # Check quality score if available
            quality = state.data.get("quality_score", 0)
            threshold = node.condition_value or 0.7
            return quality >= threshold

        if node.condition == RouteCondition.IF_COST_UNDER:
            threshold = node.condition_value or 1.0
            return state.total_cost < threshold

        return True

    async def _execute_from_node_async(self, node_name: str, state: WorkflowState):
        """Async version of node execution."""
        # Similar to sync version but with async handlers
        if not node_name or node_name not in self._nodes:
            return

        node = self._nodes[node_name]
        state.current_node = node_name

        if not self._check_condition(node, state):
            state.results[node_name] = ExecutionResult(
                node_name=node_name,
                status=ExecutionStatus.SKIPPED
            )
            return

        result = await self._execute_node_async(node, state)
        state.results[node_name] = result

        if result.status == ExecutionStatus.COMPLETED:
            state.completed_nodes.append(node_name)
            if node.node_type not in (NodeType.PARALLEL, NodeType.SEQUENCE):
                for child in node.children:
                    await self._execute_from_node_async(child, state)
        else:
            state.failed_nodes.append(node_name)

    async def _execute_node_async(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute a single node asynchronously."""
        start_time = time.time()
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        try:
            if node.handler:
                if asyncio.iscoroutinefunction(node.handler):
                    output = await node.handler(state.data)
                else:
                    output = await asyncio.to_thread(node.handler, state.data)

                if isinstance(output, dict):
                    state.data.update(output)
                    if "total_cost" in output:
                        state.total_cost += output["total_cost"]

                result.output = output
                result.status = ExecutionStatus.COMPLETED

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)

        result.duration_ms = (time.time() - start_time) * 1000
        return result

    # ==========================================================================
    # Callbacks
    # ==========================================================================

    def on_node_start(self, callback: Callable) -> "WorkflowEngine":
        """Register callback for node start."""
        self._on_node_start.append(callback)
        return self

    def on_node_complete(self, callback: Callable) -> "WorkflowEngine":
        """Register callback for node completion."""
        self._on_node_complete.append(callback)
        return self

    def on_node_error(self, callback: Callable) -> "WorkflowEngine":
        """Register callback for node errors."""
        self._on_node_error.append(callback)
        return self

    # ==========================================================================
    # Utility
    # ==========================================================================

    def get_workflow_graph(self) -> Dict[str, Any]:
        """Get workflow as graph structure."""
        return {
            "nodes": {
                name: {
                    "type": node.node_type.value,
                    "children": node.children,
                    "condition": node.condition.value if node.condition else None
                }
                for name, node in self._nodes.items()
            },
            "start_node": self._start_node
        }

    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)


# ============================================================================
# Factory Functions
# ============================================================================

def create_workflow_engine(
    max_parallel: int = 4,
    enable_retries: bool = True
) -> WorkflowEngine:
    """Create a workflow engine instance."""
    return WorkflowEngine(
        max_parallel=max_parallel,
        enable_retries=enable_retries
    )
