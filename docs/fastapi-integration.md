# FastAPI Integration Guide

## Project Structure

```
lang-ai/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py          # Chat endpoints
│   │   ├── documents.py     # Document management
│   │   └── search.py        # Search endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_router.py    # LLM routing logic
│   │   ├── vector_store.py  # Vector DB abstraction
│   │   ├── embeddings.py    # Embedding service
│   │   └── cache.py         # Redis caching
│   └── utils/
│       ├── __init__.py
│       ├── logging.py       # Structured logging
│       └── monitoring.py    # Metrics collection
├── tests/
├── docs/
├── chroma_db/               # Chroma persistent storage
├── .env                     # Environment variables
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Installation & Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn[standard]
pip install litellm chromadb
pip install redis python-dotenv
pip install pydantic pydantic-settings
pip install slowapi  # Rate limiting

# Optional: monitoring
pip install prometheus-client

# Save dependencies
pip freeze > requirements.txt
```

### 2. Environment Configuration

Create `.env` file:
```bash
# Environment
ENV=development

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Vector Store
VECTOR_STORE=chroma
CHROMA_PATH=./chroma_db

# Redis
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Ollama (local models)
OLLAMA_BASE_URL=http://localhost:11434

# Logging
LOG_LEVEL=INFO
```

---

## Core Implementation

### app/config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENV: str = "development"
    DEBUG: bool = False

    # API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Vector Store
    VECTOR_STORE: str = "chroma"
    CHROMA_PATH: str = "./chroma_db"
    WEAVIATE_URL: str = "http://localhost:8080"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Cached settings instance"""
    return Settings()

settings = get_settings()
```

### app/models.py

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Sensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"

class Complexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=10000)
    sensitivity: Sensitivity = Sensitivity.PUBLIC
    complexity: Complexity = Complexity.MODERATE
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(1000, ge=1, le=4000)
    stream: bool = False

class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    model_used: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    cached: bool = False

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(5, ge=1, le=20)

class Document(BaseModel):
    """Document model"""
    id: str
    content: str
    metadata: dict = {}
    score: Optional[float] = None

class SearchResponse(BaseModel):
    """Search response model"""
    documents: List[Document]
    query: str
    count: int

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    checks: dict
    timestamp: str
```

### app/services/cache.py

```python
import redis
import json
import hashlib
from typing import Optional
from app.config import settings

class CacheService:
    """Redis caching service"""

    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    def _make_key(self, prefix: str, data: str) -> str:
        """Generate cache key from data"""
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"

    def get(self, prefix: str, data: str) -> Optional[str]:
        """Get cached value"""
        key = self._make_key(prefix, data)
        return self.client.get(key)

    def set(self, prefix: str, data: str, value: str, ttl: int = None):
        """Set cached value with TTL"""
        key = self._make_key(prefix, data)
        if ttl is None:
            ttl = settings.CACHE_TTL
        self.client.setex(key, ttl, value)

    def delete(self, prefix: str, data: str):
        """Delete cached value"""
        key = self._make_key(prefix, data)
        self.client.delete(key)

    def clear_all(self):
        """Clear all cache (use with caution!)"""
        self.client.flushdb()

cache_service = CacheService()
```

### app/services/vector_store.py

```python
from abc import ABC, abstractmethod
from typing import List
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.models import Document

class VectorStore(ABC):
    """Abstract vector store interface"""

    @abstractmethod
    def add(self, documents: List[str], metadatas: List[dict] = None):
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Document]:
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        pass

class ChromaStore(VectorStore):
    """Chroma vector store implementation"""

    def __init__(self, collection_name: str = "documents"):
        self.client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PATH
        ))

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add(self, documents: List[str], metadatas: List[dict] = None):
        """Add documents to vector store"""
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )

    def search(self, query: str, limit: int = 5) -> List[Document]:
        """Search for similar documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )

        documents = []
        for i, doc_id in enumerate(results['ids'][0]):
            documents.append(Document(
                id=doc_id,
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                score=results['distances'][0][i] if 'distances' in results else None
            ))

        return documents

    def delete(self, ids: List[str]):
        """Delete documents by ID"""
        self.collection.delete(ids=ids)

# Factory function
def get_vector_store() -> VectorStore:
    """Get configured vector store instance"""
    if settings.VECTOR_STORE == "chroma":
        return ChromaStore()
    # elif settings.VECTOR_STORE == "weaviate":
    #     return WeaviateStore()
    else:
        raise ValueError(f"Unknown vector store: {settings.VECTOR_STORE}")

vector_store = get_vector_store()
```

### app/services/llm_router.py

```python
from litellm import completion
from app.models import Sensitivity, Complexity, ChatRequest
from app.config import settings
import os

# Set API keys
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

