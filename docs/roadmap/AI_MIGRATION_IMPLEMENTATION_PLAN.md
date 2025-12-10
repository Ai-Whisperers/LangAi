# AI Migration Implementation Plan

## Executive Summary

This plan migrates **10 hardcoded logic modules** to AI-driven alternatives, leveraging the existing LLM infrastructure. Work is organized into **6 parallel workstreams** that can be developed simultaneously by separate agents.

**Total Scope**: ~40 files to create/modify
**Estimated Effort**: 6 parallel workstreams
**Dependencies**: Existing `llm/`, `agents/base/`, `prompts/` infrastructure

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI MIGRATION ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ Workstream 1│    │ Workstream 2│    │ Workstream 3│    │ Workstream 4│  │
│  │  Sentiment  │    │   Query     │    │  Quality    │    │Classification│  │
│  │  Analysis   │    │ Generation  │    │ Assessment  │    │  & Routing  │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │          │
│         └──────────────────┴──────────────────┴──────────────────┘          │
│                                    │                                        │
│                        ┌───────────▼───────────┐                            │
│                        │   SHARED SERVICES     │                            │
│                        │  (Workstream 5 & 6)   │                            │
│                        │                       │                            │
│                        │ • AI Service Layer    │                            │
│                        │ • Pydantic Models     │                            │
│                        │ • Prompt Registry     │                            │
│                        │ • Integration Tests   │                            │
│                        └───────────────────────┘                            │
│                                    │                                        │
│                        ┌───────────▼───────────┐                            │
│                        │  EXISTING INFRA       │                            │
│                        │                       │                            │
│                        │ • SmartLLMClient      │                            │
│                        │ • ModelRouter         │                            │
│                        │ • ResponseParser      │                            │
│                        │ • CostTracker         │                            │
│                        └───────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Workstream Dependencies

```
Workstream 5 (Foundation) ──┬──► Workstream 1 (Sentiment)
                           ├──► Workstream 2 (Query Gen)
                           ├──► Workstream 3 (Quality)
                           └──► Workstream 4 (Classification)
                                        │
                                        ▼
                              Workstream 6 (Integration)
```

**Parallel Execution**:
- Workstreams 1-4 can run in parallel AFTER Workstream 5 foundation
- Workstream 6 runs last (integration testing)

---

## WORKSTREAM 1: AI-Driven Sentiment Analysis

**Owner**: Agent 1
**Priority**: HIGH
**Files to Create/Modify**: 6

### Current State
- File: `src/company_researcher/agents/research/news_sentiment.py`
- 60+ hardcoded keywords
- Manual scoring algorithm
- No context awareness

### Target State
- LLM-based sentiment with entity awareness
- Context understanding (negations, sarcasm)
- Multi-language support
- Confidence scoring

### Files to Create

#### 1.1 `src/company_researcher/ai/sentiment/models.py`
```python
"""Pydantic models for AI sentiment analysis."""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SentimentLevel(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class EntitySentiment(BaseModel):
    """Sentiment for a specific entity mentioned in text."""
    entity_name: str = Field(description="Name of the entity")
    entity_type: str = Field(description="Type: company, person, product, etc.")
    sentiment: SentimentLevel
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Why this sentiment was assigned")
    context_snippet: str = Field(description="Relevant text excerpt")

class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result."""
    overall_sentiment: SentimentLevel
    overall_confidence: float = Field(ge=0.0, le=1.0)
    entity_sentiments: List[EntitySentiment] = []
    key_factors: List[str] = Field(description="Main factors driving sentiment")
    detected_language: str = "en"
    has_negations: bool = False
    has_uncertainty: bool = False
    news_category: Optional[str] = None
    summary: str = Field(description="One-sentence summary")

class NewsCategorization(BaseModel):
    """News article categorization."""
    primary_category: str
    secondary_categories: List[str] = []
    relevance_to_company: float = Field(ge=0.0, le=1.0)
    is_about_target_company: bool
    mentioned_companies: List[str] = []
```

#### 1.2 `src/company_researcher/ai/sentiment/prompts.py`
```python
"""Prompts for AI sentiment analysis."""

SENTIMENT_ANALYSIS_PROMPT = """You are an expert financial news analyst. Analyze the sentiment of this news article about {company_name}.

<article>
{article_text}
</article>

Analyze:
1. **Overall Sentiment**: What is the overall sentiment toward {company_name}? Consider the full context.
2. **Entity-Specific Sentiment**: For each company/person mentioned, what is the sentiment about THEM specifically?
3. **Key Factors**: What specific information drives the sentiment? (earnings, layoffs, partnerships, etc.)
4. **Context Awareness**:
   - Are there negations? ("not a failure" = positive)
   - Is there sarcasm or irony?
   - Is uncertainty expressed? ("might", "could", "reportedly")
5. **News Category**: Financial, Product, Legal, Partnership, Executive, Market, Other

CRITICAL: Distinguish between sentiment ABOUT {company_name} vs sentiment about their competitors.
"Competitor X failed" is POSITIVE for {company_name}, not negative.

Respond in this exact JSON format:
{{
    "overall_sentiment": "very_positive|positive|neutral|negative|very_negative",
    "overall_confidence": 0.0-1.0,
    "entity_sentiments": [
        {{
            "entity_name": "Company/Person name",
            "entity_type": "company|person|product",
            "sentiment": "very_positive|positive|neutral|negative|very_negative",
            "confidence": 0.0-1.0,
            "reasoning": "Brief explanation",
            "context_snippet": "Relevant quote from article"
        }}
    ],
    "key_factors": ["factor1", "factor2"],
    "detected_language": "en|es|pt|etc",
    "has_negations": true|false,
    "has_uncertainty": true|false,
    "news_category": "financial|product|legal|partnership|executive|market|other",
    "summary": "One sentence summary of the news and its implications"
}}
"""

NEWS_CATEGORIZATION_PROMPT = """Categorize this news article and assess its relevance to {company_name}.

<article>
{article_text}
</article>

Determine:
1. Primary category (financial, product, legal, partnership, executive, market, other)
2. How relevant is this to {company_name}? (0.0-1.0)
3. Is this article primarily ABOUT {company_name} or just mentions them?
4. What other companies are mentioned?

Respond in JSON format:
{{
    "primary_category": "category",
    "secondary_categories": ["cat1", "cat2"],
    "relevance_to_company": 0.0-1.0,
    "is_about_target_company": true|false,
    "mentioned_companies": ["company1", "company2"]
}}
"""
```

