"""
Unified Interface - Common interface across all agent frameworks.

Provides:
- Unified agent and workflow representations
- Cross-framework conversion
- Framework detection
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedGraph,
    MappedNode,
    NodeType,
)
from .crewai_mapper import CrewAIMapper
from .langgraph_mapper import LangGraphMapper
from .openai_agents_mapper import OpenAIAgentsMapper
from .swarm_mapper import SwarmMapper
from .pydantic_mapper import PydanticMapper


@dataclass
class UnifiedAgent:
    """
    Unified representation of an agent across frameworks.

    Provides a common interface regardless of source framework.
    """
    name: str
    role: str
    goal: str
    instructions: str = ""
    backstory: str = ""
    tools: List[str] = field(default_factory=list)
    source_framework: FrameworkType = FrameworkType.CUSTOM
    config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapped_node(cls, node: MappedNode) -> "UnifiedAgent":
        """Create from MappedNode."""
        return cls(
            name=node.name,
            role=node.role or node.name,
            goal=node.goal or "",
            instructions=node.description or "",
            backstory=node.backstory or "",
            tools=node.tools,
            source_framework=node.framework,
            config=node.config
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "instructions": self.instructions,
            "backstory": self.backstory,
            "tools": self.tools,
            "source_framework": self.source_framework.value,
            "config": self.config
        }


@dataclass
class UnifiedWorkflow:
    """
    Unified representation of a workflow across frameworks.

    Provides a common interface for workflow operations.
    """
    name: str
    agents: List[UnifiedAgent]
    graph: MappedGraph
    source_framework: FrameworkType
    config: Dict[str, Any] = field(default_factory=dict)

    @property
    def agent_count(self) -> int:
        """Number of agents in workflow."""
        return len(self.agents)

    @property
    def tool_count(self) -> int:
        """Number of tools across all agents."""
        return sum(len(a.tools) for a in self.agents)

    def get_agent(self, name: str) -> Optional[UnifiedAgent]:
        """Get agent by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None

    def get_tools(self) -> List[str]:
        """Get all tools from all agents."""
        tools = []
        for agent in self.agents:
            tools.extend(agent.tools)
        return list(set(tools))

    def to_mermaid(self) -> str:
        """Generate Mermaid diagram."""
        return self.graph.to_mermaid()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "agents": [a.to_dict() for a in self.agents],
            "graph": self.graph.to_dict(),
            "source_framework": self.source_framework.value,
            "config": self.config,
            "statistics": {
                "agent_count": self.agent_count,
                "tool_count": self.tool_count
            }
        }

    def convert_to(self, target_framework: FrameworkType) -> Any:
        """
        Convert workflow to target framework.

        Args:
            target_framework: Target framework type

        Returns:
            Framework-specific workflow object
        """
        mapper = _get_mapper(target_framework)
        return mapper.to_langgraph(self.graph)


def _get_mapper(framework: FrameworkType) -> BaseMapper:
    """Get appropriate mapper for framework."""
    mappers = {
        FrameworkType.LANGGRAPH: LangGraphMapper,
        FrameworkType.CREWAI: CrewAIMapper,
        FrameworkType.OPENAI_AGENTS: OpenAIAgentsMapper,
        FrameworkType.SWARM: SwarmMapper,
        FrameworkType.PYDANTIC: PydanticMapper,
    }

    mapper_class = mappers.get(framework)
    if mapper_class is None:
        raise ValueError(f"No mapper available for framework: {framework}")

    return mapper_class()


def detect_framework(source: Any) -> FrameworkType:
    """
    Detect the framework of a source object.

    Args:
        source: Agent, workflow, or code to analyze

    Returns:
        Detected FrameworkType
    """
    # Check for LangGraph
    if hasattr(source, 'get_graph') or hasattr(source, 'nodes') and hasattr(source, 'edges'):
        return FrameworkType.LANGGRAPH

    # Check for CrewAI
    if hasattr(source, 'agents') and hasattr(source, 'tasks'):
        return FrameworkType.CREWAI

    # Check for class with CrewBase-like decorators
    if isinstance(source, type):
        for name, method in vars(source).items():
            if hasattr(method, '_agent_config') or hasattr(method, '_task_config'):
                return FrameworkType.CREWAI

    # Check for Swarm
    if hasattr(source, 'functions') and hasattr(source, 'instructions'):
        return FrameworkType.SWARM

    # Check for OpenAI Agents
    if hasattr(source, 'handoffs') or (hasattr(source, 'tools') and hasattr(source, 'instructions')):
        return FrameworkType.OPENAI_AGENTS

    # Check for Pydantic
    try:
        from pydantic import BaseModel
        if isinstance(source, type) and issubclass(source, BaseModel):
            return FrameworkType.PYDANTIC
        if hasattr(source, 'model_fields') or hasattr(source, '__fields__'):
            return FrameworkType.PYDANTIC
    except ImportError:
        pass

    return FrameworkType.CUSTOM


