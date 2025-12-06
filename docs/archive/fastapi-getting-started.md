# Getting Started with LangAI

Welcome to LangAI! This guide will help you get your AI-powered API up and running.

## Quick Start (5 Minutes)

### 1. Prerequisites

- Python 3.10 or higher
- Redis (for caching)
- Git

### 2. Clone & Setup

```bash
# Navigate to your project directory
cd "c:\Users\Alejandro\Documents\Ivan\Work\Lang ai"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn[standard] litellm chromadb redis python-dotenv pydantic-settings slowapi
```

### 3. Configure Environment

Create `.env` file in project root:

```bash
# Copy this template and fill in your API keys

# API Keys (get from respective providers)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Environment
ENV=development
DEBUG=true

# Vector Store
VECTOR_STORE=chroma
CHROMA_PATH=./chroma_db

# Redis
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
```

### 4. Start Services

**Terminal 1: Redis**
```bash
# Install Redis first if you haven't:
# Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
# Mac: brew install redis
# Linux: sudo apt-get install redis

redis-server
```

**Terminal 2: Ollama (optional, for local models)**
```bash
# Install Ollama: https://ollama.com/download
ollama serve

# In another terminal, pull Llama
ollama pull llama3
```

**Terminal 3: FastAPI**
```bash
# Create minimal app first (see below)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "complexity": "simple"}'
```

Visit http://localhost:8000/docs for interactive API documentation!

---

## Project Setup Phases

### Phase 1: Minimal Working App (Day 1)

**Goal:** Get a simple chat endpoint running

```
Lang ai/
├── app/
│   ├── __init__.py
│   ├── main.py           # Start here
│   ├── config.py
│   └── models.py
├── .env
├── requirements.txt
└── docs/
```

**Files to create:**