#### 1.3 `src/company_researcher/ai/sentiment/analyzer.py`
```python
"""AI-powered sentiment analyzer using LLM."""
from typing import List, Optional
from company_researcher.llm import get_smart_client, TaskType
from company_researcher.llm.response_parser import parse_json_response
from .models import SentimentAnalysisResult, NewsCategorization, SentimentLevel
from .prompts import SENTIMENT_ANALYSIS_PROMPT, NEWS_CATEGORIZATION_PROMPT

class AISentimentAnalyzer:
    """AI-driven sentiment analysis replacing keyword-based approach."""

    def __init__(self):
        self.client = get_smart_client()

    async def analyze_sentiment(
        self,
        article_text: str,
        company_name: str,
        include_entities: bool = True
    ) -> SentimentAnalysisResult:
        """Analyze sentiment of article using LLM."""
        prompt = SENTIMENT_ANALYSIS_PROMPT.format(
            company_name=company_name,
            article_text=article_text[:8000]  # Truncate for context window
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.CLASSIFICATION,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={})
        return SentimentAnalysisResult(**parsed)

    async def categorize_news(
        self,
        article_text: str,
        company_name: str
    ) -> NewsCategorization:
        """Categorize news article using LLM."""
        prompt = NEWS_CATEGORIZATION_PROMPT.format(
            company_name=company_name,
            article_text=article_text[:4000]
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.CLASSIFICATION,
            complexity="low"
        )

        parsed = parse_json_response(result.content, default={})
        return NewsCategorization(**parsed)

    async def analyze_batch(
        self,
        articles: List[dict],
        company_name: str
    ) -> List[SentimentAnalysisResult]:
        """Analyze multiple articles efficiently."""
        # Use batch processing for cost savings
        results = []
        for article in articles:
            result = await self.analyze_sentiment(
                article.get("content", article.get("snippet", "")),
                company_name
            )
            results.append(result)
        return results

    def aggregate_sentiment(
        self,
        results: List[SentimentAnalysisResult]
    ) -> dict:
        """Aggregate sentiment across multiple articles."""
        if not results:
            return {"overall": SentimentLevel.NEUTRAL, "confidence": 0.0}

        sentiment_scores = {
            SentimentLevel.VERY_POSITIVE: 2,
            SentimentLevel.POSITIVE: 1,
            SentimentLevel.NEUTRAL: 0,
            SentimentLevel.NEGATIVE: -1,
            SentimentLevel.VERY_NEGATIVE: -2
        }

        weighted_sum = sum(
            sentiment_scores[r.overall_sentiment] * r.overall_confidence
            for r in results
        )
        total_weight = sum(r.overall_confidence for r in results)

        avg_score = weighted_sum / total_weight if total_weight > 0 else 0

        # Map back to sentiment level
        if avg_score >= 1.5:
            overall = SentimentLevel.VERY_POSITIVE
        elif avg_score >= 0.5:
            overall = SentimentLevel.POSITIVE
        elif avg_score >= -0.5:
            overall = SentimentLevel.NEUTRAL
        elif avg_score >= -1.5:
            overall = SentimentLevel.NEGATIVE
        else:
            overall = SentimentLevel.VERY_NEGATIVE

        return {
            "overall": overall,
            "confidence": total_weight / len(results),
            "article_count": len(results),
            "sentiment_distribution": self._get_distribution(results)
        }

    def _get_distribution(self, results: List[SentimentAnalysisResult]) -> dict:
        """Get distribution of sentiments."""
        dist = {}
        for r in results:
            key = r.overall_sentiment.value
            dist[key] = dist.get(key, 0) + 1
        return dist


# Factory function for easy access
_analyzer_instance = None

def get_sentiment_analyzer() -> AISentimentAnalyzer:
    """Get singleton sentiment analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = AISentimentAnalyzer()
    return _analyzer_instance
```

#### 1.4 Modify `src/company_researcher/agents/research/news_sentiment.py`
- Add import for new AI analyzer
- Create adapter that uses AI analyzer but maintains same interface
- Deprecate old keyword-based methods
- Add feature flag to toggle between old/new

#### 1.5 `src/company_researcher/ai/sentiment/__init__.py`
```python
"""AI-powered sentiment analysis module."""
from .analyzer import AISentimentAnalyzer, get_sentiment_analyzer
from .models import (
    SentimentLevel,
    EntitySentiment,
    SentimentAnalysisResult,
    NewsCategorization
)

__all__ = [
    "AISentimentAnalyzer",
    "get_sentiment_analyzer",
    "SentimentLevel",
    "EntitySentiment",
    "SentimentAnalysisResult",
    "NewsCategorization"
]
```

#### 1.6 `tests/ai/test_sentiment_analyzer.py`
- Unit tests for AI sentiment analyzer
- Comparison tests vs old keyword approach
- Edge case tests (negations, sarcasm, multi-entity)

---

## WORKSTREAM 2: AI-Driven Query Generation

**Owner**: Agent 2
**Priority**: HIGH
**Files to Create/Modify**: 6

### Current State
- File: `src/company_researcher/agents/base/query_generation.py`
- 60+ static query templates
- No adaptation to company type
- English-only

### Target State
- Dynamic query generation based on context
- Learns from search result quality
- Multi-language support
- Industry-specific queries

### Files to Create

#### 2.1 `src/company_researcher/ai/query/models.py`
```python
"""Pydantic models for AI query generation."""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class QueryPurpose(str, Enum):
    OVERVIEW = "overview"
    FINANCIAL = "financial"
    PRODUCTS = "products"
    COMPETITORS = "competitors"
    NEWS = "news"
    LEADERSHIP = "leadership"
    MARKET = "market"
    ESG = "esg"
    TECHNOLOGY = "technology"
    STRATEGY = "strategy"

class CompanyContext(BaseModel):
    """Context about the company for query generation."""
    company_name: str
    known_industry: Optional[str] = None
    known_region: Optional[str] = None
    is_public: Optional[bool] = None
    stock_ticker: Optional[str] = None
    known_products: List[str] = []
    known_competitors: List[str] = []
    research_focus: List[str] = []
    languages: List[str] = ["en"]

class GeneratedQuery(BaseModel):
    """A generated search query with metadata."""
    query: str
    purpose: QueryPurpose
    expected_sources: List[str] = Field(description="Types of sources expected")
    language: str = "en"
    priority: int = Field(ge=1, le=5, description="1=highest priority")
    reasoning: str = Field(description="Why this query was generated")

class QueryGenerationResult(BaseModel):
    """Result of AI query generation."""
    queries: List[GeneratedQuery]
    company_context_inferred: dict = Field(description="What was inferred about company")
    suggested_follow_ups: List[str] = Field(description="Additional queries if initial fail")
    estimated_coverage: dict = Field(description="Expected coverage by category")
```

#### 2.2 `src/company_researcher/ai/query/prompts.py`
```python
"""Prompts for AI query generation."""

QUERY_GENERATION_PROMPT = """You are an expert research analyst. Generate optimal search queries to research {company_name}.

<context>
Known Industry: {industry}
Known Region: {region}
Is Public Company: {is_public}
Stock Ticker: {ticker}
Known Products: {products}
Known Competitors: {competitors}
Research Focus: {focus}
Languages to Search: {languages}
</context>

<previous_results_summary>
{previous_results}
</previous_results_summary>

Generate {num_queries} search queries that will:
1. Find comprehensive, authoritative information
2. Cover different aspects (financial, products, market, news)
3. Use industry-specific terminology
4. Include queries in relevant languages for the region
5. Avoid redundancy with previous successful queries
6. Target high-quality sources (official sites, news, SEC filings)

For each query, explain:
- What information you expect to find
- Why this query formulation is optimal
- What sources you expect to match

IMPORTANT:
- For LATAM companies, include Spanish/Portuguese queries
- For public companies, include SEC/regulatory queries
- For private companies, focus on news and industry reports
- Avoid generic queries that return noise

Respond in JSON format:
{{
    "queries": [
        {{
            "query": "exact search query text",
            "purpose": "overview|financial|products|competitors|news|leadership|market|esg|technology|strategy",
            "expected_sources": ["type1", "type2"],
            "language": "en|es|pt",
            "priority": 1-5,
            "reasoning": "Why this query"
        }}
    ],
    "company_context_inferred": {{
        "likely_industry": "inferred industry",
        "likely_size": "startup|smb|enterprise|conglomerate",
        "likely_region": "region"
    }},
    "suggested_follow_ups": ["query if initial fail", "another backup"],
    "estimated_coverage": {{
        "financial": 0.0-1.0,
        "products": 0.0-1.0,
        "market": 0.0-1.0,
        "news": 0.0-1.0
    }}
}}
"""

QUERY_REFINEMENT_PROMPT = """Based on the search results quality, refine the queries for better coverage.

<original_queries>
{original_queries}
</original_queries>

<results_quality>
{results_quality}
</results_quality>

<gaps_identified>
{gaps}
</gaps_identified>

Generate {num_queries} refined queries to fill the gaps. Focus on:
1. Topics with low coverage scores
2. Alternative phrasings for failed queries
3. More specific queries for broad results
4. Different source types if current sources are poor

Respond in the same JSON format as before.
"""
```

