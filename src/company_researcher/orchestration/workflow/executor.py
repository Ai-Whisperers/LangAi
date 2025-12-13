"""
Workflow Executor Module.

Node execution logic for different node types.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List

from .models import (
    ExecutionStatus,
    RouteCondition,
    NodeConfig,
    ExecutionResult,
    WorkflowState,
)
from ...utils import utc_now


class NodeExecutor:
    """
    Executes workflow nodes.

    Handles different node types:
    - Agent nodes (invoke handlers)
    - Parallel nodes (concurrent execution)
    - Sequence nodes (sequential execution)
    - Router nodes (conditional routing)
    - Transform nodes (data transformation)
    - Checkpoint nodes (state snapshots)
    """

    def __init__(
        self,
        nodes: Dict[str, NodeConfig],
        max_parallel: int = 4,
        enable_retries: bool = True
    ):
        """
        Initialize executor.

        Args:
            nodes: Dictionary of node configurations
            max_parallel: Maximum parallel executions
            enable_retries: Enable automatic retries
        """
        self._nodes = nodes
        self._max_parallel = max_parallel
        self._enable_retries = enable_retries
        self._executor = ThreadPoolExecutor(max_workers=max_parallel)

        # Callbacks
        self._on_node_start: List[Callable] = []
        self._on_node_complete: List[Callable] = []
        self._on_node_error: List[Callable] = []

    def execute_agent_node(
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

    def execute_parallel_nodes(
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
                    self.execute_agent_node,
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

    def execute_sequence_nodes(
        self,
        node: NodeConfig,
        state: WorkflowState,
        execute_from_node_callback: Callable
    ) -> ExecutionResult:
        """Execute child nodes in sequence."""
        start_time = time.time()
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        for child_name in node.children:
            execute_from_node_callback(child_name, state)

        result.status = ExecutionStatus.COMPLETED
        result.duration_ms = (time.time() - start_time) * 1000

        return result

    def execute_router_node(
        self,
        node: NodeConfig,
        state: WorkflowState,
        check_condition_callback: Callable,
        execute_from_node_callback: Callable
    ) -> ExecutionResult:
        """Execute router node (selects path based on conditions)."""
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        # Find first matching route
        selected_child = None
        for child_name in node.children:
            child_node = self._nodes.get(child_name)
            if child_node and check_condition_callback(child_node, state):
                selected_child = child_name
                break

        if selected_child:
            execute_from_node_callback(selected_child, state)
            result.output = {"selected_route": selected_child}
            result.status = ExecutionStatus.COMPLETED
        else:
            result.status = ExecutionStatus.SKIPPED

        return result

    def execute_transform_node(
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

    def execute_checkpoint_node(
        self,
        node: NodeConfig,
        state: WorkflowState
    ) -> ExecutionResult:
        """Execute checkpoint node (state snapshot)."""
        result = ExecutionResult(node_name=node.name, status=ExecutionStatus.RUNNING)

        # Create state snapshot
        checkpoint = {
            "timestamp": utc_now().isoformat(),
            "completed_nodes": state.completed_nodes.copy(),
            "data_keys": list(state.data.keys()),
            "total_cost": state.total_cost
        }

        result.output = checkpoint
        result.status = ExecutionStatus.COMPLETED

        return result

    async def execute_node_async(
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

    def check_condition(self, node: NodeConfig, state: WorkflowState) -> bool:
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

    def on_node_start(self, callback: Callable) -> "NodeExecutor":
        """Register callback for node start."""
        self._on_node_start.append(callback)
        return self

    def on_node_complete(self, callback: Callable) -> "NodeExecutor":
        """Register callback for node completion."""
        self._on_node_complete.append(callback)
        return self

    def on_node_error(self, callback: Callable) -> "NodeExecutor":
        """Register callback for node errors."""
        self._on_node_error.append(callback)
        return self

    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=True)
