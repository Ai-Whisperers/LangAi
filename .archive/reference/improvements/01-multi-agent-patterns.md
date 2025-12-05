# Multi-Agent Coordination Patterns

**Source:** `langchain-reference/03-multi-agent-patterns/`

---

## Overview

Two primary patterns for multi-agent coordination:
1. **Supervisor Pattern** - Centralized coordination
2. **Swarm Pattern** - Decentralized peer-to-peer

---

## Pattern 1: Supervisor (Recommended for Company Researcher)

### When to Use
- ✅ Complex research workflows
- ✅ Need central oversight
- ✅ Strategic task allocation
- ✅ Context needs careful management

### Architecture
```
┌─────────────────────────────────┐
│         Supervisor              │
│   (Strategic Coordinator)       │
└───────────┬─────────────────────┘
            │
    ┌───────┴────────┬──────────┬─────────┐
    │                │          │         │
┌───▼────┐  ┌───────▼─┐  ┌────▼─────┐  ┌▼──────┐
│Research│  │Financial│  │  Market  │  │Critic │
│ Agent  │  │  Agent  │  │ Analyst  │  │ Agent │
└────────┘  └─────────┘  └──────────┘  └───────┘
```

### Implementation Example

```python
# src/improvements/supervisor_pattern.py
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import Literal

@dataclass
class SupervisorState:
    """State for supervisor workflow"""
    company_name: str
    research_plan: dict | None = None
    agent_results: dict[str, Any] = field(default_factory=dict)
    final_report: dict | None = None

class SupervisorAgent:
    """Central coordinator that assigns tasks to specialists"""

    def __init__(self, agents: dict[str, Any], llm):
        self.agents = agents
        self.llm = llm

    def plan_research(self, state: SupervisorState) -> Command:
        """Create research plan and assign agents"""

        prompt = f"""You are coordinating research on {state.company_name}.

Available specialists:
{self._format_agent_capabilities()}

Create a research plan:
1. Which specialists should work?
2. What tasks for each?
3. Parallel or sequential execution?

Return JSON:
{{
  "agents": ["agent1", "agent2"],
  "tasks": {{"agent1": "task", "agent2": "task"}},
  "mode": "parallel"
}}"""

        response = self.llm.invoke(prompt)
        plan = eval(response.content)

        # Use Command to route to first agent
        return Command(
            goto=plan["agents"][0],
            update={"research_plan": plan}
        )

    def _format_agent_capabilities(self) -> str:
        """Format agent descriptions"""
        return "\n".join([
            f"- {name}: {agent.description}"
            for name, agent in self.agents.items()
        ])

def build_supervisor_graph(agents: dict, llm) -> StateGraph:
    """Build supervisor workflow graph"""

    supervisor = SupervisorAgent(agents, llm)
    workflow = StateGraph(SupervisorState)

    # Add supervisor node
    workflow.add_node("supervisor", supervisor.plan_research)

    # Add agent nodes
    for name, agent in agents.items():
        workflow.add_node(name, agent.execute)

    # Add synthesis node
    workflow.add_node("synthesize", synthesize_results)

    # Routing logic
    workflow.add_edge(START, "supervisor")

    # Supervisor routes to agents
    def route_from_supervisor(state: SupervisorState):
        plan = state.research_plan
        if plan["mode"] == "parallel":
            # LangGraph will execute in parallel
            return plan["agents"]
        else:
            # Sequential - return first agent
            return plan["agents"][0]

    workflow.add_conditional_edges("supervisor", route_from_supervisor)

    # All agents converge to synthesis
    for name in agents.keys():
        workflow.add_edge(name, "synthesize")

    workflow.add_edge("synthesize", END)

    return workflow.compile()
```

### Key Features

**1. Centralized Decision Making**
```python
# Supervisor decides task allocation
plan = supervisor.plan_research(state)

# Example plan:
{
  "agents": ["financial_agent", "market_analyst"],
  "tasks": {
    "financial_agent": "Get revenue, funding, growth metrics",
    "market_analyst": "Analyze market size and positioning"
  },
  "mode": "parallel"
}
```

**2. Context Management**
```python
# Two modes for message history:

# Mode 1: Full History (each agent sees everything)
output_mode = "full_history"

# Mode 2: Last Message Only (each agent sees only their task)
output_mode = "last_message"  # Better for focused agents
```

**3. Hierarchical Routing**
```python
# Supervisor can have multiple levels
level1_supervisor = SupervisorAgent(worker_agents)
level2_supervisor = SupervisorAgent({
    "research_team": level1_supervisor,
    "analysis_team": analysis_supervisor
})
```

### When to Choose Supervisor

✅ **Use Supervisor when:**
- Research is complex with many steps
- Need strategic coordination
- Agents have dependencies
- Central quality control needed
- Budget/resource management important

❌ **Don't use Supervisor when:**
- Simple workflows (single agent enough)
- Agents are truly independent
- Overhead of coordination too high

---

## Pattern 2: Swarm (Alternative)

### When to Use
- ✅ Collaborative conversations
- ✅ Dynamic agent selection
- ✅ Peer-to-peer workflows
- ✅ Lightweight coordination

### Architecture
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Agent A │ ←─→ │ Agent B │ ←─→ │ Agent C │
└─────────┘     └─────────┘     └─────────┘
     ↓               ↓               ↓
  ┌──────────────────────────────────┐
  │   Active Agent Tracking (State)  │
  └──────────────────────────────────┘