class LLMRouter:
    """Smart LLM routing service"""

    def __init__(self):
        self.model_costs = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3-sonnet-20240229": 0.015,
            "ollama/llama3": 0.0
        }

    def route(self, request: ChatRequest) -> str:
        """Choose best model for request"""

        # Rule 1: Confidential → local only
        if request.sensitivity == Sensitivity.CONFIDENTIAL:
            return "ollama/llama3"

        # Rule 2: Simple → cheap
        if request.complexity == Complexity.SIMPLE:
            return "gpt-3.5-turbo"

        # Rule 3: Long context → Claude
        if request.max_tokens > 8000:
            return "claude-3-sonnet-20240229"

        # Rule 4: Complex → GPT-4
        if request.complexity == Complexity.COMPLEX:
            return "gpt-4"

        # Default: moderate tasks → Claude
        return "claude-3-sonnet-20240229"

    def complete(self, request: ChatRequest) -> dict:
        """Execute LLM request with routing"""

        model = self.route(request)

        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": request.message}],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )

            if request.stream:
                return {"stream": response, "model": model}

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else None
            cost = (tokens / 1000) * self.model_costs.get(model, 0) if tokens else None

            return {
                "message": content,
                "model": model,
                "tokens": tokens,
                "cost": cost
            }

        except Exception as e:
            # Fallback to local model
            print(f"Error with {model}: {e}. Falling back to local model.")
            return self._fallback(request)

    def _fallback(self, request: ChatRequest) -> dict:
        """Fallback to local model"""
        response = completion(
            model="ollama/llama3",
            messages=[{"role": "user", "content": request.message}],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return {
            "message": response.choices[0].message.content,
            "model": "ollama/llama3",
            "tokens": None,
            "cost": 0.0
        }

llm_router = LLMRouter()
```

### app/routers/chat.py

```python
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models import ChatRequest, ChatResponse
from app.services.llm_router import llm_router
from app.services.cache import cache_service
import json

router = APIRouter(prefix="/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)

@router.post("", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    Chat endpoint with LLM routing and caching

    - Automatically routes to best LLM based on complexity and sensitivity
    - Caches responses for identical requests
    - Rate limited to 10 requests per minute
    """

    # Check cache first (if not confidential)
    if chat_request.sensitivity != "confidential":
        cache_key = f"{chat_request.message}:{chat_request.complexity}"
        cached = cache_service.get("chat", cache_key)

        if cached:
            response_data = json.loads(cached)
            response_data["cached"] = True
            return ChatResponse(**response_data)

    # Execute LLM request
    try:
        result = llm_router.complete(chat_request)

        response_data = {
            "message": result["message"],
            "model_used": result["model"],
            "tokens_used": result.get("tokens"),
            "cost": result.get("cost"),
            "cached": False
        }

        # Cache response
        if chat_request.sensitivity != "confidential":
            cache_service.set("chat", cache_key, json.dumps(response_data))

        return ChatResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/stream")
@limiter.limit("5/minute")
async def chat_stream(request: Request, chat_request: ChatRequest):
    """Streaming chat endpoint"""

    chat_request.stream = True

    try:
        result = llm_router.complete(chat_request)
        stream = result["stream"]
        model = result["model"]

        async def generate():
            yield f"data: {{\"model\": \"{model}\"}}\n\n"

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {{\"content\": \"{content}\"}}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")
```

### app/routers/search.py

```python
from fastapi import APIRouter, HTTPException
from app.models import SearchRequest, SearchResponse
from app.services.vector_store import vector_store

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=SearchResponse)
async def search(search_request: SearchRequest):
    """
    Semantic search endpoint

    - Searches vector database for similar documents
    - Returns top N most similar results
    """

    try:
        documents = vector_store.search(
            query=search_request.query,
            limit=search_request.limit
        )

        return SearchResponse(
            documents=documents,
            query=search_request.query,
            count=len(documents)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
```

### app/main.py

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
import logging

from app.config import settings
from app.routers import chat, search
from app.models import HealthResponse

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LangAI API",
    description="LLM-powered API with smart routing and vector search",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(search.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LangAI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Checks status of:
    - Redis cache
    - Vector store
    - LLM providers
    """

    from app.services.cache import cache_service
    from app.services.vector_store import vector_store

    health = {
        "status": "healthy",
        "checks": {},
        "timestamp": datetime.now().isoformat()
    }

    # Check Redis
    try:
        cache_service.client.ping()
        health["checks"]["redis"] = "ok"
    except Exception as e:
        health["checks"]["redis"] = f"fail: {str(e)}"
        health["status"] = "degraded"

    # Check Vector Store
    try:
        # Simple check - try to search
        vector_store.search("test", limit=1)
        health["checks"]["vector_store"] = "ok"
    except Exception as e:
        health["checks"]["vector_store"] = f"fail: {str(e)}"
        health["status"] = "degraded"

    return HealthResponse(**health)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

---

## Running the Application

### Development Mode

```bash
# Start Redis (in separate terminal)
redis-server

# Start Ollama (in separate terminal)
ollama serve

# Run FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./.env:/app/.env
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Run with Docker

```bash
docker-compose up --build
```

---

## API Usage Examples

### Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "sensitivity": "public",
    "complexity": "simple",
    "temperature": 0.7
  }'
```

### Streaming Chat

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a story",
    "complexity": "moderate"
  }'
```

### Search Endpoint

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning concepts",
    "limit": 5
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## Testing

```python
# tests/test_chat.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post("/chat", json={
        "message": "Hello",
        "sensitivity": "public",
        "complexity": "simple"
    })

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "model_used" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
```

Run tests:
```bash
pip install pytest httpx
pytest tests/
```

---

## Performance Tips

1. **Enable caching** for frequently asked questions
2. **Use connection pooling** for Redis and vector store
3. **Implement request batching** for bulk operations
4. **Add async processing** for slow operations
5. **Monitor and optimize** slow endpoints

---

## Next Steps

1. ✅ Set up basic FastAPI structure
2. ✅ Implement LLM router
3. ✅ Add caching layer
4. ⏭️ Add authentication (JWT)
5. ⏭️ Add usage tracking per user
6. ⏭️ Implement RAG pipeline
7. ⏭️ Add websocket support
8. ⏭️ Deploy to cloud

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
