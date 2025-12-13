"""
CrewAI Mapper - Analysis and conversion for CrewAI workflows.

Supports:
- AST-based analysis of CrewAI code
- Agent and Task extraction
- Conversion to LangGraph
"""

import ast
import inspect
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from .base_mapper import (
    BaseMapper,
    FrameworkType,
    MappedEdge,
    MappedGraph,
    MappedNode,
    NodeType,
)


@dataclass
class CrewAIAgent:
    """Representation of a CrewAI Agent."""
    name: str
    role: str
    goal: str
    backstory: str = ""
    tools: List[str] = field(default_factory=list)
    allow_delegation: bool = False
    verbose: bool = False
    llm: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrewAITask:
    """Representation of a CrewAI Task."""
    name: str
    description: str
    expected_output: str
    agent: str  # Agent name
    tools: List[str] = field(default_factory=list)
    context: List[str] = field(default_factory=list)  # Other task names
    async_execution: bool = False
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrewAICrew:
    """Representation of a CrewAI Crew."""
    name: str
    agents: List[CrewAIAgent] = field(default_factory=list)
    tasks: List[CrewAITask] = field(default_factory=list)
    process: str = "sequential"  # "sequential" or "hierarchical"
    verbose: bool = False
    config: Dict[str, Any] = field(default_factory=dict)


