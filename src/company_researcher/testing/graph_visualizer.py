"""
Graph Visualizer - Workflow visualization and export.

Provides:
- Mermaid diagram generation
- JSON export
- Interactive visualization
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class GraphNode:
    """Node in visualization graph."""

    id: str
    name: str
    node_type: str
    metadata: Dict[str, Any]


@dataclass
class GraphEdge:
    """Edge in visualization graph."""

    source: str
    target: str
    label: Optional[str] = None
    edge_type: str = "default"


class GraphVisualizer:
    """
    Visualize LangGraph and other workflow graphs.

    Usage:
        visualizer = GraphVisualizer()

        # From LangGraph
        visualizer.from_langgraph(compiled_graph)

        # Generate Mermaid
        mermaid = visualizer.to_mermaid()

        # Export to JSON
        visualizer.export_json("workflow.json")
    """

    def __init__(self):
        self.nodes: List[GraphNode] = []
        self.edges: List[GraphEdge] = []
        self.name = "workflow"

    def from_langgraph(self, graph: Any) -> "GraphVisualizer":
        """
        Load from LangGraph.

        Args:
            graph: Compiled LangGraph or StateGraph
        """
        self.nodes = []
        self.edges = []

        if hasattr(graph, "get_graph"):
            # Compiled graph
            graph_data = graph.get_graph()
            self._load_from_dict(graph_data)
        elif hasattr(graph, "nodes"):
            # StateGraph
            self._load_from_state_graph(graph)

        return self

    def _load_from_dict(self, graph_data: Dict[str, Any]) -> None:
        """Load from graph dictionary."""
        for node_data in graph_data.get("nodes", []):
            node_id = node_data.get("id", str(len(self.nodes)))
            self.nodes.append(
                GraphNode(
                    id=node_id,
                    name=node_data.get("name", node_id),
                    node_type=node_data.get("type", "default"),
                    metadata=node_data.get("metadata", {}),
                )
            )

        for edge_data in graph_data.get("edges", []):
            self.edges.append(
                GraphEdge(
                    source=edge_data.get("source", ""),
                    target=edge_data.get("target", ""),
                    label=edge_data.get("data", {}).get("label"),
                    edge_type="conditional" if edge_data.get("conditional") else "default",
                )
            )

    def _load_from_state_graph(self, graph: Any) -> None:
        """Load from StateGraph object."""
        # Add nodes
        for node_name in getattr(graph, "nodes", {}).keys():
            node_type = "agent" if "agent" in node_name.lower() else "default"
            self.nodes.append(
                GraphNode(id=node_name, name=node_name, node_type=node_type, metadata={})
            )

        # Add START and END
        self.nodes.insert(
            0, GraphNode(id="__start__", name="START", node_type="entry", metadata={})
        )
        self.nodes.append(GraphNode(id="__end__", name="END", node_type="exit", metadata={}))

        # Add edges
        for edge in getattr(graph, "edges", []):
            if isinstance(edge, tuple) and len(edge) >= 2:
                self.edges.append(GraphEdge(source=edge[0], target=edge[1]))

    def add_node(
        self, id: str, name: Optional[str] = None, node_type: str = "default", **metadata
    ) -> "GraphVisualizer":
        """Add a node to the graph."""
        self.nodes.append(GraphNode(id=id, name=name or id, node_type=node_type, metadata=metadata))
        return self

    def add_edge(
        self, source: str, target: str, label: Optional[str] = None, edge_type: str = "default"
    ) -> "GraphVisualizer":
        """Add an edge to the graph."""
        self.edges.append(GraphEdge(source=source, target=target, label=label, edge_type=edge_type))
        return self

    def to_mermaid(self, direction: str = "TD") -> str:
        """
        Generate Mermaid diagram syntax.

        Args:
            direction: Diagram direction (TD, LR, BT, RL)

        Returns:
            Mermaid diagram string
        """
        lines = [f"graph {direction}"]

        # Add styling
        lines.append("    %% Node styling")
        lines.append("    classDef agent fill:#e1f5fe,stroke:#01579b")
        lines.append("    classDef tool fill:#f3e5f5,stroke:#4a148c")
        lines.append("    classDef entry fill:#e8f5e9,stroke:#1b5e20")
        lines.append("    classDef exit fill:#ffebee,stroke:#b71c1c")
        lines.append("")

        # Add nodes
        for node in self.nodes:
            shape = self._get_mermaid_shape(node.node_type)
            escaped_name = node.name.replace('"', '\\"')
            lines.append(f'    {node.id}{shape[0]}"{escaped_name}"{shape[1]}')

        lines.append("")

        # Add edges
        for edge in self.edges:
            if edge.label:
                lines.append(f'    {edge.source} -->|"{edge.label}"| {edge.target}')
            elif edge.edge_type == "conditional":
                lines.append(f"    {edge.source} -.-> {edge.target}")
            else:
                lines.append(f"    {edge.source} --> {edge.target}")

        # Apply classes
        lines.append("")
        agent_nodes = [n.id for n in self.nodes if n.node_type == "agent"]
        tool_nodes = [n.id for n in self.nodes if n.node_type == "tool"]
        entry_nodes = [n.id for n in self.nodes if n.node_type == "entry"]
        exit_nodes = [n.id for n in self.nodes if n.node_type == "exit"]

        if agent_nodes:
            lines.append(f"    class {','.join(agent_nodes)} agent")
        if tool_nodes:
            lines.append(f"    class {','.join(tool_nodes)} tool")
        if entry_nodes:
            lines.append(f"    class {','.join(entry_nodes)} entry")
        if exit_nodes:
            lines.append(f"    class {','.join(exit_nodes)} exit")

        return "\n".join(lines)

    def _get_mermaid_shape(self, node_type: str) -> tuple[str, str]:
        """Get Mermaid shape delimiters for node type."""
        shapes = {
            "agent": ("[", "]"),
            "tool": ("((", "))"),
            "router": ("{", "}"),
            "conditional": ("{{", "}}"),
            "entry": ("([", "])"),
            "exit": ("([", "])"),
            "default": ("[", "]"),
        }
        return shapes.get(node_type, ("[", "]"))

    def to_json(self) -> Dict[str, Any]:
        """
        Export graph to JSON format.

        Returns:
            JSON-serializable dictionary
        """
        return {
            "name": self.name,
            "nodes": [
                {"id": n.id, "name": n.name, "type": n.node_type, "metadata": n.metadata}
                for n in self.nodes
            ],
            "edges": [
                {"source": e.source, "target": e.target, "label": e.label, "type": e.edge_type}
                for e in self.edges
            ],
        }

    def export_json(self, path: str) -> None:
        """Export graph to JSON file."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_json(), f, indent=2)

    def export_mermaid(self, path: str, direction: str = "TD") -> None:
        """Export graph to Mermaid file."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(self.to_mermaid(direction))

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        node_types: Dict[str, int] = {}
        for node in self.nodes:
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1

        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": node_types,
            "has_cycles": self._has_cycles(),
        }

    def _has_cycles(self) -> bool:
        """Check if graph has cycles."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        adj: Dict[str, List[str]] = {}
        for edge in self.edges:
            if edge.source not in adj:
                adj[edge.source] = []
            adj[edge.source].append(edge.target)

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node.id not in visited:
                if dfs(node.id):
                    return True
        return False


def visualize_workflow(graph: Any) -> str:
    """
    Convenience function to visualize a workflow.

    Args:
        graph: LangGraph or similar workflow

    Returns:
        Mermaid diagram string
    """
    visualizer = GraphVisualizer()
    visualizer.from_langgraph(graph)
    return visualizer.to_mermaid()


def export_to_mermaid(graph: Any, path: str) -> None:
    """Export workflow to Mermaid file."""
    visualizer = GraphVisualizer()
    visualizer.from_langgraph(graph)
    visualizer.export_mermaid(path)


def export_to_json(graph: Any, path: str) -> None:
    """Export workflow to JSON file."""
    visualizer = GraphVisualizer()
    visualizer.from_langgraph(graph)
    visualizer.export_json(path)
