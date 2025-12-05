# AgentCloud - Detailed Analysis

**Repository:** agentcloud/
**Type:** Private LLM Chat Platform
**Priority:** 🔧 SPECIFIC (Production Deployment)

---

## Overview

AgentCloud is an open-source platform for building and deploying private LLM chat applications. It provides a complete stack for teams to securely interact with their data through AI agents.

**Key Value:** Self-hosted, production-ready platform for RAG chatbots with multi-component architecture.

---

## Architecture

### Three Main Components

```
agentcloud/
├── agent-backend/          # Python + CrewAI
│   └── Socket.io communication
├── webapp/                 # Next.js + Tailwind
│   └── Express custom server
└── vector-db-proxy/        # Rust
    └── Qdrant integration
```

### Component Details

#### 1. **Agent Backend** (Python)
- Runs CrewAI agents
- Socket.io for real-time communication
- Handles LLM orchestration
- Manages agent execution

#### 2. **Webapp** (Next.js)
- User interface
- Chat interface
- Agent configuration
- Dashboard views

#### 3. **Vector DB Proxy** (Rust)
- High-performance vector operations
- Qdrant database interface
- Embedding management

---

## Extractable Patterns

### Pattern 1: Microservice Architecture

```yaml
# docker-compose.yml structure
services:
  agent-backend:
    build: ./agent-backend
    depends_on:
      - vector-db-proxy
      - redis
    environment:
      - OPENAI_API_KEY
      - VECTOR_DB_URL

  webapp:
    build: ./webapp
    depends_on:
      - agent-backend
    ports:
      - "3000:3000"

  vector-db-proxy:
    build: ./vector-db-proxy
    depends_on:
      - qdrant

  qdrant:
    image: qdrant/qdrant
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:alpine
```

### Pattern 2: Socket.io Real-Time Communication

```python
# agent-backend pattern
from socketio import AsyncServer
from aiohttp import web

sio = AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

@sio.on('execute_agent')
async def execute_agent(sid, data):
    """Handle agent execution request"""

    # Emit status updates
    await sio.emit('agent_status', {'status': 'running'}, room=sid)

    try:
        # Run agent
        result = await run_crew_agent(data['agent_config'])

        # Stream results
        await sio.emit('agent_result', result, room=sid)

    except Exception as e:
        await sio.emit('agent_error', {'error': str(e)}, room=sid)

@sio.on('stream_message')
async def stream_message(sid, data):
    """Stream LLM responses"""
    async for chunk in llm.stream(data['prompt']):
        await sio.emit('message_chunk', chunk, room=sid)
```

```typescript
// webapp pattern
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000');

socket.on('connect', () => {
  console.log('Connected to agent backend');
});

socket.on('agent_status', (data) => {
  setStatus(data.status);
});

socket.on('agent_result', (data) => {
  setResult(data);
});

socket.on('message_chunk', (chunk) => {
  appendToMessage(chunk);
});

// Execute agent
socket.emit('execute_agent', {
  agent_config: agentConfig
});
```

### Pattern 3: Vector DB Proxy (Rust)

```rust
// High-performance vector operations
use qdrant_client::prelude::*;

pub struct VectorProxy {
    client: QdrantClient,
}

impl VectorProxy {
    pub async fn new(url: &str) -> Result<Self> {
        let client = QdrantClient::from_url(url).build()?;
        Ok(Self { client })
    }

    pub async fn search(
        &self,
        collection: &str,
        vector: Vec<f32>,
        limit: usize,
    ) -> Result<Vec<ScoredPoint>> {
        self.client
            .search_points(&SearchPoints {
                collection_name: collection.to_string(),
                vector,
                limit: limit as u64,
                with_payload: Some(true.into()),
                ..Default::default()
            })
            .await
    }

    pub async fn upsert(
        &self,
        collection: &str,
        points: Vec<PointStruct>,
    ) -> Result<()> {
        self.client
            .upsert_points(collection, points, None)
            .await?;
        Ok(())
    }
}
```