```

### Implementation Example

```python
# src/improvements/swarm_pattern.py
from langgraph_swarm import create_swarm, create_handoff_tool

class ResearcherAgent:
    """Agent that can hand off to others"""

    def __init__(self, name: str, specialty: str):
        self.name = name
        self.specialty = specialty

    def get_handoff_tools(self, other_agents: list):
        """Create handoff tools to other agents"""
        return [
            create_handoff_tool(
                agent_name=agent.name,
                description=f"Transfer to {agent.name} for {agent.specialty}"
            )
            for agent in other_agents
            if agent.name != self.name
        ]

# Create agents
general_researcher = ResearcherAgent("GeneralResearcher", "company overview")
financial_analyst = ResearcherAgent("FinancialAnalyst", "financial analysis")
market_analyst = ResearcherAgent("MarketAnalyst", "market research")

# Each agent gets handoff tools to others
all_agents = [general_researcher, financial_analyst, market_analyst]

for agent in all_agents:
    other_agents = [a for a in all_agents if a != agent]
    agent.tools = agent.get_handoff_tools(other_agents)

# Create swarm
swarm = create_swarm(
    agents=all_agents,
    default_active_agent="GeneralResearcher"
)

# Agents can hand off to each other
result = swarm.invoke({
    "messages": [("user", "Research Tesla's financial performance")]
})

# Flow might be:
# GeneralResearcher → "I'll hand off to FinancialAnalyst"
# FinancialAnalyst → Does analysis
# FinancialAnalyst → "I'll hand off to MarketAnalyst for context"
# MarketAnalyst → Adds market context
```

### Key Features

**1. Peer-to-Peer Handoff**
```python
# Agents decide who to hand off to
def research_agent(state):
    if needs_financial_analysis(state):
        return handoff_to_financial_agent()
    elif needs_market_context(state):
        return handoff_to_market_agent()
    else:
        return continue_research()
```

**2. Active Agent Memory**
```python
# System tracks who's active
state.active_agent = "FinancialAnalyst"

# Can resume from where left off
swarm.invoke(state)  # Continues with FinancialAnalyst
```

**3. Dynamic Routing**
```python
# No pre-planned routing
# Agents make decisions in real-time
# More flexible, less predictable
```

### When to Choose Swarm

✅ **Use Swarm when:**
- Conversational workflows
- Agent collaboration needed
- Dynamic decision making
- Lightweight coordination

❌ **Don't use Swarm when:**
- Need predictable execution
- Central control required
- Complex dependencies
- Quality assurance critical

---

## Comparison

| Aspect | Supervisor | Swarm |
|--------|-----------|-------|
| **Control** | Centralized | Distributed |
| **Predictability** | High | Low |
| **Flexibility** | Medium | High |
| **Complexity** | Higher | Lower |
| **Best For** | Research, analysis | Collaboration, chat |
| **Quality Control** | Easier | Harder |
| **Debugging** | Easier | Harder |

---

## Recommendation for Company Researcher

**Use Supervisor Pattern**

Reasons:
1. Research requires strategic coordination
2. Need quality control (central oversight)
3. Agents have dependencies (financial → market context)
4. Predictable execution important
5. Cost control (supervisor manages resources)
6. Easier to debug and monitor

---

## Implementation Roadmap

### Phase 1: Simple Supervisor (MVP)
```python
# 1 supervisor + 3 agents
- Supervisor plans research
- Agents execute in parallel
- Supervisor synthesizes results
```

### Phase 2: Advanced Supervisor
```python
# Add features:
- Context compression
- Iterative refinement
- Quality gates
- Cost tracking
```

### Phase 3: Hierarchical (Future)
```python
# Multi-level supervision
- Research supervisor → Research agents
- Analysis supervisor → Analysis agents
- Meta supervisor → Coordinates supervisors
```

---

## Code Templates

### Template: Basic Supervisor Node
```python
def supervisor_node(state: State, config: RunnableConfig) -> Command:
    """Supervisor decides next agent"""

    # Analyze state
    next_agent = analyze_and_decide(state)

    # Prepare task
    task = prepare_task_for_agent(state, next_agent)

    # Route with Command
    return Command(
        goto=next_agent,
        update={"current_task": task}
    )
```

### Template: Agent Node
```python
def agent_node(state: State, config: RunnableConfig) -> dict:
    """Specialist agent executes task"""

    # Get task from supervisor
    task = state.current_task

    # Execute research
    result = execute_research(task)

    # Return results
    return {
        "agent_results": {
            agent_name: result
        }
    }
```

### Template: Synthesis Node
```python
def synthesis_node(state: State, config: RunnableConfig) -> dict:
    """Combine all agent results"""

    # Get all results
    all_results = state.agent_results

    # Synthesize
    final_report = synthesize(all_results)

    return {"final_report": final_report}
```

---

## References

- **LangGraph Supervisor:** `langchain-reference/03-multi-agent-patterns/langgraph-supervisor-py/`
- **LangGraph Swarm:** `langchain-reference/03-multi-agent-patterns/langgraph-swarm-py/`
- **Open Deep Research:** Uses supervisor pattern successfully

---

## Next Steps

1. Implement basic supervisor in MVP
2. Add 3 specialist agents
3. Test parallel execution
4. Add quality control to supervisor
5. Consider swarm for conversational features later
