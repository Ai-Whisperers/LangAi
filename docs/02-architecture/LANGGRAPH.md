# LangGraph in this repo

This repo uses **LangGraph** in three main places:

---

## 1) Workflows (primary orchestration graphs)

Directory:

- `src/company_researcher/workflows/`

These files build LangGraph graphs over the shared `OverallState` schema (`src/company_researcher/state.py`).

Examples:

- `workflows/parallel_agent_research.py`: fan-out/fan-in + logic critic QA
- `workflows/comprehensive_research.py`: full-feature workflow built from modular nodes

---

## 2) Packaged graphs (advanced / modular graph system)

Directory:

- `src/company_researcher/graphs/`

This package contains:

- legacy graphs (`research_graph.py`, `simple_graph.py`)
- a larger modular graph architecture (`main_graph.py`, `subgraphs/`, `streaming/`, `persistence/`, etc.)

---

## 3) LangGraph Studio wrappers (what Studio loads)

Directory:

- `src/graphs/`

These are small wrapper modules that export compiled graphs as module-level variables (usually `graph`) so LangGraph Studio can load them.

Configured in:

- `langgraph.json`

---

## Running LangGraph Studio

1. Ensure `.env` exists (copy from `env.example`)
2. Install dependencies
3. Run:

```bash
langgraph studio
```

The Studio UI reads `langgraph.json` to discover available graphs.
