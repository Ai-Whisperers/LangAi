# LangGraph Studio Installation & Usage Guide

**Status:** ✅ Installed and Ready
**Date:** 2025-12-05

---

## ✅ What's Installed

- [x] LangGraph (v1.0.3)
- [x] LangGraph CLI (v0.4.7)
- [x] Configuration file: `langgraph.json`
- [x] Example graphs: `src/graphs/`
  - `simple_graph.py` - Basic test graph
  - `research_graph.py` - Company research workflow

---

## 🚀 Quick Start

### Option 1: Use LangGraph Desktop App (Recommended)

**Download:**
- **Windows:** https://github.com/langchain-ai/langgraph-studio/releases/latest
- Look for: `LangGraph-Studio-Setup-x.x.x.exe`

**Steps:**
1. Download and install the desktop app
2. Open LangGraph Studio
3. Click "Open Project"
4. Select this directory: `C:\Users\Alejandro\Documents\Ivan\Work\Lang ai`
5. Studio will read `langgraph.json` and show your graphs!

**Benefits:**
- Beautiful visual interface
- No command line needed
- Built-in graph editor
- State inspection
- Debugging tools

---

### Option 2: Use CLI (Already Installed)

**Start the dev server:**

```powershell
# Navigate to project
cd "C:\Users\Alejandro\Documents\Ivan\Work\Lang ai"

# Activate your virtual environment
.\venv\Scripts\activate

# Start LangGraph Studio server
python -m langgraph_cli dev

# OR use full path to langgraph command
C:\Users\Alejandro\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\langgraph.exe dev
```

**Access:**
- Browser: http://localhost:8123
- API: http://localhost:8123/docs

---

## 📁 Project Structure

```
Lang ai/
├── langgraph.json          # Configuration (points to graphs)
├── .env                    # Your API keys (auto-loaded)
│
├── src/
│   └── graphs/
│       ├── simple_graph.py      # Test graph (3 steps)
│       └── research_graph.py    # Company research workflow
│
└── outputs/                # Research reports saved here
```

---

## 🎨 Available Graphs

### 1. Simple Test Graph

**File:** `src/graphs/simple_graph.py`
**Purpose:** Verify LangGraph Studio is working

**Workflow:**
```
START → step1 → step2 → step3 → END
```

**Test it:**
```bash
python src/graphs/simple_graph.py
```

**Expected Output:**
```
[OK] Graph executed successfully!
Output: Processed: Hello LangGraph! | Enhanced | Complete!
Steps completed: 3
```

**In Studio:**
1. Select graph: `simple_test`
2. Click "Run"
3. Input: `{"input": "Test", "step": 0}`
4. Watch it execute step-by-step!

---

### 2. Company Research Graph

**File:** `src/graphs/research_graph.py`
**Purpose:** Visualize complete company research workflow

**Workflow:**
```
START
  ↓
generate_queries (Claude generates 5 search queries)
  ↓
search_web (Tavily searches with all queries)
  ↓
extract_data (Claude extracts structured info)
  ↓
generate_report (Creates markdown report)
  ↓
END
```

**Test it:**
```bash
# Make sure you have API keys in .env!
python src/graphs/research_graph.py
```

**Expected Output:**
```
============================================================
  Company Research Graph Test
============================================================

Generating queries for: Tesla
Generated 5 queries
Searching web with 5 queries...
  Searching: Tesla company overview...
  Searching: Tesla revenue financials...
  ...
Found 15 search results
Extracting data from 15 results...
Extracted data for: Tesla, Inc.
Generating report...
Report generated (2341 characters)

============================================================
  Research Complete!
============================================================

Company: Tesla
Queries Generated: 5
Search Results: 15
Total Cost: $0.3214
Total Tokens: 12453

[OK] Report generated (2341 chars)
```

**In Studio:**
1. Select graph: `company_research`
2. Click "Run"
3. Input:
   ```json
   {
     "company_name": "Tesla",
     "queries": [],
     "search_results": [],
     "extracted_data": {},
     "report": "",
     "total_cost": 0.0,
     "total_tokens": 0,
     "error": null
   }
   ```
4. Watch each node execute!
5. Inspect state at each step
6. See the final report

---

## 🎯 Using LangGraph Studio

### Visual Features

**1. Graph Visualization**
- See your workflow as a flowchart
- Nodes = Steps in your process
- Edges = Flow between steps
- START/END nodes clearly marked

**2. State Inspection**
- Click any node to see its state
- View inputs and outputs
- Track how data flows through

**3. Execution Controls**
- **Run:** Execute the entire graph
- **Step:** Execute one node at a time
- **Pause:** Pause execution
- **Reset:** Start over

**4. Debugging**
- Set breakpoints on nodes
- Inspect intermediate results
- See exactly where errors occur
- View full stack traces

**5. Streaming**
- Watch results appear in real-time
- See each node execute
- Monitor progress

---

## 💡 Tips & Tricks

### Debugging Your Graph

**Problem:** Graph doesn't execute
**Solution:**
1. Check `langgraph.json` syntax
2. Verify graph imports work: `python src/graphs/research_graph.py`
3. Check API keys in `.env`
4. Look at Studio console for errors

**Problem:** Can't see my graph
**Solution:**
1. Restart Studio
2. Check graph is exported: `graph = workflow.compile()`
3. Verify path in `langgraph.json` is correct

**Problem:** Node fails during execution
**Solution:**
1. Click the failed node in Studio
2. View the error message
3. Check input state was valid
4. Test the node function directly in Python

---

### Modifying Graphs

**To add a new node:**

