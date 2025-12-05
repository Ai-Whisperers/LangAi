# CrewAI Reference - Detailed Analysis

**Repository:** crewai-reference/
**Type:** CrewAI Examples & Patterns
**Priority:** 🔧 SPECIFIC (CrewAI Development)

---

## Overview

Collection of CrewAI examples organized into crews, flows, integrations, and notebooks. Best resource for learning CrewAI-specific patterns and best practices.

---

## Structure

```
crewai-reference/
├── crewAI-examples/
│   ├── crews/          # Multi-agent crew examples
│   ├── flows/          # Flow orchestration
│   ├── integrations/   # Tool integrations
│   └── notebooks/      # Jupyter notebooks
├── crewAI-main/        # Main framework code
└── crewAI-quickstarts/ # Quick start templates
```

---

## Key Concepts

### 1. Crew Composition

```python
# Standard CrewAI pattern
from crewai import Agent, Task, Crew

# Define agents with roles
researcher = Agent(
    role="Senior Researcher",
    goal="Research and analyze topics thoroughly",
    backstory="Expert researcher with 10+ years experience",
    tools=[search_tool, scrape_tool],
    verbose=True
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and extract insights",
    backstory="Statistical analysis expert",
    tools=[python_tool],
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging content from research",
    backstory="Professional writer and editor",
    tools=[],
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research {topic} thoroughly",
    agent=researcher,
    expected_output="Comprehensive research report"
)

analysis_task = Task(
    description="Analyze the research findings",
    agent=analyst,
    context=[research_task],  # Depends on research
    expected_output="Data analysis report"
)

writing_task = Task(
    description="Write article about {topic}",
    agent=writer,
    context=[research_task, analysis_task],
    expected_output="Published article"
)

# Create crew
crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential  # or Process.hierarchical
)

# Execute
result = crew.kickoff(inputs={"topic": "AI Agents"})
```

---

## Extractable Patterns

### Pattern 1: Role-Based Agents

```python
# Extract role specialization pattern
class RoleBasedAgent:
    """Template for creating specialized agents"""

    def __init__(self, role, goal, backstory, tools):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools

    def create_agent(self):
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.tools,
            verbose=True,
            allow_delegation=True,
            memory=True
        )

# Use template
research_agent = RoleBasedAgent(
    role="Researcher",
    goal="Find accurate information",
    backstory="PhD in Computer Science",
    tools=[search_tool]
).create_agent()
```

### Pattern 2: Task Dependencies

```python
# Extract task chain pattern
class TaskChain:
    def __init__(self):
        self.tasks = []

    def add_task(self, description, agent, depends_on=None):
        task = Task(
            description=description,
            agent=agent,
            context=depends_on or [],  # Task dependencies
            expected_output=f"Output from {agent.role}"
        )
        self.tasks.append(task)
        return task

# Build chain
chain = TaskChain()
task1 = chain.add_task("Research topic", researcher)
task2 = chain.add_task("Analyze research", analyst, depends_on=[task1])
task3 = chain.add_task("Write report", writer, depends_on=[task1, task2])
```

### Pattern 3: Hierarchical Process

```python
# Extract hierarchical coordination
crew = Crew(
    agents=[researcher, analyst, writer, reviewer],
    tasks=tasks,
    process=Process.hierarchical,  # Manager delegates tasks
    manager_llm="gpt-4"  # Manager uses powerful LLM
)

# Manager agent automatically:
# 1. Analyzes tasks
# 2. Assigns to appropriate agents
# 3. Reviews outputs
# 4. Coordinates handoffs
```

### Pattern 4: Flows (Orchestration)

```python
# Extract flow pattern from flows/
from crewai_flows import Flow, listen, start

class ResearchFlow(Flow):
    @start()
    def start_research(self, topic):
        """Entry point"""
        return {"topic": topic, "sources": []}

    @listen(start_research)
    def gather_sources(self, context):
        """Triggered after start_research"""
        sources = search_engine.search(context["topic"])
        return {**context, "sources": sources}

    @listen(gather_sources)
    def analyze_sources(self, context):
        """Triggered after gather_sources"""
        analysis = analyzer.analyze(context["sources"])
        return {**context, "analysis": analysis}

    @listen(analyze_sources)
    def write_report(self, context):
        """Final step"""
        report = writer.write(context)
        return report

# Execute flow
flow = ResearchFlow()
result = flow.kickoff(topic="AI Agents")
```

---

## Common Crew Patterns

### 1. Research Crew

```python
# From crews/ directory
research_crew = Crew(
    agents=[
        web_researcher,
        data_collector,
        fact_checker,
        report_writer
    ],
    tasks=[
        search_task,
        collect_task,
        verify_task,
        write_task
    ],
    process=Process.sequential
)
```

