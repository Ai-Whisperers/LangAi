# LLM Setup & Routing Strategy

## Available Models

We have access to three tiers of LLMs:

### Cloud Models
1. **OpenAI GPT-4** - Best reasoning, most expensive
2. **Anthropic Claude** - Long context, safe outputs

### Local Models
3. **Llama** - Privacy-first, zero cost per request
4. **Other local models** - Specialized use cases

---

## LiteLLM - Unified Interface

### Why LiteLLM?

**Problem:** Each LLM provider has different APIs:
```python
# OpenAI
response = openai.ChatCompletion.create(...)

# Anthropic
response = anthropic.messages.create(...)

# Local models (Ollama)
response = ollama.chat(...)
```

**Solution:** LiteLLM provides one interface:
```python
from litellm import completion

# Works for ALL models
response = completion(
    model="gpt-4",  # or "claude-3", "ollama/llama3"
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Installation
```bash
pip install litellm
```

### Configuration
```python
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
```

### Basic Usage
```python
import os
from litellm import completion

# Set API keys
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["ANTHROPIC_API_KEY"] = "your-key"

# GPT-4
response = completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)

# Claude
response = completion(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)

# Local Llama (via Ollama)
response = completion(
    model="ollama/llama3",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    api_base="http://localhost:11434"
)

print(response.choices[0].message.content)
```

---

## Smart LLM Router

### Routing Strategy

Route requests based on:
1. **Sensitivity** - Is data private?
2. **Complexity** - Simple vs complex reasoning
3. **Cost** - Budget constraints
4. **Latency** - Speed requirements
5. **Context length** - Token limits

### Implementation

```python
from enum import Enum
from dataclasses import dataclass
from litellm import completion

