# Company Researcher - Comprehensive Refactoring Analysis

**Generated**: 2025-12-08
**Last Updated**: 2025-12-08
**Codebase Size**: ~240 Python files, ~82,822 lines (reduced after refactoring)
**Priority**: HIGH - Multiple critical duplication and abstraction opportunities

## Implementation Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Quick Wins | **COMPLETED** | Duplicate directories deleted, enums centralized |
| Phase 2: Infrastructure | **COMPLETED** | Agents refactored to use BaseSpecialistAgent + ParsingMixin |
| Phase 3: Config Restructuring | **DEFERRED** | Assessed - flat config works well, nested structure is low-ROI |
| Phase 4: Documentation | **COMPLETED** | Architecture docs and agent development guide created |
| Phase 5: Cleanup | **COMPLETED** | Empty cache/ directory deleted, module structure clarified |

### Phase 5 Cleanup Notes

- Deleted empty `cache/` directory (only had `__pycache__/`)
- Verified `quality/validation/` duplicate was already deleted in Phase 1
- Clarified `memory/` vs `caching/` are **complementary**, not duplicates:
  - `memory/` - In-memory research data management (conversation, entity, working memory)
  - `caching/` - General caching infrastructure (Redis, TTL, query dedup, result cache)

### Phase 4 Documentation Created

- [ARCHITECTURE.md](ARCHITECTURE.md) - System overview, data flow, module structure
- [AGENT_DEVELOPMENT_GUIDE.md](AGENT_DEVELOPMENT_GUIDE.md) - How to create new agents

### Phase 2 Detailed Completion

**Agents Refactored to BaseSpecialistAgent + ParsingMixin:**

- `BrandAuditorAgent` - Full refactoring with backwards-compatible `audit()` alias
- `SalesIntelligenceAgent` - Full refactoring with extraction method delegation
- `SocialMediaAgent` - Full refactoring with extraction method delegation

**Agents Refactored with ParsingMixin Only:**

- `InvestmentAnalystAgent` - Different interface (meta-agent pattern), uses ParsingMixin

**Agents Using @agent_node Decorator (Already Abstracted):**

- `ProductAgent` (`specialized/product.py`)
- `FinancialAgent` (`financial/financial.py`)
- `MarketAgent` (`market/market.py`)

**Agents with Complex External Integrations (Deferred):**

- `CompetitorScoutAgent` - Complex constructor with external API tools
- `EnhancedFinancialAgent` - Alpha Vantage, SEC EDGAR integrations
- `EnhancedMarketAgent` - Complex market data integrations
- `DeepResearchAgent` - Multi-stage research with custom workflow

### Agent Architecture Patterns Identified

| Pattern | Count | Description |
|---------|-------|-------------|
| `BaseSpecialistAgent` | 3 | Standard specialist agents with search_results input |
| `ParsingMixin` | 4 | Agents using extraction utilities |
| `@agent_node` decorator | 3 | Decorator-based boilerplate reduction |
| Complex/External APIs | 4+ | Agents with external data source integrations |
| Core/Simple | 3 | Core workflow agents (researcher, analyst, synthesizer) |

---

## Executive Summary

This analysis identifies **23 major refactoring opportunities** across 6 categories that could:
- Reduce codebase size by **~30-40%**
- Eliminate **~15,000 lines** of duplicate code
- Significantly improve maintainability and testability
- Reduce bug surface area through centralization

---

## 1. CRITICAL: Duplicate Module Directories

### 1.1 Quality Module Duplication (SEVERITY: CRITICAL)

**Problem**: Two nearly identical quality module hierarchies exist:
- `quality/` (root level)
- `quality/validation/` (nested)

| File | `quality/` | `quality/validation/` | Status |
|------|-----------|----------------------|--------|
| `contradiction_detector.py` | 450 lines | 448 lines | ~99% identical |
| `quality_checker.py` | 75 lines | 85 lines | ~95% identical |
| `fact_extractor.py` | Present | Present | Different |

