# Quick Start Guide

Get up and running with the Research Workflow System in 5 minutes.

## Prerequisites

- Python 3.11+
- PostgreSQL with pgvector (optional, for full memory features)
- API keys for:
  - Anthropic (Claude)
  - OpenAI (GPT)
  - Tavily (web search)

## Installation

### 1. Clone/Setup the Project

```bash
cd research-workflow-system
```

### 2. Install Dependencies

**Option A: Using pip**
```bash
pip install -r requirements.txt
```

**Option B: Using uv (faster)**
```bash
pip install uv
uv pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
# Required:
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Optional:
OPENAI_API_KEY=your_key_here
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/research_db
```

### 4. (Optional) Set Up PostgreSQL

If you want full memory features:

```bash
# Install PostgreSQL and pgvector extension
# Then create database:
createdb research_db

# Install pgvector:
psql research_db -c "CREATE EXTENSION vector;"
```

## Usage

### Option 1: Python Script

```python
from src.main import ResearchWorkflowSystem

# Initialize
system = ResearchWorkflowSystem()

# Research a company
result = system.research_topic(
    topic="OpenAI",
    topic_type="company"
)

print(result)
```

### Option 2: Jupyter Notebook

```bash
jupyter notebook notebooks/01_getting_started.ipynb
```

## What Happens Next

The system will:

1. ✅ **Search the web** for information about your topic (3-5 queries)
2. ✅ **Track sources** visited and rate their quality
3. ✅ **Extract data** in structured format (JSON)
4. ✅ **Generate report** in Markdown format
5. ✅ **Save files** to `research_outputs/`
6. ✅ **Remember** for future cross-topic enhancement

## File Structure After First Run

```
research_outputs/
└── companies/
    └── OpenAI/
        ├── research_2025-12-05_abc123.md    # Main report
        ├── sources_tracker.json              # Source quality tracking
        ├── data_extracted.json               # Structured data
        └── metadata.json                     # Cross-references
```

## Current Implementation Status

| Phase | Status | Features |
|-------|--------|----------|
| Phase 1 | ✅ Complete | Project structure, basic workflow |
| Phase 2 | 🚧 In Progress | Core research agent, Tavily integration |
| Phase 3 | 📋 Planned | Memory system (LangMem) |
| Phase 4 | 📋 Planned | File management system |
| Phase 5 | 📋 Planned | Cross-topic learning |
| Phase 6 | 📋 Planned | Integration & testing |

## Next Steps

### For Development:

1. **Implement Tavily Search** (Phase 2)
   ```python
   # src/research_agent/tools.py
   from tavily import TavilyClient
   # Add real web search
   ```

2. **Add LangMem Integration** (Phase 3)
   ```python
   # src/memory/setup.py
   from langmem import create_manage_memory_tool
   # Set up persistent memory
   ```

3. **Complete File Manager** (Phase 4)
   ```python
   # src/files/file_manager.py
   # Full implementation provided in architecture doc
   ```

### For Testing:

```bash
# Run tests
pytest tests/

# Run a specific test
pytest tests/test_research_agent.py -v
```

### For Evaluation:

```bash
# Evaluate research quality
python evals/research_quality_eval.py

# Evaluate source accuracy
python evals/source_accuracy_eval.py
```

## Example Use Cases

### 1. Company Research
```python
system.research_topic("Anthropic", "company")
```

### 2. Market Analysis
```python
system.research_topic("Cloud AI Market 2025", "market")
```

### 3. Regional Research
```python
system.research_topic("European AI Regulations", "region")
```

### 4. Competitor Analysis
```python
system.research_topic("OpenAI vs Anthropic", "competitor")
```

## Troubleshooting

### No API Key Error
```
Error: ANTHROPIC_API_KEY not found
```
**Solution:** Make sure you've created `.env` file with your API keys.

### Import Error
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution:** Install dependencies: `pip install -r requirements.txt`

### PostgreSQL Connection Error
```
Error: could not connect to server
```
**Solution:** PostgreSQL is optional. Comment out `POSTGRES_CONNECTION_STRING` in `.env` to use in-memory storage.

## Need Help?

- Check the [README.md](README.md) for architecture details
- See [architecture documentation](docs/architecture.md)
- Review [implementation roadmap](README.md#implementation-roadmap)
- Study [reference implementations](README.md#key-repositories-to-use)

## What's Next?

Follow the implementation roadmap:
- Week 1-2: ✅ Foundation complete
- Week 3-4: 🚧 Core research agent (current)
- Week 5-6: 📋 Memory & learning system
- Week 7: 📋 File management
- Week 8-9: 📋 Cross-topic learning
- Week 10: 📋 Integration & testing
