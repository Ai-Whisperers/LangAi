"""
LangGraph Mapper - Analysis of LangGraph workflows.

Provides:
- Graph structure analysis
- Node and edge extraction
- State schema extraction
- Visualization support
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedEdge,
    MappedGraph,
    MappedNode,
    NodeType,
)


@dataclass
class LangGraphNode:
    """Representation of a LangGraph node."""
    name: str
    function: Optional[Callable] = None
    function_name: Optional[str] = None
    docstring: Optional[str] = None
    is_async: bool = False
    source_file: Optional[str] = None
    source_line: Optional[int] = None


@dataclass
class LangGraphEdge:
    """Representation of a LangGraph edge."""
    source: str
    target: str
    is_conditional: bool = False
    condition_function: Optional[Callable] = None
    route_map: Dict[str, str] = field(default_factory=dict)


@dataclass
class LangGraphState:
    """Representation of LangGraph state schema."""
    schema_class: Optional[Type] = None
    fields: Dict[str, Any] = field(default_factory=dict)
    reducers: Dict[str, str] = field(default_factory=dict)


class LangGraphMapper(BaseMapper):
    """
    Mapper for LangGraph framework.

    Usage:
        mapper = LangGraphMapper()

        # Analyze compiled graph
        analysis = mapper.analyze(compiled_graph)

        # Get statistics
        stats = mapper.get_statistics(analysis)

        # Generate visualization
        mermaid = analysis.to_mermaid()
    """

    def __init__(self):
        super().__init__(FrameworkType.LANGGRAPH)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze LangGraph source.

        Args:
            source: Compiled LangGraph or StateGraph

        Returns:
            MappedGraph representation
        """
        # Handle compiled graph
        if hasattr(source, 'get_graph'):
            return self._analyze_compiled(source)
        # Handle StateGraph
        elif hasattr(source, 'nodes') and hasattr(source, 'edges'):
            return self._analyze_state_graph(source)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def _analyze_compiled(self, compiled_graph: Any) -> MappedGraph:
        """Analyze compiled LangGraph."""
        nodes = []
        edges = []

        # Get graph structure
        graph_dict = compiled_graph.get_graph()

        # Extract nodes
        for node_data in graph_dict.get('nodes', []):
            node_id = node_data.get('id', str(len(nodes)))
            node_name = node_data.get('name', node_id)

            node_type = NodeType.CUSTOM
            if node_name == "__start__":
                node_type = NodeType.ENTRY
            elif node_name == "__end__":
                node_type = NodeType.EXIT
            elif "router" in node_name.lower():
                node_type = NodeType.ROUTER

            nodes.append(MappedNode(
                id=node_id,
                name=node_name,
                node_type=node_type,
                framework=FrameworkType.LANGGRAPH,
                metadata=node_data.get('metadata', {})
            ))

        # Extract edges
        for edge_data in graph_dict.get('edges', []):
            source = edge_data.get('source', '')
            target = edge_data.get('target', '')
            conditional = edge_data.get('conditional', False)

            edges.append(MappedEdge(
                source=source,
                target=target,
                edge_type="conditional" if conditional else "default",
                metadata=edge_data.get('metadata', {})
            ))

        # Find entry and exit
        entry_point = None
        exit_points = []
        for node in nodes:
            if node.node_type == NodeType.ENTRY:
                entry_point = node.id
            elif node.node_type == NodeType.EXIT:
                exit_points.append(node.id)

        return MappedGraph(
            name=getattr(compiled_graph, 'name', 'langgraph'),
            framework=FrameworkType.LANGGRAPH,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=exit_points
        )

    def _analyze_state_graph(self, state_graph: Any) -> MappedGraph:
        """Analyze uncompiled StateGraph."""
        nodes = []
        edges = []

        # Extract nodes
        for node_name, node_func in getattr(state_graph, 'nodes', {}).items():
            # Get function info
            func_name = getattr(node_func, '__name__', str(node_func))
            docstring = inspect.getdoc(node_func) if callable(node_func) else None
            is_async = inspect.iscoroutinefunction(node_func)

            # Try to get source location
            source_file = None
            source_line = None
            try:
                source_file = inspect.getfile(node_func)
                source_line = inspect.getsourcelines(node_func)[1]
            except (TypeError, OSError):
                pass

            node_type = NodeType.CUSTOM
            if "agent" in node_name.lower():
                node_type = NodeType.AGENT
            elif "tool" in node_name.lower():
                node_type = NodeType.TOOL
            elif "router" in node_name.lower() or "route" in node_name.lower():
                node_type = NodeType.ROUTER

            nodes.append(MappedNode(
                id=node_name,
                name=node_name,
                node_type=node_type,
                framework=FrameworkType.LANGGRAPH,
                function=node_func if callable(node_func) else None,
                function_name=func_name,
                docstring=docstring,
                source_file=source_file,
                source_line=source_line,
                config={"is_async": is_async}
            ))

        # Extract edges
        for edge_data in getattr(state_graph, 'edges', []):
            if isinstance(edge_data, tuple) and len(edge_data) >= 2:
                source, target = edge_data[0], edge_data[1]
                edges.append(MappedEdge(
                    source=source,
                    target=target,
                    edge_type="default"
                ))

        # Extract conditional edges
        for source, edge_info in getattr(state_graph, 'conditional_edges', {}).items():
            if isinstance(edge_info, dict):
                for condition, target in edge_info.items():
                    edges.append(MappedEdge(
                        source=source,
                        target=target,
                        edge_type="conditional",
                        condition=str(condition)
                    ))

        # Extract state schema
        state_schema = getattr(state_graph, 'schema', None)
        state_fields = {}
        if state_schema:
            try:
                hints = get_type_hints(state_schema)
                state_fields = {k: str(v) for k, v in hints.items()}
            except Exception:
                pass

        # Get entry point
        entry_point = getattr(state_graph, 'entry_point', None)
        if not entry_point and nodes:
            entry_point = nodes[0].id

        return MappedGraph(
            name=getattr(state_graph, 'name', 'langgraph'),
            framework=FrameworkType.LANGGRAPH,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=["__end__"],
            state_schema=state_schema,
            state_fields=state_fields
        )

    def to_langgraph(self, graph: MappedGraph) -> Any:
        """
        Convert MappedGraph back to LangGraph (identity for LangGraph source).

        For non-LangGraph sources, creates a new StateGraph.
        """
        if graph.framework == FrameworkType.LANGGRAPH:
            # Already LangGraph, return as-is if we have the original
            return graph.metadata.get('original_graph')

        # Create new StateGraph
        try:
            from langgraph.graph import StateGraph, END
            from typing import TypedDict
        except ImportError:
            raise ImportError("langgraph is required for conversion")

        # Create minimal state
        class State(TypedDict):
            messages: list
            data: dict

        workflow = StateGraph(State)

        # Add nodes
        for node in graph.nodes:
            if node.node_type not in (NodeType.ENTRY, NodeType.EXIT):
                if node.function:
                    workflow.add_node(node.id, node.function)
                else:
                    # Create placeholder function
                    def make_placeholder(n):
                        async def placeholder(state):
                            return {"messages": [], "data": {n.id: "completed"}}
                        return placeholder
                    workflow.add_node(node.id, make_placeholder(node))

        # Add edges
        for edge in graph.edges:
            if edge.target in ("END", "__end__"):
                workflow.add_edge(edge.source, END)
            elif edge.edge_type == "default":
                workflow.add_edge(edge.source, edge.target)

        # Set entry point
        if graph.entry_point:
            workflow.set_entry_point(graph.entry_point)

        return workflow


def analyze_langgraph(graph: Any) -> Dict[str, Any]:
    """
    Convenience function to analyze a LangGraph.

    Args:
        graph: LangGraph StateGraph or compiled graph

    Returns:
        Analysis dictionary with nodes, edges, stats
    """
    mapper = LangGraphMapper()
    mapped = mapper.analyze(graph)

    return {
        "graph": mapped.to_dict(),
        "statistics": mapper.get_statistics(mapped),
        "validation": mapper.validate(mapped),
        "mermaid": mapped.to_mermaid()
    }
