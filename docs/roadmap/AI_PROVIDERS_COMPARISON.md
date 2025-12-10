# AI Providers Comparison for Company Research

Last Updated: December 2024

## Executive Summary

Your project can achieve **70-90% cost reduction** by implementing a hybrid multi-provider architecture while maintaining or improving research quality.

| Strategy | Cost Reduction | Quality Impact |
|----------|---------------|----------------|
| Current (Claude only) | Baseline | Excellent |
| + Prompt Caching | 60-70% | Same |
| + DeepSeek for bulk | 85-90% | Good (for extraction) |
| + Gemini for search | 75-85% | Good + citations |

---

## Quick Reference: Best Model by Task

| Task | Recommended Model | Cost/1M Tokens | Why |
|------|-------------------|----------------|-----|
| Simple extraction | DeepSeek-V3 | $0.14 / $0.27 | 99% cheaper, good quality |
| Search queries | Gemini Flash-8B | $0.04 / $0.15 | Native grounding, citations |
| Financial analysis | Claude Sonnet 4.5 | $3 / $15 | Best reasoning |
| Complex synthesis | Claude Opus 4.5 | $5 / $25 | Highest quality |
| Real-time queries | Groq Llama 70B | $0.59 / $0.79 | 1,300 tokens/sec |
| Bulk overnight | Any + Batch API | 50% off | All major providers |

---

## Tier 1: Premium Providers

### Anthropic Claude (Current - Keep for Quality)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| Opus 4.5 | $5 | $25 | Complex synthesis, investment thesis |
| Sonnet 4.5 | $3 | $15 | Daily research, analysis |
| Haiku 4.5 | $1 | $5 | Fast extraction, classification |

**Key Features:**
- Extended Thinking: Model "thinks" before responding (best for complex analysis)
- Prompt Caching: 90% savings on repeated contexts
- Batch API: 50% off for non-urgent work
- Web Search: $10/1K searches
- MCP: Model Context Protocol for tool integration

**Cost Optimization Already Implemented:**
- [x] Prompt caching ([prompt_cache.py](../../src/company_researcher/llm/prompt_cache.py))
- [x] Cost tracking ([cost_tracker.py](../../src/company_researcher/llm/cost_tracker.py))
- [x] Batch processing ([batch_processor.py](../../src/company_researcher/llm/batch_processor.py))
- [x] Model routing ([model_router.py](../../src/company_researcher/llm/model_router.py))

### OpenAI GPT-4

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| GPT-4o | $2.50 | $10 | General analysis |
| GPT-4o-mini | $0.15 | $0.60 | Budget extraction |
| o1 (reasoning) | $15 | $60 | Complex reasoning |

**Unique Features:**
- File Search: Built-in RAG ($0.10/GB/day, 1GB free)
- Code Interpreter: Python sandbox ($0.03/session)
- Assistants API: Persistent threads
- Batch API: 50% discount

### Google Gemini (Best for Long Context + Search)

| Model | Input | Output | Context | Best For |
|-------|-------|--------|---------|----------|
| Flash-8B | $0.04 | $0.15 | 1M | High-volume simple tasks |
| 1.5 Flash | $0.08 | $0.30 | 1M | General research |
| 1.5 Pro | $1.25 | $5.00 | 2M | Long document analysis |
| 2.0 Flash | $0.10 | $0.40 | 1M | Latest features |

**Unique Features:**
- Native Google Search Grounding: $35/1K queries (free in preview)
- 2M token context (largest available)
- Context Caching: 75% savings
- Batch Mode: 50% discount

---

## Tier 2: Chinese Providers (Ultra Low Cost)

### DeepSeek (Recommended for Bulk Work)

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| DeepSeek-V3 | $0.14 | $0.27 | Frontier quality, MIT license |
| DeepSeek-R1 | Variable | Variable | 75% off-peak discount |

**Why Use DeepSeek:**
- 99% cheaper than Claude/GPT-4
- 75.9% MMLU-Pro (beats GPT-4)
- Open source - can self-host
- 75% additional discount during off-peak hours
- Strong English + Chinese support

**Considerations:**
- Newer to market (Dec 2024)
- Data sovereignty concerns for sensitive data
- Less ecosystem/tooling support

### Alibaba Qwen

| Model | Price | Notes |
|-------|-------|-------|
| Qwen-Max | $0.41/1M | Best performance |
| Qwen-Plus | 80% price cut | Mid-tier |
| Qwen-Turbo | 85% price cut | Fast, economical |

