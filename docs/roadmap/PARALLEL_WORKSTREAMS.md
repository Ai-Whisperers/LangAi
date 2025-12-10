# Parallel Workstreams for AI Migration

## Quick Reference: Agent Assignments

This document provides instructions for each agent working on a parallel workstream.

---

## Execution Order

```
                    ┌─────────────────┐
                    │  WORKSTREAM 5   │
                    │   Foundation    │
                    │  (DO FIRST)     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ WORKSTREAM 1  │  │ WORKSTREAM 2  │  │ WORKSTREAM 3  │
│   Sentiment   │  │  Query Gen    │  │   Quality     │
└───────────────┘  └───────────────┘  └───────────────┘
        │                    │                    │
        │          ┌─────────────────┐            │
        │          │ WORKSTREAM 4    │            │
        │          │   Extraction    │            │
        │          └─────────────────┘            │
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  WORKSTREAM 6   │
                    │  Integration    │
                    │   (DO LAST)     │
                    └─────────────────┘
```

---

## WORKSTREAM 5: Foundation (DO FIRST)

**Agent Instructions:**
```
Create the foundation layer for AI components. This must complete before other workstreams begin.

Files to create:
1. src/company_researcher/ai/__init__.py
2. src/company_researcher/ai/base.py
3. src/company_researcher/ai/config.py
4. src/company_researcher/ai/exceptions.py
5. src/company_researcher/ai/fallback.py
6. src/company_researcher/ai/utils.py
7. tests/ai/__init__.py
8. tests/ai/conftest.py

Key requirements:
- AIComponent base class with LLM calling
- AIComponentRegistry for feature flags
- AIConfig with enable/disable per component
- Fallback handlers for graceful degradation
- Exception hierarchy for AI errors

Reference existing infrastructure:
- Use get_smart_client() from llm/
- Use parse_json_response() from llm/response_parser.py
- Use cost tracking from llm/cost_tracker.py
```

---

## WORKSTREAM 1: Sentiment Analysis (PARALLEL)

**Agent Instructions:**
```
Replace keyword-based sentiment analysis with LLM-powered analysis.

Files to create:
1. src/company_researcher/ai/sentiment/__init__.py
2. src/company_researcher/ai/sentiment/models.py
3. src/company_researcher/ai/sentiment/prompts.py
4. src/company_researcher/ai/sentiment/analyzer.py
5. tests/ai/test_sentiment_analyzer.py

File to modify:
6. src/company_researcher/agents/research/news_sentiment.py

Key requirements:
- SentimentAnalysisResult Pydantic model
- Entity-aware sentiment (who is sentiment about?)
- Context understanding (negations, sarcasm)
- Multi-language support
- Backward compatible interface
- Feature flag to toggle AI vs legacy

Reference existing:
- Current file: agents/research/news_sentiment.py (lines 77-206)
- Has POSITIVE_KEYWORDS, NEGATIVE_KEYWORDS, CATEGORY_KEYWORDS
```

---

## WORKSTREAM 2: Query Generation (PARALLEL)

**Agent Instructions:**
```
Replace static query templates with dynamic AI-generated queries.

Files to create:
1. src/company_researcher/ai/query/__init__.py
2. src/company_researcher/ai/query/models.py
3. src/company_researcher/ai/query/prompts.py
4. src/company_researcher/ai/query/generator.py
5. tests/ai/test_query_generator.py

File to modify:
6. src/company_researcher/agents/base/query_generation.py

Key requirements:
- QueryGenerationResult Pydantic model
- CompanyContext for adaptive generation
- Multi-language query generation
- Query refinement based on results quality
- Keep static templates as fallback
- Feature flag to toggle

Reference existing:
- Current file: agents/base/query_generation.py (lines 63-157)
- Has OVERVIEW_TEMPLATES, FINANCIAL_TEMPLATES, etc.
```

---

## WORKSTREAM 3: Quality Assessment (PARALLEL)

**Agent Instructions:**
```
Replace rule-based quality scoring with semantic AI assessment.

Files to create:
1. src/company_researcher/ai/quality/__init__.py
2. src/company_researcher/ai/quality/models.py
3. src/company_researcher/ai/quality/prompts.py
4. src/company_researcher/ai/quality/assessor.py
5. tests/ai/test_quality_assessor.py

Files to modify:
6. src/company_researcher/quality/quality_enforcer.py
7. src/company_researcher/quality/confidence_scorer.py
8. src/company_researcher/quality/source_assessor.py

Key requirements:
- ContentQualityAssessment, SourceQualityAssessment models
- Semantic quality assessment (not just length)
- Factual density evaluation
- Context-aware thresholds by industry
- Source quality beyond domain reputation
- Feature flags for each component

Reference existing:
- quality_enforcer.py (lines 58-286) - magic numbers
- confidence_scorer.py (lines 58-125) - word lists
- source_assessor.py (lines 24-116) - domain mapping
```