#### 2.3 `src/company_researcher/ai/query/generator.py`
```python
"""AI-powered query generator using LLM."""
from typing import List, Optional, Dict
from company_researcher.llm import get_smart_client, TaskType
from company_researcher.llm.response_parser import parse_json_response
from .models import CompanyContext, GeneratedQuery, QueryGenerationResult, QueryPurpose
from .prompts import QUERY_GENERATION_PROMPT, QUERY_REFINEMENT_PROMPT

class AIQueryGenerator:
    """AI-driven query generation replacing static templates."""

    def __init__(self):
        self.client = get_smart_client()

    async def generate_queries(
        self,
        company_name: str,
        context: Optional[CompanyContext] = None,
        num_queries: int = 10,
        previous_results: Optional[str] = None
    ) -> QueryGenerationResult:
        """Generate optimal search queries using LLM."""

        if context is None:
            context = CompanyContext(company_name=company_name)

        prompt = QUERY_GENERATION_PROMPT.format(
            company_name=company_name,
            industry=context.known_industry or "Unknown",
            region=context.known_region or "Unknown",
            is_public=context.is_public if context.is_public is not None else "Unknown",
            ticker=context.stock_ticker or "Unknown",
            products=", ".join(context.known_products) or "Unknown",
            competitors=", ".join(context.known_competitors) or "Unknown",
            focus=", ".join(context.research_focus) or "General research",
            languages=", ".join(context.languages),
            previous_results=previous_results or "No previous results",
            num_queries=num_queries
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.SEARCH_QUERY,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={"queries": []})

        # Convert to typed model
        queries = [GeneratedQuery(**q) for q in parsed.get("queries", [])]

        return QueryGenerationResult(
            queries=queries,
            company_context_inferred=parsed.get("company_context_inferred", {}),
            suggested_follow_ups=parsed.get("suggested_follow_ups", []),
            estimated_coverage=parsed.get("estimated_coverage", {})
        )

    async def refine_queries(
        self,
        original_queries: List[GeneratedQuery],
        results_quality: Dict[str, float],
        gaps: List[str],
        num_queries: int = 5
    ) -> QueryGenerationResult:
        """Refine queries based on results quality."""

        prompt = QUERY_REFINEMENT_PROMPT.format(
            original_queries="\n".join([f"- {q.query} ({q.purpose})" for q in original_queries]),
            results_quality="\n".join([f"- {k}: {v:.1%}" for k, v in results_quality.items()]),
            gaps="\n".join([f"- {g}" for g in gaps]),
            num_queries=num_queries
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.SEARCH_QUERY,
            complexity="low"
        )

        parsed = parse_json_response(result.content, default={"queries": []})
        queries = [GeneratedQuery(**q) for q in parsed.get("queries", [])]

        return QueryGenerationResult(
            queries=queries,
            company_context_inferred=parsed.get("company_context_inferred", {}),
            suggested_follow_ups=parsed.get("suggested_follow_ups", []),
            estimated_coverage=parsed.get("estimated_coverage", {})
        )

    def get_queries_by_purpose(
        self,
        result: QueryGenerationResult,
        purpose: QueryPurpose
    ) -> List[GeneratedQuery]:
        """Filter queries by purpose."""
        return [q for q in result.queries if q.purpose == purpose]

    def get_multilingual_queries(
        self,
        result: QueryGenerationResult
    ) -> Dict[str, List[GeneratedQuery]]:
        """Group queries by language."""
        by_lang = {}
        for q in result.queries:
            if q.language not in by_lang:
                by_lang[q.language] = []
            by_lang[q.language].append(q)
        return by_lang


# Factory function
_generator_instance = None

def get_query_generator() -> AIQueryGenerator:
    """Get singleton query generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = AIQueryGenerator()
    return _generator_instance
```

#### 2.4 Modify `src/company_researcher/agents/base/query_generation.py`
- Add import for new AI generator
- Create adapter maintaining same interface
- Add feature flag for old/new
- Keep static templates as fallback

#### 2.5 `src/company_researcher/ai/query/__init__.py`

#### 2.6 `tests/ai/test_query_generator.py`

---

## WORKSTREAM 3: AI-Driven Quality Assessment

**Owner**: Agent 3
**Priority**: HIGH
**Files to Create/Modify**: 8

### Current State
- Files: `quality_enforcer.py`, `confidence_scorer.py`, `source_assessor.py`
- Magic numbers for scoring
- Pattern-based quality detection
- Static thresholds

### Target State
- Semantic quality assessment
- Context-aware scoring
- Dynamic thresholds by industry
- Factual density evaluation

### Files to Create

#### 3.1 `src/company_researcher/ai/quality/models.py`
```python
"""Pydantic models for AI quality assessment."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class QualityLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INSUFFICIENT = "insufficient"

class ContentQualityAssessment(BaseModel):
    """Quality assessment for a content section."""
    section_name: str
    quality_level: QualityLevel
    score: float = Field(ge=0.0, le=100.0)
    factual_density: float = Field(ge=0.0, le=1.0, description="Facts per 100 words")
    specificity: float = Field(ge=0.0, le=1.0, description="How specific vs vague")
    completeness: float = Field(ge=0.0, le=1.0)
    issues: List[str] = []
    strengths: List[str] = []
    improvement_suggestions: List[str] = []

class SourceQualityAssessment(BaseModel):
    """Quality assessment for a source."""
    url: str
    domain: str
    quality_level: QualityLevel
    authority_score: float = Field(ge=0.0, le=1.0)
    recency_score: float = Field(ge=0.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    is_primary_source: bool
    source_type: str  # official, news, blog, academic, etc.
    reasoning: str

class ConfidenceAssessment(BaseModel):
    """Confidence assessment for a claim."""
    claim: str
    confidence_level: QualityLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    supporting_sources: int
    contradicting_sources: int
    uncertainty_indicators: List[str] = []
    verification_status: str  # verified, unverified, conflicting
    reasoning: str

class OverallQualityReport(BaseModel):
    """Complete quality assessment report."""
    overall_score: float = Field(ge=0.0, le=100.0)
    overall_level: QualityLevel
    section_assessments: List[ContentQualityAssessment]
    source_assessments: List[SourceQualityAssessment]
    key_gaps: List[str]
    critical_issues: List[str]
    recommendations: List[str]
    ready_for_delivery: bool
    iteration_needed: bool
    focus_areas_for_iteration: List[str] = []
```

