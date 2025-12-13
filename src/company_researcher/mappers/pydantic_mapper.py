"""
Pydantic Mapper - Analysis and conversion for Pydantic-based agents.

Supports:
- Pydantic model extraction
- Agent configuration from models
- Conversion to LangGraph
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from ..utils import get_logger

logger = get_logger(__name__)

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedEdge,
    MappedGraph,
    MappedNode,
    NodeType,
)


@dataclass
class PydanticAgent:
    """Representation of a Pydantic-based Agent."""
    name: str
    model_class: Optional[Type] = None
    fields: Dict[str, Any] = field(default_factory=dict)
    validators: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class PydanticMapper(BaseMapper):
    """
    Mapper for Pydantic-based agent patterns.

    Pydantic is often used for:
    - Agent configuration models
    - Structured output definitions
    - Input/output validation

    Usage:
        mapper = PydanticMapper()
        graph = mapper.analyze(MyAgentConfig)
        langgraph = mapper.to_langgraph(graph)
    """

    def __init__(self):
        super().__init__(FrameworkType.PYDANTIC)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze Pydantic source.

        Args:
            source: Pydantic BaseModel class or instance

        Returns:
            MappedGraph representation
        """
        if isinstance(source, list):
            agents = [self._extract_agent(s) for s in source]
        elif isinstance(source, type):
            agents = [self._extract_agent(source)]
        else:
            agents = [self._extract_agent(type(source))]

        return self._build_graph(agents)

    def _extract_agent(self, model_class: Type) -> PydanticAgent:
        """Extract agent information from Pydantic model."""
        # Get fields
        fields = {}
        try:
            if hasattr(model_class, 'model_fields'):
                # Pydantic v2
                for name, field_info in model_class.model_fields.items():
                    fields[name] = {
                        "type": str(field_info.annotation),
                        "required": field_info.is_required(),
                        "default": str(field_info.default) if field_info.default is not None else None
                    }
            elif hasattr(model_class, '__fields__'):
                # Pydantic v1
                for name, field_info in model_class.__fields__.items():
                    fields[name] = {
                        "type": str(field_info.outer_type_),
                        "required": field_info.required,
                        "default": str(field_info.default) if field_info.default is not None else None
                    }
        except Exception as e:
            logger.debug(f"Failed to extract Pydantic fields from {model_class.__name__}: {e}")

        # Get validators
        validators = []
        for name, method in inspect.getmembers(model_class, predicate=inspect.isfunction):
            if name.startswith('validate_') or hasattr(method, '__validator_config__'):
                validators.append(name)

        # Get methods
        methods = []
        for name, method in inspect.getmembers(model_class, predicate=inspect.isfunction):
            if not name.startswith('_') and name not in validators:
                methods.append(name)

        # Get config
        config = {}
        if hasattr(model_class, 'model_config'):
            config = dict(model_class.model_config)
        elif hasattr(model_class, 'Config'):
            config_class = model_class.Config
            config = {k: v for k, v in vars(config_class).items() if not k.startswith('_')}

        return PydanticAgent(
            name=model_class.__name__,
            model_class=model_class,
            fields=fields,
            validators=validators,
            methods=methods,
            config=config
        )

    def _build_graph(self, agents: List[PydanticAgent]) -> MappedGraph:
        """Build MappedGraph from Pydantic agents."""
        nodes = []
        edges = []

        for agent in agents:
            # Add main agent node
            agent_node = MappedNode(
                id=f"agent_{agent.name}",
                name=agent.name,
                node_type=NodeType.AGENT,
                framework=FrameworkType.PYDANTIC,
                config={
                    "fields": agent.fields,
                    "validators": agent.validators,
                    "pydantic_config": agent.config
                }
            )
            nodes.append(agent_node)

            # Add validator nodes
            for validator in agent.validators:
                val_node = MappedNode(
                    id=f"validator_{agent.name}_{validator}",
                    name=validator,
                    node_type=NodeType.CUSTOM,
                    framework=FrameworkType.PYDANTIC,
                    description=f"Validator for {agent.name}"
                )
                nodes.append(val_node)
                edges.append(MappedEdge(
                    source=agent_node.id,
                    target=val_node.id,
                    edge_type="validates"
                ))

            # Add method nodes for significant methods
            for method in agent.methods:
                if method not in ('dict', 'json', 'copy', 'schema'):
                    method_node = MappedNode(
                        id=f"method_{agent.name}_{method}",
                        name=method,
                        node_type=NodeType.TOOL,
                        framework=FrameworkType.PYDANTIC
                    )
                    nodes.append(method_node)
                    edges.append(MappedEdge(
                        source=agent_node.id,
                        target=method_node.id,
                        edge_type="method"
                    ))

        entry_point = nodes[0].id if nodes else None

        return MappedGraph(
            name="pydantic_workflow",
            framework=FrameworkType.PYDANTIC,
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

        class PydanticState(TypedDict):
            messages: Annotated[list, operator.add]
            validated_data: dict
            errors: list

        workflow = StateGraph(PydanticState)

        # Add agent nodes
        agent_nodes = [n for n in graph.nodes if n.node_type == NodeType.AGENT]

        for node in agent_nodes:
            def make_agent_node(agent_node: MappedNode):
                async def agent_func(state: PydanticState) -> PydanticState:
                    return {
                        "messages": [],
                        "validated_data": {},
                        "errors": []
                    }
                return agent_func

            workflow.add_node(node.id, make_agent_node(node))

        # Set entry point
        if agent_nodes:
            workflow.set_entry_point(agent_nodes[0].id)
            workflow.add_edge(agent_nodes[-1].id, END)

        return workflow


def map_pydantic_to_langgraph(
    model: Any,
    compile: bool = False
) -> Any:
    """
    Convenience function to map Pydantic model to LangGraph.

    Args:
        model: Pydantic BaseModel class or instance
        compile: Whether to compile the graph

    Returns:
        LangGraph StateGraph or CompiledGraph
    """
    mapper = PydanticMapper()
    graph = mapper.analyze(model)
    langgraph = mapper.to_langgraph(graph)

    if compile:
        return langgraph.compile()
    return langgraph
