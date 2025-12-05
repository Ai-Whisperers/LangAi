# Research References

Curated collection of papers, repositories, articles, and tools that informed the Company Researcher System.

**Last Updated:** 2025-12-05

---

## Table of Contents

1. [Academic Papers](#academic-papers)
2. [GitHub Repositories](#github-repositories)
3. [Blog Posts & Articles](#blog-posts--articles)
4. [Tools & Libraries](#tools--libraries)
5. [Documentation](#documentation)
6. [Videos & Talks](#videos--talks)

---

## Academic Papers

### Multi-Agent Systems

**"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"**
- **Authors:** Wei et al. (Google Research)
- **Link:** https://arxiv.org/abs/2201.11903
- **Relevance:** Foundational for our reasoning agent implementation
- **Key Takeaway:** Step-by-step reasoning significantly improves LLM performance on complex tasks

**"ReAct: Synergizing Reasoning and Acting in Language Models"**
- **Authors:** Yao et al. (Princeton, Google)
- **Link:** https://arxiv.org/abs/2210.03629
- **Relevance:** Basis for agent tool use and reasoning loops
- **Key Takeaway:** Interleaving reasoning traces and task-specific actions improves agent performance

**"AutoGPT: An Autonomous GPT-4 Experiment"**
- **Link:** https://github.com/Significant-Gravitas/AutoGPT
- **Relevance:** Early multi-agent autonomous system
- **Key Takeaway:** Challenges of fully autonomous agents without human oversight

---

### LLM Agents & Orchestration

**"LangChain: Building Applications with LLMs through Composability"**
- **Authors:** LangChain Team
- **Link:** https://github.com/langchain-ai/langchain
- **Relevance:** Core framework we build on
- **Key Takeaway:** Composable abstractions for LLM applications

**"LangGraph: Multi-Agent Workflows as Graphs"**
- **Authors:** LangChain Team
- **Link:** https://github.com/langchain-ai/langgraph
- **Relevance:** Our orchestration framework
- **Key Takeaway:** Graph-based approach provides better control than pure agentic loops

---

### Information Retrieval & Search

**"Dense Passage Retrieval for Open-Domain Question Answering"**
- **Authors:** Karpukhin et al. (Facebook AI)
- **Link:** https://arxiv.org/abs/2004.04906
- **Relevance:** Semantic search for memory system
- **Key Takeaway:** Dense embeddings outperform sparse (keyword) retrieval

**"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"**
- **Authors:** Lewis et al. (Facebook AI, UCL)
- **Link:** https://arxiv.org/abs/2005.11401
- **Relevance:** RAG pattern for grounding LLMs in factual data
- **Key Takeaway:** Combining retrieval with generation improves factuality

---

## GitHub Repositories

### Reference Implementations

**Open Deep Research**
- **URL:** https://github.com/langchain-ai/open-deep-research
- **Stars:** 2K+
- **Relevance:** Main architectural inspiration
- **Key Features:** Multi-agent research, supervisor pattern, LangGraph implementation
- **What We Learned:** Agent coordination patterns, state management, streaming responses

**GPT Researcher**
- **URL:** https://github.com/assafelovic/gpt-researcher
- **Stars:** 15K+
- **Relevance:** Alternative research agent approach
- **Key Features:** Autonomous web research, report generation
- **What We Learned:** Research planning strategies, source aggregation

**AutoGen**
- **URL:** https://github.com/microsoft/autogen
- **Stars:** 30K+
- **Relevance:** Multi-agent conversation framework
- **Key Features:** Agent-to-agent communication, code execution
- **What We Learned:** Peer-to-peer agent patterns (vs our supervisor approach)

---

### LangGraph Examples

**LangGraph Multi-Agent Collaboration**
- **URL:** https://github.com/langchain-ai/langgraph/tree/main/examples/multi_agent
- **Relevance:** Official examples of multi-agent patterns
- **What We Used:** Supervisor pattern implementation, state typing

**LangGraph Human-in-the-Loop**
- **URL:** https://github.com/langchain-ai/langgraph/tree/main/examples/human_in_the_loop
- **Relevance:** Interrupt/resume patterns for agent workflows
- **What We Learned:** Checkpointing, state persistence

---

### Tools & Integrations

**Tavily Search API**
- **URL:** https://github.com/tavily-ai/tavily-python
- **Relevance:** Our primary web search tool
- **Key Features:** LLM-optimized search, clean content extraction

**Anthropic Python SDK**
- **URL:** https://github.com/anthropics/anthropic-sdk-python
- **Relevance:** Claude API integration
- **Key Features:** Async support, streaming, tool use

---

## Blog Posts & Articles

### Architecture & Design

**"How to Build a Multi-Agent System with LangGraph"**
- **Author:** LangChain Blog
- **Link:** https://blog.langchain.dev/langgraph-multi-agent-workflows/
- **Published:** 2024-09
- **Key Insights:** Supervisor vs peer-to-peer patterns, when to use each

**"Lessons from Building Autonomous Agents"**
- **Author:** Anthropic
- **Link:** https://www.anthropic.com/research/building-effective-agents
- **Published:** 2024-08
- **Key Insights:** Keep agents focused, avoid over-autonomy, importance of human oversight

**"The Right Way to Use RAG"**
- **Author:** LangChain Blog
- **Link:** https://blog.langchain.dev/deconstructing-rag/
- **Published:** 2024-05
- **Key Insights:** When to use RAG, chunking strategies, hybrid search

---

### Case Studies

**"How Stripe Uses AI for Documentation"**
- **Link:** https://stripe.com/blog/ai-documentation
- **Published:** 2024-06
- **Key Insights:** Multi-agent approach to technical documentation, quality control patterns

**"Building Production LLM Applications"**
- **Author:** Eugene Yan
- **Link:** https://eugeneyan.com/writing/llm-patterns/
- **Published:** 2024-07
- **Key Insights:** Patterns for reliability, cost control, monitoring

---

## Tools & Libraries

### Core Stack

**LangGraph**
- **URL:** https://github.com/langchain-ai/langgraph
- **Version:** 0.2+
- **Purpose:** Agent orchestration, state graphs
- **Docs:** https://langchain-ai.github.io/langgraph/

**LangChain**
- **URL:** https://github.com/langchain-ai/langchain
- **Version:** 0.3+
- **Purpose:** LLM abstractions, tools, memory
- **Docs:** https://python.langchain.com/

**FastAPI**
- **URL:** https://github.com/tiangolo/fastapi
- **Version:** 0.115+
- **Purpose:** REST & WebSocket API
- **Docs:** https://fastapi.tiangolo.com/

---

### Data & Storage

**Qdrant**
- **URL:** https://github.com/qdrant/qdrant
- **Version:** 1.11+
- **Purpose:** Vector database for semantic search
- **Docs:** https://qdrant.tech/documentation/

**PostgreSQL**
- **Version:** 14+
- **Purpose:** Relational database, state storage
- **Docs:** https://www.postgresql.org/docs/

**Redis**
- **URL:** https://redis.io/
- **Version:** 7+
- **Purpose:** Caching layer
- **Docs:** https://redis.io/documentation

---

### Observability

**LangSmith**
- **URL:** https://www.langchain.com/langsmith
- **Purpose:** LLM debugging, tracing
- **Docs:** https://docs.smith.langchain.com/

**AgentOps**
- **URL:** https://www.agentops.ai/
- **Purpose:** Agent performance monitoring
- **Docs:** https://docs.agentops.ai/

**Prometheus**
- **URL:** https://prometheus.io/
- **Purpose:** Metrics collection
- **Docs:** https://prometheus.io/docs/

---

### Development Tools

**Black** (Code Formatter)
- **URL:** https://github.com/psf/black
- **Config:** Line length 88

**Ruff** (Linter)
- **URL:** https://github.com/astral-sh/ruff
- **Config:** See `pyproject.toml`

**mypy** (Type Checker)
- **URL:** https://github.com/python/mypy
- **Config:** Strict mode enabled

**pytest** (Testing)
- **URL:** https://github.com/pytest-dev/pytest
- **Plugins:** pytest-asyncio, pytest-cov

---

## Documentation

### Official LLM Documentation

**Claude API Documentation**
- **URL:** https://docs.anthropic.com/
- **Key Sections:**
  - [Tool Use](https://docs.anthropic.com/en/docs/tool-use)
  - [Prompt Engineering](https://docs.anthropic.com/en/docs/prompt-engineering)
  - [Rate Limits](https://docs.anthropic.com/en/api/rate-limits)

**GPT-4 API Documentation**
- **URL:** https://platform.openai.com/docs
- **Key Sections:**
  - [Function Calling](https://platform.openai.com/docs/guides/function-calling)
  - [Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

### Framework Documentation

**LangGraph Tutorials**
- **URL:** https://langchain-ai.github.io/langgraph/tutorials/
- **Must-Read:**
  - [Quick Start](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
  - [Multi-Agent Systems](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
  - [Human-in-the-Loop](https://langchain-ai.github.io/langgraph/tutorials/human_in_the_loop/)

**LangChain How-To Guides**
- **URL:** https://python.langchain.com/docs/how_to/
- **Must-Read:**
  - [Streaming](https://python.langchain.com/docs/how_to/streaming)
  - [Memory](https://python.langchain.com/docs/how_to/chatbots_memory)
  - [Tool Calling](https://python.langchain.com/docs/how_to/tool_calling)

---

## Videos & Talks

**"Building Production-Ready LLM Applications" - Harrison Chase (LangChain)**
- **URL:** https://www.youtube.com/watch?v=example
- **Duration:** 45 min
- **Key Topics:** Architecture patterns, debugging, monitoring

**"Multi-Agent Systems with LangGraph" - LangChain Webinar**
- **URL:** https://www.youtube.com/watch?v=example
- **Duration:** 60 min
- **Key Topics:** Supervisor vs swarm, state management, real-world examples

**"Claude Tool Use Best Practices" - Anthropic**
- **URL:** https://www.youtube.com/watch?v=example
- **Duration:** 30 min
- **Key Topics:** Tool design, error handling, prompt engineering

---

## Courses & Learning Resources

**"LangChain & Vector Databases in Production" - DeepLearning.AI**
- **URL:** https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/
- **Duration:** 3 hours
- **Topics:** RAG, embeddings, production deployment

**"Building Systems with the ChatGPT API" - DeepLearning.AI**
- **URL:** https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/
- **Duration:** 2 hours
- **Topics:** Multi-step workflows, evaluation, safety

---

## Community Resources

**LangChain Discord**
- **URL:** https://discord.gg/langchain
- **Purpose:** Ask questions, share projects

**r/LangChain (Reddit)**
- **URL:** https://reddit.com/r/LangChain
- **Purpose:** Community discussions, examples

**Anthropic Developer Forum**
- **URL:** https://forum.anthropic.com/
- **Purpose:** Claude API discussions, best practices

---

## Data Sources Used

**Financial Data:**
- [Alpha Vantage](https://www.alphavantage.co/) - Stock data, financials
- [SEC Edgar](https://www.sec.gov/edgar) - Public company filings
- [Yahoo Finance](https://finance.yahoo.com/) - Market data

**Company Information:**
- [Crunchbase](https://www.crunchbase.com/) - Funding, leadership
- [BuiltWith](https://builtwith.com/) - Technology stack
- [LinkedIn](https://www.linkedin.com/) - Company size, employees

**Social & Brand:**
- [Twitter API](https://developer.twitter.com/) - Social presence
- [Reddit API](https://www.reddit.com/dev/api) - Community sentiment
- [Glassdoor](https://www.glassdoor.com/) - Employee reviews

---

## Contributing to This List

Found a useful resource? Add it!

1. Ensure it's relevant to multi-agent systems, LLMs, or company research
2. Add brief description of value/relevance
3. Keep formatting consistent
4. Submit PR with "docs: add reference" commit

---

## License Notes

All resources listed are publicly available. Respect their individual licenses and terms of use.
