"""
Swarm Collaboration Pattern

Enables multiple agents to work on problems in parallel with:
- Parallel exploration from different angles
- Consensus voting on findings
- Conflict resolution
- Result aggregation and deduplication

Usage:
    from company_researcher.orchestration.swarm_collaboration import (
        SwarmOrchestrator,
        SwarmConfig,
        ConsensusStrategy
    )

    swarm = SwarmOrchestrator(config)
    result = await swarm.execute(task, agents)
"""

import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import hashlib
import statistics
import logging

logger = logging.getLogger(__name__)


class ConsensusStrategy(Enum):
    """Strategies for reaching consensus."""
    MAJORITY_VOTE = "majority_vote"         # Simple majority wins
    WEIGHTED_VOTE = "weighted_vote"         # Vote weighted by agent confidence
    UNANIMOUS = "unanimous"                 # All must agree
    FIRST_AGREEMENT = "first_agreement"     # First N agents to agree
    BEST_CONFIDENCE = "best_confidence"     # Highest confidence wins
    AGGREGATION = "aggregation"             # Combine all results


class ConflictResolution(Enum):
    """Methods for resolving conflicts."""
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_RECENT = "most_recent"
    MOST_DETAILED = "most_detailed"
    WEIGHTED_MERGE = "weighted_merge"
    HUMAN_REVIEW = "human_review"


class AgentRole(Enum):
    """Roles agents can play in a swarm."""
    EXPLORER = "explorer"           # Searches for information
    ANALYST = "analyst"             # Analyzes information
    VALIDATOR = "validator"         # Validates findings
    SYNTHESIZER = "synthesizer"     # Combines results
    CRITIC = "critic"               # Challenges findings


@dataclass
class SwarmConfig:
    """Configuration for swarm execution."""
    min_agents: int = 2
    max_agents: int = 5
    timeout_seconds: int = 120
    consensus_strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_VOTE
    conflict_resolution: ConflictResolution = ConflictResolution.HIGHEST_CONFIDENCE
    require_validation: bool = True
    diversity_threshold: float = 0.3    # Minimum result diversity
    confidence_threshold: float = 0.6   # Minimum confidence to accept
    max_retries: int = 2


@dataclass
class AgentResult:
    """Result from a single agent in the swarm."""
    agent_id: str
    agent_role: AgentRole
    result: Dict[str, Any]
    confidence: float
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def result_hash(self) -> str:
        """Hash of result for comparison."""
        # Create deterministic hash of key findings
        import json
        content = json.dumps(self.result, sort_keys=True, default=str)
        return hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class ConsensusResult:
    """Result of consensus voting."""
    reached_consensus: bool
    consensus_value: Any
    confidence: float
    supporting_agents: List[str]
    dissenting_agents: List[str]
    vote_distribution: Dict[str, int]
    reasoning: str


@dataclass
class SwarmResult:
    """Final result from swarm execution."""
    task_id: str
    task_description: str
    final_result: Dict[str, Any]
    consensus: ConsensusResult
    agent_results: List[AgentResult]
    conflicts_found: int
    conflicts_resolved: int
    execution_time: float
    confidence: float
    coverage_score: float           # How many aspects were covered
    timestamp: datetime = field(default_factory=datetime.now)


class AgentWrapper:
    """Wrapper for agents to participate in swarm."""

    def __init__(
        self,
        agent_id: str,
        agent_func: Callable,
        role: AgentRole,
        weight: float = 1.0
    ):
        self.agent_id = agent_id
        self.agent_func = agent_func
        self.role = role
        self.weight = weight
        self.execution_history: List[float] = []

    async def execute(self, task: Dict[str, Any]) -> AgentResult:
        """Execute the agent and return result."""
        start_time = datetime.now()

        try:
            # Execute the agent function
            if asyncio.iscoroutinefunction(self.agent_func):
                result = await self.agent_func(task)
            else:
                result = self.agent_func(task)

            # Extract confidence if present
            confidence = result.pop("confidence", 0.8) if isinstance(result, dict) else 0.8

            execution_time = (datetime.now() - start_time).total_seconds()
            self.execution_history.append(execution_time)

            return AgentResult(
                agent_id=self.agent_id,
                agent_role=self.role,
                result=result if isinstance(result, dict) else {"value": result},
                confidence=confidence,
                execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"Agent {self.agent_id} failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResult(
                agent_id=self.agent_id,
                agent_role=self.role,
                result={"error": str(e)},
                confidence=0.0,
                execution_time=execution_time,
                metadata={"failed": True, "error_type": type(e).__name__}
            )

    @property
    def avg_execution_time(self) -> float:
        """Average execution time."""
        return statistics.mean(self.execution_history) if self.execution_history else 0


