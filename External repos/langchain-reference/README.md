# LangChain Reference Library 📚

Complete collection of LangChain repositories organized for research workflow development.

**Total Repositories:** 60+
**Last Updated:** 2025-12-05

---

## 📁 Folder Structure

```
langchain-reference/
├── 01-research-agents/          # Company, market, competitor research
├── 02-deep-agents/              # Advanced agent frameworks
├── 03-multi-agent-patterns/     # Supervisor & swarm patterns
├── 04-production-apps/          # Production-ready applications
├── 05-memory-learning/          # Memory systems & learning
├── 06-mcp-integration/          # Model Context Protocol
├── 07-evaluation-testing/       # Evaluation & testing tools
├── 08-templates-starters/       # Project templates
├── 09-tools-utilities/          # Tools & code generation
├── 10-docs-tutorials/           # Documentation & tutorials
├── 11-langsmith/                # LangSmith SDKs & tools
└── 12-llama-meta/               # Meta LLaMA integrations
```

---

## 01. Research Agents 🔍

**Focus:** Multi-topic research (companies, markets, regions, competitors)

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [company-researcher](./01-research-agents/company-researcher) | 211 | Company research | 3-phase workflow (search, extract, reflect) |
| [people-researcher](./01-research-agents/people-researcher) | 153 | People research | Person-focused research agent |
| [competitor-analysis-bot](./01-research-agents/competitor-analysis-bot) | 37 | Competitor analysis | Competitive intelligence |
| [generic-researcher](./01-research-agents/generic-researcher) | 7 | Generic research | TypeScript research agent |
| [multi-modal-researcher](./01-research-agents/multi-modal-researcher) | 582 | Multimodal research | Text + image research |
| [rag-research-agent-template](./01-research-agents/rag-research-agent-template) | 278 | RAG research | Retrieval-augmented research |
| [rag-research-agent-template-js](./01-research-agents/rag-research-agent-template-js) | 35 | RAG research (JS) | TypeScript RAG template |
| [url_scraper](./01-research-agents/url_scraper) | 9 | URL scraping | Barebones scraper with evals |
| [web-explorer](./01-research-agents/web-explorer) | 387 | Web exploration | Interactive web research |

**When to Use:**
- Building company/market/region research tools
- Implementing web scraping with quality scoring
- Creating RAG-based research workflows

---

## 02. Deep Agents 🤖

**Focus:** Advanced agent frameworks with planning & subagents

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [deepagents](./02-deep-agents/deepagents) | 6.8k | Advanced agent harness | Planning, filesystem backend, subagents |
| [deep-agents-ui](./02-deep-agents/deep-agents-ui) | 1.2k | DeepAgents UI | Custom UI for deep agents |
| [stateful-deepagents](./02-deep-agents/stateful-deepagents) | 0 | Stateful demos | Stateful agent examples |
| [deepagents-quickstarts](./02-deep-agents/deepagents-quickstarts) | 350 | Quickstart examples | Common agent patterns |

**When to Use:**
- Building complex multi-step agents
- Implementing planning & reasoning
- Creating subagent hierarchies

---

## 03. Multi-Agent Patterns 👥

**Focus:** Coordination patterns for multiple agents

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [langgraph-supervisor-py](./03-multi-agent-patterns/langgraph-supervisor-py) | 1.4k | Supervisor pattern | Multi-agent coordination |
| [langgraph-swarm-py](./03-multi-agent-patterns/langgraph-swarm-py) | 1.3k | Swarm pattern | Collaborative agent swarms |

**When to Use:**
- Coordinating multiple specialized agents
- Implementing hierarchical agent systems
- Building collaborative agent workflows

---

## 04. Production Apps 🚀

**Focus:** Production-ready reference implementations

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [open_deep_research](./04-production-apps/open_deep_research) | 9.8k | Deep research agent | Multi-model, MCP support, benchmarked |
| [local-deep-researcher](./04-production-apps/local-deep-researcher) | 8.4k | Local research | Fully local web research |
| [chat-langchain](./04-production-apps/chat-langchain) | 6.2k | Chat interface | LangChain docs chat |
| [executive-ai-assistant](./04-production-apps/executive-ai-assistant) | 2.1k | Executive assistant | AI assistant for executives |
| [data-enrichment](./04-production-apps/data-enrichment) | 209 | Data enrichment | Web research + data extraction |
| [retrieval-agent-template](./04-production-apps/retrieval-agent-template) | 145 | RAG agent | Retrieval agent template |

