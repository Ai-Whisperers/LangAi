# O'Reilly AI Agents - Detailed Analysis

**Repository:** oreilly-ai-agents/
**Type:** Educational Notebooks & Tutorials
**Priority:** ⚡ MEDIUM (Learning Resource)

---

## Overview

Comprehensive educational repository with Jupyter notebooks covering AI agent frameworks, evaluation techniques, and modern agent paradigms.

**Best For:** Learning by example, framework comparisons, evaluation methodologies.

---

## Key Notebooks

### 1. Framework Introductions

#### **SmolAgents** ([SmolAgents.ipynb](oreilly-ai-agents/notebooks/SmolAgents.ipynb))
- HuggingFace's lightweight agent framework
- Simple function-calling agents
- Tool integration patterns

#### **CrewAI** ([CrewAI_Hello_World.ipynb](oreilly-ai-agents/notebooks/CrewAI_Hello_World.ipynb))
- Multi-agent crew creation
- Role-based agents
- Task delegation

#### **Autogen** ([Autogen_HelloWorld.ipynb](oreilly-ai-agents/notebooks/Autogen_HelloWorld.ipynb))
- Microsoft's multi-agent framework
- Conversation patterns
- Human-in-the-loop

#### **OpenAI Swarm** ([Swarm_Hello_World.ipynb](oreilly-ai-agents/notebooks/Swarm_Hello_World.ipynb))
- Lightweight multi-agent coordination
- Handoff patterns
- Context switching

#### **OpenAI Agents SDK** ([OpenAI Agents.ipynb](oreilly-ai-agents/notebooks/OpenAI%20Agents.ipynb))
- New official agents SDK
- Function calling
- Streaming responses

---

### 2. LangGraph Workflows

#### **Basic Workflow** ([LangGraph_Hello_World.ipynb](oreilly-ai-agents/notebooks/LangGraph_Hello_World.ipynb))
- RAG workflow implementation
- State machine basics
- Node and edge patterns

#### **ReAct Agents** ([LangGraph_React.ipynb](oreilly-ai-agents/notebooks/LangGraph_React.ipynb))
- Reason + Act pattern
- Tool integration
- Thought process tracking

#### **Local LLMs** ([LangGraph_React_Local_LLMs.ipynb](oreilly-ai-agents/notebooks/LangGraph_React_Local_LLMs.ipynb))
- Use Ollama for local inference
- Cost-free development
- Privacy-focused agents

#### **MCP Integration** ([LangGraph_React - MCP + Tool Selection.ipynb](oreilly-ai-agents/notebooks/LangGraph_React%20-%20MCP%20+%20Tool%20Selection.ipynb))
- Model Context Protocol tools
- Tool positional bias testing
- Selection accuracy measurement

---

### 3. Evaluation & Testing

#### **Evaluating with Rubrics** ([Evaluating_LLMs_with_Rubrics.ipynb](oreilly-ai-agents/notebooks/Evaluating_LLMs_with_Rubrics.ipynb))
- Rubric-based evaluation
- Multi-criteria scoring
- Positional bias detection

**Extract This:**
```python
# Rubric evaluation pattern
class RubricEvaluator:
    def __init__(self):
        self.criteria = {
            "accuracy": {
                "weight": 0.3,
                "description": "Factual correctness"
            },
            "completeness": {
                "weight": 0.3,
                "description": "Coverage of requirements"
            },
            "relevance": {
                "weight": 0.25,
                "description": "Relevance to query"
            },
            "coherence": {
                "weight": 0.15,
                "description": "Logical flow"
            }
        }

    async def evaluate(self, output, expected=None):
        scores = {}

        for criterion, config in self.criteria.items():
            prompt = self.build_rubric_prompt(
                criterion,
                config["description"],
                output,
                expected
            )

            score = await self.llm_score(prompt)
            scores[criterion] = score

        weighted_score = sum(
            scores[c] * self.criteria[c]["weight"]
            for c in scores
        )

        return {
            "overall": weighted_score,
            "breakdown": scores
        }
```

#### **Tool Selection Accuracy** ([agent_positional_bias_tools.ipynb](oreilly-ai-agents/notebooks/agent_positional_bias_tools.ipynb))
- Measures tool selection accuracy
- Tests for positional bias
- Compares different LLMs

**Extract This:**
```python
# Test for positional bias in tool selection
class ToolSelectionTester:
    def __init__(self, llm):
        self.llm = llm

    async def test_positional_bias(self, tools, query):
        results = []

        # Test all permutations
        for perm in itertools.permutations(tools):
            response = await self.llm.select_tool(query, list(perm))
            results.append({
                "order": [t.name for t in perm],
                "selected": response.tool_name,
                "position": list(perm).index(response.tool_name)
            })

        # Calculate bias
        positions = [r["position"] for r in results]
        bias_score = self.calculate_bias(positions)

        return {
            "results": results,
            "bias_score": bias_score,
            "first_position_frequency": positions.count(0) / len(positions)
        }
```

#### **Workflow Evaluation** ([LangGraph_Workfow_Eval.ipynb](oreilly-ai-agents/notebooks/LangGraph_Workfow_Eval.ipynb))
- End-to-end workflow testing
- Performance benchmarking
- Quality metrics

