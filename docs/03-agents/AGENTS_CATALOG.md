# Agents Catalog (code map)

This is a “pointer map” from agent names to the authoritative code that implements them.

---

## Node functions used by workflows

The workflows commonly import node functions directly from `company_researcher.agents`.

Authoritative export list:

- `src/company_researcher/agents/__init__.py`

Examples (nodes):

- Researcher: `researcher_agent_node` (`agents/core/researcher.py`)
- Analyst: `analyst_agent_node` (`agents/core/analyst.py`)
- Synthesizer: `synthesizer_agent_node` (`agents/core/synthesizer.py`)
- Financial: `financial_agent_node` (`agents/financial/financial.py`)
- Market: `market_agent_node` (`agents/market/market.py`)
- Product: `product_agent_node` (`agents/specialized/product.py`)
- Competitor scout: `competitor_scout_agent_node` (`agents/market/competitor_scout.py`)
- Logic critic: `logic_critic_agent_node` (`agents/quality/logic_critic.py`)

---

## How agents “plug into” workflows

Workflows call these node functions in one of two styles:

- **Sequential pipelines** (comprehensive workflow): `src/company_researcher/workflows/comprehensive_research.py`
- **Fan-out/fan-in** (parallel workflow): `src/company_researcher/workflows/parallel_agent_research.py`

Nodes communicate through shared state; see:

- `docs/02-architecture/STATE_MANAGEMENT.md`