**When to Use:**
- Learning production architecture patterns
- Understanding multi-model orchestration
- Studying benchmarked implementations

**⭐ Priority:** Study `open_deep_research` first - it's the most comprehensive

---

## 05. Memory & Learning 🧠

**Focus:** Persistent memory, context management, learning

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [langmem](./05-memory-learning/langmem) | 1.2k | Memory management | Hot path + persistent memory |
| [memory-agent](./05-memory-learning/memory-agent) | 383 | Memory agent | User-scoped persistent memory |
| [context_engineering](./05-memory-learning/context_engineering) | 133 | Context optimization | Write, select, compress, isolate |
| [learning-langchain](./05-memory-learning/learning-langchain) | 233 | Learning examples | Educational examples |
| [langgraph-example](./05-memory-learning/langgraph-example) | 437 | LangGraph examples | Example implementations |

**When to Use:**
- Implementing persistent memory across sessions
- Managing context windows effectively
- Building learning systems that improve over time

**⭐ Priority:** Study `langmem` + `context_engineering` for your research system

---

## 06. MCP Integration 🔌

**Focus:** Model Context Protocol tool integration

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [langchain-mcp-adapters](./06-mcp-integration/langchain-mcp-adapters) | 3.2k | MCP adapters | Convert MCP tools to LangChain |
| [langsmith-mcp-server](./06-mcp-integration/langsmith-mcp-server) | 51 | LangSmith MCP | MCP server for LangSmith |
| [mcpdoc](./06-mcp-integration/mcpdoc) | 867 | MCP docs | Expose llms-txt to IDEs |
| [mcp-agent](./06-mcp-integration/mcp-agent) | 9 | MCP agent | MCP-based agent |

**When to Use:**
- Expanding agent tool capabilities
- Integrating with Anthropic MCP ecosystem
- Building custom MCP servers

---

## 07. Evaluation & Testing 🧪

**Focus:** Quality assurance, benchmarking, evaluation

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [openevals](./07-evaluation-testing/openevals) | 822 | LLM evaluators | Readymade eval functions |
| [agentevals](./07-evaluation-testing/agentevals) | 409 | Agent evaluators | Agent trajectory evaluation |
| [claude-code-evals](./07-evaluation-testing/claude-code-evals) | 53 | Claude Code evals | Configuration studies |

**When to Use:**
- Evaluating research quality
- Benchmarking agent performance
- Testing agent trajectories

---

## 08. Templates & Starters 🎯

**Focus:** Project templates and quickstart boilerplates

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [new-langgraph-project](./08-templates-starters/new-langgraph-project) | 195 | LangGraph starter | Empty project template |
| [memory-template](./08-templates-starters/memory-template) | 210 | Memory template | Memory agent template |
| [langchain-integration-template](./08-templates-starters/langchain-integration-template) | 2 | Integration template | Package template |

**When to Use:**
- Starting new LangGraph projects
- Creating custom integrations
- Building agents with memory

---

## 09. Tools & Utilities 🛠️

**Focus:** Code generation, extraction, utilities

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [langchain-extract](./09-tools-utilities/langchain-extract) | 1.2k | Data extraction | Structured data extraction |
| [langchain-unstructured](./09-tools-utilities/langchain-unstructured) | 13 | Document processing | Unstructured doc handling |
| [langchain-sandbox](./09-tools-utilities/langchain-sandbox) | 204 | Safe execution | Pyodide sandbox |
| [text-split-explorer](./09-tools-utilities/text-split-explorer) | 267 | Text splitting | Chunking strategies |
| [langgraph-gen-py](./09-tools-utilities/langgraph-gen-py) | 101 | Code generation | Generate LangGraph stubs |
| [langgraph-builder](./09-tools-utilities/langgraph-builder) | 222 | Visual builder | Visual graph builder |
| [langgraph-bigtool](./09-tools-utilities/langgraph-bigtool) | 479 | Large tool sets | Many tools handling |
| [langgraph-codeact](./09-tools-utilities/langgraph-codeact) | 667 | Code execution | Code execution agent |
| [langgraph-cua-py](./09-tools-utilities/langgraph-cua-py) | 191 | Computer use | Computer use agent |

**When to Use:**
- Extracting structured data from sources
- Processing unstructured documents
- Building code generation tools
- Handling large numbers of tools

---

## 10. Documentation & Tutorials 📖