class SwarmOrchestrator:
    """
    Orchestrates swarm collaboration between multiple agents.

    Coordinates parallel execution, consensus building, and
    result aggregation.
    """

    def __init__(self, config: Optional[SwarmConfig] = None):
        self.config = config or SwarmConfig()
        self.agents: Dict[str, AgentWrapper] = {}
        self.task_history: List[SwarmResult] = []

    def register_agent(
        self,
        agent_id: str,
        agent_func: Callable,
        role: AgentRole,
        weight: float = 1.0
    ):
        """Register an agent with the swarm."""
        wrapper = AgentWrapper(
            agent_id=agent_id,
            agent_func=agent_func,
            role=role,
            weight=weight
        )
        self.agents[agent_id] = wrapper
        logger.info(f"Registered agent: {agent_id} as {role.value}")

    def remove_agent(self, agent_id: str):
        """Remove an agent from the swarm."""
        if agent_id in self.agents:
            del self.agents[agent_id]

    async def execute(
        self,
        task: Dict[str, Any],
        agent_ids: Optional[List[str]] = None,
        roles: Optional[List[AgentRole]] = None
    ) -> SwarmResult:
        """
        Execute task with swarm of agents.

        Args:
            task: Task to execute
            agent_ids: Specific agents to use (None = all)
            roles: Filter by roles (None = all roles)

        Returns:
            SwarmResult with consensus result
        """
        start_time = datetime.now()
        task_id = hashlib.md5(str(task).encode()).hexdigest()[:8]
        task_description = task.get("description", str(task)[:100])

        # Select agents
        selected_agents = self._select_agents(agent_ids, roles)

        if len(selected_agents) < self.config.min_agents:
            raise ValueError(
                f"Need at least {self.config.min_agents} agents, got {len(selected_agents)}"
            )

        logger.info(f"Executing task {task_id} with {len(selected_agents)} agents")

        # Execute agents in parallel
        agent_results = await self._execute_parallel(selected_agents, task)

        # Filter out failed results
        valid_results = [r for r in agent_results if "error" not in r.result]

        if not valid_results:
            return SwarmResult(
                task_id=task_id,
                task_description=task_description,
                final_result={"error": "All agents failed"},
                consensus=ConsensusResult(
                    reached_consensus=False,
                    consensus_value=None,
                    confidence=0,
                    supporting_agents=[],
                    dissenting_agents=[a.agent_id for a in agent_results],
                    vote_distribution={},
                    reasoning="All agents failed to produce results"
                ),
                agent_results=agent_results,
                conflicts_found=0,
                conflicts_resolved=0,
                execution_time=(datetime.now() - start_time).total_seconds(),
                confidence=0,
                coverage_score=0
            )

        # Detect conflicts
        conflicts = self._detect_conflicts(valid_results)

        # Build consensus
        consensus = self._build_consensus(valid_results)

        # Resolve conflicts
        resolved_conflicts = 0
        if conflicts and self.config.conflict_resolution != ConflictResolution.HUMAN_REVIEW:
            resolved_conflicts = self._resolve_conflicts(conflicts, valid_results)

        # Aggregate final result
        final_result = self._aggregate_results(valid_results, consensus)

        # Validate if required
        if self.config.require_validation:
            validators = [a for a in selected_agents if a.role == AgentRole.VALIDATOR]
            if validators:
                final_result = await self._validate_result(
                    final_result, validators[0], task
                )

        # Calculate coverage score
        coverage_score = self._calculate_coverage(valid_results)

        execution_time = (datetime.now() - start_time).total_seconds()

        result = SwarmResult(
            task_id=task_id,
            task_description=task_description,
            final_result=final_result,
            consensus=consensus,
            agent_results=agent_results,
            conflicts_found=len(conflicts),
            conflicts_resolved=resolved_conflicts,
            execution_time=execution_time,
            confidence=consensus.confidence,
            coverage_score=coverage_score
        )

        self.task_history.append(result)
        return result

    def _select_agents(
        self,
        agent_ids: Optional[List[str]],
        roles: Optional[List[AgentRole]]
    ) -> List[AgentWrapper]:
        """Select agents for execution."""
        selected = []

        for agent_id, agent in self.agents.items():
            if agent_ids and agent_id not in agent_ids:
                continue
            if roles and agent.role not in roles:
                continue
            selected.append(agent)

        # Limit to max agents
        return selected[:self.config.max_agents]

    async def _execute_parallel(
        self,
        agents: List[AgentWrapper],
        task: Dict[str, Any]
    ) -> List[AgentResult]:
        """Execute agents in parallel with timeout."""
        tasks = [agent.execute(task) for agent in agents]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.timeout_seconds
            )

            # Convert exceptions to error results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(AgentResult(
                        agent_id=agents[i].agent_id,
                        agent_role=agents[i].role,
                        result={"error": str(result)},
                        confidence=0,
                        execution_time=self.config.timeout_seconds
                    ))
                else:
                    final_results.append(result)

            return final_results

        except asyncio.TimeoutError:
            logger.warning(f"Swarm execution timed out after {self.config.timeout_seconds}s")
            return [
                AgentResult(
                    agent_id=agent.agent_id,
                    agent_role=agent.role,
                    result={"error": "timeout"},
                    confidence=0,
                    execution_time=self.config.timeout_seconds
                )
                for agent in agents
            ]

    def _detect_conflicts(self, results: List[AgentResult]) -> List[Dict[str, Any]]:
        """Detect conflicts between agent results."""
        conflicts = []

        # Group results by hash
        hash_groups: Dict[str, List[AgentResult]] = defaultdict(list)
        for result in results:
            hash_groups[result.result_hash].append(result)

        # If all hashes are different, check for specific conflicts
        if len(hash_groups) == len(results):
            # Check for numerical conflicts
            for key in self._get_common_keys(results):
                values = []
                for result in results:
                    value = result.result.get(key)
                    if isinstance(value, (int, float)):
                        values.append((result.agent_id, value))

                if len(values) >= 2:
                    all_values = [v for _, v in values]
                    if max(all_values) != 0:
                        variance = (max(all_values) - min(all_values)) / max(abs(v) for v in all_values)
                        if variance > 0.2:  # 20% variance
                            conflicts.append({
                                "key": key,
                                "type": "numerical",
                                "values": values,
                                "variance": variance
                            })

        return conflicts

    def _get_common_keys(self, results: List[AgentResult]) -> Set[str]:
        """Get keys present in all results."""
        if not results:
            return set()

        common = set(results[0].result.keys())
        for result in results[1:]:
            common = common & set(result.result.keys())

        return common

    def _build_consensus(self, results: List[AgentResult]) -> ConsensusResult:
        """Build consensus from agent results."""
        if not results:
            return ConsensusResult(
                reached_consensus=False,
                consensus_value=None,
                confidence=0,
                supporting_agents=[],
                dissenting_agents=[],
                vote_distribution={},
                reasoning="No results to build consensus"
            )

        strategy = self.config.consensus_strategy

        if strategy == ConsensusStrategy.MAJORITY_VOTE:
            return self._majority_vote(results)
        elif strategy == ConsensusStrategy.WEIGHTED_VOTE:
            return self._weighted_vote(results)
        elif strategy == ConsensusStrategy.BEST_CONFIDENCE:
            return self._best_confidence(results)
        elif strategy == ConsensusStrategy.AGGREGATION:
            return self._aggregation_consensus(results)
        else:
            return self._majority_vote(results)

    def _majority_vote(self, results: List[AgentResult]) -> ConsensusResult:
        """Simple majority voting."""
        votes: Dict[str, List[str]] = defaultdict(list)

        for result in results:
            votes[result.result_hash].append(result.agent_id)

        # Find majority
        sorted_votes = sorted(votes.items(), key=lambda x: len(x[1]), reverse=True)
        winner_hash, supporters = sorted_votes[0]

        # Find winning result
        winner_result = next(r for r in results if r.result_hash == winner_hash)

        # Check if majority achieved
        majority = len(supporters) > len(results) / 2

        dissenting = [r.agent_id for r in results if r.result_hash != winner_hash]

        return ConsensusResult(
            reached_consensus=majority,
            consensus_value=winner_result.result,
            confidence=len(supporters) / len(results),
            supporting_agents=supporters,
            dissenting_agents=dissenting,
            vote_distribution={h: len(v) for h, v in votes.items()},
            reasoning=f"Majority vote: {len(supporters)}/{len(results)} agents agreed"
        )

    def _weighted_vote(self, results: List[AgentResult]) -> ConsensusResult:
        """Confidence-weighted voting."""
        weighted_votes: Dict[str, float] = defaultdict(float)
        vote_agents: Dict[str, List[str]] = defaultdict(list)

        for result in results:
            agent = self.agents.get(result.agent_id)
            weight = agent.weight if agent else 1.0
            weighted_votes[result.result_hash] += result.confidence * weight
            vote_agents[result.result_hash].append(result.agent_id)

        # Find winner
        sorted_votes = sorted(weighted_votes.items(), key=lambda x: x[1], reverse=True)
        winner_hash, winner_weight = sorted_votes[0]

        total_weight = sum(weighted_votes.values())
        winner_result = next(r for r in results if r.result_hash == winner_hash)

        supporters = vote_agents[winner_hash]
        dissenting = [r.agent_id for r in results if r.result_hash != winner_hash]

        return ConsensusResult(
            reached_consensus=winner_weight / total_weight > 0.5,
            consensus_value=winner_result.result,
            confidence=winner_weight / total_weight,
            supporting_agents=supporters,
            dissenting_agents=dissenting,
            vote_distribution={h: w for h, w in weighted_votes.items()},
            reasoning=f"Weighted vote: {winner_weight:.2f}/{total_weight:.2f} weight for winner"
        )

    def _best_confidence(self, results: List[AgentResult]) -> ConsensusResult:
        """Select result with highest confidence."""
        best = max(results, key=lambda r: r.confidence)

        return ConsensusResult(
            reached_consensus=best.confidence >= self.config.confidence_threshold,
            consensus_value=best.result,
            confidence=best.confidence,
            supporting_agents=[best.agent_id],
            dissenting_agents=[r.agent_id for r in results if r != best],
            vote_distribution={best.result_hash: 1},
            reasoning=f"Best confidence: {best.agent_id} with {best.confidence:.2f}"
        )

    def _aggregation_consensus(self, results: List[AgentResult]) -> ConsensusResult:
        """Aggregate all results."""
        aggregated = self._aggregate_results(results, None)

        avg_confidence = statistics.mean(r.confidence for r in results)

        return ConsensusResult(
            reached_consensus=True,
            consensus_value=aggregated,
            confidence=avg_confidence,
            supporting_agents=[r.agent_id for r in results],
            dissenting_agents=[],
            vote_distribution={"aggregated": len(results)},
            reasoning=f"Aggregated {len(results)} agent results"
        )

    def _resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
        results: List[AgentResult]
    ) -> int:
        """Resolve detected conflicts."""
        resolved = 0

        for conflict in conflicts:
            if self.config.conflict_resolution == ConflictResolution.HIGHEST_CONFIDENCE:
                # Find agent with highest confidence
                best_agent = max(
                    [r for r in results],
                    key=lambda r: r.confidence
                )
                conflict["resolved_value"] = best_agent.result.get(conflict["key"])
                resolved += 1

            elif self.config.conflict_resolution == ConflictResolution.WEIGHTED_MERGE:
                # Weighted average for numerical conflicts
                if conflict["type"] == "numerical":
                    values = conflict["values"]
                    total_weight = 0
                    weighted_sum = 0

                    for agent_id, value in values:
                        agent = self.agents.get(agent_id)
                        weight = agent.weight if agent else 1.0
                        weighted_sum += value * weight
                        total_weight += weight

                    conflict["resolved_value"] = weighted_sum / total_weight
                    resolved += 1

        return resolved

    def _aggregate_results(
        self,
        results: List[AgentResult],
        consensus: Optional[ConsensusResult]
    ) -> Dict[str, Any]:
        """Aggregate results from multiple agents."""
        if consensus and consensus.consensus_value:
            # Start with consensus value
            aggregated = dict(consensus.consensus_value)
        else:
            aggregated = {}

        # Collect all keys
        all_keys: Set[str] = set()
        for result in results:
            all_keys.update(result.result.keys())

        # Aggregate each key
        for key in all_keys:
            if key in aggregated:
                continue

            values = []
            for result in results:
                if key in result.result:
                    values.append((result.result[key], result.confidence))

            if not values:
                continue

            # Select best value by confidence
            best_value, _ = max(values, key=lambda x: x[1])
            aggregated[key] = best_value

        return aggregated

    async def _validate_result(
        self,
        result: Dict[str, Any],
        validator: AgentWrapper,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate result using validator agent."""
        validation_task = {
            **task,
            "result_to_validate": result,
            "validation_mode": True
        }

        validation_result = await validator.execute(validation_task)

        if validation_result.confidence >= self.config.confidence_threshold:
            result["validated"] = True
            result["validation_confidence"] = validation_result.confidence
        else:
            result["validated"] = False
            result["validation_issues"] = validation_result.result.get("issues", [])

        return result

    def _calculate_coverage(self, results: List[AgentResult]) -> float:
        """Calculate how much of the task was covered."""
        all_keys: Set[str] = set()
        key_coverage: Dict[str, int] = defaultdict(int)

        for result in results:
            for key in result.result.keys():
                all_keys.add(key)
                key_coverage[key] += 1

        if not all_keys:
            return 0.0

        # Coverage = (average key coverage) / (number of agents)
        avg_coverage = sum(key_coverage.values()) / len(all_keys)
        return avg_coverage / len(results)

    def get_swarm_stats(self) -> Dict[str, Any]:
        """Get swarm performance statistics."""
        if not self.task_history:
            return {"tasks_executed": 0}

        return {
            "tasks_executed": len(self.task_history),
            "avg_execution_time": statistics.mean(t.execution_time for t in self.task_history),
            "avg_confidence": statistics.mean(t.confidence for t in self.task_history),
            "consensus_rate": sum(1 for t in self.task_history if t.consensus.reached_consensus) / len(self.task_history),
            "avg_conflicts": statistics.mean(t.conflicts_found for t in self.task_history),
            "agents": {
                agent_id: {
                    "role": agent.role.value,
                    "avg_execution_time": agent.avg_execution_time,
                    "weight": agent.weight
                }
                for agent_id, agent in self.agents.items()
            }
        }


def create_research_swarm() -> SwarmOrchestrator:
    """Create a swarm configured for research tasks."""
    config = SwarmConfig(
        min_agents=2,
        max_agents=5,
        timeout_seconds=180,
        consensus_strategy=ConsensusStrategy.WEIGHTED_VOTE,
        conflict_resolution=ConflictResolution.HIGHEST_CONFIDENCE,
        require_validation=True,
        confidence_threshold=0.7
    )
    return SwarmOrchestrator(config)


def create_analysis_swarm() -> SwarmOrchestrator:
    """Create a swarm configured for analysis tasks."""
    config = SwarmConfig(
        min_agents=3,
        max_agents=7,
        timeout_seconds=240,
        consensus_strategy=ConsensusStrategy.AGGREGATION,
        conflict_resolution=ConflictResolution.WEIGHTED_MERGE,
        require_validation=False,
        diversity_threshold=0.4
    )
    return SwarmOrchestrator(config)