def create_unified_workflow(
    source: Any,
    name: Optional[str] = None,
    framework: Optional[FrameworkType] = None
) -> UnifiedWorkflow:
    """
    Create a UnifiedWorkflow from any framework source.

    Args:
        source: Framework-specific source (agent, workflow, code)
        name: Optional workflow name
        framework: Optional framework type (auto-detected if not provided)

    Returns:
        UnifiedWorkflow instance

    Example:
        # From CrewAI
        workflow = create_unified_workflow(my_crew)

        # From LangGraph
        workflow = create_unified_workflow(my_graph)

        # From OpenAI Agents
        workflow = create_unified_workflow([agent1, agent2])
    """
    # Detect framework if not provided
    if framework is None:
        framework = detect_framework(source)

    # Get appropriate mapper
    mapper = _get_mapper(framework)

    # Analyze source
    graph = mapper.analyze(source)

    # Extract agents
    agents = []
    for node in graph.nodes:
        if node.node_type == NodeType.AGENT:
            agents.append(UnifiedAgent.from_mapped_node(node))

    # Create unified workflow
    return UnifiedWorkflow(
        name=name or graph.name,
        agents=agents,
        graph=graph,
        source_framework=framework,
        config=graph.config
    )


def convert_workflow(
    source: Any,
    target_framework: FrameworkType,
    compile: bool = False
) -> Any:
    """
    Convert a workflow from one framework to another.

    Args:
        source: Source workflow or agent
        target_framework: Target framework
        compile: Whether to compile the result (for LangGraph)

    Returns:
        Framework-specific workflow object

    Example:
        # Convert CrewAI to LangGraph
        langgraph = convert_workflow(my_crew, FrameworkType.LANGGRAPH)

        # Convert Swarm to LangGraph
        langgraph = convert_workflow(swarm_agents, FrameworkType.LANGGRAPH)
    """
    # Create unified workflow
    unified = create_unified_workflow(source)

    # Get target mapper
    target_mapper = _get_mapper(target_framework)

    # Convert
    result = target_mapper.to_langgraph(unified.graph)

    if compile and hasattr(result, 'compile'):
        return result.compile()

    return result


def compare_workflows(
    workflow1: UnifiedWorkflow,
    workflow2: UnifiedWorkflow
) -> Dict[str, Any]:
    """
    Compare two unified workflows.

    Returns:
        Comparison dictionary with differences
    """
    comparison = {
        "frameworks": {
            "workflow1": workflow1.source_framework.value,
            "workflow2": workflow2.source_framework.value
        },
        "agent_comparison": {
            "workflow1_count": workflow1.agent_count,
            "workflow2_count": workflow2.agent_count,
            "common_agents": [],
            "unique_to_workflow1": [],
            "unique_to_workflow2": []
        },
        "tool_comparison": {
            "workflow1_tools": workflow1.get_tools(),
            "workflow2_tools": workflow2.get_tools(),
            "common_tools": [],
            "unique_to_workflow1": [],
            "unique_to_workflow2": []
        }
    }

    # Compare agents
    agents1 = {a.name for a in workflow1.agents}
    agents2 = {a.name for a in workflow2.agents}
    comparison["agent_comparison"]["common_agents"] = list(agents1 & agents2)
    comparison["agent_comparison"]["unique_to_workflow1"] = list(agents1 - agents2)
    comparison["agent_comparison"]["unique_to_workflow2"] = list(agents2 - agents1)

    # Compare tools
    tools1 = set(workflow1.get_tools())
    tools2 = set(workflow2.get_tools())
    comparison["tool_comparison"]["common_tools"] = list(tools1 & tools2)
    comparison["tool_comparison"]["unique_to_workflow1"] = list(tools1 - tools2)
    comparison["tool_comparison"]["unique_to_workflow2"] = list(tools2 - tools1)

    return comparison