### ByteDance Doubao

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| Doubao Pro | $0.11 | $0.27 | 99.8% cheaper than GPT-4 |
| Doubao Vision | $0.00041/1K | - | Cheapest vision model |

### Other Chinese Options

| Provider | Model | Price | Notes |
|----------|-------|-------|-------|
| Zhipu AI | GLM-4 | $0.14/1M | 25M free tokens |
| Baidu | ERNIE 4.0 | $0.016/1K | Speed/Lite free |
| Moonshot | Kimi | $0.70/1M cache | Ultra-long context |
| 01.AI | Yi-Lightning | $0.14/1M | Strong engineering |

---

## Tier 3: Speed & Budget Western

### Groq (Fastest Inference)

| Model | Input | Output | Speed |
|-------|-------|--------|-------|
| Llama 3.1 8B | $0.05 | $0.08 | 1,300 tok/sec |
| Llama 3.1 70B | $0.59 | $0.79 | 814 tok/sec |
| Llama 3.1 405B | $3.00 | $3.00 | Variable |

**Why Groq:**
- 10-100x faster than GPU inference
- Batch processing: 50% off
- Free tier available
- Ideal for real-time research queries

### Mistral AI

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| Large 2 | $8.00 | $24.00 | 123B params, European |
| Small | Variable | Variable | 22B params |
| Codestral | Variable | Variable | Code specialist |

**Why Mistral:**
- European data sovereignty
- Free tier for prototyping
- Can self-host
- Open-source options

### Together AI / Fireworks AI

| Provider | Llama 70B Price | Speed | Notes |
|----------|-----------------|-------|-------|
| Together AI | ~$0.88/1M | High | Reliable infrastructure |
| Fireworks AI | ~$0.90/1M | Highest | HIPAA/SOC2 compliant |

### Perplexity API

**Pricing:**
- Search API: Per-request (no token costs)
- Pro users: $5/month API credits
- Enterprise: $40/user/month

**Why Perplexity:**
- Search-native with citations
- Structured source returns
- No token costs for pure search

---

## Implementation Architecture

### Recommended Hybrid Setup

```
                    ┌─────────────────────────────────────┐
                    │         Research Request            │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │         Task Router           │
                    │   (model_router.py enhanced)  │
                    └───────────────────────────────┘
                        │           │           │
         ┌──────────────┴──┐   ┌────┴────┐   ┌──┴──────────────┐
         │                 │   │         │   │                 │
    ┌────▼────┐       ┌────▼───▼┐   ┌────▼───▼┐       ┌────────▼────────┐
    │ BULK    │       │ SEARCH  │   │ ANALYSIS│       │ SYNTHESIS       │
    │ DeepSeek│       │ Gemini  │   │ Claude  │       │ Claude Opus     │
    │ $0.14/M │       │ $0.04/M │   │ $3/M    │       │ $5/M            │
    └─────────┘       └─────────┘   └─────────┘       └─────────────────┘
         │                 │             │                    │
         └─────────────────┴─────────────┴────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │        Cost Tracker           │
                    │   (multi-provider support)    │
                    └───────────────────────────────┘
```

### Cost Flow by Task Type

| Task | Volume | Provider | Cost/1M | Monthly Est. |
|------|--------|----------|---------|--------------|
| Search queries | 500M tokens | Gemini Flash-8B | $0.04 | $20 |
| Data extraction | 300M tokens | DeepSeek-V3 | $0.14 | $42 |
| Analysis | 100M tokens | Claude Sonnet | $3.00 | $300 |
| Synthesis | 20M tokens | Claude Opus | $5.00 | $100 |
| **Total** | **920M tokens** | **Hybrid** | - | **$462** |

**vs. Claude-only:** 920M tokens @ $3/1M = $2,760/month
**Savings:** $2,298/month (83%)

---

## Implementation Plan

### Phase 1: Optimize Current Claude (Week 1)

**Already Done:**
- [x] Prompt caching (90% savings)
- [x] Batch processing (50% savings)
- [x] Model routing
- [x] Cost tracking

**To Do:**
- [ ] Update to latest models (Sonnet 4.5, Opus 4.5, Haiku 4.5)
- [ ] Enable extended thinking for complex analysis
- [ ] Integrate web search tool

### Phase 2: Add Budget Providers (Week 2-3)

**Priority 1: DeepSeek-V3**
- Best value for bulk extraction
- $0.14/1M tokens (99% savings)
- Use for: Initial data gathering, simple extraction