#### 3.2 `src/company_researcher/ai/quality/prompts.py`
```python
"""Prompts for AI quality assessment."""

CONTENT_QUALITY_PROMPT = """You are an expert research quality assessor. Evaluate this research content for {company_name}.

<section_name>{section_name}</section_name>
<content>
{content}
</content>

<industry_context>{industry}</industry_context>
<company_type>{company_type}</company_type>

Assess quality based on:
1. **Factual Density**: How many concrete facts per 100 words?
   - Numbers, dates, names, specific events = high density
   - Vague statements, filler text = low density

2. **Specificity**: How specific is the information?
   - "Revenue of $10.5B in 2024" = highly specific
   - "Large revenue" = not specific

3. **Completeness**: Does it cover expected topics for this section?
   - For financial: revenue, profit, growth, key metrics
   - For products: main offerings, features, market fit
   - For market: position, share, competitors, trends

4. **Issues to Flag**:
   - "Data not available" or similar placeholder text
   - Outdated information (>2 years old for fast-moving industries)
   - Unsubstantiated claims
   - Missing critical information

Respond in JSON:
{{
    "section_name": "{section_name}",
    "quality_level": "excellent|good|acceptable|poor|insufficient",
    "score": 0-100,
    "factual_density": 0.0-1.0,
    "specificity": 0.0-1.0,
    "completeness": 0.0-1.0,
    "issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"],
    "improvement_suggestions": ["suggestion1", "suggestion2"]
}}
"""

SOURCE_QUALITY_PROMPT = """Assess the quality and reliability of this source for company research.

<source>
URL: {url}
Title: {title}
Snippet: {snippet}
</source>

<target_company>{company_name}</target_company>

Evaluate:
1. **Authority**: Is this an authoritative source for this information?
   - Official company site, SEC filings, major news = high
   - Blogs, forums, unknown sites = low

2. **Recency**: How recent is the information?
   - Within 6 months = high
   - 1-2 years = medium
   - Older = low (unless historical context)

3. **Relevance**: How relevant to {company_name}?
   - Primary focus on company = high
   - Mentions company = medium
   - Tangentially related = low

4. **Source Type**: Categorize the source
   - official, news, academic, industry_report, blog, social, government, financial_data

Respond in JSON:
{{
    "url": "{url}",
    "domain": "extracted domain",
    "quality_level": "excellent|good|acceptable|poor|insufficient",
    "authority_score": 0.0-1.0,
    "recency_score": 0.0-1.0,
    "relevance_score": 0.0-1.0,
    "is_primary_source": true|false,
    "source_type": "type",
    "reasoning": "Brief explanation"
}}
"""

OVERALL_QUALITY_PROMPT = """Provide an overall quality assessment for this company research report.

<company>{company_name}</company>
<industry>{industry}</industry>
<company_type>{company_type}</company_type>

<section_scores>
{section_scores}
</section_scores>

<source_summary>
{source_summary}
</source_summary>

Determine:
1. Overall quality score (0-100) considering:
   - Section quality weighted by importance
   - Source quality and coverage
   - Completeness for this company type

2. Is this ready for delivery?
   - Public companies need: financials, products, market position, competitors
   - Private companies need: overview, products, market, key metrics if available
   - Startups need: product, funding, team, market opportunity

3. If not ready, what specific areas need iteration?

Respond in JSON:
{{
    "overall_score": 0-100,
    "overall_level": "excellent|good|acceptable|poor|insufficient",
    "key_gaps": ["gap1", "gap2"],
    "critical_issues": ["issue1"],
    "recommendations": ["rec1", "rec2"],
    "ready_for_delivery": true|false,
    "iteration_needed": true|false,
    "focus_areas_for_iteration": ["area1", "area2"]
}}
"""
```

#### 3.3 `src/company_researcher/ai/quality/assessor.py`
```python
"""AI-powered quality assessment using LLM."""
from typing import List, Optional, Dict
from company_researcher.llm import get_smart_client, TaskType
from company_researcher.llm.response_parser import parse_json_response
from .models import (
    ContentQualityAssessment,
    SourceQualityAssessment,
    ConfidenceAssessment,
    OverallQualityReport,
    QualityLevel
)
from .prompts import (
    CONTENT_QUALITY_PROMPT,
    SOURCE_QUALITY_PROMPT,
    OVERALL_QUALITY_PROMPT
)

class AIQualityAssessor:
    """AI-driven quality assessment replacing rule-based approach."""

    def __init__(self):
        self.client = get_smart_client()

    async def assess_content_quality(
        self,
        content: str,
        section_name: str,
        company_name: str,
        industry: str = "Unknown",
        company_type: str = "Unknown"
    ) -> ContentQualityAssessment:
        """Assess quality of a content section using LLM."""

        prompt = CONTENT_QUALITY_PROMPT.format(
            section_name=section_name,
            content=content[:6000],
            company_name=company_name,
            industry=industry,
            company_type=company_type
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.REFLECTION,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={})
        return ContentQualityAssessment(**parsed)

    async def assess_source_quality(
        self,
        url: str,
        title: str,
        snippet: str,
        company_name: str
    ) -> SourceQualityAssessment:
        """Assess quality of a source using LLM."""

        prompt = SOURCE_QUALITY_PROMPT.format(
            url=url,
            title=title,
            snippet=snippet[:1000],
            company_name=company_name
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.CLASSIFICATION,
            complexity="low"
        )

        parsed = parse_json_response(result.content, default={})
        return SourceQualityAssessment(**parsed)

    async def generate_overall_report(
        self,
        company_name: str,
        section_assessments: List[ContentQualityAssessment],
        source_assessments: List[SourceQualityAssessment],
        industry: str = "Unknown",
        company_type: str = "Unknown"
    ) -> OverallQualityReport:
        """Generate overall quality report using LLM."""

        section_scores = "\n".join([
            f"- {s.section_name}: {s.score}/100 ({s.quality_level})"
            for s in section_assessments
        ])

        source_summary = f"""
Total sources: {len(source_assessments)}
High quality: {sum(1 for s in source_assessments if s.quality_level in [QualityLevel.EXCELLENT, QualityLevel.GOOD])}
Primary sources: {sum(1 for s in source_assessments if s.is_primary_source)}
Average authority: {sum(s.authority_score for s in source_assessments) / len(source_assessments) if source_assessments else 0:.2f}
"""

        prompt = OVERALL_QUALITY_PROMPT.format(
            company_name=company_name,
            industry=industry,
            company_type=company_type,
            section_scores=section_scores,
            source_summary=source_summary
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.REASONING,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={})

        return OverallQualityReport(
            section_assessments=section_assessments,
            source_assessments=source_assessments,
            **parsed
        )


# Factory function
_assessor_instance = None

def get_quality_assessor() -> AIQualityAssessor:
    """Get singleton quality assessor instance."""
    global _assessor_instance
    if _assessor_instance is None:
        _assessor_instance = AIQualityAssessor()
    return _assessor_instance
```

#### 3.4-3.8 Additional files
- `src/company_researcher/ai/quality/__init__.py`
- Modify `src/company_researcher/quality/quality_enforcer.py`
- Modify `src/company_researcher/quality/confidence_scorer.py`
- Modify `src/company_researcher/quality/source_assessor.py`
- `tests/ai/test_quality_assessor.py`

---

## WORKSTREAM 4: AI-Driven Classification & Data Extraction

**Owner**: Agent 4
**Priority**: MEDIUM-HIGH
**Files to Create/Modify**: 10

### Current State
- Files: `company_classifier.py`, `data_threshold.py`, `contradiction_detector.py`
- Static company lists
- Regex-based extraction
- Hardcoded country mappings

### Target State
- Context-aware classification
- Semantic data extraction
- Universal entity recognition
- Intelligent contradiction resolution

### Files to Create

#### 4.1 `src/company_researcher/ai/extraction/models.py`
```python
"""Pydantic models for AI data extraction."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import date

class CompanyType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    STARTUP = "startup"
    CONGLOMERATE = "conglomerate"
    SUBSIDIARY = "subsidiary"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"

class CompanyClassification(BaseModel):
    """AI-inferred company classification."""
    company_name: str
    normalized_name: str
    company_type: CompanyType
    industry: str
    sub_industry: Optional[str] = None
    region: str
    country: str
    country_code: str
    stock_ticker: Optional[str] = None
    stock_exchange: Optional[str] = None
    parent_company: Optional[str] = None
    is_conglomerate: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

class ExtractedFact(BaseModel):
    """A fact extracted from text."""
    category: str  # financial, product, market, etc.
    fact_type: str  # revenue, employee_count, founding_date, etc.
    value: Any
    unit: Optional[str] = None
    time_period: Optional[str] = None
    source_text: str
    confidence: float = Field(ge=0.0, le=1.0)

class FinancialData(BaseModel):
    """Extracted financial data."""
    revenue: Optional[float] = None
    revenue_currency: str = "USD"
    revenue_period: Optional[str] = None
    profit: Optional[float] = None
    market_cap: Optional[float] = None
    employee_count: Optional[int] = None
    funding_total: Optional[float] = None
    funding_stage: Optional[str] = None
    growth_rate: Optional[float] = None
    raw_facts: List[ExtractedFact] = []

class ContradictionAnalysis(BaseModel):
    """Analysis of contradicting facts."""
    fact_type: str
    values_found: List[Dict[str, Any]]
    is_contradiction: bool
    severity: str  # critical, high, medium, low
    resolution: Optional[str] = None
    most_likely_value: Optional[Any] = None
    reasoning: str

class ExtractionResult(BaseModel):
    """Complete extraction result."""
    company_classification: CompanyClassification
    financial_data: FinancialData
    all_facts: List[ExtractedFact]
    contradictions: List[ContradictionAnalysis]
    data_coverage: Dict[str, float]
    extraction_confidence: float
```