class Sensitivity(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"

class Complexity(Enum):
    SIMPLE = "simple"      # FAQ, classification
    MODERATE = "moderate"  # Summarization, translation
    COMPLEX = "complex"    # Reasoning, code generation

@dataclass
class LLMRequest:
    prompt: str
    sensitivity: Sensitivity
    complexity: Complexity
    max_tokens: int = 1000
    temperature: float = 0.7

class LLMRouter:
    """Smart routing between GPT-4, Claude, and Llama"""

    def __init__(self):
        self.model_config = {
            "gpt-4": {
                "cost_per_1k_tokens": 0.03,
                "max_context": 8192,
                "strengths": ["reasoning", "code", "complex_tasks"]
            },
            "gpt-3.5-turbo": {
                "cost_per_1k_tokens": 0.002,
                "max_context": 16385,
                "strengths": ["simple_tasks", "fast", "cheap"]
            },
            "claude-3-sonnet-20240229": {
                "cost_per_1k_tokens": 0.015,
                "max_context": 200000,
                "strengths": ["long_context", "safety", "instruction_following"]
            },
            "ollama/llama3": {
                "cost_per_1k_tokens": 0.0,
                "max_context": 8192,
                "strengths": ["privacy", "offline", "zero_cost"]
            }
        }

    def route(self, request: LLMRequest) -> str:
        """Choose the best model for this request"""

        # Rule 1: Confidential data → local model only
        if request.sensitivity == Sensitivity.CONFIDENTIAL:
            return "ollama/llama3"

        # Rule 2: Simple tasks → cheapest cloud model
        if request.complexity == Complexity.SIMPLE:
            return "gpt-3.5-turbo"

        # Rule 3: Long context → Claude
        if request.max_tokens > 8000:
            return "claude-3-sonnet-20240229"

        # Rule 4: Complex reasoning → GPT-4
        if request.complexity == Complexity.COMPLEX:
            return "gpt-4"

        # Default: Moderate tasks → Claude (good balance)
        return "claude-3-sonnet-20240229"

    def complete(self, request: LLMRequest) -> str:
        """Execute request with automatic routing"""

        model = self.route(request)

        print(f"🤖 Routing to: {model}")
        print(f"📊 Reason: {request.complexity.value}, {request.sensitivity.value}")

        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ {model} failed: {e}")
            # Fallback to local model
            print("🔄 Falling back to local Llama...")
            return self._fallback(request)

    def _fallback(self, request: LLMRequest) -> str:
        """Fallback to local model"""
        response = completion(
            model="ollama/llama3",
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return response.choices[0].message.content

# Usage
router = LLMRouter()

# Example 1: Simple public task → GPT-3.5
response = router.complete(LLMRequest(
    prompt="What is the capital of France?",
    sensitivity=Sensitivity.PUBLIC,
    complexity=Complexity.SIMPLE
))

# Example 2: Complex confidential task → Llama
response = router.complete(LLMRequest(
    prompt="Analyze this confidential customer data...",
    sensitivity=Sensitivity.CONFIDENTIAL,
    complexity=Complexity.COMPLEX
))

# Example 3: Long context → Claude
response = router.complete(LLMRequest(
    prompt="Summarize this 50-page document...",
    sensitivity=Sensitivity.INTERNAL,
    complexity=Complexity.MODERATE,
    max_tokens=15000
))
```

---

## Cost Optimization Patterns

### Pattern 1: Cascade Approach
```python
def cascade_completion(prompt: str):
    """Try cheap model first, escalate if needed"""

    # Step 1: Try cheap model
    response = completion(model="gpt-3.5-turbo", messages=[...])

    # Step 2: Check confidence
    confidence = extract_confidence(response)

    # Step 3: Escalate if low confidence
    if confidence < 0.7:
        print("⬆️ Escalating to GPT-4...")
        response = completion(model="gpt-4", messages=[...])

    return response
```

### Pattern 2: Retrieval-First
```python
def retrieval_first(query: str):
    """Use cheap embeddings + retrieval, expensive LLM only for generation"""

    # Step 1: Cheap embedding (OpenAI text-embedding-3-small)
    embedding = get_embedding(query)  # $0.02 per 1M tokens

    # Step 2: Vector search (fast, cheap)
    results = vector_db.search(embedding, limit=5)

    # Step 3: Check if answer is in results
    has_answer = cheap_classifier(query, results)  # GPT-3.5

    # Step 4: Only use expensive model if needed
    if not has_answer:
        response = completion(model="gpt-4", messages=[...])  # $30 per 1M tokens
    else:
        response = results[0]

    return response
```

### Pattern 3: Caching Layer
```python
import hashlib
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def cached_completion(prompt: str, model: str):
    """Cache LLM responses to avoid duplicate API calls"""

    # Create cache key
    cache_key = hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()

    # Check cache
    cached = cache.get(cache_key)
    if cached:
        print("💰 Cache hit - saved API call!")
        return cached.decode()

    # Call LLM
    response = completion(model=model, messages=[{"role": "user", "content": prompt}])
    result = response.choices[0].message.content

    # Store in cache (24 hour TTL)
    cache.setex(cache_key, 86400, result)

    return result
```

---

## Model Comparison

| Model | Cost/1M tokens | Speed | Context | Best For |
|-------|---------------|-------|---------|----------|
| GPT-4 | $30 | Slow | 8K | Complex reasoning, code |
| GPT-3.5-turbo | $2 | Fast | 16K | Simple tasks, high volume |
| Claude 3 Sonnet | $15 | Medium | 200K | Long docs, safety |
| Llama 3 (local) | $0 | Fast* | 8K | Privacy, offline, high volume |

*After initial model load

---

## Fallback Strategy

```python
class RobustLLMRouter:
    """Router with automatic fallbacks"""

    def __init__(self):
        self.fallback_chain = [
            "gpt-4",                      # Primary
            "claude-3-sonnet-20240229",   # Fallback 1
            "gpt-3.5-turbo",              # Fallback 2
            "ollama/llama3"               # Last resort (always available)
        ]

    def complete_with_fallback(self, prompt: str):
        """Try models in order until one succeeds"""

        last_error = None

        for model in self.fallback_chain:
            try:
                print(f"🔄 Trying {model}...")
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=30
                )
                print(f"✅ Success with {model}")
                return response.choices[0].message.content

            except Exception as e:
                print(f"❌ {model} failed: {e}")
                last_error = e
                continue

        raise Exception(f"All models failed. Last error: {last_error}")
```

---

## Monitoring & Logging

```python
import time
from datetime import datetime

class LLMMonitor:
    """Track LLM usage, costs, and performance"""

    def __init__(self):
        self.metrics = []

    def track_request(self, model: str, prompt: str, response: str):
        """Log each LLM request"""

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": len(prompt.split()) * 1.3,  # Rough estimate
            "completion_tokens": len(response.split()) * 1.3,
            "total_tokens": None,  # Will calculate
            "cost": None,  # Will calculate
            "latency": None  # Set during request
        }

        # Calculate totals
        metrics["total_tokens"] = metrics["prompt_tokens"] + metrics["completion_tokens"]

        # Calculate cost
        cost_per_1k = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3-sonnet-20240229": 0.015,
            "ollama/llama3": 0.0
        }

        metrics["cost"] = (metrics["total_tokens"] / 1000) * cost_per_1k.get(model, 0)

        self.metrics.append(metrics)

        # Log to console
        print(f"📊 {model}: {metrics['total_tokens']:.0f} tokens, ${metrics['cost']:.4f}")

    def get_daily_summary(self):
        """Get daily cost summary"""
        total_cost = sum(m["cost"] for m in self.metrics)
        total_requests = len(self.metrics)

        by_model = {}
        for m in self.metrics:
            model = m["model"]
            if model not in by_model:
                by_model[model] = {"requests": 0, "cost": 0}
            by_model[model]["requests"] += 1
            by_model[model]["cost"] += m["cost"]

        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "by_model": by_model
        }

# Usage with monitor
monitor = LLMMonitor()

def tracked_completion(model: str, prompt: str):
    start = time.time()

    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    latency = time.time() - start
    result = response.choices[0].message.content

    monitor.track_request(model, prompt, result)

    return result
```

---

## Local Model Setup (Ollama)

### Installation
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3
ollama pull llama3

# Pull other models
ollama pull mistral
ollama pull codellama
```

### Running
```bash
# Start Ollama server
ollama serve

# Test
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is the sky blue?"
}'
```

### Python Integration
```python
from litellm import completion

response = completion(
    model="ollama/llama3",
    messages=[{"role": "user", "content": "Hello!"}],
    api_base="http://localhost:11434"
)
```

---

## Decision Matrix

Use this table to decide which model to use:

| Scenario | Recommended Model | Rationale |
|----------|------------------|-----------|
| Customer-facing chat | GPT-4 or Claude | Best quality |
| Internal tools | GPT-3.5-turbo | Good balance |
| High-volume simple tasks | GPT-3.5-turbo | Cheapest |
| Long document analysis | Claude | 200K context |
| Sensitive/private data | Llama (local) | Zero data leaks |
| Offline/air-gapped | Llama (local) | No internet needed |
| Code generation | GPT-4 | Best at code |
| Cost-sensitive | Llama (local) | $0 per request |

---

## Next Steps

1. Install LiteLLM: `pip install litellm`
2. Set up API keys in `.env`
3. Install Ollama for local models
4. Implement basic router
5. Add monitoring
6. Test fallback chain
7. Optimize based on actual usage patterns

---

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Ollama Documentation](https://ollama.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [Anthropic Pricing](https://www.anthropic.com/api)
