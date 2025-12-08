"""
Base Mapper - Foundation for framework mappers.

Provides common types and base class for all framework mappers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type


class FrameworkType(str, Enum):
    """Supported agent frameworks."""
    LANGGRAPH = "langgraph"
    CREWAI = "crewai"
    OPENAI_AGENTS = "openai_agents"
    SWARM = "swarm"
    PYDANTIC = "pydantic"
    GOOGLE_ADK = "google_adk"
    MCP = "mcp"
    AUTOGEN = "autogen"
    CUSTOM = "custom"


class NodeType(str, Enum):
    """Types of nodes in agent graphs."""
    AGENT = "agent"
    TASK = "task"
    TOOL = "tool"
    ROUTER = "router"
    CONDITIONAL = "conditional"
    ENTRY = "entry"
    EXIT = "exit"
    SUBGRAPH = "subgraph"
    CUSTOM = "custom"


@dataclass
class MappedNode:
    """
    Unified representation of a node in any agent framework.

    This abstraction allows converting between different frameworks.
    """
    id: str
    name: str
    node_type: NodeType
    framework: FrameworkType

    # Function/callable info
    function: Optional[Callable] = None
    function_name: Optional[str] = None
    docstring: Optional[str] = None

    # Agent-specific
    role: Optional[str] = None
    goal: Optional[str] = None
    backstory: Optional[str] = None
    tools: List[str] = field(default_factory=list)

    # Task-specific
    description: Optional[str] = None
    expected_output: Optional[str] = None
    context: List[str] = field(default_factory=list)

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Source location
    source_file: Optional[str] = None
    source_line: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "framework": self.framework.value,
            "function_name": self.function_name,
            "docstring": self.docstring,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "tools": self.tools,
            "description": self.description,
            "expected_output": self.expected_output,
            "context": self.context,
            "config": self.config,
            "metadata": self.metadata,
            "source_file": self.source_file,
            "source_line": self.source_line
        }


@dataclass
class MappedEdge:
    """
    Unified representation of an edge between nodes.
    """
    source: str
    target: str
    edge_type: str = "default"  # "default", "conditional", "loop"

    # Conditional edge info
    condition: Optional[str] = None
    condition_function: Optional[Callable] = None

    # Routing info
    route_map: Dict[str, str] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "condition": self.condition,
            "route_map": self.route_map,
            "metadata": self.metadata
        }


@dataclass
class MappedGraph:
    """
    Unified representation of an agent workflow graph.
    """
    name: str
    framework: FrameworkType
    nodes: List[MappedNode] = field(default_factory=list)
    edges: List[MappedEdge] = field(default_factory=list)

    # Entry/exit points
    entry_point: Optional[str] = None
    exit_points: List[str] = field(default_factory=list)

    # State schema
    state_schema: Optional[Type] = None
    state_fields: Dict[str, Any] = field(default_factory=dict)

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Analysis timestamp
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

    def get_node(self, node_id: str) -> Optional[MappedNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_edges_from(self, node_id: str) -> List[MappedEdge]:
        """Get all edges from a node."""
        return [e for e in self.edges if e.source == node_id]

    def get_edges_to(self, node_id: str) -> List[MappedEdge]:
        """Get all edges to a node."""
        return [e for e in self.edges if e.target == node_id]

    def get_node_types(self) -> Dict[NodeType, int]:
        """Count nodes by type."""
        counts: Dict[NodeType, int] = {}
        for node in self.nodes:
            counts[node.node_type] = counts.get(node.node_type, 0) + 1
        return counts

    def get_agent_nodes(self) -> List[MappedNode]:
        """Get all agent nodes."""
        return [n for n in self.nodes if n.node_type == NodeType.AGENT]

    def get_tool_nodes(self) -> List[MappedNode]:
        """Get all tool nodes."""
        return [n for n in self.nodes if n.node_type == NodeType.TOOL]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "framework": self.framework.value,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "entry_point": self.entry_point,
            "exit_points": self.exit_points,
            "state_fields": self.state_fields,
            "config": self.config,
            "metadata": self.metadata,
            "analyzed_at": self.analyzed_at.isoformat(),
            "node_counts": {k.value: v for k, v in self.get_node_types().items()}
        }

    def to_mermaid(self) -> str:
        """Generate Mermaid diagram syntax."""
        lines = ["graph TD"]

        # Add nodes
        for node in self.nodes:
            shape = self._mermaid_shape(node.node_type)
            label = node.name or node.id
            lines.append(f"    {node.id}{shape[0]}{label}{shape[1]}")

        # Add edges
        for edge in self.edges:
            if edge.edge_type == "conditional":
                label = edge.condition or ""
                lines.append(f"    {edge.source} -->|{label}| {edge.target}")
            else:
                lines.append(f"    {edge.source} --> {edge.target}")

        return "\n".join(lines)

    def _mermaid_shape(self, node_type: NodeType) -> tuple:
        """Get Mermaid shape for node type."""
        shapes = {
            NodeType.AGENT: ("[", "]"),
            NodeType.TASK: ("[[", "]]"),
            NodeType.TOOL: ("((", "))"),
            NodeType.ROUTER: ("{", "}"),
            NodeType.CONDITIONAL: ("{{", "}}"),
            NodeType.ENTRY: ("([", "])"),
            NodeType.EXIT: ("([", "])"),
            NodeType.SUBGRAPH: ("[/", "/]"),
            NodeType.CUSTOM: ("[", "]")
        }
        return shapes.get(node_type, ("[", "]"))


class BaseMapper(ABC):
    """
    Base class for framework mappers.

    Subclasses implement framework-specific analysis and conversion.
    """

    def __init__(self, framework: FrameworkType):
        self.framework = framework

    @abstractmethod
    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze source (code, object, file) and create MappedGraph.

        Args:
            source: Framework-specific source to analyze

        Returns:
            MappedGraph representation
        """
        pass

    @abstractmethod
    def to_langgraph(self, graph: MappedGraph) -> Any:
        """
        Convert MappedGraph to LangGraph workflow.

        Args:
            graph: MappedGraph to convert

        Returns:
            LangGraph StateGraph or CompiledGraph
        """
        pass

    def validate(self, graph: MappedGraph) -> List[str]:
        """
        Validate a mapped graph for common issues.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check for entry point
        if not graph.entry_point:
            errors.append("Graph has no entry point defined")

        # Check for orphan nodes
        connected_nodes = set()
        for edge in graph.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)

        for node in graph.nodes:
            if node.id not in connected_nodes:
                if node.id != graph.entry_point:
                    errors.append(f"Node '{node.id}' is not connected to any edges")

        # Check for missing edge targets
        node_ids = {n.id for n in graph.nodes}
        for edge in graph.edges:
            if edge.source not in node_ids:
                errors.append(f"Edge source '{edge.source}' not found in nodes")
            if edge.target not in node_ids and edge.target not in ("END", "__end__"):
                errors.append(f"Edge target '{edge.target}' not found in nodes")

        return errors

    def get_statistics(self, graph: MappedGraph) -> Dict[str, Any]:
        """Get statistics about the graph."""
        return {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "node_types": {k.value: v for k, v in graph.get_node_types().items()},
            "agent_count": len(graph.get_agent_nodes()),
            "tool_count": len(graph.get_tool_nodes()),
            "has_entry": graph.entry_point is not None,
            "exit_count": len(graph.exit_points),
            "conditional_edges": len([e for e in graph.edges if e.edge_type == "conditional"])
        }
