"""
OpenAI Agents Mapper - Analysis and conversion for OpenAI Agents SDK.

Supports:
- Agent and tool extraction
- Function definitions
- Conversion to LangGraph
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedEdge,
    MappedGraph,
    MappedNode,
    NodeType,
)


@dataclass
class OpenAITool:
    """Representation of an OpenAI Agent tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    function: Optional[Callable] = None


@dataclass
class OpenAIAgent:
    """Representation of an OpenAI Agent."""
    name: str
    instructions: str
    model: str = "gpt-4"
    tools: List[OpenAITool] = field(default_factory=list)
    handoffs: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class OpenAIAgentsMapper(BaseMapper):
    """
    Mapper for OpenAI Agents SDK.

    Usage:
        mapper = OpenAIAgentsMapper()
        graph = mapper.analyze(agent)
        langgraph = mapper.to_langgraph(graph)
    """

    def __init__(self):
        super().__init__(FrameworkType.OPENAI_AGENTS)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze OpenAI Agent source.

        Args:
            source: OpenAI Agent instance or list of agents

        Returns:
            MappedGraph representation
        """
        if isinstance(source, list):
            agents = [self._extract_agent(a) for a in source]
        else:
            agents = [self._extract_agent(source)]

        return self._build_graph(agents)

    def _extract_agent(self, agent: Any) -> OpenAIAgent:
        """Extract agent information."""
        # Get tools
        tools = []
        for tool in getattr(agent, 'tools', []):
            if hasattr(tool, 'name'):
                tools.append(OpenAITool(
                    name=tool.name,
                    description=getattr(tool, 'description', ''),
                    parameters=getattr(tool, 'parameters', {}),
                    function=getattr(tool, 'function', None)
                ))
            elif callable(tool):
                tools.append(OpenAITool(
                    name=getattr(tool, '__name__', 'unknown'),
                    description=inspect.getdoc(tool) or '',
                    function=tool
                ))

        # Get handoffs
        handoffs = []
        for handoff in getattr(agent, 'handoffs', []):
            if hasattr(handoff, 'name'):
                handoffs.append(handoff.name)
            elif isinstance(handoff, str):
                handoffs.append(handoff)

        return OpenAIAgent(
            name=getattr(agent, 'name', 'agent'),
            instructions=getattr(agent, 'instructions', ''),
            model=getattr(agent, 'model', 'gpt-4'),
            tools=tools,
            handoffs=handoffs
        )

    def _build_graph(self, agents: List[OpenAIAgent]) -> MappedGraph:
        """Build MappedGraph from agents."""
        nodes = []
        edges = []

        for agent in agents:
            # Add agent node
            agent_node = MappedNode(
                id=f"agent_{agent.name}",
                name=agent.name,
                node_type=NodeType.AGENT,
                framework=FrameworkType.OPENAI_AGENTS,
                description=agent.instructions,
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
                    framework=FrameworkType.OPENAI_AGENTS,
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

            # Add handoff edges
            for handoff in agent.handoffs:
                edges.append(MappedEdge(
                    source=agent_node.id,
                    target=f"agent_{handoff}",
                    edge_type="handoff"
                ))

        entry_point = nodes[0].id if nodes else None

        return MappedGraph(
            name="openai_agents_workflow",
            framework=FrameworkType.OPENAI_AGENTS,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=[]
        )

    def to_langgraph(self, graph: MappedGraph) -> Any:
        """Convert to LangGraph StateGraph."""
        try:
            from langgraph.graph import StateGraph, END
            from langgraph.prebuilt import ToolNode
            from typing import TypedDict, Annotated
            import operator
        except ImportError:
            raise ImportError("langgraph is required for conversion")

        class AgentState(TypedDict):
            messages: Annotated[list, operator.add]
            current_agent: str

        workflow = StateGraph(AgentState)

        # Add agent nodes
        agent_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]

        for node in agent_nodes:
            def make_agent_node(agent_node: MappedNode):
                async def agent_func(state: AgentState) -> AgentState:
                    return {
                        "messages": [{"role": "assistant", "content": f"Agent {agent_node.name} response"}],
                        "current_agent": agent_node.name
                    }
                return agent_func

            workflow.add_node(node.id, make_agent_node(node))

        # Add tool node if there are tools
        tool_nodes = [n for n in graph.nodes if n.node_type == NodeType.TOOL]
        if tool_nodes:
            tools = [n.function for n in tool_nodes if n.function]
            if tools:
                workflow.add_node("tools", ToolNode(tools))

        # Set entry point
        if agent_nodes:
            workflow.set_entry_point(agent_nodes[0].id)

        # Add edges
        for edge in graph.edges:
            if edge.edge_type == "handoff":
                workflow.add_edge(edge.source, edge.target)

        # Add edge to END for last agent
        if agent_nodes:
            workflow.add_edge(agent_nodes[-1].id, END)

        return workflow


def map_openai_to_langgraph(
    agent: Any,
    compile: bool = False
) -> Any:
    """
    Convenience function to map OpenAI Agent to LangGraph.

    Args:
        agent: OpenAI Agent or list of agents
        compile: Whether to compile the graph

    Returns:
        LangGraph StateGraph or CompiledGraph
    """
    mapper = OpenAIAgentsMapper()
    graph = mapper.analyze(agent)
    langgraph = mapper.to_langgraph(graph)

    if compile:
        return langgraph.compile()
    return langgraph
