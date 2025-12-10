# Claude API Implementation Guide

This document outlines how to leverage the latest Claude API features in the Company Researcher project.

## Current Integration Status

| Feature | Status | Notes |
|---------|--------|-------|
| Anthropic API | Implemented | [client_factory.py](../../src/company_researcher/llm/client_factory.py) |
| Prompt Caching | Implemented | [prompt_cache.py](../../src/company_researcher/llm/prompt_cache.py) |
| Cost Tracking | Implemented | [cost_tracker.py](../../src/company_researcher/llm/cost_tracker.py) |
| Model Routing | Implemented | [model_router.py](../../src/company_researcher/llm/model_router.py) |
| **Batch API** | **Not Implemented** | 50% cost savings opportunity |
| **Web Search Tool** | **Not Implemented** | $10/1K searches |
| **Code Execution** | Not Needed | Python sandbox for data analysis |

---

## 1. Updated Model Pricing (December 2024)

### Latest Models

| Model | Input | Output | Cached Read | Use Case |
|-------|-------|--------|-------------|----------|
| **Opus 4.5** | $5/MTok | $25/MTok | $0.50/MTok | Complex synthesis, investment thesis |
| **Sonnet 4.5** | $3/MTok | $15/MTok | $0.30/MTok | Daily research, analysis |
| **Haiku 4.5** | $1/MTok | $5/MTok | $0.10/MTok | Fast extraction, classification |

### Legacy Models (Still Supported)

| Model | Input | Output | Cached Read |
|-------|-------|--------|-------------|
| Opus 4.1 | $15/MTok | $75/MTok | $1.50/MTok |
| Sonnet 4 | $3/MTok | $15/MTok | $0.30/MTok |
| Haiku 3.5 | $0.80/MTok | $4/MTok | $0.08/MTok |

### Cost Comparison for Company Research

Assuming 50K input tokens + 5K output per research:

| Model | Cost per Research | Quality |
|-------|-------------------|---------|
| Haiku 4.5 | $0.075 | Good for extraction |
| Sonnet 4.5 | $0.225 | Best value for analysis |
| Opus 4.5 | $0.375 | Premium for synthesis |
| **Batch (Sonnet 4.5)** | **$0.1125** | **50% savings** |

---

## 2. Batch API Integration

The Batch API provides **50% cost savings** for non-urgent workloads.

### When to Use Batch API

- Processing multiple companies overnight
- Generating comparison reports
- Bulk data extraction
- Non-time-sensitive analysis

### Implementation