### Pattern 4: RAG Implementation

```python
# RAG pattern from agent-backend
class RAGAgent:
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm

    async def query(self, user_query, collection):
        # 1. Embed query
        query_embedding = await self.embed(user_query)

        # 2. Vector search
        relevant_docs = await self.vector_store.search(
            collection=collection,
            vector=query_embedding,
            limit=5
        )

        # 3. Build context
        context = "\n\n".join([
            doc.payload["text"] for doc in relevant_docs
        ])

        # 4. Generate response
        prompt = f"""Answer the question using the following context:

Context:
{context}

Question: {user_query}

Answer:"""

        response = await self.llm.agenerate(prompt)

        return {
            "answer": response,
            "sources": [doc.payload for doc in relevant_docs],
            "confidence": calculate_confidence(relevant_docs)
        }
```

---

## Deployment Patterns

### 1. Docker Setup

```bash
# Install script pattern
#!/bin/bash

# 1. Check prerequisites
command -v docker >/dev/null 2>&1 || {
    echo "Docker is required but not installed"
    exit 1
}

# 2. Build images
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Wait for health checks
while ! docker-compose ps | grep healthy; do
    sleep 1
done

echo "AgentCloud is ready!"
```

### 2. GCP Integration

```python
# GCP Secret Manager integration
from google.cloud import secretmanager

class SecretManager:
    def __init__(self, project_id):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

    def get_secret(self, secret_name):
        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
        response = self.client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")

# Usage
secrets = SecretManager(project_id="my-project")
openai_key = secrets.get_secret("openai-api-key")
```

### 3. GCS for Storage

```python
# File storage with GCS
from google.cloud import storage

class FileStorage:
    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    async def upload_file(self, file_path, destination_blob_name):
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        return blob.public_url

    async def download_file(self, source_blob_name, destination_file_path):
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_path)
```

---

## What to Extract

### 1. **Architecture Patterns**
- Microservice separation
- Backend/Frontend/Vector DB split
- Docker orchestration
- Service health checks

### 2. **Real-Time Communication**
- Socket.io patterns
- Event-driven architecture
- Streaming responses
- Status updates

### 3. **RAG Implementation**
- Vector search integration
- Context building
- Source tracking
- Confidence scoring

### 4. **Deployment**
- Docker-compose setup
- GCP integration
- Secret management
- File storage

### 5. **Data Source Integration**
- PostgreSQL connector
- BigQuery connector
- MongoDB connector
- Google Sheets connector

---

## Use Cases

1. **Internal Knowledge Base**
   - Company documentation Q&A
   - Policy and procedure lookup
   - Technical documentation search

2. **Customer Support**
   - FAQ chatbot
   - Product documentation
   - Ticket deflection

3. **Data Analysis**
   - Query company databases
   - Business intelligence
   - Report generation

---

## Implementation Guide

### Week 1: Setup
```bash
# Clone and install
git clone https://github.com/rnadigital/agentcloud
cd agentcloud
chmod +x install.sh
./install.sh
```

### Week 2: Configuration
```
- Configure data sources
- Set up vector database
- Configure LLM providers
- Test RAG pipeline
```

### Week 3: Customization
```
- Customize UI
- Add custom agents
- Configure permissions
- Set up authentication
```

### Week 4: Production
```
- Set up GCP project
- Configure secrets
- Deploy services
- Set up monitoring
```

---

## Key Takeaways

1. **Microservices:** Clean separation of concerns
2. **Real-Time:** Socket.io for streaming
3. **RAG Ready:** Built-in vector search
4. **Self-Hosted:** Full control and privacy
5. **Production-Grade:** Docker + GCP integration

---

## Related
- [Back to Overview](../REPOSITORY-ANALYSIS-OVERVIEW.md)
- [langchain-reference](./langchain-reference.md)