**Differences Found**:
```python
# quality/contradiction_detector.py
from ..llm.client_factory import safe_extract_text

# quality/validation/contradiction_detector.py
from ...llm.client_factory import safe_extract_text  # Different import path only!
```

**Recommendation**:
1. Delete `quality/validation/` directory entirely
2. Update all imports to use `quality/` modules
3. Move unique functionality from `validation/` to `quality/`

**Estimated Savings**: ~1,000 lines, import confusion eliminated

---

### 1.2 Cache Module Duplication (SEVERITY: HIGH)

**Problem**: Two separate caching directories with overlapping functionality:

| Directory | Files | Purpose |
|-----------|-------|---------|
| `cache/` | 1 file | Basic research caching |
| `caching/` | 9 files | Comprehensive caching layer |

Both contain `research_cache.py` with different implementations!

```
cache/
└── research_cache.py (150 lines - simple file-based)

caching/
├── cache_manager.py
├── lru_cache.py          # Also exists in memory/
├── query_dedup.py
├── redis_cache.py
├── research_cache.py     # DUPLICATE NAME!
├── result_cache.py
├── token_cache.py
├── ttl_cache.py
└── vector_store.py       # Also exists in memory/
```

**Additional Duplication**:
- `memory/lru_cache.py` vs `caching/lru_cache.py`
- `memory/vector_store.py` vs `caching/vector_store.py`

**Recommendation**:
1. Consolidate all caching into `caching/` module
2. Remove `cache/` directory
3. Create unified `CacheInterface` abstract base class
4. Move LRU and vector store to single location

**Estimated Savings**: ~500 lines, clearer architecture

---

## 2. CRITICAL: Enum Duplication

### Problem: Same enums defined in multiple files

| Enum | `types.py` | Agent File | Total Duplicates |
|------|-----------|------------|------------------|
| `BrandStrength` | Line 79 | `brand_auditor.py:30` | 2 |
| `BrandHealth` | Line 87 | `brand_auditor.py:39` | 2 |
| `SentimentCategory` | Line 95 | `brand_auditor.py:48` | 2 |
| `LeadScore` | Line 118 | `sales_intelligence.py:30` | 2 |
| `BuyingStage` | Line 127 | `sales_intelligence.py:39` | 2 |
| `CompanySize` | Line 136 | `sales_intelligence.py:48` | 2 |
| `SocialPlatform` | Line 158 | `social_media.py:31` | 2 |
| `EngagementLevel` | Line 168 | `social_media.py:41` | 2 |
| `ContentStrategy` | Line 177 | `social_media.py:50` | 2 |
| `ContradictionSeverity` | Line 298 | `contradiction_detector.py:30` | **3** |
| `InvestmentRating` | Line 188 | `investment_analyst.py` | 2 |
| `RiskLevel` | Line 197 | `investment_analyst.py` | 2 |
| `MoatStrength` | Line 206 | `investment_analyst.py` | 2 |
| `GrowthStage` | Line 214 | `investment_analyst.py` | 2 |

**Risk**: If enums diverge, silent bugs occur when comparing values.

**Recommendation**:
```python
# BEFORE (in brand_auditor.py)
class BrandStrength(str, Enum):
    DOMINANT = "DOMINANT"
    # ...

# AFTER (in brand_auditor.py)
from ...types import BrandStrength  # Import from centralized location
```

1. Remove all duplicate enum definitions from agent files
2. Import exclusively from `types.py`
3. Add deprecation warnings if local enums are accessed

**Estimated Savings**: ~400 lines, prevents silent bugs

---

## 3. HIGH: Agent Pattern Abstraction

### Problem: All specialized agents follow identical structure

**Current Pattern** (repeated 10+ times):

