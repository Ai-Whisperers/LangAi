"""
Swarm Mapper - Analysis and conversion for OpenAI Swarm pattern.

Supports:
- Agent extraction with function-based routing
- Handoff patterns
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
class SwarmFunction:
    """Representation of a Swarm function."""
    name: str
    description: str
    function: Optional[Callable] = None
    returns_agent: bool = False  # True if function returns an agent handoff


@dataclass
class SwarmAgent:
    """Representation of a Swarm Agent."""
    name: str
    instructions: str
    functions: List[SwarmFunction] = field(default_factory=list)
    model: str = "gpt-4"


class SwarmMapper(BaseMapper):
    """
    Mapper for OpenAI Swarm pattern.

    The Swarm pattern uses lightweight agents with function-based routing.

    Usage:
        mapper = SwarmMapper()
        graph = mapper.analyze([triage_agent, sales_agent, support_agent])
        langgraph = mapper.to_langgraph(graph)
    """

    def __init__(self):
        super().__init__(FrameworkType.SWARM)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze Swarm agents.

        Args:
            source: Swarm Agent or list of agents

        Returns:
            MappedGraph representation
        """
        if isinstance(source, list):
            agents = [self._extract_agent(a) for a in source]
        else:
            agents = [self._extract_agent(source)]

        return self._build_graph(agents)

    def _extract_agent(self, agent: Any) -> SwarmAgent:
        """Extract agent information."""
        functions = []

        for func in getattr(agent, 'functions', []):
            # Check if function returns another agent
            returns_agent = False
            if callable(func):
                try:
                    hints = getattr(func, '__annotations__', {})
                    return_hint = hints.get('return', None)
                    if return_hint and 'Agent' in str(return_hint):
                        returns_agent = True
                except Exception:
                    pass

            functions.append(SwarmFunction(
                name=getattr(func, '__name__', 'unknown') if callable(func) else str(func),
                description=inspect.getdoc(func) if callable(func) else '',
                function=func if callable(func) else None,
                returns_agent=returns_agent
            ))

        return SwarmAgent(
            name=getattr(agent, 'name', 'agent'),
            instructions=getattr(agent, 'instructions', ''),
            functions=functions,
            model=getattr(agent, 'model', 'gpt-4')
        )

    def _build_graph(self, agents: List[SwarmAgent]) -> MappedGraph:
        """Build MappedGraph from Swarm agents."""
        nodes = []
        edges = []
        agent_names = {a.name for a in agents}

        for agent in agents:
            # Add agent node
            agent_node = MappedNode(
                id=f"agent_{agent.name}",
                name=agent.name,
                node_type=NodeType.AGENT,
                framework=FrameworkType.SWARM,
                description=agent.instructions,
                tools=[f.name for f in agent.functions],
                config={"model": agent.model}
            )
            nodes.append(agent_node)

            # Add function nodes and edges
            for func in agent.functions:
                func_node = MappedNode(
                    id=f"func_{agent.name}_{func.name}",
                    name=func.name,
                    node_type=NodeType.TOOL,
                    framework=FrameworkType.SWARM,
                    description=func.description,
                    function=func.function,
                    config={"returns_agent": func.returns_agent}
                )
                nodes.append(func_node)

                # Edge from agent to function
                edges.append(MappedEdge(
                    source=agent_node.id,
                    target=func_node.id,
                    edge_type="function_call"
                ))

                # If function returns agent, add potential handoff edges
                if func.returns_agent:
                    # Add edges to all other agents (runtime determines actual target)
                    for other_agent in agent_names:
                        if other_agent != agent.name:
                            edges.append(MappedEdge(
                                source=func_node.id,
                                target=f"agent_{other_agent}",
                                edge_type="conditional",
                                condition=f"handoff_to_{other_agent}"
                            ))

        # Determine entry point (first agent or triage agent)
        entry_point = None
        for node in nodes:
            if node.node_type == NodeType.AGENT:
                if 'triage' in node.name.lower():
                    entry_point = node.id
                    break
                if entry_point is None:
                    entry_point = node.id

        return MappedGraph(
            name="swarm_workflow",
            framework=FrameworkType.SWARM,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=[]
        )

    def to_langgraph(self, graph: MappedGraph) -> Any:
        """Convert to LangGraph StateGraph."""
        try:
            from langgraph.graph import StateGraph, END
            from typing import TypedDict, Annotated, Literal
            import operator
        except ImportError:
            raise ImportError("langgraph is required for conversion")

        class SwarmState(TypedDict):
            messages: Annotated[list, operator.add]
            current_agent: str
            handoff_to: str

        workflow = StateGraph(SwarmState)

        # Add agent nodes
        agent_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]
        agent_names = [n.name for n in agent_nodes]

        for node in agent_nodes:
            def make_agent_node(agent_node: MappedNode):
                async def agent_func(state: SwarmState) -> SwarmState:
                    # Agent logic - check for handoffs
                    return {
                        "messages": [{"role": "assistant", "content": f"Agent {agent_node.name}"}],
                        "current_agent": agent_node.name,
                        "handoff_to": ""
                    }
                return agent_func

            workflow.add_node(node.id, make_agent_node(node))

        # Add router node for handoff decisions
        def should_handoff(state: SwarmState) -> str:
            """Router function for handoffs."""
            if state.get("handoff_to"):
                return f"agent_{state['handoff_to']}"
            return END

        # Set entry point
        if agent_nodes:
            workflow.set_entry_point(agent_nodes[0].id)

            # Add conditional edges for handoffs
            for node in agent_nodes:
                route_map = {END: END}
                for other in agent_nodes:
                    if other.id != node.id:
                        route_map[other.id] = other.id

                workflow.add_conditional_edges(
                    node.id,
                    should_handoff,
                    route_map
                )

        return workflow


def map_swarm_to_langgraph(
    agents: Any,
    compile: bool = False
) -> Any:
    """
    Convenience function to map Swarm agents to LangGraph.

    Args:
        agents: Swarm Agent or list of agents
        compile: Whether to compile the graph

    Returns:
        LangGraph StateGraph or CompiledGraph
    """
    mapper = SwarmMapper()
    graph = mapper.analyze(agents)
    langgraph = mapper.to_langgraph(graph)

    if compile:
        return langgraph.compile()
    return langgraph
