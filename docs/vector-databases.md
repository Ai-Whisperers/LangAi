# Vector Database Strategy

## Decision: Start with Chroma, Migrate to Weaviate

### Why This Approach?

**Phase 1: Development & Prototyping (Chroma)**
- Zero configuration, embedded database
- Perfect for rapid iteration
- No separate server to manage
- Free and lightweight

**Phase 2: Production (Weaviate)**
- Hybrid search (keywords + vectors)
- Better scalability
- Production-grade features
- Multi-tenancy support

---

## Chroma Setup (Current Phase)

### Installation
```bash
pip install chromadb
```

### Basic Usage
```python
import chromadb
from chromadb.config import Settings

# Initialize client
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

# Create collection
collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

# Add documents
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["search query"],
    n_results=5
)
```

### Pros
- ✅ Embedded (no separate server)
- ✅ Fast setup (< 5 minutes)
- ✅ Perfect for local development
- ✅ Persistent storage
- ✅ Works offline

### Cons
- ❌ Limited scalability (< 1M vectors recommended)
- ❌ No distributed deployment
- ❌ Basic filtering capabilities
- ❌ Single machine only

---

## Weaviate Setup (Future Phase)

### Installation Options

**Option 1: Docker (Recommended for Development)**
```bash
# docker-compose.yml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: 'text2vec-openai,generative-openai'
      OPENAI_APIKEY: ${OPENAI_API_KEY}
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
```

**Option 2: Weaviate Cloud (Managed)**
```python
import weaviate

client = weaviate.Client(
    url="https://your-cluster.weaviate.network",
    auth_client_secret=weaviate.AuthApiKey(api_key="your-api-key"),
    additional_headers={
        "X-OpenAI-Api-Key": "your-openai-key"
    }
)
```

**Option 3: Self-Hosted (Kubernetes)**
```bash
helm repo add weaviate https://weaviate.github.io/weaviate-helm
helm install weaviate weaviate/weaviate
```

### Basic Usage
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Create schema
schema = {
    "class": "Document",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "text-embedding-3-small",
            "modelVersion": "003"
        }
    },
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Document content"
        },
        {
            "name": "source",
            "dataType": ["string"],
            "description": "Document source"
        },
        {
            "name": "timestamp",
            "dataType": ["date"]
        }
    ]
}

client.schema.create_class(schema)

# Add data
client.data_object.create(
    data_object={
        "content": "This is a document",
        "source": "doc1",
        "timestamp": "2025-12-05T00:00:00Z"
    },
    class_name="Document"
)

# Hybrid search (vector + keyword)
result = (
    client.query
    .get("Document", ["content", "source"])
    .with_hybrid(query="search query", alpha=0.5)
    .with_limit(5)
    .do()
)
```

### Pros
- ✅ Hybrid search (best of both worlds)
- ✅ Production-ready scalability
- ✅ GraphQL API
- ✅ Multi-model support
- ✅ Built-in vectorizers
- ✅ Advanced filtering
- ✅ Multi-tenancy

### Cons
- ❌ Requires separate server
- ❌ More complex setup
- ❌ Higher resource usage
- ❌ Steeper learning curve

---

## Migration Strategy

### When to Migrate?
Migrate from Chroma to Weaviate when:
- Dataset > 100K documents
- Need distributed deployment
- Need hybrid search
- Going to production with users
- Need advanced filtering
- Need multi-tenancy

### Migration Steps

**Step 1: Export from Chroma**
```python
import chromadb

client = chromadb.Client()
collection = client.get_collection("documents")

# Get all data
results = collection.get(
    include=["documents", "metadatas", "embeddings"]
)

documents = results["documents"]
metadatas = results["metadatas"]
embeddings = results["embeddings"]
ids = results["ids"]
```

**Step 2: Import to Weaviate**
```python
import weaviate

weaviate_client = weaviate.Client("http://localhost:8080")

# Batch import
with weaviate_client.batch as batch:
    batch.batch_size = 100

    for i, doc in enumerate(documents):
        batch.add_data_object(
            data_object={
                "content": doc,
                **metadatas[i]
            },
            class_name="Document",
            vector=embeddings[i]  # Use existing embeddings
        )
```

**Step 3: Update Application Code**
```python
# Abstract the vector store behind an interface
class VectorStore:
    def search(self, query: str, limit: int):
        raise NotImplementedError

class ChromaStore(VectorStore):
    # Chroma implementation
    pass

class WeaviateStore(VectorStore):
    # Weaviate implementation
    pass

# Switch between implementations via config
VECTOR_STORE = os.getenv("VECTOR_STORE", "chroma")
store = ChromaStore() if VECTOR_STORE == "chroma" else WeaviateStore()
```

---

## Comparison Table

| Feature | Chroma | Weaviate |
|---------|--------|----------|
| Setup Time | 5 min | 30 min |
| Deployment | Embedded | Server |
| Scalability | < 1M vectors | 100M+ vectors |
| Search Type | Vector only | Hybrid (vector + keyword) |
| Filtering | Basic | Advanced |
| Production Ready | Testing only | Yes |
| Cost | Free | Free (self-hosted) or $25+/mo |
| Best For | Prototypes | Production apps |

---

## Recommended Timeline

```
Week 1-4: Chroma
├─ Develop features
├─ Test locally
└─ Validate architecture

Week 5: Migration Planning
├─ Set up Weaviate dev environment
├─ Test migration script
└─ Compare performance

Week 6: Production Deploy
├─ Migrate data
├─ Deploy Weaviate
└─ Monitor performance
```

---

## Cost Considerations

### Chroma
- **Cost:** $0 (embedded)
- **Infrastructure:** Local disk space only

### Weaviate
- **Self-hosted:** $20-100/month (VPS/cloud compute)
- **Weaviate Cloud Sandbox:** Free (14 days)
- **Weaviate Cloud Standard:** $25/month (small cluster)
- **Weaviate Cloud Enterprise:** Custom pricing

---

## Performance Benchmarks

**Chroma:**
- Insert: ~1000 docs/sec
- Query: ~100ms (10K docs)
- Query: ~500ms (100K docs)

**Weaviate:**
- Insert: ~5000 docs/sec (with batching)
- Query: ~50ms (1M docs)
- Query: ~100ms (10M docs)
- Hybrid search: ~80ms (1M docs)

---

## Decision Log

**2025-12-05:** Decided to start with Chroma for rapid prototyping
- Rationale: Fastest path to MVP
- Risk: May need to migrate if scale exceeds expectations
- Mitigation: Abstract vector store behind interface from day 1

**Future Decision Point:** Migrate to Weaviate when:
- [ ] Dataset > 100K documents
- [ ] Need hybrid search features
- [ ] Ready for production deployment
- [ ] Have 100+ concurrent users