#### 4.2 `src/company_researcher/ai/extraction/prompts.py`
```python
"""Prompts for AI data extraction."""

COMPANY_CLASSIFICATION_PROMPT = """Classify this company based on the available information.

<company_name>{company_name}</company_name>

<available_information>
{context}
</available_information>

Determine:
1. **Company Type**: public, private, startup, conglomerate, subsidiary, nonprofit, government
2. **Industry**: Primary industry classification
3. **Region/Country**: Where is this company headquartered?
4. **Stock Information**: If public, what exchange and ticker?
5. **Corporate Structure**: Is it part of a larger group?

Use clues like:
- Domain extensions (.com.br = Brazil, .mx = Mexico)
- Currency mentions (R$ = Brazil, MXN = Mexico)
- Regulatory filings (SEC = US, CVM = Brazil)
- Company suffixes (S.A. = Latin America, Inc. = US)
- Language of sources
- Mentioned executives' names

Respond in JSON:
{{
    "company_name": "{company_name}",
    "normalized_name": "Clean company name without suffixes",
    "company_type": "public|private|startup|conglomerate|subsidiary|nonprofit|government",
    "industry": "Primary industry",
    "sub_industry": "More specific category or null",
    "region": "North America|Latin America|Europe|Asia|etc",
    "country": "Full country name",
    "country_code": "ISO 2-letter code",
    "stock_ticker": "ticker or null",
    "stock_exchange": "exchange name or null",
    "parent_company": "parent company name or null",
    "is_conglomerate": true|false,
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of classification"
}}
"""

FACT_EXTRACTION_PROMPT = """Extract structured facts from this text about {company_name}.

<text>
{text}
</text>

Extract ALL factual claims including:
1. **Financial**: Revenue, profit, market cap, funding, valuations
2. **Company Info**: Founded date, headquarters, employee count
3. **Products**: Product names, features, pricing
4. **Market**: Market share, competitors, positioning
5. **Leadership**: CEO, founders, executives

For each fact:
- Extract the exact value with units
- Note the time period if mentioned
- Quote the source text
- Assess confidence (is it stated or implied?)

Handle different formats:
- "$10.5B" = 10,500,000,000
- "10.5 billion" = 10,500,000,000
- "R$ 50 milhões" = 50,000,000 BRL
- "~$500M" = approximately 500,000,000 (lower confidence)

Respond in JSON:
{{
    "facts": [
        {{
            "category": "financial|company_info|product|market|leadership",
            "fact_type": "revenue|profit|employee_count|founding_date|etc",
            "value": "extracted value (number or string)",
            "unit": "USD|employees|year|etc or null",
            "time_period": "2024|Q3 2024|etc or null",
            "source_text": "Exact quote from text",
            "confidence": 0.0-1.0
        }}
    ]
}}
"""

CONTRADICTION_RESOLUTION_PROMPT = """Analyze these potentially contradicting facts about {company_name}.

<fact_type>{fact_type}</fact_type>

<values_found>
{values}
</values_found>

Determine:
1. Is this actually a contradiction, or can values be explained by:
   - Different time periods (2023 vs 2024 revenue)
   - Different metrics (revenue vs gross revenue)
   - Different currencies
   - Rounding differences

2. If it's a real contradiction:
   - How severe is it? (>50% difference = critical)
   - Which value is most likely correct? (prefer official sources)
   - What's the reasoning?

Respond in JSON:
{{
    "fact_type": "{fact_type}",
    "values_found": [...],
    "is_contradiction": true|false,
    "severity": "critical|high|medium|low",
    "resolution": "Explanation if resolvable, or null",
    "most_likely_value": "Best estimate or null",
    "reasoning": "Detailed explanation"
}}
"""
```

#### 4.3 `src/company_researcher/ai/extraction/extractor.py`
```python
"""AI-powered data extraction using LLM."""
from typing import List, Optional, Dict, Any
from company_researcher.llm import get_smart_client, TaskType
from company_researcher.llm.response_parser import parse_json_response
from .models import (
    CompanyClassification,
    ExtractedFact,
    FinancialData,
    ContradictionAnalysis,
    ExtractionResult,
    CompanyType
)
from .prompts import (
    COMPANY_CLASSIFICATION_PROMPT,
    FACT_EXTRACTION_PROMPT,
    CONTRADICTION_RESOLUTION_PROMPT
)

class AIDataExtractor:
    """AI-driven data extraction replacing regex-based approach."""

    def __init__(self):
        self.client = get_smart_client()

    async def classify_company(
        self,
        company_name: str,
        context: str
    ) -> CompanyClassification:
        """Classify company using LLM."""

        prompt = COMPANY_CLASSIFICATION_PROMPT.format(
            company_name=company_name,
            context=context[:6000]
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.CLASSIFICATION,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={})
        return CompanyClassification(**parsed)

    async def extract_facts(
        self,
        text: str,
        company_name: str
    ) -> List[ExtractedFact]:
        """Extract structured facts from text using LLM."""

        prompt = FACT_EXTRACTION_PROMPT.format(
            company_name=company_name,
            text=text[:8000]
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.EXTRACTION,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={"facts": []})
        return [ExtractedFact(**f) for f in parsed.get("facts", [])]

    async def resolve_contradiction(
        self,
        fact_type: str,
        values: List[Dict[str, Any]],
        company_name: str
    ) -> ContradictionAnalysis:
        """Resolve contradicting facts using LLM."""

        values_str = "\n".join([
            f"- Value: {v['value']}, Source: {v.get('source', 'Unknown')}, "
            f"Period: {v.get('period', 'Unknown')}"
            for v in values
        ])

        prompt = CONTRADICTION_RESOLUTION_PROMPT.format(
            company_name=company_name,
            fact_type=fact_type,
            values=values_str
        )

        result = await self.client.complete(
            prompt=prompt,
            task_type=TaskType.REASONING,
            complexity="medium"
        )

        parsed = parse_json_response(result.content, default={})
        return ContradictionAnalysis(**parsed)

    async def extract_all(
        self,
        company_name: str,
        search_results: List[Dict]
    ) -> ExtractionResult:
        """Complete extraction pipeline."""

        # Combine all text
        all_text = "\n\n".join([
            f"Source: {r.get('url', 'Unknown')}\n{r.get('content', r.get('snippet', ''))}"
            for r in search_results
        ])

        # Classify company
        classification = await self.classify_company(company_name, all_text)

        # Extract facts from each source
        all_facts = []
        for result in search_results:
            text = result.get('content', result.get('snippet', ''))
            if text:
                facts = await self.extract_facts(text, company_name)
                all_facts.extend(facts)

        # Find and resolve contradictions
        contradictions = await self._find_contradictions(all_facts, company_name)

        # Build financial data
        financial_data = self._build_financial_data(all_facts)

        # Calculate coverage
        coverage = self._calculate_coverage(all_facts)

        return ExtractionResult(
            company_classification=classification,
            financial_data=financial_data,
            all_facts=all_facts,
            contradictions=contradictions,
            data_coverage=coverage,
            extraction_confidence=self._calculate_confidence(all_facts)
        )

    async def _find_contradictions(
        self,
        facts: List[ExtractedFact],
        company_name: str
    ) -> List[ContradictionAnalysis]:
        """Find and analyze contradictions in facts."""
        # Group facts by type
        by_type = {}
        for fact in facts:
            key = f"{fact.category}:{fact.fact_type}"
            if key not in by_type:
                by_type[key] = []
            by_type[key].append(fact)

        contradictions = []
        for fact_type, type_facts in by_type.items():
            if len(type_facts) > 1:
                # Check for significant differences
                values = [
                    {"value": f.value, "source": f.source_text, "period": f.time_period}
                    for f in type_facts
                ]
                analysis = await self.resolve_contradiction(fact_type, values, company_name)
                if analysis.is_contradiction:
                    contradictions.append(analysis)

        return contradictions

    def _build_financial_data(self, facts: List[ExtractedFact]) -> FinancialData:
        """Build financial data from extracted facts."""
        financial = FinancialData(raw_facts=[f for f in facts if f.category == "financial"])

        for fact in facts:
            if fact.category == "financial":
                if fact.fact_type == "revenue" and financial.revenue is None:
                    financial.revenue = self._to_number(fact.value)
                    financial.revenue_period = fact.time_period
                elif fact.fact_type == "profit" and financial.profit is None:
                    financial.profit = self._to_number(fact.value)
                elif fact.fact_type == "market_cap" and financial.market_cap is None:
                    financial.market_cap = self._to_number(fact.value)
            elif fact.category == "company_info":
                if fact.fact_type == "employee_count" and financial.employee_count is None:
                    financial.employee_count = int(self._to_number(fact.value) or 0)

        return financial

    def _to_number(self, value: Any) -> Optional[float]:
        """Convert value to number."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = value.replace('$', '').replace(',', '').replace(' ', '')
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _calculate_coverage(self, facts: List[ExtractedFact]) -> Dict[str, float]:
        """Calculate data coverage by category."""
        categories = ["financial", "company_info", "product", "market", "leadership"]
        coverage = {}
        for cat in categories:
            cat_facts = [f for f in facts if f.category == cat]
            # Simple heuristic: more facts = higher coverage
            coverage[cat] = min(1.0, len(cat_facts) / 5.0)
        return coverage

    def _calculate_confidence(self, facts: List[ExtractedFact]) -> float:
        """Calculate overall extraction confidence."""
        if not facts:
            return 0.0
        return sum(f.confidence for f in facts) / len(facts)


# Factory function
_extractor_instance = None

def get_data_extractor() -> AIDataExtractor:
    """Get singleton data extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = AIDataExtractor()
    return _extractor_instance
```

