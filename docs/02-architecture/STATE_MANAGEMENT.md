# State Management

This system uses **shared state dictionaries** to pass data between workflow nodes, plus reducers to safely merge concurrent updates.

---

## LangGraph workflow state (`OverallState`)

Authoritative definition:

- `src/company_researcher/state.py`

Key idea: several fields are annotated with reducers, so multiple nodes can update them safely:

- `search_results`: `Annotated[List[Dict[str, Any]], operator.add]` (append semantics)
- `sources`: `Annotated[List[Dict[str, str]], operator.add]` (append semantics)
- `agent_outputs`: `Annotated[Optional[Dict[str, Any]], merge_dicts]` (merge semantics)
- `total_cost`: `Annotated[float, operator.add]` (sum semantics)
- `total_tokens`: `Annotated[Dict[str, int], add_tokens]` (sum-per-field)

Reducers are implemented in the same file:

- `merge_dicts()`
- `add_tokens()`

---

## Creating initial state

Workflows that use `OverallState` generally start from:

- `create_initial_state(company_name: str)` in `src/company_researcher/state.py`

That function fills required fields with sensible defaults (empty lists/dicts, counters, timestamps).

---

## Output state

The “final output” for some workflows is normalized via:

- `create_output_state(state: OverallState) -> OutputState` in `src/company_researcher/state.py`

This provides a compact payload:

- report path
- duration, cost, tokens
- sources count, quality score, iterations

---

## Orchestration engine state (`WorkflowState`)

The orchestration engine has its own state model:

- `src/company_researcher/orchestration/workflow/models.py`

This is a dataclass that tracks:

- execution status, current node, completed nodes
- `data` payload (dict) for results
- timing and total cost