```python
# src/company_researcher/llm/batch_processor.py
"""
Batch API integration for cost-efficient bulk processing.

Provides 50% cost reduction on input and output tokens.
Results available within 24 hours (typically faster).
"""

from anthropic import Anthropic
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import time


@dataclass
class BatchRequest:
    """Individual request in a batch."""
    custom_id: str
    model: str
    max_tokens: int
    messages: List[Dict[str, str]]
    system: Optional[str] = None


@dataclass
class BatchJob:
    """Batch job tracking."""
    batch_id: str
    status: str
    created_at: datetime
    request_count: int
    company_names: List[str]


class BatchProcessor:
    """
    Process multiple company analyses via Batch API.

    Benefits:
    - 50% cost reduction
    - Parallel processing
    - Results within 24 hours

    Usage:
        processor = BatchProcessor()

        # Add research requests
        processor.add_request("tesla", "Analyze Tesla's market position")
        processor.add_request("nvidia", "Analyze NVIDIA's competitive moat")

        # Submit batch
        batch_id = processor.submit_batch()

        # Check status (or wait)
        results = processor.wait_for_results(batch_id, timeout_hours=2)
    """

    def __init__(self, client: Optional[Anthropic] = None):
        from ..config import get_config
        self.config = get_config()
        self.client = client or Anthropic(api_key=self.config.anthropic_api_key)
        self.requests: List[BatchRequest] = []
        self.jobs: Dict[str, BatchJob] = {}

    def add_request(
        self,
        company_name: str,
        prompt: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Add a company analysis request to the batch.

        Args:
            company_name: Company identifier (used as custom_id)
            prompt: Analysis prompt
            model: Model to use (default: Sonnet 4.5)
            max_tokens: Max output tokens
            system_prompt: Optional system instructions

        Returns:
            custom_id for tracking
        """
        custom_id = f"research_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        request = BatchRequest(
            custom_id=custom_id,
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            system=system_prompt
        )
        self.requests.append(request)
        return custom_id

    def submit_batch(self) -> str:
        """
        Submit all pending requests as a batch.

        Returns:
            batch_id for tracking
        """
        if not self.requests:
            raise ValueError("No requests to submit")

        # Create JSONL file content
        requests_jsonl = []
        company_names = []

        for req in self.requests:
            request_body = {
                "model": req.model,
                "max_tokens": req.max_tokens,
                "messages": req.messages
            }
            if req.system:
                request_body["system"] = req.system

            requests_jsonl.append({
                "custom_id": req.custom_id,
                "params": request_body
            })

            # Extract company name from custom_id
            parts = req.custom_id.split("_")
            if len(parts) >= 2:
                company_names.append(parts[1])

        # Submit batch via API
        batch = self.client.batches.create(
            requests=requests_jsonl
        )

        # Track job
        self.jobs[batch.id] = BatchJob(
            batch_id=batch.id,
            status=batch.processing_status,
            created_at=datetime.now(),
            request_count=len(self.requests),
            company_names=company_names
        )

        # Clear pending requests
        self.requests = []

        return batch.id

    def get_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get status of a batch job.

        Returns:
            Dict with status, progress, and any errors
        """
        batch = self.client.batches.retrieve(batch_id)

        return {
            "id": batch.id,
            "status": batch.processing_status,
            "request_counts": {
                "total": batch.request_counts.total,
                "completed": batch.request_counts.succeeded,
                "failed": batch.request_counts.errored
            },
            "created_at": batch.created_at,
            "ended_at": batch.ended_at
        }

    def get_results(self, batch_id: str) -> Dict[str, Any]:
        """
        Retrieve results from a completed batch.

        Returns:
            Dict mapping custom_id to response content
        """
        batch = self.client.batches.retrieve(batch_id)

        if batch.processing_status != "ended":
            raise ValueError(f"Batch not complete. Status: {batch.processing_status}")

        results = {}

        # Iterate through results
        for result in self.client.batches.results(batch_id):
            custom_id = result.custom_id

            if result.result.type == "succeeded":
                content = result.result.message.content[0].text
                results[custom_id] = {
                    "status": "success",
                    "content": content,
                    "usage": {
                        "input_tokens": result.result.message.usage.input_tokens,
                        "output_tokens": result.result.message.usage.output_tokens
                    }
                }
            else:
                results[custom_id] = {
                    "status": "error",
                    "error": str(result.result.error)
                }

        return results

    def wait_for_results(
        self,
        batch_id: str,
        timeout_hours: float = 24,
        poll_interval_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Wait for batch completion and return results.

        Args:
            batch_id: Batch to wait for
            timeout_hours: Max wait time (default 24h)
            poll_interval_seconds: How often to check (default 60s)

        Returns:
            Results dict from get_results()
        """
        timeout_seconds = timeout_hours * 3600
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            status = self.get_status(batch_id)

            if status["status"] == "ended":
                return self.get_results(batch_id)

            if status["status"] == "failed":
                raise RuntimeError(f"Batch failed: {status}")

            time.sleep(poll_interval_seconds)

        raise TimeoutError(f"Batch {batch_id} did not complete within {timeout_hours} hours")


# Module-level convenience function
_batch_processor: Optional[BatchProcessor] = None

def get_batch_processor() -> BatchProcessor:
    """Get singleton batch processor instance."""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor
```

### Usage Example

```python
from company_researcher.llm.batch_processor import get_batch_processor

# Initialize
processor = get_batch_processor()

# Queue multiple companies
companies = ["Tesla", "NVIDIA", "Apple", "Microsoft", "Google"]

for company in companies:
    processor.add_request(
        company_name=company.lower(),
        prompt=f"""Analyze {company}'s competitive position:
        1. Market share and trends
        2. Key competitors
        3. Moats and advantages
        4. Risks and challenges
        5. Growth outlook""",
        system_prompt="You are a senior financial analyst."
    )

# Submit batch (50% cheaper than real-time)
batch_id = processor.submit_batch()
print(f"Submitted batch: {batch_id}")

# Wait for results (typically 1-2 hours)
results = processor.wait_for_results(batch_id, timeout_hours=4)

# Process results
for custom_id, result in results.items():
    if result["status"] == "success":
        print(f"\n=== {custom_id} ===")
        print(result["content"][:500] + "...")
```

---

## 3. Web Search Tool Integration

Claude's Web Search tool provides real-time information at **$10 per 1,000 searches**.