**Priority 2: Gemini Flash-8B**
- Best for search with citations
- $0.04/1M tokens
- Use for: Search queries, grounding, fact-checking

**Priority 3: Groq Llama 70B**
- Best for speed
- $0.59/1M tokens, 1,300 tok/sec
- Use for: Real-time queries, interactive features

### Phase 3: Specialized Tools (Week 4+)

- [ ] Perplexity API for search citations
- [ ] OpenAI File Search for document RAG
- [ ] Gemini grounding for fact-checking

---

## Provider Integration Code

### DeepSeek Client

```python
# src/company_researcher/llm/deepseek_client.py
"""
DeepSeek API integration for ultra-low-cost bulk processing.

Cost: $0.14 input, $0.27 output per 1M tokens
Performance: Matches GPT-4/Claude on most benchmarks
"""

from openai import OpenAI  # DeepSeek uses OpenAI-compatible API
from typing import Optional, Dict, Any, List
import os

class DeepSeekClient:
    """
    DeepSeek API client for cost-effective bulk processing.

    Uses OpenAI-compatible API format.
    99% cheaper than Claude/GPT-4.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.default_model = "deepseek-chat"  # V3

    def create_message(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """Create a completion with DeepSeek."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return {
            "content": response.choices[0].message.content,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "model": response.model
        }

    def extract_company_data(
        self,
        company_name: str,
        search_results: str,
        fields: List[str]
    ) -> Dict[str, Any]:
        """
        Extract structured company data.

        Cost-effective for bulk extraction tasks.
        """
        prompt = f"""Extract the following fields for {company_name}:
{chr(10).join(f'- {field}' for field in fields)}

Search Results:
{search_results}

Return JSON with the extracted fields. Use null for missing data."""

        response = self.create_message(
            prompt=prompt,
            system="You are a data extraction specialist. Return valid JSON only.",
            max_tokens=2000
        )

        return response


# Pricing (per 1M tokens)
DEEPSEEK_PRICING = {
    "deepseek-chat": {  # V3
        "input": 0.14,
        "output": 0.27,
        "cache_hit": 0.014  # 90% discount for cached
    },
    "deepseek-reasoner": {  # R1
        "input": 0.55,
        "output": 2.19,
        "cache_hit": 0.14
    }
}
```

### Gemini Client with Grounding

```python
# src/company_researcher/llm/gemini_client.py
"""
Google Gemini integration with native search grounding.

Features:
- 1-2M token context
- Native Google Search grounding ($35/1K queries, free in preview)
- Context caching (75% savings)
"""

import google.generativeai as genai
from typing import Optional, Dict, Any, List
import os


class GeminiClient:
    """
    Gemini API client with search grounding.

    Best for: Long context, search with citations
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        self.default_model = "gemini-1.5-flash-8b"

    def search_with_grounding(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search with Google grounding - returns citations.

        Cost: $35/1K grounded queries (free during preview)
        """
        model_name = model or self.default_model
        model_instance = genai.GenerativeModel(
            model_name,
            tools=[genai.Tool(google_search=genai.GoogleSearch())]
        )

        prompt = query
        if context:
            prompt = f"{context}\n\nSearch for: {query}"

        response = model_instance.generate_content(prompt)

        # Extract grounding metadata
        sources = []
        if hasattr(response, 'grounding_metadata'):
            for chunk in response.grounding_metadata.grounding_chunks:
                if hasattr(chunk, 'web'):
                    sources.append({
                        "title": chunk.web.title,
                        "uri": chunk.web.uri
                    })

        return {
            "content": response.text,
            "sources": sources,
            "grounding_used": bool(sources)
        }

    def analyze_long_document(
        self,
        document: str,
        analysis_prompt: str,
        model: str = "gemini-1.5-pro"
    ) -> Dict[str, Any]:
        """
        Analyze documents up to 2M tokens.

        Best for: Annual reports, large document sets
        """
        model_instance = genai.GenerativeModel(model)

        response = model_instance.generate_content(
            f"{analysis_prompt}\n\nDocument:\n{document}"
        )

        return {
            "content": response.text,
            "model": model
        }


# Pricing (per 1M tokens)
GEMINI_PRICING = {
    "gemini-1.5-flash-8b": {
        "input": 0.0375,
        "output": 0.15,
        "input_long": 0.075,  # >128K tokens
        "output_long": 0.30
    },
    "gemini-1.5-flash": {
        "input": 0.075,
        "output": 0.30,
        "input_long": 0.15,
        "output_long": 0.60
    },
    "gemini-1.5-pro": {
        "input": 1.25,
        "output": 5.00,
        "input_long": 2.50,
        "output_long": 10.00
    },
    "grounding": {
        "per_1k_queries": 35.00  # Free during preview
    }
}
```