```python
class [AgentName]Agent:
    def __init__(self, config=None):
        self._config = config or get_config()
        self._client = get_anthropic_client()

    def analyze(self, company_name: str, search_results: List[Dict]) -> [Result]:
        formatted_results = self._format_search_results(search_results)
        prompt = [PROMPT].format(company_name=company_name, search_results=formatted_results)
        response = self._client.messages.create(...)
        analysis = safe_extract_text(response, agent_name="...")
        cost = calculate_cost(...)
        result = self._parse_analysis(company_name, analysis)
        return result

    def _format_search_results(self, results): ...  # Duplicated 5+ times
    def _parse_analysis(self, company_name, analysis): ...
```

**Agents with this pattern**:
1. `BrandAuditorAgent`
2. `SalesIntelligenceAgent`
3. `SocialMediaAgent`
4. `InvestmentAnalystAgent`
5. `DeepResearchAgent`
6. `ESGAgent`
7. And more...

### Recommendation: Create Proper Abstract Base

```python
# agents/base/analysis_agent.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict, Any

T = TypeVar('T')  # Result type

class BaseAnalysisAgent(ABC, Generic[T]):
    """Abstract base class for all analysis agents."""

    agent_name: str  # Class attribute for logging
    prompt_template: str  # Class attribute for prompt
    max_tokens_config_key: str  # e.g., "brand_auditor_max_tokens"

    def __init__(self, config=None):
        self._config = config or get_config()
        self._client = get_anthropic_client()

    def analyze(self, company_name: str, search_results: List[Dict]) -> T:
        """Template method - shared logic."""
        formatted = self._format_results(search_results)
        prompt = self._build_prompt(company_name, formatted)
        response = self._call_llm(prompt)
        return self._parse_response(company_name, response)

    def _format_results(self, results: List[Dict]) -> str:
        """Default formatting - override for custom."""
        return format_search_results(
            results,
            max_sources=10,
            content_length=400
        )

    def _build_prompt(self, company_name: str, results: str) -> str:
        return self.prompt_template.format(
            company_name=company_name,
            search_results=results
        )

    def _call_llm(self, prompt: str) -> str:
        max_tokens = getattr(self._config, self.max_tokens_config_key)
        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=max_tokens,
            temperature=self._config.llm_temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return safe_extract_text(response, agent_name=self.agent_name)

    @abstractmethod
    def _parse_response(self, company_name: str, analysis: str) -> T:
        """Each agent implements its own parsing."""
        pass
```

**Simplified Agent Implementation**:
```python
# agents/specialized/brand_auditor.py
from ..base.analysis_agent import BaseAnalysisAgent
from ...types import BrandStrength, BrandHealth, SentimentCategory

class BrandAuditorAgent(BaseAnalysisAgent[BrandAuditResult]):
    agent_name = "brand_auditor"
    prompt_template = BRAND_AUDIT_PROMPT
    max_tokens_config_key = "brand_auditor_max_tokens"

    def _parse_response(self, company_name: str, analysis: str) -> BrandAuditResult:
        # Only agent-specific parsing logic
        return BrandAuditResult(...)
```

**Estimated Savings**: ~3,000 lines across 10+ agents

---

## 4. HIGH: Search Result Formatting Duplication

### Problem: 5+ nearly identical `_format_search_results` methods

**Locations**:
| File | Lines | Custom Logic |
|------|-------|--------------|
| `agents/base/specialist.py:116` | 20 | Generic |
| `agents/research/deep_research.py:471` | 15 | Generic |
| `agents/specialized/brand_auditor.py:285` | 3 | Uses centralized |
| `agents/specialized/sales_intelligence.py:314` | 13 | Custom |
| `agents/specialized/social_media.py:299` | 24 | Keyword scoring |

**Recommendation**: Already have `SearchResultFormatter` in `agents/base/search_formatting.py`!

```python
# CURRENT: Each agent defines its own
def _format_search_results(self, results):
    if not results:
        return "No search results"
    formatted = []
    for i, r in enumerate(results[:12], 1):
        formatted.append(f"Source {i}: {r.get('title')}\nContent: {r.get('content')[:400]}...")
    return "\n".join(formatted)

# SHOULD BE: Use existing infrastructure
from ..base.search_formatting import format_search_results, BrandSearchFormatter

def _format_search_results(self, results):
    return format_search_results(results, formatter=BrandSearchFormatter())
```