### Benefits for Company Research

- Real-time news and press releases
- Latest financial data
- Current market sentiment
- Recent company announcements

### Implementation

```python
# src/company_researcher/llm/web_search.py
"""
Claude Web Search integration for real-time company information.

Cost: $10 per 1,000 searches (separate from token costs)
"""

from anthropic import Anthropic
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ClaudeWebSearch:
    """
    Real-time web search via Claude API.

    Use for:
    - Latest news and press releases
    - Current market data
    - Recent announcements
    - Competitive intelligence

    Cost: $10 per 1,000 searches
    """

    def __init__(self, client: Optional[Anthropic] = None):
        from ..config import get_config
        self.config = get_config()
        self.client = client or Anthropic(api_key=self.config.anthropic_api_key)
        self.search_count = 0

    def search(
        self,
        query: str,
        context: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Perform web search via Claude.

        Args:
            query: Search query (e.g., "Tesla Q4 2024 earnings")
            context: Additional context for the search
            model: Model to use
            max_tokens: Max response tokens

        Returns:
            Dict with search results and analysis
        """
        prompt = f"Search for: {query}"
        if context:
            prompt += f"\n\nContext: {context}"

        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=[{"type": "web_search"}],
            messages=[{"role": "user", "content": prompt}]
        )

        self.search_count += 1

        # Extract search results and analysis
        result = {
            "query": query,
            "content": "",
            "sources": [],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

        for block in response.content:
            if block.type == "text":
                result["content"] = block.text
            elif block.type == "tool_use" and block.name == "web_search":
                # Extract source URLs if available
                if hasattr(block, "input") and "urls" in block.input:
                    result["sources"] = block.input["urls"]

        return result

    def research_company_news(
        self,
        company_name: str,
        topics: Optional[List[str]] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get latest news for a company.

        Args:
            company_name: Company to research
            topics: Specific topics (e.g., ["earnings", "acquisitions"])
            days_back: How far back to search

        Returns:
            Structured news analysis
        """
        topics_str = ", ".join(topics) if topics else "general news"

        query = f"{company_name} latest {topics_str} past {days_back} days"
        context = f"""
        Focus on:
        1. Financial results and guidance
        2. Strategic announcements
        3. Product launches
        4. Leadership changes
        5. Market reactions

        Provide structured analysis with:
        - Key headlines
        - Important facts with dates
        - Sentiment analysis
        - Source citations
        """

        return self.search(query, context)

    def get_competitive_intelligence(
        self,
        company_name: str,
        competitors: List[str]
    ) -> Dict[str, Any]:
        """
        Get competitive analysis from recent sources.

        Args:
            company_name: Target company
            competitors: List of competitor names

        Returns:
            Competitive analysis with sources
        """
        competitors_str = ", ".join(competitors)

        query = f"{company_name} vs {competitors_str} competitive analysis market share"
        context = f"""
        Compare {company_name} with {competitors_str}:
        1. Market share comparison
        2. Recent competitive moves
        3. Product/service differentiation
        4. Pricing strategies
        5. Growth trajectories

        Use the most recent data available.
        Cite specific sources and dates.
        """

        return self.search(query, context)

    def get_search_stats(self) -> Dict[str, Any]:
        """Get search usage statistics."""
        return {
            "total_searches": self.search_count,
            "estimated_cost": self.search_count * 0.01  # $0.01 per search
        }


# Module-level convenience
_web_search: Optional[ClaudeWebSearch] = None

def get_web_search() -> ClaudeWebSearch:
    """Get singleton web search instance."""
    global _web_search
    if _web_search is None:
        _web_search = ClaudeWebSearch()
    return _web_search
```

### Usage Example

```python
from company_researcher.llm.web_search import get_web_search

search = get_web_search()

# Get latest news
news = search.research_company_news(
    company_name="Tesla",
    topics=["earnings", "Cybertruck", "FSD"],
    days_back=14
)

print(news["content"])
print(f"Sources: {news['sources']}")

# Competitive intelligence
intel = search.get_competitive_intelligence(
    company_name="NVIDIA",
    competitors=["AMD", "Intel", "Qualcomm"]
)

print(intel["content"])
```

---

## 4. Updated Cost Tracker

Update the pricing table in [cost_tracker.py](../../src/company_researcher/llm/cost_tracker.py):