### Groq Client for Speed

```python
# src/company_researcher/llm/groq_client.py
"""
Groq integration for ultra-fast inference.

Speed: 1,300 tokens/second (10-100x faster than GPU)
Cost: $0.05-$0.59 input, $0.08-$0.79 output per 1M tokens
"""

from groq import Groq
from typing import Optional, Dict, Any
import os


class GroqClient:
    """
    Groq API client for speed-critical operations.

    Best for: Real-time queries, interactive features
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.default_model = "llama-3.1-70b-versatile"

    def fast_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Ultra-fast completion (1,300 tok/sec).

        Ideal for real-time company lookups.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0
        )

        return {
            "content": response.choices[0].message.content,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "model": response.model
        }


# Pricing (per 1M tokens)
GROQ_PRICING = {
    "llama-3.1-8b-instant": {
        "input": 0.05,
        "output": 0.08,
        "speed": 1300  # tokens/sec
    },
    "llama-3.1-70b-versatile": {
        "input": 0.59,
        "output": 0.79,
        "speed": 814
    },
    "llama-3.1-405b": {
        "input": 3.00,
        "output": 3.00,
        "speed": "variable"
    }
}
```

---

## Environment Variables

Add to `.env`:

```bash
# Anthropic (current)
ANTHROPIC_API_KEY=sk-ant-...

# Chinese Providers (ultra-low cost)
DEEPSEEK_API_KEY=sk-...
QWEN_API_KEY=...
DOUBAO_API_KEY=...

# Western Budget
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=...
MISTRAL_API_KEY=...

# Specialized
PERPLEXITY_API_KEY=pplx-...
OPENAI_API_KEY=sk-...

# Provider Selection
DEFAULT_BULK_PROVIDER=deepseek
DEFAULT_SEARCH_PROVIDER=gemini
DEFAULT_ANALYSIS_PROVIDER=anthropic
DEFAULT_SPEED_PROVIDER=groq
```

---

## Cost Comparison Summary

### Per 1M Tokens (Input/Output)

| Provider | Model | Input | Output | vs Claude |
|----------|-------|-------|--------|-----------|
| DeepSeek | V3 | $0.14 | $0.27 | **99% cheaper** |
| Doubao | Pro | $0.11 | $0.27 | **99% cheaper** |
| Gemini | Flash-8B | $0.04 | $0.15 | **99% cheaper** |
| Groq | Llama 8B | $0.05 | $0.08 | **98% cheaper** |
| Groq | Llama 70B | $0.59 | $0.79 | **80% cheaper** |
| Gemini | 1.5 Flash | $0.08 | $0.30 | **97% cheaper** |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | **95% cheaper** |
| Qwen | Max | $0.41 | ~$1.00 | **86% cheaper** |
| Gemini | 1.5 Pro | $1.25 | $5.00 | **58% cheaper** |
| OpenAI | GPT-4o | $2.50 | $10.00 | **17% cheaper** |
| Anthropic | Sonnet 4.5 | $3.00 | $15.00 | Baseline |
| Anthropic | Opus 4.5 | $5.00 | $25.00 | Premium |

---

## Recommendations

### For Your Project

1. **Keep Claude for quality work** - Final synthesis, complex analysis
2. **Add DeepSeek for bulk** - 99% savings on extraction tasks
3. **Add Gemini for search** - Native grounding with citations
4. **Add Groq for speed** - Real-time interactive features

### Implementation Priority

| Priority | Action | Savings | Effort |
|----------|--------|---------|--------|
| 1 | Update Claude models to 4.5 | 10-20% | Low |
| 2 | Enable extended thinking | Quality++ | Low |
| 3 | Add DeepSeek client | 85-90% on bulk | Medium |
| 4 | Add Gemini grounding | Better citations | Medium |
| 5 | Add Groq for speed | 10-100x faster | Medium |

### Risk Mitigation

**For Chinese Providers:**
- Use only for public company data
- Implement fallback to Western providers
- Consider self-hosting open-source versions
- Monitor API availability

**For All Providers:**
- A/B test quality before full migration
- Implement circuit breakers for cost control
- Maintain multi-provider redundancy