**Focus:** Official docs, examples, learning resources

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [docs](./10-docs-tutorials/docs) | 132 | Official docs | LangChain documentation |
| [cookbooks](./10-docs-tutorials/cookbooks) | 2 | Code snippets | Design patterns |
| [langchain-teacher](./10-docs-tutorials/langchain-teacher) | 269 | Teaching tool | Teach LangChain with LangChain |
| [cicd-pipeline-example](./10-docs-tutorials/cicd-pipeline-example) | 27 | CI/CD | Deployment pipeline |
| [langserve-launch-example](./10-docs-tutorials/langserve-launch-example) | 79 | LangServe | Deployment example |

**When to Use:**
- Learning LangChain concepts
- Setting up CI/CD pipelines
- Understanding best practices

---

## 11. LangSmith 📊

**Focus:** Observability, monitoring, debugging

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [langsmith-sdk](./11-langsmith/langsmith-sdk) | 692 | LangSmith SDK | Python/JS SDK |
| [langsmith-cookbook](./11-langsmith/langsmith-cookbook) | 980 | Recipes | LangSmith examples |
| [langsmith-starter-kit](./11-langsmith/langsmith-starter-kit) | 4 | Starter kit | Getting started resources |

**When to Use:**
- Adding observability to agents
- Debugging agent behavior
- Tracking research quality

---

## 12. LLaMA & Meta 🦙

**Focus:** Meta LLaMA model integrations

| Repo | Stars | Purpose | Key Features |
|------|-------|---------|--------------|
| [langchain-meta](./12-llama-meta/langchain-meta) | 8 | Meta integration | Meta models support |
| [langchain-llama-stack](./12-llama-meta/langchain-llama-stack) | 2 | LLaMA Stack | LLaMA Stack integration |

**When to Use:**
- Using Meta's LLaMA models
- Integrating with LLaMA Stack

---

## 🎯 Quick Start Guides

### For Research Workflow System

**Priority Order:**

1. **Start Here** (Week 1-2):
   - [open_deep_research](./04-production-apps/open_deep_research) - Study architecture
   - [company-researcher](./01-research-agents/company-researcher) - 3-phase workflow
   - [data-enrichment](./04-production-apps/data-enrichment) - Data extraction

2. **Memory System** (Week 3-4):
   - [langmem](./05-memory-learning/langmem) - Memory management
   - [memory-agent](./05-memory-learning/memory-agent) - Persistence patterns
   - [context_engineering](./05-memory-learning/context_engineering) - Context optimization

3. **Multi-Agent Patterns** (Week 5-6):
   - [langgraph-supervisor-py](./03-multi-agent-patterns/langgraph-supervisor-py) - Coordination
   - [langgraph-swarm-py](./03-multi-agent-patterns/langgraph-swarm-py) - Collaboration

4. **Evaluation** (Week 7-8):
   - [openevals](./07-evaluation-testing/openevals) - Quality evaluation
   - [agentevals](./07-evaluation-testing/agentevals) - Agent evaluation

---

## 🔥 Most Important Repos for Your Project

### **Must Study (Top Priority):**