```python
# Add to PRICING dict in cost_tracker.py

PRICING = {
    # Latest models (December 2024)
    "claude-opus-4-5-20250929": {
        "input": 5.0,
        "output": 25.0,
        "cached_input": 0.50,
        "cache_write": 6.25,
        "batch_input": 2.5,
        "batch_output": 12.5
    },
    "claude-sonnet-4-5-20250929": {
        "input": 3.0,
        "output": 15.0,
        "cached_input": 0.30,
        "cache_write": 3.75,
        "batch_input": 1.5,
        "batch_output": 7.5
    },
    "claude-haiku-4-5-20250929": {
        "input": 1.0,
        "output": 5.0,
        "cached_input": 0.10,
        "cache_write": 1.25,
        "batch_input": 0.5,
        "batch_output": 2.5
    },
    # Legacy models
    "claude-opus-4-1-20250514": {
        "input": 15.0,
        "output": 75.0,
        "cached_input": 1.50,
        "cache_write": 18.75
    },
    "claude-sonnet-4-20250514": {
        "input": 3.0,
        "output": 15.0,
        "cached_input": 0.30,
        "cache_write": 3.75
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.80,
        "output": 4.0,
        "cached_input": 0.08,
        "cache_write": 1.0
    },
    # Web search pricing (per search, not per token)
    "web_search": {
        "per_search": 0.01  # $10 per 1,000 searches
    }
}
```

---

## 5. Model Selection Strategy

### Recommended Model by Task

| Task | Model | Reasoning |
|------|-------|-----------|
| Search query generation | Haiku 4.5 | Fast, cheap, simple task |
| Data extraction | Haiku 4.5 | Structured output, speed |
| Financial analysis | Sonnet 4.5 | Balance of quality/cost |
| Competitive analysis | Sonnet 4.5 | Nuanced reasoning |
| Executive synthesis | Opus 4.5 | Highest quality writing |
| Investment thesis | Opus 4.5 | Complex reasoning |
| **Batch processing** | Sonnet 4.5 | 50% savings for bulk |

### Cost Optimization Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Research Request                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │ Is it urgent?  │
                   └────────────────┘
                     │           │
                    Yes          No
                     │           │
                     ▼           ▼
              ┌───────────┐  ┌─────────────┐
              │ Real-time │  │ Batch API   │
              │ API       │  │ (50% off)   │
              └───────────┘  └─────────────┘
                     │           │
                     ▼           ▼
              ┌───────────────────────────┐
              │    Select Model by Task   │
              │                           │
              │  Simple → Haiku ($1/MTok) │
              │  Analysis → Sonnet ($3)   │
              │  Synthesis → Opus ($5)    │
              └───────────────────────────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │    Enable Prompt Caching  │
              │    (90% savings on cache) │
              └───────────────────────────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │    Track Costs            │
              │    cost_tracker.record()  │
              └───────────────────────────┘
```

---

## 6. Implementation Priority

### Phase 1: Update Models (Low effort, immediate benefit)
1. Update [config.py](../../src/company_researcher/config.py) default model to `claude-sonnet-4-5-20250929`
2. Update pricing in [cost_tracker.py](../../src/company_researcher/llm/cost_tracker.py)
3. Test with existing workflows

### Phase 2: Batch API (Medium effort, 50% savings)
1. Create `batch_processor.py` module
2. Add batch endpoint to research CLI
3. Create overnight batch job scheduler

### Phase 3: Web Search (Medium effort, better data quality)
1. Create `web_search.py` module
2. Integrate with researcher agent
3. Add web search option to config

---

## 7. Environment Variables

Add to `.env`:

```bash
# Model selection
CLAUDE_DEFAULT_MODEL=claude-sonnet-4-5-20250929
CLAUDE_SYNTHESIS_MODEL=claude-opus-4-5-20250929
CLAUDE_EXTRACTION_MODEL=claude-haiku-4-5-20250929

# Feature flags
ENABLE_BATCH_API=true
ENABLE_WEB_SEARCH=true

# Cost controls
MAX_COST_PER_RESEARCH=1.00
BATCH_COST_THRESHOLD=0.50  # Use batch if estimated cost > $0.50
```

---

## Summary

| Feature | Status | Priority | Savings |
|---------|--------|----------|---------|
| Latest models | Ready to implement | High | 5-10% |
| Batch API | Code provided | High | **50%** |
| Web Search | Code provided | Medium | Better quality |
| Prompt Caching | Already implemented | - | Up to 90% |
| Cost Tracking | Already implemented | - | Visibility |

**Total potential savings: 50-60%** on non-urgent research with Batch API + caching.
