# Codebase Tour

This document is a high-level map of **where the code lives** and **how you run it**.

---

## Entry points (how you run the system)

### CLI (recommended for local use)

- Repo entrypoint: `run_research.py`
  - Calls: `scripts/research/cli.py`
  - Modes:
    - default: orchestration engine (`company_researcher.orchestration`)
    - `--use-graph`: legacy LangGraph graph (`src/company_researcher/graphs/research_graph.py`)

### Minimal demo

- `examples/hello_research.py`
  - Simple prototype script (useful as a “hello world” for the stack)

### API server (FastAPI)

- ASGI app: `company_researcher.api.main:app` (deployment stable)
- Local run: `python -m company_researcher.api.app --host 0.0.0.0 --port 8000`

### LangGraph Studio

- Studio config: `langgraph.json`
- Graph exports (wrappers for Studio):
  - `src/graphs/simple_graph.py:graph`
  - `src/graphs/research_graph.py:graph` (wraps the comprehensive workflow)

---

## Where the logic lives (major packages)

### `src/company_researcher/agents/`

Agent implementations and the `agent_node` pattern.

### `src/company_researcher/workflows/`

LangGraph workflows (graphs) that orchestrate agents, data collection, quality checks, and report output.

Key files:
- `workflows/parallel_agent_research.py`: parallel specialist workflow + logic-critic QA
- `workflows/comprehensive_research.py`: full-feature sequential workflow built from modular nodes
- `workflows/nodes/`: modular node implementations (data collection, analysis, enrichment, output)

### `src/company_researcher/orchestration/`

A separate orchestration layer that returns a `WorkflowState` object and is used by the CLI default path.

### `src/company_researcher/integrations/`

External providers (search, financial data, news, scraping) and routing/fallback logic.

### `src/company_researcher/quality/`

Quality scoring, contradiction detection, validation, and source assessment.

### `src/company_researcher/config.py`

Pydantic settings model (`ResearchConfig`) loaded from `.env` / environment variables via `get_config()`.

---

## Outputs (where results are written)

Output location depends on the execution path:

- **Comprehensive LangGraph workflow**: uses `config.output_dir` (default: `outputs/`)
- **CLI wrapper** (`run_research.py`): writes to `--output` (default: `outputs/research/`)

See:
- `src/company_researcher/config.py` (`output_dir`)
- `scripts/research/cli.py` (`--output`)
- `src/company_researcher/workflows/nodes/comprehensive_output_nodes.py` (report writing)
