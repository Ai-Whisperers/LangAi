# Agent Patterns

This repo implements “agents” as Python classes/functions, and integrates them into workflows using node functions that **read from state and return partial state updates**.

---

## Where agents live

- `src/company_researcher/agents/`

The `agents` package also exports many “node functions” used directly by workflows, for example:

- `researcher_agent_node`
- `financial_agent_node`
- `market_agent_node`
- `product_agent_node`
- `competitor_scout_agent_node`
- `logic_critic_agent_node`

See:

- `src/company_researcher/agents/__init__.py`

---

## Base infrastructure (node pattern)

Core utilities live under:

- `src/company_researcher/agents/base/`

Common pattern:

1. Node reads `company_name`, `search_results`, and/or previous `agent_outputs`
2. Node calls LLM/providers (via integrations/llm modules)
3. Node returns a **dict** with a partial update, e.g.:
   - new/updated `agent_outputs`
   - cost/token increments

Workflows then merge these updates into the shared state using reducers (see `docs/02-architecture/STATE_MANAGEMENT.md`).

---

## Parallel-safe updates

When agents run in parallel (fan-out), their contributions must merge safely. The shared state supports this via:

- list append reducers (`operator.add`)
- dict merge reducers (`merge_dicts`)
- numeric accumulators (`operator.add`, `add_tokens`)

Authoritative reducers:

- `src/company_researcher/state.py`