#### 4.4-4.10 Additional files
- `src/company_researcher/ai/extraction/__init__.py`
- Modify `src/company_researcher/agents/core/company_classifier.py`
- Modify `src/company_researcher/agents/research/data_threshold.py`
- Modify `src/company_researcher/quality/contradiction_detector.py`
- `src/company_researcher/ai/extraction/country_resolver.py` (AI country detection)
- `tests/ai/test_data_extractor.py`
- `tests/ai/test_company_classifier.py`

---

## WORKSTREAM 5: Foundation & Shared Services

**Owner**: Agent 5
**Priority**: CRITICAL (Do First)
**Files to Create/Modify**: 8

### Purpose
Create the shared foundation that all other workstreams depend on.

### Files to Create

#### 5.1 `src/company_researcher/ai/__init__.py`
```python
"""
AI-driven components for company research.

This module provides AI-powered alternatives to hardcoded logic:
- Sentiment analysis (replaces keyword-based)
- Query generation (replaces static templates)
- Quality assessment (replaces rule-based scoring)
- Data extraction (replaces regex patterns)

Usage:
    from company_researcher.ai import (
        get_sentiment_analyzer,
        get_query_generator,
        get_quality_assessor,
        get_data_extractor
    )

    analyzer = get_sentiment_analyzer()
    result = await analyzer.analyze_sentiment(text, company_name)
"""

from .sentiment import get_sentiment_analyzer, AISentimentAnalyzer
from .query import get_query_generator, AIQueryGenerator
from .quality import get_quality_assessor, AIQualityAssessor
from .extraction import get_data_extractor, AIDataExtractor

__all__ = [
    # Sentiment
    "get_sentiment_analyzer",
    "AISentimentAnalyzer",
    # Query
    "get_query_generator",
    "AIQueryGenerator",
    # Quality
    "get_quality_assessor",
    "AIQualityAssessor",
    # Extraction
    "get_data_extractor",
    "AIDataExtractor",
]
```

#### 5.2 `src/company_researcher/ai/base.py`
```python
"""Base classes and utilities for AI components."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel
from company_researcher.llm import get_smart_client, TaskType
from company_researcher.llm.response_parser import parse_json_response
from company_researcher.llm.cost_tracker import track_api_call

T = TypeVar('T', bound=BaseModel)

class AIComponent(ABC, Generic[T]):
    """Base class for AI-driven components."""

    component_name: str = "base"
    default_task_type: TaskType = TaskType.REASONING
    default_complexity: str = "medium"

    def __init__(self):
        self.client = get_smart_client()
        self._call_count = 0
        self._total_cost = 0.0

    async def _call_llm(
        self,
        prompt: str,
        task_type: Optional[TaskType] = None,
        complexity: Optional[str] = None,
        response_model: Optional[type] = None
    ) -> Any:
        """Call LLM with standard handling."""
        result = await self.client.complete(
            prompt=prompt,
            task_type=task_type or self.default_task_type,
            complexity=complexity or self.default_complexity
        )

        self._call_count += 1
        self._total_cost += result.cost

        if response_model:
            parsed = parse_json_response(result.content, default={})
            return response_model(**parsed)

        return result.content

    def get_stats(self) -> dict:
        """Get component usage statistics."""
        return {
            "component": self.component_name,
            "call_count": self._call_count,
            "total_cost": self._total_cost
        }

    @abstractmethod
    async def process(self, *args, **kwargs) -> T:
        """Main processing method to implement."""
        pass


class AIComponentRegistry:
    """Registry for AI components with feature flags."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._components = {}
            cls._instance._feature_flags = {}
        return cls._instance

    def register(self, name: str, component: AIComponent, enabled: bool = True):
        """Register an AI component."""
        self._components[name] = component
        self._feature_flags[name] = enabled

    def get(self, name: str) -> Optional[AIComponent]:
        """Get a registered component if enabled."""
        if self._feature_flags.get(name, False):
            return self._components.get(name)
        return None

    def is_enabled(self, name: str) -> bool:
        """Check if a component is enabled."""
        return self._feature_flags.get(name, False)

    def enable(self, name: str):
        """Enable a component."""
        self._feature_flags[name] = True

    def disable(self, name: str):
        """Disable a component."""
        self._feature_flags[name] = False

    def get_all_stats(self) -> dict:
        """Get stats for all components."""
        return {
            name: comp.get_stats()
            for name, comp in self._components.items()
            if self._feature_flags.get(name, False)
        }


def get_ai_registry() -> AIComponentRegistry:
    """Get the AI component registry singleton."""
    return AIComponentRegistry()
```

