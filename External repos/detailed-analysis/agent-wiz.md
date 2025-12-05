# Agent-Wiz - Detailed Analysis

**Repository:** Agent-Wiz/
**Type:** Security Analysis & Threat Modeling
**Priority:** 💡 REFERENCE (Security-focused)

---

## Overview

Agent-Wiz is a Python CLI for extracting agentic workflows and performing automated threat assessments. It uses AST-based static parsing to analyze agent code and generate security reports.

**Key Value:** Visualize agent workflows and identify security vulnerabilities without running code.

---

## Core Capabilities

### 1. Workflow Extraction
- **AST-based parsing** of agent code
- Extracts agents, tools, transitions, and communication patterns
- Framework-agnostic approach

### 2. Supported Frameworks
- ✅ Autogen (core)
- ✅ AgentChat
- ✅ CrewAI
- ✅ LangGraph
- ✅ LlamaIndex
- ✅ n8n
- ✅ OpenAI Agents
- ✅ Pydantic-AI
- ✅ Swarm
- ✅ Google-ADK

### 3. Threat Modeling
- **MAESTRO Framework:**
  - M: Mission (system purpose)
  - A: Assets (components inventory)
  - E: Entrypoints (attack surfaces)
  - S: Security Controls
  - T: Threats (vulnerabilities)
  - R: Risks (impact/likelihood)
  - O: Operations (runtime security)

### 4. Visualization
- D3-based HTML visualizations
- Interactive workflow graphs
- Agent-to-agent connections
- Tool usage mapping

---

## Extractable Patterns

### Pattern 1: AST-Based Code Analysis

```python
# Extract AST parsing for workflow discovery
import ast

class AgentWorkflowParser:
    def __init__(self, framework="crewai"):
        self.framework = framework
        self.agents = []
        self.tools = []
        self.transitions = []

    def parse_file(self, filepath):
        with open(filepath) as f:
            tree = ast.parse(f.read())

        # Visit all nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.extract_agent(node)
            elif isinstance(node, ast.FunctionDef):
                self.extract_tool(node)
            elif isinstance(node, ast.Call):
                self.extract_transition(node)

        return {
            "agents": self.agents,
            "tools": self.tools,
            "transitions": self.transitions
        }

    def extract_agent(self, node):
        # CrewAI example
        if any(base.id == "Agent" for base in node.bases if hasattr(base, 'id')):
            agent_info = {
                "name": node.name,
                "type": "agent",
                "tools": []
            }
            # Extract agent configuration...
            self.agents.append(agent_info)

    def extract_tool(self, node):
        # Check for @tool decorator
        if any(d.id == "tool" for d in node.decorator_list if hasattr(d, 'id')):
            tool_info = {
                "name": node.name,
                "type": "tool"
            }
            self.tools.append(tool_info)
```

### Pattern 2: Graph Generation

```python
# Extract graph structure
class WorkflowGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_agent(self, agent_name, agent_config):
        self.nodes.append({
            "id": agent_name,
            "type": "agent",
            "config": agent_config
        })

    def add_tool(self, tool_name, tool_config):
        self.nodes.append({
            "id": tool_name,
            "type": "tool",
            "config": tool_config
        })

    def add_transition(self, from_node, to_node, condition=None):
        self.edges.append({
            "source": from_node,
            "target": to_node,
            "condition": condition
        })

    def to_json(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "metadata": {
                "framework": self.framework,
                "timestamp": datetime.now().isoformat()
            }
        }
```

### Pattern 3: Threat Assessment

```python
# Extract threat modeling pattern
class ThreatAssessor:
    def __init__(self, workflow_graph):
        self.graph = workflow_graph
        self.threats = []

    def assess_maestro(self):
        report = {
            "mission": self.define_mission(),
            "assets": self.inventory_assets(),
            "entrypoints": self.map_entrypoints(),
            "security_controls": self.evaluate_controls(),
            "threats": self.identify_threats(),
            "risks": self.calculate_risks(),
            "operations": self.assess_operations()
        }
        return report

    def identify_threats(self):
        threats = []

        # Check for prompt injection risks
        for node in self.graph.nodes:
            if node["type"] == "agent":
                if not self.has_input_validation(node):
                    threats.append({
                        "type": "Prompt Injection",
                        "component": node["id"],
                        "severity": "HIGH",
                        "description": "Agent accepts user input without validation"
                    })

        # Check for tool misuse
        for edge in self.graph.edges:
            if self.is_tool_call(edge):
                if not self.has_authorization(edge):
                    threats.append({
                        "type": "Unauthorized Tool Access",
                        "component": f"{edge['source']} -> {edge['target']}",
                        "severity": "MEDIUM",
                        "description": "Tool can be called without authorization"
                    })

        return threats

    def calculate_risks(self):
        risks = []
        for threat in self.threats:
            impact = self.assess_impact(threat)
            likelihood = self.assess_likelihood(threat)
            risk_score = impact * likelihood

            risks.append({
                "threat": threat,
                "impact": impact,
                "likelihood": likelihood,
                "score": risk_score,
                "mitigation": self.suggest_mitigation(threat)
            })

        return sorted(risks, key=lambda x: x["score"], reverse=True)
```

---

## CLI Usage

```bash
# Extract workflow
agent-wiz extract \
    --framework crewai \
    --directory ./my_agents \
    --output workflow.json

# Visualize
agent-wiz visualize \
    --input workflow.json \
    --open

# Analyze threats
agent-wiz analyze \
    --input workflow.json \
    --output threat_report.md
```

---

## What to Extract

### 1. Static Analysis Patterns
- AST parsing for Python code
- Framework-specific pattern detection
- Workflow graph construction

### 2. Visualization
- D3.js graph rendering
- Interactive workflow diagrams
- Node/edge styling

### 3. Threat Modeling
- MAESTRO framework implementation
- Automated vulnerability detection
- Risk scoring algorithms

### 4. Security Checklists
- Input validation checks
- Authorization verification
- Data flow analysis
- Tool access control

---

## Use Cases

1. **Security Audits**
   - Analyze agent systems for vulnerabilities
   - Generate compliance reports
   - Track security improvements

2. **Workflow Documentation**
   - Visualize complex agent interactions
   - Document system architecture
   - Onboard new developers

3. **Quality Assurance**
   - Verify agent behavior
   - Check tool usage patterns
   - Validate security controls

---

## Implementation Steps

1. **Install Agent-Wiz**
   ```bash
   pip install repello-agent-wiz
   ```

2. **Extract Your Workflow**
   ```bash
   agent-wiz extract --framework crewai --directory ./ --output graph.json
   ```

3. **Visualize**
   ```bash
   agent-wiz visualize --input graph.json --open
   ```

4. **Run Threat Analysis**
   ```bash
   agent-wiz analyze --input graph.json
   ```

---

**Related:**
- [Back to Overview](../REPOSITORY-ANALYSIS-OVERVIEW.md)
- [agentops Analysis](./agentops.md)