**Estimated Savings**: ~300 lines, consistent formatting

---

## 5. MEDIUM: Extraction Method Duplication

### Problem: Similar extraction patterns repeated across agents

**Common patterns duplicated**:

```python
# Pattern 1: List extraction (appears 8+ times)
def _extract_list(self, analysis: str, keyword: str) -> List[str]:
    items = []
    lines = analysis.split("\n")
    for line in lines:
        if keyword.lower() in line.lower():
            cleaned = line.strip().lstrip("0123456789.-* ").strip()
            if cleaned and len(cleaned) > 10:
                items.append(cleaned[:150])
    return items[:5]

# Pattern 2: Score extraction (appears 6+ times)
def _extract_score(self, analysis: str, label: str = "Score") -> float:
    patterns = [
        rf"{label}[:\s]*(\d{{1,3}})",
        r"Overall.*?(\d{1,3})\s*/\s*100"
    ]
    for pattern in patterns:
        match = re.search(pattern, analysis, re.IGNORECASE)
        if match:
            return min(100, float(match.group(1)))
    return 50.0

# Pattern 3: Enum extraction (appears 10+ times)
def _extract_enum_value(self, analysis: str, enum_class, keywords_map: Dict) -> Enum:
    analysis_upper = analysis.upper()
    for keyword, enum_value in keywords_map.items():
        if keyword in analysis_upper:
            return enum_value
    return default_value
```

### Recommendation: Create `ExtractionMixin`

```python
# agents/base/extraction_mixin.py
class ExtractionMixin:
    """Reusable extraction methods for all agents."""

    def extract_list_items(
        self,
        text: str,
        keyword: str,
        max_items: int = 5,
        min_length: int = 10
    ) -> List[str]: ...

    def extract_score(
        self,
        text: str,
        label: str = "Score",
        default: float = 50.0
    ) -> float: ...

    def extract_enum(
        self,
        text: str,
        enum_class: Type[Enum],
        keyword_mapping: Dict[str, Enum],
        default: Enum
    ) -> Enum: ...

    def extract_table_rows(
        self,
        text: str,
        expected_columns: int
    ) -> List[List[str]]: ...
```

**Note**: `ParsingMixin` exists but isn't universally used!

**Estimated Savings**: ~1,500 lines

---

## 6. MEDIUM: Config Parameter Sprawl

### Problem: Config has 50+ agent-specific parameters

```python
# Current config.py has:
researcher_max_tokens: int = 500
researcher_temperature: float = 0.7
analyst_max_tokens: int = 1000
analyst_temperature: float = 0.1
financial_max_tokens: int = 800
financial_temperature: float = 0.0
enhanced_financial_max_tokens: int = 1200
market_max_tokens: int = 800
market_temperature: float = 0.1
enhanced_market_max_tokens: int = 1200
# ... 40+ more parameters
```

### Recommendation: Use nested config structure

```python
# config.py - IMPROVED
from pydantic import BaseModel

class AgentConfig(BaseModel):
    max_tokens: int = 1000
    temperature: float = 0.1

class AgentConfigs(BaseModel):
    researcher: AgentConfig = AgentConfig(max_tokens=500, temperature=0.7)
    analyst: AgentConfig = AgentConfig(max_tokens=1000, temperature=0.1)
    financial: AgentConfig = AgentConfig(max_tokens=800, temperature=0.0)
    # ...

class ResearchConfig(BaseSettings):
    agents: AgentConfigs = AgentConfigs()

    # Usage becomes:
    # config.agents.financial.max_tokens
```

**Estimated Savings**: Cleaner config, easier testing

---

## 7. MEDIUM: Workflow/Orchestration Overlap

### Problem: Multiple overlapping workflow modules