---

### 4. Modern Agent Paradigms

#### **Plan & Execute** ([LangGraph_Plan_Execute.ipynb](oreilly-ai-agents/notebooks/LangGraph_Plan_Execute.ipynb))
- Two-phase agent pattern
- Planning with LLM
- Execution with tools

**Extract This:**
```python
# Plan & Execute pattern
class PlanExecuteAgent:
    def __init__(self, planner_llm, executor_llm, tools):
        self.planner = planner_llm
        self.executor = executor_llm
        self.tools = tools

    async def run(self, task):
        # Phase 1: Planning
        plan = await self.planner.create_plan(task)

        # Phase 2: Execution
        results = []
        for step in plan.steps:
            result = await self.executor.execute_step(
                step,
                self.tools,
                previous_results=results
            )
            results.append(result)

        # Synthesize final result
        final_result = await self.planner.synthesize(results)
        return final_result
```

#### **Reflection** ([LangGraph_Reflect.ipynb](oreilly-ai-agents/notebooks/LangGraph_Reflect.ipynb))
- Generator + Reflector pattern
- Iterative improvement
- Self-critique

**Extract This:**
```python
# Reflection pattern
class ReflectionAgent:
    def __init__(self, generator_llm, reflector_llm):
        self.generator = generator_llm
        self.reflector = reflector_llm

    async def generate_with_reflection(self, task, max_iterations=3):
        output = await self.generator.generate(task)

        for i in range(max_iterations):
            # Reflect on output
            reflection = await self.reflector.critique(output, task)

            if reflection.is_satisfactory:
                break

            # Improve based on reflection
            output = await self.generator.improve(
                output,
                task,
                reflection.suggestions
            )

        return {
            "output": output,
            "iterations": i + 1,
            "final_reflection": reflection
        }
```

#### **Computer Use** ([computer_use_reasoning.ipynb](oreilly-ai-agents/notebooks/computer_use_reasoning.ipynb))
- Screen interaction patterns
- Mouse/keyboard control
- Vision-based agents

---

## Extractable Patterns

### 1. Framework Comparison Matrix

```python
frameworks = {
    "CrewAI": {
        "pros": ["Easy to use", "Role-based", "Good for teams"],
        "cons": ["Less flexible", "Opinionated structure"],
        "best_for": "Quick multi-agent prototypes"
    },
    "LangGraph": {
        "pros": ["Flexible", "State machine", "Production-ready"],
        "cons": ["Steeper learning curve"],
        "best_for": "Complex custom workflows"
    },
    "Autogen": {
        "pros": ["Conversation-based", "Human-in-loop"],
        "cons": ["Complex setup"],
        "best_for": "Interactive multi-agent systems"
    },
    "Swarm": {
        "pros": ["Lightweight", "Simple handoffs"],
        "cons": ["Limited features", "Experimental"],
        "best_for": "Simple agent coordination"
    }
}
```

### 2. Evaluation Framework

```python
# Multi-criteria evaluation system
class AgentEvaluator:
    def __init__(self):
        self.evaluators = {
            "accuracy": AccuracyEvaluator(),
            "completeness": CompletenessEvaluator(),
            "efficiency": EfficiencyEvaluator(),
            "cost": CostEvaluator()
        }

    async def evaluate_agent(self, agent, test_cases):
        results = []

        for test_case in test_cases:
            result = await agent.run(test_case.input)

            scores = {}
            for name, evaluator in self.evaluators.items():
                scores[name] = await evaluator.evaluate(
                    result,
                    test_case.expected,
                    test_case.metadata
                )

            results.append({
                "test_case": test_case.name,
                "scores": scores,
                "passed": all(s >= 0.7 for s in scores.values())
            })

        return self.aggregate_results(results)
```

---

## Key Learnings

### 1. **Framework Selection**
- Start with simpler frameworks (Swarm, CrewAI)
- Move to LangGraph for production
- Use Autogen for conversational agents

### 2. **Evaluation is Critical**
- Test for positional bias
- Use rubrics for consistency
- Measure both quality and cost

### 3. **Modern Patterns Work**
- Plan & Execute reduces errors
- Reflection improves quality
- Computer use enables new capabilities

### 4. **Local LLMs are Viable**
- Use Ollama for development
- Switch to cloud for production
- Test locally, deploy remotely

---

## Implementation Roadmap

### Week 1: Exploration
```
Day 1-2: Run SmolAgents + CrewAI notebooks
Day 3-4: Try LangGraph React agent
Day 5: Experiment with Swarm handoffs
```

### Week 2: Evaluation
```
Day 1-3: Implement rubric evaluation
Day 4-5: Test tool selection bias
```

### Week 3: Advanced Patterns
```
Day 1-3: Build Plan & Execute agent
Day 4-5: Add Reflection
```

### Week 4: Production
```
Day 1-3: Choose framework for your use case
Day 4-5: Build production agent
```

---

## Related
- [Back to Overview](../REPOSITORY-ANALYSIS-OVERVIEW.md)
- [langchain-reference](./langchain-reference.md)
- [agentops](./agentops.md)