class CrewAIMapper(BaseMapper):
    """
    Mapper for CrewAI framework.

    Usage:
        mapper = CrewAIMapper()

        # Analyze from code
        graph = mapper.analyze_code(crew_code)

        # Analyze from object
        graph = mapper.analyze(crew_instance)

        # Convert to LangGraph
        langgraph = mapper.to_langgraph(graph)
    """

    def __init__(self):
        super().__init__(FrameworkType.CREWAI)

    def analyze(self, source: Any) -> MappedGraph:
        """
        Analyze CrewAI source.

        Args:
            source: CrewAI Crew instance, class, or code string

        Returns:
            MappedGraph representation
        """
        if isinstance(source, str):
            return self.analyze_code(source)
        elif hasattr(source, 'agents') and hasattr(source, 'tasks'):
            return self.analyze_crew(source)
        elif inspect.isclass(source):
            return self.analyze_class(source)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    def analyze_code(self, code: str) -> MappedGraph:
        """Analyze CrewAI code using AST."""
        tree = ast.parse(code)
        visitor = CrewAIASTVisitor()
        visitor.visit(tree)

        return self._build_graph(visitor.crew)

    def analyze_crew(self, crew: Any) -> MappedGraph:
        """Analyze CrewAI Crew instance."""
        # Extract agents
        agents = []
        for agent in getattr(crew, 'agents', []):
            agents.append(CrewAIAgent(
                name=getattr(agent, 'role', 'unknown'),
                role=getattr(agent, 'role', ''),
                goal=getattr(agent, 'goal', ''),
                backstory=getattr(agent, 'backstory', ''),
                tools=[str(t) for t in getattr(agent, 'tools', [])],
                allow_delegation=getattr(agent, 'allow_delegation', False),
                verbose=getattr(agent, 'verbose', False)
            ))

        # Extract tasks
        tasks = []
        for task in getattr(crew, 'tasks', []):
            agent_name = 'unknown'
            if hasattr(task, 'agent') and task.agent:
                agent_name = getattr(task.agent, 'role', 'unknown')

            tasks.append(CrewAITask(
                name=getattr(task, 'name', f"task_{len(tasks)}"),
                description=getattr(task, 'description', ''),
                expected_output=getattr(task, 'expected_output', ''),
                agent=agent_name,
                tools=[str(t) for t in getattr(task, 'tools', [])],
                async_execution=getattr(task, 'async_execution', False)
            ))

        crew_data = CrewAICrew(
            name=getattr(crew, '__class__', type(crew)).__name__,
            agents=agents,
            tasks=tasks,
            process=getattr(crew, 'process', 'sequential'),
            verbose=getattr(crew, 'verbose', False)
        )

        return self._build_graph(crew_data)

    def analyze_class(self, cls: Type) -> MappedGraph:
        """Analyze CrewAI class with decorators."""
        agents = []
        tasks = []

        # Look for @agent and @task decorated methods
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Check for agent decorator markers
            if hasattr(method, '_agent_config'):
                config = method._agent_config
                agents.append(CrewAIAgent(
                    name=name,
                    role=config.get('role', name),
                    goal=config.get('goal', ''),
                    backstory=config.get('backstory', ''),
                    tools=config.get('tools', [])
                ))

            # Check for task decorator markers
            if hasattr(method, '_task_config'):
                config = method._task_config
                tasks.append(CrewAITask(
                    name=name,
                    description=config.get('description', ''),
                    expected_output=config.get('expected_output', ''),
                    agent=config.get('agent', 'unknown'),
                    context=config.get('context', [])
                ))

        crew_data = CrewAICrew(
            name=cls.__name__,
            agents=agents,
            tasks=tasks
        )

        return self._build_graph(crew_data)

    def _build_graph(self, crew: CrewAICrew) -> MappedGraph:
        """Build MappedGraph from CrewAI data."""
        nodes = []
        edges = []

        # Add agent nodes
        for agent in crew.agents:
            nodes.append(MappedNode(
                id=f"agent_{agent.name}",
                name=agent.name,
                node_type=NodeType.AGENT,
                framework=FrameworkType.CREWAI,
                role=agent.role,
                goal=agent.goal,
                backstory=agent.backstory,
                tools=agent.tools,
                config={
                    "allow_delegation": agent.allow_delegation,
                    "verbose": agent.verbose,
                    "llm": agent.llm
                }
            ))

        # Add task nodes and edges
        prev_task_id = None
        for i, task in enumerate(crew.tasks):
            task_id = f"task_{task.name}"

            nodes.append(MappedNode(
                id=task_id,
                name=task.name,
                node_type=NodeType.TASK,
                framework=FrameworkType.CREWAI,
                description=task.description,
                expected_output=task.expected_output,
                tools=task.tools,
                context=task.context,
                config={
                    "agent": task.agent,
                    "async_execution": task.async_execution
                }
            ))

            # Add edge from agent to task
            agent_id = f"agent_{task.agent}"
            edges.append(MappedEdge(
                source=agent_id,
                target=task_id,
                edge_type="executes"
            ))

            # Add sequential edge between tasks
            if crew.process == "sequential" and prev_task_id:
                edges.append(MappedEdge(
                    source=prev_task_id,
                    target=task_id,
                    edge_type="default"
                ))

            # Add context edges
            for ctx_task in task.context:
                edges.append(MappedEdge(
                    source=f"task_{ctx_task}",
                    target=task_id,
                    edge_type="context"
                ))

            prev_task_id = task_id

        # Set entry and exit
        entry_point = nodes[0].id if nodes else None
        exit_points = [prev_task_id] if prev_task_id else []

        return MappedGraph(
            name=crew.name,
            framework=FrameworkType.CREWAI,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=exit_points,
            config={
                "process": crew.process,
                "verbose": crew.verbose
            }
        )

    def to_langgraph(self, graph: MappedGraph) -> Any:
        """
        Convert MappedGraph to LangGraph StateGraph.

        Returns:
            LangGraph StateGraph (not compiled)
        """
        try:
            from langgraph.graph import StateGraph, END
            from typing import TypedDict, Annotated
            import operator
        except ImportError:
            raise ImportError("langgraph is required for conversion")

        # Create state schema
        class CrewState(TypedDict):
            messages: Annotated[list, operator.add]
            task_results: dict
            current_task: str
            completed_tasks: list

        # Create graph
        workflow = StateGraph(CrewState)

        # Add nodes for each task
        task_nodes = [n for n in graph.nodes if n.node_type == NodeType.TASK]

        for node in task_nodes:
            # Create node function
            def make_task_node(task_node: MappedNode):
                async def task_func(state: CrewState) -> CrewState:
                    # This is a placeholder - actual implementation would
                    # invoke the agent and tool calls
                    task_name = task_node.name
                    result = f"Result of {task_name}"

                    return {
                        "messages": [{"role": "assistant", "content": result}],
                        "task_results": {task_name: result},
                        "current_task": task_name,
                        "completed_tasks": [task_name]
                    }
                return task_func

            workflow.add_node(node.id, make_task_node(node))

        # Add edges
        for edge in graph.edges:
            if edge.edge_type == "default":
                if edge.target in ("END", "__end__"):
                    workflow.add_edge(edge.source, END)
                else:
                    # Check if target is a task node
                    if any(n.id == edge.target for n in task_nodes):
                        workflow.add_edge(edge.source, edge.target)

        # Set entry point
        if task_nodes:
            workflow.set_entry_point(task_nodes[0].id)

        # Add final edge to END
        if task_nodes:
            workflow.add_edge(task_nodes[-1].id, END)

        return workflow


