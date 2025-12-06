# Documentation Archive

**IMPORTANT**: These documents describe a **different project** (FastAPI/RAG/Vector DB system).

The files in this archive are **NOT related** to the current Company Researcher multi-agent system.

---

## What This Archive Contains

This directory contains legacy documentation from a **previous project** that used:
- FastAPI for API endpoints
- Vector databases (Chroma, Weaviate) for RAG
- LLM routing patterns
- Different architecture than Company Researcher

---

## Why These Are Archived

The current project is the **Company Researcher** multi-agent system (Phase 4), which:
- Uses LangGraph for agent orchestration (not FastAPI)
- Uses Tavily for web search (not vector databases)
- Has 5 specialized agents running in parallel
- Focuses on company research (not general RAG)

**These docs were causing confusion** because they described a completely different system architecture.

---

## Archived Documents

| Document | Original Purpose | Why Archived |
|----------|-----------------|--------------|
| `fastapi-architecture.md` | FastAPI/RAG system architecture | Different project |
| `fastapi-integration.md` | FastAPI implementation patterns | Not used in current system |
| `fastapi-getting-started.md` | FastAPI setup guide | Different tech stack |
| `vector-databases.md` | Chroma/Weaviate comparison | Not used (current system uses Tavily) |

---

## For Current Project Documentation

See the **Company Researcher** documentation instead:

**Getting Started**:
- [Installation Guide](../../INSTALLATION.md)
- [Quick Start](../../QUICK_START.md)
- [User Guide](../company-researcher/USER_GUIDE.md)

**Technical Documentation**:
- [Architecture](../company-researcher/ARCHITECTURE.md) - LangGraph multi-agent architecture
- [Implementation](../company-researcher/IMPLEMENTATION.md) - How current system works
- [API Reference](../company-researcher/API_REFERENCE.md) - Current system API

**Project Info**:
- [Main README](../../README.md) - Current project overview
- [Master Plan](../planning/MASTER_20_PHASE_PLAN.md) - Future roadmap

---

## If You Need These Docs

These documents may still be useful for reference purposes:

**Use cases**:
- Learning FastAPI patterns
- Understanding RAG architectures
- Vector database comparison
- LLM routing strategies

**Note**: These patterns may be incorporated into future phases of the Company Researcher system (see [Master Plan](../planning/MASTER_20_PHASE_PLAN.md)), but they are not part of Phase 4.

---

## Future Vector DB Usage

The Company Researcher **may** use vector databases in future phases:

- **Phase 11**: Dual-layer memory system (hot/cold storage)
- **Phase 19**: Advanced memory features (semantic search, entity tracking)

When implemented, we'll create **new documentation** specific to the Company Researcher architecture.

---

**Summary**: These docs are from a different project. For the current Company Researcher system, see [docs/company-researcher/](../company-researcher/).

**Archived**: December 5, 2025
**Reason**: Confusion prevention - these describe different system architecture
