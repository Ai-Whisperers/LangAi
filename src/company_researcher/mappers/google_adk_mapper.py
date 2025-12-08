"""
Google ADK Mapper - Analysis and conversion for Google Agent Development Kit.

Supports:
- Google ADK agent extraction
- Tool and function analysis
- Conversion to LangGraph
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedEdge,
    MappedGraph,
    MappedNode,
    NodeType,
)


@dataclass
class GoogleADKTool:
    """Representation of a Google ADK tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    function: Optional[Callable] = None


@dataclass
class GoogleADKAgent:
    """Representation of a Google ADK Agent."""
    name: str
    model: str = "gemini-pro"
    system_instruction: str = ""
    tools: List[GoogleADKTool] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class GoogleADKMapper(BaseMapper):
    """
    Mapper for Google Agent Development Kit.

    Usage:
        mapper = GoogleADKMapper()
        graph = mapper.analyze(adk_agent)
        langgraph = mapper.to_langgraph(graph)
    """

    def __init__(self):
        super().__init__(FrameworkType.GOOGLE_ADK)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze Google ADK source.

        Args:
            source: Google ADK Agent instance or config

        Returns:
            MappedGraph representation
        """
        if isinstance(source, list):
            agents = [self._extract_agent(a) for a in source]
        else:
            agents = [self._extract_agent(source)]

        return self._build_graph(agents)

    def _extract_agent(self, agent: Any) -> GoogleADKAgent:
        """Extract agent information from Google ADK agent."""
        tools = []

        # Extract tools from agent
        for tool in getattr(agent, 'tools', []):
            if hasattr(tool, '__name__'):
                tools.append(GoogleADKTool(
                    name=tool.__name__,
                    description=inspect.getdoc(tool) or '',
                    function=tool
                ))
            elif hasattr(tool, 'name'):
                tools.append(GoogleADKTool(
                    name=tool.name,
                    description=getattr(tool, 'description', ''),
                    parameters=getattr(tool, 'parameters', {})
                ))

        return GoogleADKAgent(
            name=getattr(agent, 'name', 'google_adk_agent'),
            model=getattr(agent, 'model', 'gemini-pro'),
            system_instruction=getattr(agent, 'system_instruction', ''),
            tools=tools,
            config=getattr(agent, 'config', {})
        )

    def _build_graph(self, agents: List[GoogleADKAgent]) -> MappedGraph:
        """Build MappedGraph from Google ADK agents."""
        nodes = []
        edges = []

        for agent in agents:
            # Add agent node
            agent_node = MappedNode(
                id=f"agent_{agent.name}",
                name=agent.name,
                node_type=NodeType.AGENT,
                framework=FrameworkType.GOOGLE_ADK,
                description=agent.system_instruction,
                tools=[t.name for t in agent.tools],
                config={"model": agent.model}
            )
            nodes.append(agent_node)

            # Add tool nodes
            for tool in agent.tools:
                tool_node = MappedNode(
                    id=f"tool_{tool.name}",
                    name=tool.name,
                    node_type=NodeType.TOOL,
                    framework=FrameworkType.GOOGLE_ADK,
                    description=tool.description,
                    function=tool.function,
                    config={"parameters": tool.parameters}
                )
                nodes.append(tool_node)

                # Edge from agent to tool
                edges.append(MappedEdge(
                    source=agent_node.id,
                    target=tool_node.id,
                    edge_type="tool_call"
                ))

        entry_point = nodes[0].id if nodes else None

        return MappedGraph(
            name="google_adk_workflow",
            framework=FrameworkType.GOOGLE_ADK,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=[]
        )

    def to_langgraph(self, graph: MappedGraph) -> Any:
        """Convert to LangGraph StateGraph."""
        try:
            from langgraph.graph import StateGraph, END
            from typing import TypedDict, Annotated
            import operator
        except ImportError:
            raise ImportError("langgraph is required for conversion")

        class ADKState(TypedDict):
            messages: Annotated[list, operator.add]
            tool_results: dict

        workflow = StateGraph(ADKState)

        # Add agent nodes
        agent_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]

        for node in agent_nodes:
            def make_agent_node(agent_node: MappedNode):
                async def agent_func(state: ADKState) -> ADKState:
                    return {
                        "messages": [{"role": "assistant", "content": f"Agent {agent_node.name}"}],
                        "tool_results": {}
                    }
                return agent_func

            workflow.add_node(node.id, make_agent_node(node))

        # Set entry point
        if agent_nodes:
            workflow.set_entry_point(agent_nodes[0].id)
            workflow.add_edge(agent_nodes[-1].id, END)

        return workflow


def map_google_adk_to_langgraph(
    agent: Any,
    compile: bool = False
) -> Any:
    """
    Convenience function to map Google ADK agent to LangGraph.

    Args:
        agent: Google ADK Agent
        compile: Whether to compile the graph

    Returns:
        LangGraph StateGraph or CompiledGraph
    """
    mapper = GoogleADKMapper()
    graph = mapper.analyze(agent)
    langgraph = mapper.to_langgraph(graph)

    if compile:
        return langgraph.compile()
    return langgraph