#### 5.3 `src/company_researcher/ai/config.py`
```python
"""Configuration for AI components."""
from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum

class AIComponentConfig(BaseModel):
    """Configuration for an AI component."""
    enabled: bool = True
    fallback_to_legacy: bool = True  # Use old logic if AI fails
    max_retries: int = 2
    timeout_seconds: float = 30.0
    cost_limit_per_call: float = 0.10
    preferred_model: Optional[str] = None

class AIConfig(BaseModel):
    """Global AI configuration."""

    # Component-specific configs
    sentiment: AIComponentConfig = Field(default_factory=AIComponentConfig)
    query_generation: AIComponentConfig = Field(default_factory=AIComponentConfig)
    quality_assessment: AIComponentConfig = Field(default_factory=AIComponentConfig)
    data_extraction: AIComponentConfig = Field(default_factory=AIComponentConfig)

    # Global settings
    global_enabled: bool = True
    log_all_prompts: bool = False
    log_all_responses: bool = False
    track_costs: bool = True

    # Cost controls
    max_cost_per_research: float = 1.00
    warn_at_cost: float = 0.50

    @classmethod
    def from_env(cls) -> "AIConfig":
        """Load configuration from environment."""
        import os
        return cls(
            global_enabled=os.getenv("AI_COMPONENTS_ENABLED", "true").lower() == "true",
            sentiment=AIComponentConfig(
                enabled=os.getenv("AI_SENTIMENT_ENABLED", "true").lower() == "true"
            ),
            query_generation=AIComponentConfig(
                enabled=os.getenv("AI_QUERY_GEN_ENABLED", "true").lower() == "true"
            ),
            quality_assessment=AIComponentConfig(
                enabled=os.getenv("AI_QUALITY_ENABLED", "true").lower() == "true"
            ),
            data_extraction=AIComponentConfig(
                enabled=os.getenv("AI_EXTRACTION_ENABLED", "true").lower() == "true"
            )
        )


# Global config instance
_ai_config: Optional[AIConfig] = None

def get_ai_config() -> AIConfig:
    """Get global AI configuration."""
    global _ai_config
    if _ai_config is None:
        _ai_config = AIConfig.from_env()
    return _ai_config

def set_ai_config(config: AIConfig):
    """Set global AI configuration."""
    global _ai_config
    _ai_config = config
```

#### 5.4 `src/company_researcher/ai/exceptions.py`
```python
"""Custom exceptions for AI components."""

class AIComponentError(Exception):
    """Base exception for AI component errors."""
    def __init__(self, component: str, message: str, original_error: Exception = None):
        self.component = component
        self.original_error = original_error
        super().__init__(f"[{component}] {message}")

class AIExtractionError(AIComponentError):
    """Error during data extraction."""
    pass

class AISentimentError(AIComponentError):
    """Error during sentiment analysis."""
    pass

class AIQueryGenerationError(AIComponentError):
    """Error during query generation."""
    pass

class AIQualityAssessmentError(AIComponentError):
    """Error during quality assessment."""
    pass

class AIFallbackTriggered(AIComponentError):
    """AI component failed, falling back to legacy logic."""
    pass

class AICostLimitExceeded(AIComponentError):
    """Cost limit exceeded for AI component."""
    pass
```

#### 5.5 `src/company_researcher/ai/fallback.py`
```python
"""Fallback handlers for AI components."""
from typing import Callable, TypeVar, Any
from functools import wraps
import logging
from .config import get_ai_config
from .exceptions import AIFallbackTriggered

logger = logging.getLogger(__name__)

T = TypeVar('T')

def with_fallback(
    legacy_func: Callable[..., T],
    component_name: str
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add fallback to legacy logic."""

    def decorator(ai_func: Callable[..., T]) -> Callable[..., T]:
        @wraps(ai_func)
        async def wrapper(*args, **kwargs) -> T:
            config = get_ai_config()
            component_config = getattr(config, component_name.replace("-", "_"), None)

            # Check if AI is enabled
            if not config.global_enabled or (component_config and not component_config.enabled):
                logger.debug(f"AI {component_name} disabled, using legacy")
                return legacy_func(*args, **kwargs)

            try:
                return await ai_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"AI {component_name} failed: {e}")

                if component_config and component_config.fallback_to_legacy:
                    logger.info(f"Falling back to legacy {component_name}")
                    return legacy_func(*args, **kwargs)
                else:
                    raise AIFallbackTriggered(
                        component=component_name,
                        message="AI failed and fallback disabled",
                        original_error=e
                    )

        return wrapper
    return decorator


class FallbackHandler:
    """Handler for managing fallbacks between AI and legacy logic."""

    def __init__(self, component_name: str):
        self.component_name = component_name
        self._ai_success_count = 0
        self._ai_failure_count = 0
        self._fallback_count = 0

    async def execute(
        self,
        ai_func: Callable,
        legacy_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute AI function with fallback to legacy."""
        config = get_ai_config()

        try:
            result = await ai_func(*args, **kwargs)
            self._ai_success_count += 1
            return result
        except Exception as e:
            self._ai_failure_count += 1
            logger.warning(f"AI {self.component_name} failed: {e}")

            # Try legacy
            self._fallback_count += 1
            return legacy_func(*args, **kwargs)

    def get_stats(self) -> dict:
        """Get fallback statistics."""
        total = self._ai_success_count + self._ai_failure_count
        return {
            "component": self.component_name,
            "ai_success_rate": self._ai_success_count / total if total > 0 else 0,
            "ai_success_count": self._ai_success_count,
            "ai_failure_count": self._ai_failure_count,
            "fallback_count": self._fallback_count
        }
```

#### 5.6-5.8 Additional foundation files
- `src/company_researcher/ai/utils.py` - Common utilities
- `tests/ai/__init__.py` - Test module init
- `tests/ai/conftest.py` - Pytest fixtures for AI tests

---

## WORKSTREAM 6: Integration & Migration

**Owner**: Agent 6
**Priority**: HIGH (Do Last)
**Files to Create/Modify**: 10

### Purpose
Integrate all AI components into the main workflow and ensure backward compatibility.

### Files to Create/Modify

#### 6.1 Modify `src/company_researcher/workflows/parallel_agent_research.py`
- Import AI components
- Add feature flag checks
- Wire AI components to appropriate stages
- Add cost tracking

#### 6.2 Modify `src/company_researcher/agents/core/researcher.py`
- Replace query generation with AI
- Add fallback to legacy templates

#### 6.3 Modify `src/company_researcher/agents/quality/logic_critic.py`
- Replace rule-based quality with AI assessment
- Integrate contradiction resolution

#### 6.4 Create `src/company_researcher/ai/integration.py`
```python
"""Integration layer for AI components in workflow."""
from typing import Dict, Any, Optional
from company_researcher.state import OverallState
from .sentiment import get_sentiment_analyzer
from .query import get_query_generator
from .quality import get_quality_assessor
from .extraction import get_data_extractor
from .config import get_ai_config
import logging

logger = logging.getLogger(__name__)

class AIIntegrationLayer:
    """Integrates AI components into the research workflow."""

    def __init__(self):
        self.config = get_ai_config()
        self._sentiment = None
        self._query_gen = None
        self._quality = None
        self._extraction = None

    @property
    def sentiment_analyzer(self):
        if self._sentiment is None and self.config.sentiment.enabled:
            self._sentiment = get_sentiment_analyzer()
        return self._sentiment

    @property
    def query_generator(self):
        if self._query_gen is None and self.config.query_generation.enabled:
            self._query_gen = get_query_generator()
        return self._query_gen

    @property
    def quality_assessor(self):
        if self._quality is None and self.config.quality_assessment.enabled:
            self._quality = get_quality_assessor()
        return self._quality

    @property
    def data_extractor(self):
        if self._extraction is None and self.config.data_extraction.enabled:
            self._extraction = get_data_extractor()
        return self._extraction

    async def enhance_search_queries(
        self,
        company_name: str,
        context: Optional[Dict] = None
    ) -> list:
        """Generate AI-enhanced search queries."""
        if not self.query_generator:
            return []

        from .query.models import CompanyContext
        ctx = CompanyContext(company_name=company_name, **(context or {}))
        result = await self.query_generator.generate_queries(company_name, ctx)
        return [q.query for q in result.queries]

    async def analyze_news_sentiment(
        self,
        articles: list,
        company_name: str
    ) -> Dict[str, Any]:
        """Analyze sentiment of news articles."""
        if not self.sentiment_analyzer:
            return {"overall": "neutral", "confidence": 0.0}

        results = await self.sentiment_analyzer.analyze_batch(articles, company_name)
        return self.sentiment_analyzer.aggregate_sentiment(results)

    async def assess_research_quality(
        self,
        state: OverallState
    ) -> Dict[str, Any]:
        """Assess quality of research results."""
        if not self.quality_assessor:
            return {"score": 0, "ready": False}

        # Assess each section
        sections = [
            ("company_overview", state.get("company_overview", "")),
            ("key_metrics", str(state.get("key_metrics", {}))),
            ("products_services", str(state.get("products_services", []))),
            ("competitors", str(state.get("competitors", []))),
        ]

        assessments = []
        for name, content in sections:
            if content:
                assessment = await self.quality_assessor.assess_content_quality(
                    content=content,
                    section_name=name,
                    company_name=state["company_name"]
                )
                assessments.append(assessment)

        # Generate overall report
        report = await self.quality_assessor.generate_overall_report(
            company_name=state["company_name"],
            section_assessments=assessments,
            source_assessments=[]
        )

        return {
            "score": report.overall_score,
            "level": report.overall_level.value,
            "ready": report.ready_for_delivery,
            "gaps": report.key_gaps,
            "issues": report.critical_issues
        }

    async def extract_structured_data(
        self,
        company_name: str,
        search_results: list
    ) -> Dict[str, Any]:
        """Extract structured data from search results."""
        if not self.data_extractor:
            return {}

        result = await self.data_extractor.extract_all(company_name, search_results)
        return {
            "classification": result.company_classification.dict(),
            "financial": result.financial_data.dict(),
            "coverage": result.data_coverage,
            "confidence": result.extraction_confidence
        }


# Global integration layer
_integration_layer: Optional[AIIntegrationLayer] = None

def get_ai_integration() -> AIIntegrationLayer:
    """Get AI integration layer singleton."""
    global _integration_layer
    if _integration_layer is None:
        _integration_layer = AIIntegrationLayer()
    return _integration_layer
```