### 2. Content Creation Crew

```python
content_crew = Crew(
    agents=[
        researcher,
        content_strategist,
        writer,
        editor,
        seo_optimizer
    ],
    tasks=[
        research_task,
        strategy_task,
        writing_task,
        editing_task,
        seo_task
    ]
)
```

### 3. Analysis Crew

```python
analysis_crew = Crew(
    agents=[
        data_collector,
        statistician,
        ml_engineer,
        visualizer
    ],
    tasks=[
        collect_data,
        statistical_analysis,
        ml_analysis,
        create_viz
    ]
)
```

---

## Tool Integration Examples

### From integrations/ directory:

```python
# Web scraping tool
from crewai_tools import ScrapeWebsiteTool

scraper = ScrapeWebsiteTool()

# Search tool
from crewai_tools import SerperDevTool

search = SerperDevTool()

# File tools
from crewai_tools import FileReadTool, FileWriteTool

reader = FileReadTool()
writer = FileWriteTool()

# Code tools
from crewai_tools import CodeInterpreterTool

code_tool = CodeInterpreterTool()

# Custom tool
from crewai.tools import tool

@tool("Custom Calculator")
def calculator(operation: str) -> float:
    """Perform mathematical calculations"""
    return eval(operation)
```

---

## Best Practices (from examples)

### 1. Agent Design

```python
# Good: Specific role and clear goal
good_agent = Agent(
    role="Senior Python Developer",
    goal="Write clean, tested Python code",
    backstory="""You are an expert Python developer with 15 years
    of experience in building scalable applications.""",
    tools=[python_tool],
    verbose=True,
    allow_delegation=False  # Focused on coding only
)

# Bad: Vague role and unclear goal
bad_agent = Agent(
    role="Helper",
    goal="Help with stuff",
    backstory="You help",
    tools=[]  # No tools!
)
```

### 2. Task Design

```python
# Good: Clear, specific, measurable
good_task = Task(
    description="""
    Analyze the dataset at {file_path} and:
    1. Calculate summary statistics
    2. Identify outliers
    3. Generate 3 visualizations
    4. Write a 2-page report

    Use the Python tool for analysis.
    """,
    agent=analyst,
    expected_output="2-page PDF report with 3 charts",
    output_file="analysis_report.pdf"
)

# Bad: Vague and unmeasurable
bad_task = Task(
    description="Look at data",
    agent=analyst,
    expected_output="Something useful"
)
```

### 3. Memory Usage

```python
# Enable memory for context retention
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    memory=True,  # Agents remember past interactions
    verbose=True
)
```

---

## Notebook Examples

### Key Notebooks to Study:

1. **Basic Crew Setup** - Start here
2. **Hierarchical Process** - Manager delegation
3. **Custom Tools** - Build your own tools
4. **Memory Usage** - Long-running crews
5. **Flow Orchestration** - Complex workflows

---

## Quick Start Templates

### From crewAI-quickstarts/:

```bash
# Install CrewAI
pip install crewai crewai-tools

# Create new project
crewai create my_crew

# Project structure created:
my_crew/
├── src/
│   ├── my_crew/
│   │   ├── crew.py       # Crew definition
│   │   ├── agents.py     # Agent definitions
│   │   └── tasks.py      # Task definitions
│   └── main.py           # Entry point
├── config/
│   ├── agents.yaml       # Agent configs
│   └── tasks.yaml        # Task configs
└── .env
```

---

## Integration with AgentOps

```python
# From examples: automatic monitoring
import os
os.environ["AGENTOPS_API_KEY"] = "your_key"

# Just run crew - automatically tracked!
crew = Crew(agents=[...], tasks=[...])
result = crew.kickoff()

# All execution tracked in AgentOps dashboard
```

---

## Key Takeaways

1. **Role Clarity:** Clear roles = better results
2. **Task Dependencies:** Use context for chaining
3. **Process Choice:** Sequential vs Hierarchical
4. **Tool Integration:** Many pre-built tools available
5. **Memory:** Enable for long-running crews
6. **Flows:** For complex orchestration
7. **Monitoring:** Free with AgentOps integration

---

## When to Use CrewAI

**Use CrewAI when:**
- You want quick multi-agent prototypes
- You like role-based agent design
- You need hierarchical coordination
- You want built-in tool integrations

**Consider alternatives when:**
- You need fine-grained control (use LangGraph)
- You're building complex custom workflows
- You need state machine control

---

## Related
- [Back to Overview](../REPOSITORY-ANALYSIS-OVERVIEW.md)
- [langchain-reference](./langchain-reference.md)
- [oreilly-ai-agents](./oreilly-ai-agents.md)
