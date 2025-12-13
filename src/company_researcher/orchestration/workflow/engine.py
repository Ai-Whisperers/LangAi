"""
Workflow Engine Module.

Core workflow orchestration engine.
"""

import time
from typing import Any, Callable, Dict, Optional

from .models import (
    NodeType,
    ExecutionStatus,
    RouteCondition,
    NodeConfig,
    ExecutionResult,
    WorkflowState,
)
from .executor import NodeExecutor
from ...utils import utc_now


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
        self._executor: Optional[NodeExecutor] = None

    def _get_executor(self) -> NodeExecutor:
        """Get or create node executor."""
        if self._executor is None:
            self._executor = NodeExecutor(
                nodes=self._nodes,
                max_parallel=self._max_parallel,
                enable_retries=self._enable_retries
            )
        return self._executor

    # ==========================================================================
    # Workflow Definition
    # ==========================================================================

    def add_node(self, config: NodeConfig) -> "WorkflowEngine":
        """Add a node to the workflow."""
        self._nodes[config.name] = config

        # First node becomes start node
        if self._start_node is None:
            self._start_node = config.name

        # Invalidate executor cache
        self._executor = None

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
            start_time=utc_now()
        )

        state.status = ExecutionStatus.RUNNING

        try:
            self._execute_from_node(self._start_node, state)
            state.status = ExecutionStatus.COMPLETED
        except Exception as e:
            state.status = ExecutionStatus.FAILED
            print(f"[Workflow] Execution failed: {e}")

        state.end_time = utc_now()
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
            start_time=utc_now()
        )

        state.status = ExecutionStatus.RUNNING

        try:
            await self._execute_from_node_async(self._start_node, state)
            state.status = ExecutionStatus.COMPLETED
        except Exception as e:
            state.status = ExecutionStatus.FAILED
            print(f"[Workflow] Async execution failed: {e}")

        state.end_time = utc_now()
        return state

    def _execute_from_node(self, node_name: str, state: WorkflowState):
        """Execute workflow starting from a specific node."""
        if not node_name or node_name not in self._nodes:
            return

        node = self._nodes[node_name]
        state.current_node = node_name
        executor = self._get_executor()

        # Check condition
        if not executor.check_condition(node, state):
            state.results[node_name] = ExecutionResult(
                node_name=node_name,
                status=ExecutionStatus.SKIPPED
            )
            return

        # Execute based on node type
        if node.node_type == NodeType.AGENT:
            result = executor.execute_agent_node(node, state)
        elif node.node_type == NodeType.PARALLEL:
            result = executor.execute_parallel_nodes(node, state)
        elif node.node_type == NodeType.SEQUENCE:
            result = executor.execute_sequence_nodes(
                node, state, self._execute_from_node
            )
        elif node.node_type == NodeType.ROUTER:
            result = executor.execute_router_node(
                node, state, executor.check_condition, self._execute_from_node
            )
        elif node.node_type == NodeType.TRANSFORM:
            result = executor.execute_transform_node(node, state)
        elif node.node_type == NodeType.CHECKPOINT:
            result = executor.execute_checkpoint_node(node, state)
        elif node.node_type == NodeType.END:
            result = ExecutionResult(
                node_name=node_name,
                status=ExecutionStatus.COMPLETED
            )
        else:
            result = executor.execute_agent_node(node, state)

        state.results[node_name] = result

        if result.status == ExecutionStatus.COMPLETED:
            state.completed_nodes.append(node_name)
            # Execute children (if not parallel/sequence which handle their own)
            if node.node_type not in (NodeType.PARALLEL, NodeType.SEQUENCE):
                for child in node.children:
                    self._execute_from_node(child, state)
        else:
            state.failed_nodes.append(node_name)

    async def _execute_from_node_async(self, node_name: str, state: WorkflowState):
        """Async version of node execution."""
        if not node_name or node_name not in self._nodes:
            return

        node = self._nodes[node_name]
        state.current_node = node_name
        executor = self._get_executor()

        if not executor.check_condition(node, state):
            state.results[node_name] = ExecutionResult(
                node_name=node_name,
                status=ExecutionStatus.SKIPPED
            )
            return

        result = await executor.execute_node_async(node, state)
        state.results[node_name] = result

        if result.status == ExecutionStatus.COMPLETED:
            state.completed_nodes.append(node_name)
            if node.node_type not in (NodeType.PARALLEL, NodeType.SEQUENCE):
                for child in node.children:
                    await self._execute_from_node_async(child, state)
        else:
            state.failed_nodes.append(node_name)

    # ==========================================================================
    # Callbacks
    # ==========================================================================

    def on_node_start(self, callback: Callable) -> "WorkflowEngine":
        """Register callback for node start."""
        self._get_executor().on_node_start(callback)
        return self

    def on_node_complete(self, callback: Callable) -> "WorkflowEngine":
        """Register callback for node completion."""
        self._get_executor().on_node_complete(callback)
        return self

    def on_node_error(self, callback: Callable) -> "WorkflowEngine":
        """Register callback for node errors."""
        self._get_executor().on_node_error(callback)
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
        if self._executor:
            self._executor.shutdown()


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