class CrewAIASTVisitor(ast.NodeVisitor):
    """AST visitor to extract CrewAI components from code."""

    def __init__(self):
        self.crew = CrewAICrew(name="extracted_crew")
        self._current_class = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions."""
        # Check if class has CrewBase decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "CrewBase":
                self._current_class = node.name
                self.crew.name = node.name

        self.generic_visit(node)
        self._current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions for @agent and @task decorators."""
        for decorator in node.decorator_list:
            # Check for @agent decorator
            if isinstance(decorator, ast.Name) and decorator.id == "agent":
                self._extract_agent(node)
            elif isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'id') and decorator.func.id == "agent":
                    self._extract_agent(node)

            # Check for @task decorator
            if isinstance(decorator, ast.Name) and decorator.id == "task":
                self._extract_task(node)
            elif isinstance(decorator, ast.Call):
                if hasattr(decorator.func, 'id') and decorator.func.id == "task":
                    self._extract_task(node)

        self.generic_visit(node)

    def _extract_agent(self, node: ast.FunctionDef):
        """Extract agent info from function."""
        # Try to extract from return statement
        agent = CrewAIAgent(
            name=node.name,
            role=node.name,
            goal="",
            backstory=""
        )

        # Look for Agent() call in return
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id') and child.func.id == "Agent":
                    for keyword in child.keywords:
                        if keyword.arg == "role" and isinstance(keyword.value, ast.Constant):
                            agent.role = keyword.value.value
                        elif keyword.arg == "goal" and isinstance(keyword.value, ast.Constant):
                            agent.goal = keyword.value.value
                        elif keyword.arg == "backstory" and isinstance(keyword.value, ast.Constant):
                            agent.backstory = keyword.value.value

        self.crew.agents.append(agent)

    def _extract_task(self, node: ast.FunctionDef):
        """Extract task info from function."""
        task = CrewAITask(
            name=node.name,
            description="",
            expected_output="",
            agent=""
        )

        # Look for Task() call in return
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id') and child.func.id == "Task":
                    for keyword in child.keywords:
                        if keyword.arg == "description" and isinstance(keyword.value, ast.Constant):
                            task.description = keyword.value.value
                        elif keyword.arg == "expected_output" and isinstance(keyword.value, ast.Constant):
                            task.expected_output = keyword.value.value
                        elif keyword.arg == "agent":
                            # Try to resolve agent reference
                            if isinstance(keyword.value, ast.Call):
                                if hasattr(keyword.value.func, 'attr'):
                                    task.agent = keyword.value.func.attr

        self.crew.tasks.append(task)


def map_crewai_to_langgraph(
    source: Any,
    compile: bool = False
) -> Any:
    """
    Convenience function to map CrewAI to LangGraph.

    Args:
        source: CrewAI crew, class, or code
        compile: Whether to compile the graph

    Returns:
        LangGraph StateGraph or CompiledGraph
    """
    mapper = CrewAIMapper()
    graph = mapper.analyze(source)
    langgraph = mapper.to_langgraph(graph)

    if compile:
        return langgraph.compile()
    return langgraph