1. **app/config.py** - See [fastapi-integration.md](fastapi-integration.md#appconfigpy)
2. **app/models.py** - See [fastapi-integration.md](fastapi-integration.md#appmodelspy)
3. **app/main.py** - Minimal version:

```python
from fastapi import FastAPI
from litellm import completion
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LangAI")

@app.post("/chat")
async def chat(message: str):
    response = completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return {"response": response.choices[0].message.content}

@app.get("/health")
async def health():
    return {"status": "ok"}
```

Test it:
```bash
uvicorn app.main:app --reload
curl -X POST "http://localhost:8000/chat?message=Hello"
```

### Phase 2: Add LLM Router (Day 2-3)

**Goal:** Smart routing between multiple models

Add these files:
- `app/services/llm_router.py` - See [llm-setup.md](llm-setup.md#smart-llm-router)
- Update `app/main.py` to use router

**What you get:**
- Automatic model selection based on complexity
- Cost optimization
- Privacy support (local models for sensitive data)

### Phase 3: Add Vector Search (Day 4-5)

**Goal:** Semantic search with Chroma

Add these files:
- `app/services/vector_store.py` - See [vector-databases.md](vector-databases.md#chroma-setup-current-phase)
- `app/routers/search.py`

**What you get:**
- Store and search documents
- RAG (Retrieval-Augmented Generation) capability
- Knowledge base functionality

### Phase 4: Add Caching (Day 6)

**Goal:** Reduce costs with Redis caching

Add these files:
- `app/services/cache.py` - See [fastapi-integration.md](fastapi-integration.md#appservicescachepy)

**What you get:**
- 90% reduction in duplicate API calls
- Faster response times
- Lower costs

### Phase 5: Production Ready (Week 2)

**Goal:** Deploy-ready application

Add:
- Authentication (JWT)
- Rate limiting (slowapi)
- Monitoring (Prometheus)
- Docker setup
- Tests

---

## Documentation Overview

We've created comprehensive docs for each component:

### Core Documentation

| Document | What It Covers | When to Read |
|----------|---------------|--------------|
| [vector-databases.md](vector-databases.md) | Chroma vs Weaviate, migration strategy | Before implementing search |
| [llm-setup.md](llm-setup.md) | LiteLLM, smart routing, cost optimization | Before implementing chat |
| [architecture.md](architecture.md) | System design, patterns, decisions | Before starting Phase 2 |
| [fastapi-integration.md](fastapi-integration.md) | Complete FastAPI implementation | Reference while coding |
| [getting-started.md](getting-started.md) | This file! Step-by-step setup | Right now! |

---

## Development Workflow

### Daily Development

```bash
# 1. Activate environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 2. Start services (3 terminals)
redis-server
ollama serve  # if using local models
uvicorn app.main:app --reload

# 3. Code & test
# Visit http://localhost:8000/docs
```

### Before Committing

```bash
# Run tests
pytest tests/

# Check code quality
# pip install black flake8
black app/
flake8 app/

# Update requirements
pip freeze > requirements.txt
```

### Git Workflow

```bash
# Create .gitignore first
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
.env
chroma_db/
.DS_Store
EOF

# Commit
git add .
git commit -m "feat: add smart LLM router"
git push
```

---

## Common Issues & Solutions

### Issue: "Module not found: litellm"
```bash
# Solution: Install dependencies
pip install litellm
```

### Issue: "Redis connection refused"
```bash
# Solution: Start Redis server
redis-server

# Or check if it's running
redis-cli ping
# Should return: PONG
```

### Issue: "OpenAI API key not found"
```bash
# Solution: Check .env file exists and has correct key
cat .env | grep OPENAI_API_KEY

# Make sure to load it
from dotenv import load_dotenv
load_dotenv()
```

### Issue: "Ollama model not found"
```bash
# Solution: Pull the model first
ollama pull llama3

# Check available models
ollama list
```

### Issue: "Port 8000 already in use"
```bash
# Solution: Use different port
uvicorn app.main:app --reload --port 8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

---

## Cost Estimation

### Development Phase (Testing)
- **OpenAI:** ~$5-10/month (mostly GPT-3.5)
- **Anthropic:** ~$5-10/month
- **Infrastructure:** $0 (local Redis, Chroma)
- **Total:** ~$10-20/month

### Production (1000 users)
- **LLMs:** $100-500/month (with caching)
- **Redis:** $10-30/month (managed)
- **Hosting:** $20-50/month (VPS)
- **Total:** ~$130-580/month

**With smart routing & caching, expect 60-80% cost reduction!**

---

## Learning Path

### Week 1: Fundamentals
- [ ] Complete Phase 1 (minimal app)
- [ ] Read [llm-setup.md](llm-setup.md)
- [ ] Implement LLM router
- [ ] Test with different models

### Week 2: Advanced Features
- [ ] Read [vector-databases.md](vector-databases.md)
- [ ] Implement vector search
- [ ] Build RAG pipeline
- [ ] Add caching

### Week 3: Production
- [ ] Read [architecture.md](architecture.md)
- [ ] Add authentication
- [ ] Set up monitoring
- [ ] Deploy to cloud

### Week 4: Optimization
- [ ] Analyze costs
- [ ] Optimize prompts
- [ ] Fine-tune routing
- [ ] Scale infrastructure

---

## Example Use Cases

### Use Case 1: Customer Support Bot

```python
# High-level flow
1. User asks question
2. Search knowledge base (vector store)
3. If answer found → use GPT-3.5 (cheap)
4. If complex issue → escalate to GPT-4
5. Cache common answers

# Expected costs
- 90% questions: $0.002 per request (GPT-3.5 + cache)
- 10% questions: $0.03 per request (GPT-4)
- Average: ~$0.005 per request
```

### Use Case 2: Document Q&A

```python
# High-level flow
1. User uploads documents
2. Chunk and embed documents
3. Store in Chroma
4. User asks questions
5. RAG: retrieve + generate answer

# Expected costs
- Document upload: $0.02 per 1000 pages (one-time)
- Questions: $0.005 per question (with caching)
```

### Use Case 3: Code Assistant

```python
# High-level flow
1. User asks coding question
2. Detect: code generation = complex
3. Route to GPT-4 (best at code)
4. Cache common patterns

# Expected costs
- Simple: $0.002 per request (GPT-3.5)
- Complex: $0.03 per request (GPT-4)
- Average: ~$0.015 per request
```

---

## Next Steps

1. **Start Phase 1** - Get minimal app running
2. **Read Architecture** - Understand system design
3. **Implement Phase 2** - Add LLM router
4. **Test with Real Data** - Load documents, test search
5. **Optimize** - Monitor costs, improve prompts
6. **Deploy** - Move to production

---

## Resources

### Official Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [LiteLLM](https://docs.litellm.ai/)
- [ChromaDB](https://docs.trychroma.com/)
- [LangChain](https://python.langchain.com/)

### API Keys
- [OpenAI](https://platform.openai.com/api-keys)
- [Anthropic](https://console.anthropic.com/)

### Tools
- [Redis](https://redis.io/)
- [Ollama](https://ollama.com/)
- [Docker](https://www.docker.com/)

### Community
- [LangChain Discord](https://discord.gg/langchain)
- [FastAPI Discord](https://discord.gg/fastapi)

---

## Support

If you get stuck:

1. **Check the docs** - Each component has detailed documentation
2. **Review examples** - All docs include working code examples
3. **Test incrementally** - Build phase by phase
4. **Check logs** - Enable DEBUG mode for detailed errors

---

## Checklist

Use this checklist to track your progress:

### Setup
- [ ] Python 3.10+ installed
- [ ] Redis installed and running
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured with API keys

### Phase 1: Minimal App
- [ ] Basic FastAPI app running
- [ ] Can call OpenAI API
- [ ] Health check works
- [ ] Interactive docs accessible

### Phase 2: LLM Router
- [ ] LiteLLM integrated
- [ ] Smart routing implemented
- [ ] Multiple models working (GPT-4, Claude, Llama)
- [ ] Fallback chain tested

### Phase 3: Vector Search
- [ ] Chroma initialized
- [ ] Can add documents
- [ ] Can search documents
- [ ] RAG pipeline working

### Phase 4: Caching
- [ ] Redis connected
- [ ] Cache working for LLM responses
- [ ] Cache hit rate > 30%
- [ ] Cost reduction visible

### Phase 5: Production
- [ ] Docker setup complete
- [ ] Tests written and passing
- [ ] Monitoring added
- [ ] Deployed to cloud

---

**Ready to build? Start with Phase 1 and work your way up!**

**Questions?** Review the relevant documentation file or check the examples in [fastapi-integration.md](fastapi-integration.md).

Good luck! 🚀
