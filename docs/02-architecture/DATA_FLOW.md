# Data Flow

This document explains **how data moves** through the system during a research run.

---

## 1) Inputs

Most flows start from one of these inputs:

- **CLI** (`run_research.py`): `--company`, `--profile`, or `--market`
- **API** (`company_researcher.api.*`): JSON payloads like “start research”
- **LangGraph Studio** (`langgraph.json`): graph input state

At minimum, workflows require:

- `company_name` (string)

---

## 2) Core research state (LangGraph workflows)

The “workflow state” is a dictionary shaped by TypedDict schemas (plus reducers for parallel execution).

Authoritative schema:

- `src/company_researcher/state.py`

Key categories in `OverallState`:

- **Search**: `search_queries`, `search_results`, `sources`
- **Analysis outputs**: `company_overview`, `key_metrics`, `products_services`, `competitors`, `key_insights`
- **Quality loop**: `quality_score`, `missing_info`, `iteration_count`
- **Costs/metrics**: `total_cost`, `total_tokens`, `start_time`
- **Agent coordination**: `agent_outputs` (merged across parallel nodes)

---

## 3) Workflow layers

There are multiple ways to orchestrate research:

### A) LangGraph workflows (`src/company_researcher/workflows/`)

Example: **comprehensive workflow**

- Builder: `src/company_researcher/workflows/comprehensive_research.py`
- Node implementations: `src/company_researcher/workflows/nodes/`

Typical flow:

1. **Discovery**: loads prior research, finds gaps (`discovery_node`)
2. **Query generation**: generates search queries
3. **Search + enrichment**: web search, financial data, news
4. **Analysis nodes**: core/financial/market/esg/brand/sentiment
5. **Quality**: extract structured facts + quality check + conditional iteration
6. **Advanced analysis**: competitive matrix, risk, investment thesis
7. **Output**: enrich executive summary then write markdown + metrics

Output writing is handled in:

- `src/company_researcher/workflows/nodes/comprehensive_output_nodes.py`

### B) Orchestration engine (`src/company_researcher/orchestration/`)

The CLI default path uses a separate workflow executor that returns a `WorkflowState` object (with:
`status`, `completed_nodes`, `data`, `total_cost`, etc.).

---

## 4) Outputs on disk

Output locations depend on the execution path:

- LangGraph comprehensive workflow: `config.output_dir` (default: `outputs/`)
- CLI wrapper: `--output` flag (default: `outputs/research/`)

The full report file is typically named `00_full_report.md` and saved under a company-specific folder.