```python
# 1. Define the function
def new_node(state: ResearchState) -> dict:
    """What this node does"""
    result = do_something(state['input'])
    return {"output": result}

# 2. Add to graph
workflow.add_node("new_node_name", new_node)

# 3. Connect it
workflow.add_edge("previous_node", "new_node_name")
workflow.add_edge("new_node_name", "next_node")

# 4. Recompile
graph = workflow.compile()
```

**To change the flow:**

```python
# Conditional routing
def should_continue(state):
    if state['quality_score'] > 0.8:
        return END
    else:
        return "retry_node"

workflow.add_conditional_edges(
    "check_quality",
    should_continue
)
```

---

## 🔧 Configuration Reference

### langgraph.json

```json
{
  "dependencies": [
    "."  // Install from current directory (requirements.txt)
  ],
  "graphs": {
    "simple_test": "./src/graphs/simple_graph.py:graph",
    "company_research": "./src/graphs/research_graph.py:graph"
  },
  "env": ".env"  // Load environment variables
}
```

**Fields:**
- `dependencies`: What to install (pip packages or directories)
- `graphs`: Map of graph names to file paths
  - Format: `"name": "path/to/file.py:variable_name"`
- `env`: Path to environment file (loads API keys)

---

## 📊 Monitoring & Observability

### LangSmith Integration

LangSmith tracing is optional. If enabled in `.env`, LangGraph runs can be traced to LangSmith.

Typical `.env` settings:
```bash
LANGCHAIN_TRACING_V2=true
LANGSMITH_API_KEY=lsv2_...
LANGCHAIN_PROJECT=langai-research
```

**View traces:**
1. Go to https://smith.langchain.com/
2. Project: value of `LANGCHAIN_PROJECT` (example: `langai-research`)
3. See every execution with:
   - Input/output for each node
   - Token usage
   - Costs
   - Latency
   - Errors

### Langfuse Integration

Langfuse is also supported (see `env.example` for `LANGFUSE_*` variables). Add a Langfuse callback to a graph invocation:

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Use in graph
graph = workflow.compile()
result = graph.invoke(
    state,
    config={"callbacks": [langfuse_handler]}
)
```

---

## 🚀 Next Steps

### 1. Explore the Simple Graph (5 min)
```bash
# Run it
python src/graphs/simple_graph.py

# Open in Studio and watch it execute
```

### 2. Test Company Research (10 min)
```bash
# Make sure API keys are set
echo $env:ANTHROPIC_API_KEY  # PowerShell
# OR
echo %ANTHROPIC_API_KEY%     # CMD

# Run it
python src/graphs/research_graph.py

# View in Studio - watch it research Tesla!
```

### 3. Build Your Own Graph (30 min)

Create `src/graphs/my_graph.py`:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class MyState(TypedDict):
    input: str
    output: str

def my_node(state):
    return {"output": f"Processed: {state['input']}"}

workflow = StateGraph(MyState)
workflow.add_node("process", my_node)
workflow.add_edge(START, "process")
workflow.add_edge("process", END)

graph = workflow.compile()
```

Add to `langgraph.json`:
```json
{
  "graphs": {
    "my_custom_graph": "./src/graphs/my_graph.py:graph"
  }
}
```

Reload Studio → See your graph!

---

## 📚 Resources

### Documentation
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **LangGraph Studio:** https://github.com/langchain-ai/langgraph-studio
- **Examples:** https://github.com/langchain-ai/langgraph/tree/main/examples

### Tutorials
- **LangGraph Quickstart:** https://langchain-ai.github.io/langgraph/tutorials/introduction/
- **Multi-Agent Systems:** https://langchain-ai.github.io/langgraph/tutorials/multi_agent/
- **Human-in-the-Loop:** https://langchain-ai.github.io/langgraph/tutorials/human_in_the_loop/

### Community
- **Discord:** https://discord.gg/langchain
- **Forum:** https://community.langchain.com/
- **GitHub:** https://github.com/langchain-ai/langgraph/discussions

---

## ❓ Troubleshooting

### Issue: "Cannot find graph"
```
Error: Could not import graph from src/graphs/research_graph.py:graph
```

**Fix:**
1. Check the file exports `graph` variable
2. Run `python src/graphs/research_graph.py` to test import
3. Verify path in `langgraph.json` is correct

---

### Issue: "Module not found"
```
ModuleNotFoundError: No module named 'anthropic'
```

**Fix:**
```bash
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Issue: "API key not found"
```
Error: ANTHROPIC_API_KEY environment variable not set
```

**Fix:**
1. Check `.env` file exists
2. Verify API keys are set
3. Restart Studio (it loads .env on startup)

---

### Issue: Studio won't start
```
Error: Port 8123 already in use
```

**Fix:**
```powershell
# Find process using port 8123
netstat -ano | findstr :8123

# Kill it
taskkill /PID <process_id> /F

# Or use different port
python -m langgraph_cli dev --port 8124
```

---

## ✅ Success Checklist

- [ ] LangGraph Desktop App installed OR CLI working
- [ ] Can open project in Studio
- [ ] Can see both graphs (simple_test, company_research)
- [ ] Can run simple_test graph successfully
- [ ] Can run company_research graph successfully
- [ ] Can inspect state at each node
- [ ] Can view execution traces in LangSmith
- [ ] Understand how to add new nodes
- [ ] Understand how to modify workflow

---

**You're all set! LangGraph Studio is ready to visualize your Company Research workflow.** 🎉

**Next:** Open LangGraph Studio → Select `company_research` → Click Run → Watch it research Tesla!