1. **[open_deep_research](./04-production-apps/open_deep_research)** ⭐⭐⭐
   - Most comprehensive research architecture
   - Multi-model orchestration
   - Benchmarked performance (#6 on leaderboard)
   - MCP support
   - **Start here!**

2. **[company-researcher](./01-research-agents/company-researcher)** ⭐⭐⭐
   - Clean 3-phase workflow
   - Easy to understand
   - Production-ready patterns
   - JSON schema extraction

3. **[langmem](./05-memory-learning/langmem)** ⭐⭐⭐
   - Critical for cross-topic learning
   - Semantic search
   - Hot path + persistent memory

4. **[context_engineering](./05-memory-learning/context_engineering)** ⭐⭐
   - Essential for context management
   - 4 key strategies: write, select, compress, isolate
   - Token optimization techniques

5. **[memory-agent](./05-memory-learning/memory-agent)** ⭐⭐
   - User-scoped persistence
   - Cross-session memory
   - Store-based architecture

### **Very Useful (Study Next):**

6. [data-enrichment](./04-production-apps/data-enrichment) - Web research patterns
7. [langgraph-supervisor-py](./03-multi-agent-patterns/langgraph-supervisor-py) - Multi-agent coordination
8. [openevals](./07-evaluation-testing/openevals) - Research quality evaluation
9. [web-explorer](./01-research-agents/web-explorer) - Web exploration patterns
10. [multi-modal-researcher](./01-research-agents/multi-modal-researcher) - Multimodal research

---

## 📚 Learning Path

### **Phase 1: Understanding (Week 1-2)**
```bash
# Study these in order:
cd 04-production-apps/open_deep_research
# Read README, study graph.py, understand architecture

cd ../../01-research-agents/company-researcher
# Run examples, understand 3-phase workflow

cd ../data-enrichment
# Study data extraction patterns
```

### **Phase 2: Memory Systems (Week 3-4)**
```bash
cd ../../05-memory-learning/langmem
# Study memory tools, run examples

cd ../memory-agent
# Understand persistence, run demos

cd ../context_engineering
# Study notebooks, learn optimization techniques
```

### **Phase 3: Implementation (Week 5-10)**
- Apply patterns to your research-workflow-system
- Integrate memory management
- Add cross-topic learning
- Implement evaluation

---

## 🔧 Common Commands

### **Explore a Repo:**
```bash
cd 01-research-agents/company-researcher
cat README.md
ls -la
code .  # Open in VS Code
```

### **Run an Example:**
```bash
cd 04-production-apps/open_deep_research
pip install -r requirements.txt
# Follow README instructions
```

### **Search for Patterns:**
```bash
# Find all files with "memory" in name
find . -name "*memory*"

# Search for "LangGraph" usage
grep -r "LangGraph" --include="*.py"

# Find all README files
find . -name "README.md"
```

---

## 📋 Checklist for Research System

Use these repos for each component:

- [ ] **Research Agent Core**
  - [ ] Study: open_deep_research
  - [ ] Study: company-researcher
  - [ ] Study: data-enrichment

- [ ] **Memory System**
  - [ ] Study: langmem
  - [ ] Study: memory-agent
  - [ ] Implement: User-scoped storage

- [ ] **Context Engineering**
  - [ ] Study: context_engineering
  - [ ] Implement: Compression strategies
  - [ ] Implement: Selective retrieval

- [ ] **Source Quality**
  - [ ] Study: url_scraper (has evals)
  - [ ] Implement: Rating system
  - [ ] Implement: Learning mechanism

- [ ] **Cross-Topic Learning**
  - [ ] Study: langmem semantic search
  - [ ] Implement: Knowledge graph
  - [ ] Implement: Bidirectional updates

- [ ] **File Generation**
  - [ ] Study: open_deep_research reports
  - [ ] Implement: Markdown generation
  - [ ] Implement: JSON trackers

- [ ] **Evaluation**
  - [ ] Study: openevals
  - [ ] Study: agentevals
  - [ ] Implement: Quality scoring

---

## 💡 Tips for Using This Library

### **1. Start Small**
Don't try to understand everything at once. Focus on one repo at a time.

### **2. Run Examples First**
Every repo has examples. Run them before reading code.

### **3. Compare Implementations**
Compare how different repos solve similar problems:
- Research: company-researcher vs open_deep_research
- Memory: langmem vs memory-agent
- Patterns: supervisor vs swarm

### **4. Extract Patterns**
Look for reusable patterns you can adapt:
- State management approaches
- Error handling strategies
- File organization
- Tool integration patterns

### **5. Keep Notes**
Create a notes file for each repo:
```bash
# Example: 01-research-agents/company-researcher/MY_NOTES.md
## Key Learnings
- Uses 3-phase workflow
- JSON schema for extraction
- Tavily for search

## Patterns to Reuse
- State management structure
- Error handling approach

## Questions
- How to handle rate limits?
```

---

## 🚀 Next Steps

1. **Explore the repos:**
   ```bash
   cd langchain-reference
   ls -la
   ```

2. **Start with open_deep_research:**
   ```bash
   cd 04-production-apps/open_deep_research
   cat README.md
   ```

3. **Check your research system:**
   ```bash
   cd ../../../research-workflow-system
   cat README.md
   ```

4. **Begin implementation:**
   - Follow the roadmap in research-workflow-system/README.md
   - Reference these repos as you build each component

---

## 📞 Reference Quick Links

- **Your Project:** [../research-workflow-system](../research-workflow-system)
- **Implementation Guide:** [../research-workflow-system/README.md](../research-workflow-system/README.md)
- **Quick Start:** [../research-workflow-system/QUICKSTART.md](../research-workflow-system/QUICKSTART.md)

---

**Happy Building! 🎉**

For questions about specific repos, check their individual README files.
For questions about your research system, refer to the implementation roadmap.
