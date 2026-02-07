# Workflow Deep Dive

This document explains the main workflow implementations and their decision logic.

---

## 1) Parallel multi-agent workflow (fan-out / fan-in)

File:

- `src/company_researcher/workflows/parallel_agent_research.py`

High-level flow:

1. **Researcher** gathers sources
2. **Parallel specialists** run (financial, market, product, competitor scout)
3. **Synthesizer** combines specialist outputs
4. **Logic critic** performs QA
5. **Quality check** decides whether to iterate
6. **Save report** writes a markdown report

Iteration logic lives in `check_quality_node()`:

- If quality is below the threshold, it increases `iteration_count` and returns `missing_info`
- A conditional edge determines whether to loop or finish

State schema and reducers:

- `src/company_researcher/state.py`

---

## 2) Comprehensive workflow (full feature graph)

File:

- `src/company_researcher/workflows/comprehensive_research.py`

This workflow is built from modular nodes in:

- `src/company_researcher/workflows/nodes/`

Key design points:

- Uses `StateGraph(OverallState, input=InputState, output=OutputState)`
- Starts from `create_initial_state(company_name)`
- Uses conditional edges in `should_continue_research` to decide whether to iterate after quality checking
- Writes outputs via `save_comprehensive_report_node` (markdown + metrics)

---

## 3) Running workflows

### From Python

- Full-feature workflow helper:
  - `company_researcher.workflows.research_company_comprehensive(company_name)`

### From LangGraph Studio

Studio loads wrapper modules defined in `langgraph.json`:

- `src/graphs/research_graph.py:graph` (exports the compiled comprehensive workflow)
- `src/graphs/simple_graph.py:graph` (tiny test graph)

### From the CLI

The repo CLI (`run_research.py`) calls `scripts/research/cli.py` which supports:

- Default orchestration path (returns a `WorkflowState`)
- `--use-graph` (runs the legacy graph from `src/company_researcher/graphs/research_graph.py`)

---

## 4) State and outputs

- State schema (LangGraph workflows): `src/company_researcher/state.py`
- Output writer (comprehensive workflow): `src/company_researcher/workflows/nodes/comprehensive_output_nodes.py`