#### 6.5 Create `src/company_researcher/ai/migration.py`
```python
"""Migration utilities for transitioning from legacy to AI."""
from typing import Callable, Any
from functools import wraps
import logging
from .config import get_ai_config

logger = logging.getLogger(__name__)

def gradual_rollout(
    component_name: str,
    rollout_percentage: float = 100.0
) -> Callable:
    """Decorator for gradual rollout of AI components."""
    import random

    def decorator(ai_func: Callable) -> Callable:
        @wraps(ai_func)
        async def wrapper(*args, **kwargs):
            # Check if this request should use AI
            if random.random() * 100 > rollout_percentage:
                logger.debug(f"Skipping AI {component_name} due to rollout percentage")
                return None  # Signal to use legacy
            return await ai_func(*args, **kwargs)
        return wrapper
    return decorator


def compare_results(
    legacy_result: Any,
    ai_result: Any,
    component_name: str
) -> dict:
    """Compare legacy and AI results for validation."""
    comparison = {
        "component": component_name,
        "legacy_type": type(legacy_result).__name__,
        "ai_type": type(ai_result).__name__,
        "match": legacy_result == ai_result
    }

    # Log significant differences
    if not comparison["match"]:
        logger.info(f"AI vs Legacy difference in {component_name}")

    return comparison


class MigrationValidator:
    """Validates AI migration by comparing to legacy."""

    def __init__(self, component_name: str):
        self.component_name = component_name
        self.comparisons = []

    async def validate(
        self,
        ai_func: Callable,
        legacy_func: Callable,
        *args,
        **kwargs
    ) -> dict:
        """Run both AI and legacy, compare results."""
        legacy_result = legacy_func(*args, **kwargs)
        ai_result = await ai_func(*args, **kwargs)

        comparison = compare_results(legacy_result, ai_result, self.component_name)
        self.comparisons.append(comparison)

        return {
            "legacy": legacy_result,
            "ai": ai_result,
            "comparison": comparison
        }

    def get_stats(self) -> dict:
        """Get migration validation statistics."""
        if not self.comparisons:
            return {"component": self.component_name, "validations": 0}

        matches = sum(1 for c in self.comparisons if c["match"])
        return {
            "component": self.component_name,
            "validations": len(self.comparisons),
            "match_rate": matches / len(self.comparisons)
        }
```

#### 6.6-6.10 Additional integration files
- Update `env.example` with new AI config vars
- Create `tests/ai/test_integration.py`
- Create `tests/ai/test_migration.py`
- Update `src/company_researcher/config.py` with AI settings
- Create `docs/AI_MIGRATION_GUIDE.md`

---

## File Summary by Workstream

### Workstream 1: Sentiment (6 files)
```
src/company_researcher/ai/sentiment/
├── __init__.py
├── models.py
├── prompts.py
└── analyzer.py
tests/ai/
└── test_sentiment_analyzer.py
src/company_researcher/agents/research/
└── news_sentiment.py (MODIFY)
```

### Workstream 2: Query Generation (6 files)
```
src/company_researcher/ai/query/
├── __init__.py
├── models.py
├── prompts.py
└── generator.py
tests/ai/
└── test_query_generator.py
src/company_researcher/agents/base/
└── query_generation.py (MODIFY)
```

### Workstream 3: Quality Assessment (8 files)
```
src/company_researcher/ai/quality/
├── __init__.py
├── models.py
├── prompts.py
└── assessor.py
tests/ai/
└── test_quality_assessor.py
src/company_researcher/quality/
├── quality_enforcer.py (MODIFY)
├── confidence_scorer.py (MODIFY)
└── source_assessor.py (MODIFY)
```

### Workstream 4: Data Extraction (10 files)
```
src/company_researcher/ai/extraction/
├── __init__.py
├── models.py
├── prompts.py
├── extractor.py
└── country_resolver.py
tests/ai/
├── test_data_extractor.py
└── test_company_classifier.py
src/company_researcher/agents/core/
└── company_classifier.py (MODIFY)
src/company_researcher/agents/research/
└── data_threshold.py (MODIFY)
src/company_researcher/quality/
└── contradiction_detector.py (MODIFY)
```

### Workstream 5: Foundation (8 files)
```
src/company_researcher/ai/
├── __init__.py
├── base.py
├── config.py
├── exceptions.py
├── fallback.py
└── utils.py
tests/ai/
├── __init__.py
└── conftest.py
```

### Workstream 6: Integration (10 files)
```
src/company_researcher/ai/
├── integration.py
└── migration.py
src/company_researcher/workflows/
└── parallel_agent_research.py (MODIFY)
src/company_researcher/agents/core/
└── researcher.py (MODIFY)
src/company_researcher/agents/quality/
└── logic_critic.py (MODIFY)
src/company_researcher/
└── config.py (MODIFY)
tests/ai/
├── test_integration.py
└── test_migration.py
docs/
└── AI_MIGRATION_GUIDE.md
env.example (MODIFY)
```

---

## Execution Order

```
Phase 1 (Foundation):
  └── Workstream 5: Foundation & Shared Services

Phase 2 (Parallel Development):
  ├── Workstream 1: Sentiment Analysis
  ├── Workstream 2: Query Generation
  ├── Workstream 3: Quality Assessment
  └── Workstream 4: Data Extraction

Phase 3 (Integration):
  └── Workstream 6: Integration & Migration
```

---

## Agent Assignment Summary

| Agent | Workstream | Files | Dependencies |
|-------|------------|-------|--------------|
| Agent 5 | Foundation | 8 | None (START FIRST) |
| Agent 1 | Sentiment | 6 | Workstream 5 |
| Agent 2 | Query Gen | 6 | Workstream 5 |
| Agent 3 | Quality | 8 | Workstream 5 |
| Agent 4 | Extraction | 10 | Workstream 5 |
| Agent 6 | Integration | 10 | ALL (DO LAST) |

---

## Success Criteria

1. **All existing tests pass** - No regression
2. **Feature flags work** - Can toggle AI on/off
3. **Fallback works** - Graceful degradation to legacy
4. **Cost tracking** - All AI calls tracked
5. **Performance** - No significant latency increase
6. **Quality improvement** - Measurable improvement in output quality