```
graphs/
└── research_graph.py        # LangGraph implementation

workflows/
├── basic_research.py        # Another workflow
├── multi_agent_research.py  # Sequential agents
└── parallel_agent_research.py # Parallel agents

orchestration/
├── research_workflow.py     # Yet another!
├── workflow_engine.py
├── scheduler.py
└── conditional_router.py
```

**Recommendation**:
1. Consolidate into single `workflows/` module
2. Use LangGraph as the standard
3. Remove legacy orchestration code

---

## 8. DOCUMENTATION GAPS

### Missing Documentation:
1. No architecture diagram
2. No agent interaction flow
3. No API documentation
4. No deployment guide
5. Inconsistent docstrings

### Recommendation:
1. Add `docs/architecture.md` with diagrams
2. Add `docs/agent-guide.md` for creating new agents
3. Use consistent docstring format (Google or NumPy)

---

## Refactoring Priority Matrix

| Priority | Item | Effort | Impact | Risk |
|----------|------|--------|--------|------|
| P0 | Delete duplicate quality/validation/ | LOW | HIGH | LOW |
| P0 | Consolidate enums to types.py | LOW | HIGH | LOW |
| P1 | Create BaseAnalysisAgent | MEDIUM | HIGH | MEDIUM |
| P1 | Consolidate cache modules | MEDIUM | MEDIUM | LOW |
| P2 | Unify extraction methods | MEDIUM | MEDIUM | LOW |
| P2 | Restructure config | MEDIUM | MEDIUM | MEDIUM |
| P3 | Consolidate workflows | HIGH | MEDIUM | HIGH |
| P3 | Add documentation | MEDIUM | MEDIUM | LOW |

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 days)
1. Delete `quality/validation/` directory
2. Update imports to use `quality/` directly
3. Remove duplicate enum definitions from agent files
4. Import all enums from `types.py`

### Phase 2: Infrastructure (3-5 days)
1. Create `BaseAnalysisAgent` abstract class
2. Refactor 3-4 agents to use new base class
3. Consolidate `cache/` into `caching/`
4. Remove duplicate LRU/vector store implementations

### Phase 3: Standardization (5-7 days)
1. Migrate remaining agents to `BaseAnalysisAgent`
2. Create `ExtractionMixin` with shared methods
3. Refactor config to use nested structure
4. Add comprehensive type hints

### Phase 4: Documentation (2-3 days)
1. Create architecture documentation
2. Add agent development guide
3. Document all public APIs
4. Add inline documentation

---

## Code Examples for Immediate Action

### Delete Duplicate Quality Module
```bash
# In Git Bash or terminal
git rm -r src/company_researcher/quality/validation/
```

### Update Enum Imports
```python
# In brand_auditor.py - REPLACE:
class BrandStrength(str, Enum):
    DOMINANT = "DOMINANT"
    ...

# WITH:
from ...types import BrandStrength, BrandHealth, SentimentCategory
```

### Consolidate Cache Directory
```bash
# Move unique files from cache/ to caching/
mv src/company_researcher/cache/research_cache.py \
   src/company_researcher/caching/simple_cache.py
rm -r src/company_researcher/cache/
```

---

## Metrics After Refactoring (Estimated)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total Files | 240 | ~200 | -17% |
| Lines of Code | 82,822 | ~55,000 | -34% |
| Duplicate Enums | 14 | 0 | -100% |
| Duplicate Methods | 25+ | 5 | -80% |
| Test Coverage | ? | Improved | Higher |
| Maintainability Index | Low | High | Significant |

---

## Conclusion

This codebase has grown organically and accumulated significant technical debt. The recommended refactoring will:

1. **Reduce complexity** by eliminating duplication
2. **Improve reliability** through centralized definitions
3. **Accelerate development** with better abstractions
4. **Reduce bugs** by having single sources of truth
5. **Improve testability** with cleaner interfaces

**Start with Phase 1** - the quick wins provide immediate value with minimal risk.
