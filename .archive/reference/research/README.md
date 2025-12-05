# Research Directory

This directory contains research materials, experiments, and architecture decisions for the Company Researcher System.

---

## Contents

### [decisions.md](decisions.md)
Architecture Decision Records (ADRs) documenting key technical and design choices.

**Examples:**
- Why we chose LangGraph over other orchestration frameworks
- Why Claude 3.5 Sonnet vs GPT-4
- Supervisor pattern vs Swarm pattern
- PostgreSQL + Qdrant vs single database

---

### [experiments.md](experiments.md)
Log of experiments, A/B tests, and prototypes.

**Examples:**
- Prompt engineering experiments
- Model comparison tests
- Agent coordination pattern tests
- Performance optimization results

---

### [references.md](references.md)
Curated list of papers, repositories, articles, and resources that informed the project.

**Examples:**
- Academic papers on multi-agent systems
- Open source repositories (Open Deep Research, LangGraph examples)
- Blog posts and tutorials
- Tools and libraries documentation

---

## How to Use This Directory

### Adding a New ADR (Architecture Decision Record)

When making a significant architectural decision:

1. Document it in [decisions.md](decisions.md)
2. Use the ADR template format:
   - **Context:** What problem are we solving?
   - **Decision:** What did we decide?
   - **Rationale:** Why did we make this choice?
   - **Alternatives Considered:** What else did we evaluate?
   - **Consequences:** What are the trade-offs?

### Logging Experiments

When running an experiment:

1. Document it in [experiments.md](experiments.md)
2. Include:
   - **Hypothesis:** What are we testing?
   - **Method:** How are we testing it?
   - **Results:** What did we find?
   - **Conclusions:** What did we learn?
   - **Next Steps:** What should we do based on results?

### Adding References

When finding useful resources:

1. Add to [references.md](references.md)
2. Categorize by type (papers, repos, articles, tools)
3. Add brief description of value/relevance