---

## WORKSTREAM 4: Data Extraction (PARALLEL)

**Agent Instructions:**
```
Replace regex/rule-based extraction with semantic AI extraction.

Files to create:
1. src/company_researcher/ai/extraction/__init__.py
2. src/company_researcher/ai/extraction/models.py
3. src/company_researcher/ai/extraction/prompts.py
4. src/company_researcher/ai/extraction/extractor.py
5. src/company_researcher/ai/extraction/country_resolver.py
6. tests/ai/test_data_extractor.py
7. tests/ai/test_company_classifier.py

Files to modify:
8. src/company_researcher/agents/core/company_classifier.py
9. src/company_researcher/agents/research/data_threshold.py
10. src/company_researcher/quality/contradiction_detector.py

Key requirements:
- CompanyClassification, ExtractedFact, FinancialData models
- Context-aware company classification
- Semantic fact extraction (not regex)
- Intelligent contradiction resolution
- Multi-language extraction
- Feature flags for each component

Reference existing:
- company_classifier.py (lines 84-370) - static lists
- data_threshold.py (lines 49-109) - regex patterns
- contradiction_detector.py (lines 148-483) - topic keywords
```

---

## WORKSTREAM 6: Integration (DO LAST)

**Agent Instructions:**
```
Integrate all AI components into the main workflow.

Files to create:
1. src/company_researcher/ai/integration.py
2. src/company_researcher/ai/migration.py
3. tests/ai/test_integration.py
4. tests/ai/test_migration.py
5. docs/AI_MIGRATION_GUIDE.md

Files to modify:
6. src/company_researcher/workflows/parallel_agent_research.py
7. src/company_researcher/agents/core/researcher.py
8. src/company_researcher/agents/quality/logic_critic.py
9. src/company_researcher/config.py
10. env.example

Key requirements:
- AIIntegrationLayer for workflow integration
- Gradual rollout support (percentage-based)
- Migration validation (compare AI vs legacy)
- Update config.py with AI settings
- Update env.example with AI env vars
- Create migration documentation

WAIT for Workstreams 1-5 to complete before starting.
```

---

## Common Patterns to Follow

### 1. Pydantic Models
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MyResult(BaseModel):
    """Docstring explaining the model."""
    field_name: str = Field(description="What this field contains")
    confidence: float = Field(ge=0.0, le=1.0)
    items: List[str] = []
```

### 2. Prompt Template
```python
MY_PROMPT = """You are an expert at {task}.

<context>
{context}
</context>

<input>
{input}
</input>

Analyze and respond in JSON:
{{
    "field": "value",
    "items": ["item1", "item2"]
}}
"""
```

### 3. AI Component Class
```python
from company_researcher.llm import get_smart_client, TaskType
from company_researcher.llm.response_parser import parse_json_response

class MyAIComponent:
    def __init__(self):
        self.client = get_smart_client()

    async def process(self, input: str) -> MyResult:
        prompt = MY_PROMPT.format(...)
        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.EXTRACTION,
            complexity="medium"
        )
        parsed = parse_json_response(result.content, default={})
        return MyResult(**parsed)
```

### 4. Feature Flag Pattern
```python
from company_researcher.ai.config import get_ai_config

async def my_function(input):
    config = get_ai_config()

    if config.my_component.enabled:
        return await ai_version(input)
    else:
        return legacy_version(input)
```

### 5. Fallback Pattern
```python
from company_researcher.ai.fallback import FallbackHandler

handler = FallbackHandler("my_component")
result = await handler.execute(
    ai_func=ai_version,
    legacy_func=legacy_version,
    *args, **kwargs
)
```

---

## Testing Requirements

Each workstream must include tests for:

1. **Happy path** - Normal operation
2. **Edge cases** - Empty input, long input, special characters
3. **Error handling** - LLM failures, parsing errors
4. **Fallback** - Verify legacy fallback works
5. **Feature flag** - Verify toggle works
6. **Comparison** - Optional: compare AI vs legacy results

---

## Definition of Done

A workstream is complete when:

- [ ] All files created per the plan
- [ ] All tests pass
- [ ] Feature flag works (can enable/disable)
- [ ] Fallback to legacy works
- [ ] No regression in existing tests
- [ ] Cost tracking integrated
- [ ] Code follows existing patterns
