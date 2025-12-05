# Research Workflow System

A comprehensive multi-topic research system built on LangChain/LangGraph that:
- Researches companies, markets, regions, and competitors
- Generates structured files tracking all findings
- Remembers source quality (good/bad websites)
- Cross-references and enhances past research with new insights
- Learns and improves over time

## Architecture

Based on LangChain AI repos:
- **Core Research:** open_deep_research, company-researcher, data-enrichment
- **Memory System:** langmem, memory-agent
- **Orchestration:** langgraph
- **Storage:** langchain-postgres
- **Evaluation:** openevals, agentevals

## Features

### 1. Multi-Topic Research Agent
- Company research
- Market analysis
- Regional insights
- Competitor analysis
- Concurrent web searches (3-5 queries per topic)
- Real-time source quality scoring

### 2. Memory & Learning System
- Hot path memory (active research)
- Persistent memory (cross-session)
- Semantic memory (cross-topic)
- Source quality database
- Research preference learning

### 3. File Generation & Tracking
- Markdown research reports
- JSON source trackers
- Structured data extraction
- Metadata management
- Cross-reference linking

### 4. Cross-Topic Enhancement
- Automatic related topic discovery
- Context engineering (compress, select, isolate)
- Bidirectional research updates
- Knowledge graph connections

### 5. Source Quality Learning
- Website rating system (0-1 score)
- Visit count tracking
- Success rate calculation
- Pattern learning (e.g., .gov = reliable)
- Continuous re-evaluation

## Installation

```bash
# Clone the repository
cd research-workflow-system

# Install dependencies (using uv for speed)
pip install uv
uv pip install -r requirements.txt

# Or use traditional pip
pip install langchain langgraph langmem
pip install langchain-postgres
pip install tavily-python
pip install anthropic openai
```

## Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/research_db
```

## Quick Start

```python
from src.main import ResearchWorkflowSystem

# Initialize system
system = ResearchWorkflowSystem()

# Research a company
result = system.research_topic(
    topic="OpenAI",
    topic_type="company"
)

# Research a market (auto-enhanced with OpenAI insights)
result2 = system.research_topic(
    topic="AI Language Models Market",
    topic_type="market"
)

# View generated files
print(result["files"])
# {
#   "report": "research_outputs/companies/OpenAI/research_2025-12-05_abc123.md",
#   "tracker": "research_outputs/companies/OpenAI/sources_tracker.json",
#   "data": "research_outputs/companies/OpenAI/data_extracted.json",
#   "metadata": "research_outputs/companies/OpenAI/metadata.json"
# }
```

## File Structure

```
research_outputs/
├── companies/
│   └── OpenAI/
│       ├── research_2025-12-05_abc123.md       # Markdown report
│       ├── sources_tracker.json                 # Source quality tracking
│       ├── data_extracted.json                  # Structured data
│       └── metadata.json                        # Cross-references
├── markets/
├── regions/
└── source_quality_db/
    └── website_ratings.json                     # Global source quality
```

## Development

```bash
# Run tests
pytest tests/

# Run quality evaluation
python evals/research_quality_eval.py

# View demos
jupyter notebook notebooks/01_research_workflow_demo.ipynb
```

## Roadmap

- [x] Phase 1: Foundation (Week 1-2)
- [x] Phase 2: Core Research Agent (Week 3-4)
- [ ] Phase 3: Memory & Learning System (Week 5-6)
- [ ] Phase 4: File Management System (Week 7)
- [ ] Phase 5: Cross-Topic Learning (Week 8-9)
- [ ] Phase 6: Integration & Testing (Week 10)

## References

- [open_deep_research](https://github.com/langchain-ai/open_deep_research)
- [company-researcher](https://github.com/langchain-ai/company-researcher)
- [memory-agent](https://github.com/langchain-ai/memory-agent)
- [langmem](https://github.com/langchain-ai/langmem)
- [context_engineering](https://github.com/langchain-ai/context_engineering)

## License

MIT
