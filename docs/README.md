# LangAI Documentation

Comprehensive documentation for building an AI-powered API with smart LLM routing, vector search, and cost optimization.

## 📚 Documentation Index

### Start Here
- **[getting-started.md](getting-started.md)** - Quick setup guide, project phases, troubleshooting

### Core Components
- **[llm-setup.md](llm-setup.md)** - LLM configuration, smart routing, LiteLLM integration, cost optimization
- **[vector-databases.md](vector-databases.md)** - Chroma vs Weaviate comparison, migration strategy, setup guides
- **[fastapi-integration.md](fastapi-integration.md)** - Complete FastAPI implementation with code examples
- **[architecture.md](architecture.md)** - System design, architectural patterns, scaling strategy

---

## 🎯 Quick Navigation

### "I want to..."

**Get started quickly**
→ Read [getting-started.md](getting-started.md)

**Understand the LLM routing**
→ Read [llm-setup.md](llm-setup.md#smart-llm-router)

**Set up vector search**
→ Read [vector-databases.md](vector-databases.md#chroma-setup-current-phase)

**See complete code examples**
→ Read [fastapi-integration.md](fastapi-integration.md#core-implementation)

**Understand system architecture**
→ Read [architecture.md](architecture.md#overall-architecture)

**Optimize costs**
→ Read [llm-setup.md](llm-setup.md#cost-optimization-patterns)

**Plan for production**
→ Read [architecture.md](architecture.md#scalability-considerations)

**Migrate from Chroma to Weaviate**
→ Read [vector-databases.md](vector-databases.md#migration-strategy)

---

## 📖 Reading Order

### For Beginners
1. [getting-started.md](getting-started.md) - Setup and first steps
2. [llm-setup.md](llm-setup.md) - Understand the LLMs
3. [fastapi-integration.md](fastapi-integration.md) - Build the API
4. [vector-databases.md](vector-databases.md) - Add search capability

### For Architects
1. [architecture.md](architecture.md) - System design overview
2. [llm-setup.md](llm-setup.md) - LLM routing decisions
3. [vector-databases.md](vector-databases.md) - Vector DB trade-offs
4. [fastapi-integration.md](fastapi-integration.md) - Implementation details

### For Developers (Implementing)
1. [getting-started.md](getting-started.md) - Phase 1 setup
2. [fastapi-integration.md](fastapi-integration.md) - Follow step-by-step
3. [llm-setup.md](llm-setup.md) - Reference for LLM code
4. [vector-databases.md](vector-databases.md) - Reference for vector code

---

## 🏗️ Tech Stack Overview

### Backend
- **FastAPI** - Modern Python web framework
- **LiteLLM** - Unified interface for all LLMs
- **LangChain** - RAG and agent frameworks

### AI/ML
- **LLMs:** GPT-4, Claude, Llama 3
- **Embeddings:** OpenAI, HuggingFace
- **Vector DB:** Chroma (dev) → Weaviate (production)

### Infrastructure
- **Redis** - Caching layer
- **Docker** - Containerization
- **Ollama** - Local model serving

---

## 💡 Key Concepts

### Smart LLM Routing
Automatically choose the best model based on:
- **Sensitivity** - Private data uses local models
- **Complexity** - Simple tasks use cheaper models
- **Context length** - Long documents use Claude
- **Cost** - Optimize spending automatically

**Details:** [llm-setup.md](llm-setup.md#smart-llm-router)

### Vector Search
Store and search documents by meaning, not just keywords:
- **Chroma** - Fast setup, embedded database
- **Weaviate** - Production-scale, hybrid search
- **Migration path** - Easy upgrade when ready

**Details:** [vector-databases.md](vector-databases.md)

### RAG Pipeline
Retrieval-Augmented Generation:
1. Embed user question
2. Search vector database
3. Build context from results
4. Generate answer with LLM

**Details:** [architecture.md](architecture.md#pattern-1-rag-pipeline)

### Cost Optimization
Reduce API costs by 60-80%:
- **Caching** - Reuse responses
- **Smart routing** - Use cheap models when possible
- **Local models** - Zero cost for some queries

**Details:** [llm-setup.md](llm-setup.md#cost-optimization-patterns)

---

## 📊 Decision Matrices

### Choose Your Vector Database

| Need | Choose |
|------|--------|
| Quick prototype | Chroma |
| Production app | Weaviate |
| Hybrid search | Weaviate |
| Zero ops | Chroma |
| Scale to 10M+ docs | Weaviate or Milvus |

**Full comparison:** [vector-databases.md](vector-databases.md#comparison-table)

### Choose Your LLM

| Task | Model | Why |
|------|-------|-----|
| Customer support | GPT-3.5 or Claude | Good quality, low cost |
| Complex reasoning | GPT-4 | Best quality |
| Long documents | Claude | 200K context |
| Private data | Llama (local) | Zero data leaks |
| Code generation | GPT-4 | Best at code |

**Full guide:** [llm-setup.md](llm-setup.md#decision-matrix)

---

## 🚀 Development Phases

### Phase 1: Minimal Working App (Day 1)
- Basic FastAPI app
- Single LLM (GPT-3.5)
- One endpoint

**Guide:** [getting-started.md](getting-started.md#phase-1-minimal-working-app-day-1)

### Phase 2: Smart Routing (Day 2-3)
- Multiple LLMs
- Automatic routing
- Cost optimization

**Guide:** [getting-started.md](getting-started.md#phase-2-add-llm-router-day-2-3)

### Phase 3: Vector Search (Day 4-5)
- Chroma setup
- Document storage
- Semantic search

**Guide:** [getting-started.md](getting-started.md#phase-3-add-vector-search-day-4-5)

### Phase 4: Caching (Day 6)
- Redis integration
- Response caching
- Embedding caching

**Guide:** [getting-started.md](getting-started.md#phase-4-add-caching-day-6)

### Phase 5: Production (Week 2)
- Authentication
- Monitoring
- Deployment

**Guide:** [getting-started.md](getting-started.md#phase-5-production-ready-week-2)

---

## 💰 Cost Examples

### Development (Testing)
```
OpenAI:      $5-10/month
Anthropic:   $5-10/month
Infrastructure: $0
─────────────────────────
Total:       $10-20/month
```

### Production (1000 users, optimized)
```
LLMs:        $100-500/month (with caching & routing)
Redis:       $10-30/month
Hosting:     $20-50/month
─────────────────────────
Total:       $130-580/month
```

**Full breakdown:** [getting-started.md](getting-started.md#cost-estimation)

---

## 🔍 Code Examples

All docs include complete, working code examples:

- **LLM Router:** [llm-setup.md](llm-setup.md#implementation)
- **Vector Store:** [vector-databases.md](vector-databases.md#basic-usage)
- **FastAPI App:** [fastapi-integration.md](fastapi-integration.md#core-implementation)
- **RAG Pipeline:** [architecture.md](architecture.md#pattern-1-rag-pipeline)
- **Caching:** [fastapi-integration.md](fastapi-integration.md#appservicescachepy)

---

## 🛠️ Common Tasks

### Setup New Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Development Server
```bash
redis-server  # Terminal 1
ollama serve  # Terminal 2
uvicorn app.main:app --reload  # Terminal 3
```

### Test API
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat -d '{"message":"Hello"}'
```

### Deploy with Docker
```bash
docker-compose up --build
```

**More details:** [getting-started.md](getting-started.md#development-workflow)

---

## 📝 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| getting-started.md | ✅ Complete | 2025-12-05 |
| llm-setup.md | ✅ Complete | 2025-12-05 |
| vector-databases.md | ✅ Complete | 2025-12-05 |
| fastapi-integration.md | ✅ Complete | 2025-12-05 |
| architecture.md | ✅ Complete | 2025-12-05 |

---

## 🤝 Contributing to Docs

When updating docs:
1. Keep code examples working and tested
2. Update this README if adding new docs
3. Include cost estimates where relevant
4. Add troubleshooting tips
5. Update "Last Updated" dates

---

## 📞 Getting Help

If you're stuck:

1. **Search the docs** - Use Ctrl+F in relevant file
2. **Check examples** - All concepts have code examples
3. **Review architecture** - Understand the big picture
4. **Start simple** - Build phase by phase

---

## 🎓 Learning Resources

### Included in This Repo
- ✅ Complete implementation guides
- ✅ Working code examples
- ✅ Architecture patterns
- ✅ Best practices
- ✅ Cost optimization strategies

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)

---

**Start building:** [getting-started.md](getting-started.md)

**Questions about architecture:** [architecture.md](architecture.md)

**Need implementation details:** [fastapi-integration.md](fastapi-integration.md)

Happy coding! 🚀
