# Data Threshold Duplicate Analysis

**Date:** 2025-12-10
**Status:** ⚠️ TRUE DUPLICATE with BROKEN IMPORT - Critical Consolidation Required
**Conclusion:** Both serve similar purposes but with different input types and a broken import in researcher.py

---

## Executive Summary

The two `data_threshold.py` implementations are **TRUE DUPLICATES** with critical issues:

1. **research/data_threshold.py** (565 lines) - **Late-stage validation**
   - Validates structured research data AFTER processing
   - Section-based validation (financial, market, company_info, etc.)
   - Input: `Dict[str, Any]` (structured research_data)
   - Method: `check(research_data: Dict[str, Any])`

2. **agents/research/data_threshold.py** (339 lines) - **Early-stage validation**
   - Validates raw search results BEFORE processing
   - Source quality scoring (count, domains, content richness)
   - Input: `List[Dict[str, Any]]` (raw search results)
   - Method: `check_threshold(results: List[Dict], company_name: str)`

**CRITICAL ISSUE:** `researcher.py` imports from `research/` but calls methods from `agents/research/`!

```python
# researcher.py (BROKEN!)
from ...research.data_threshold import (
    DataThresholdChecker,
    create_threshold_checker,  # ← Doesn't exist in research/!
    RetryStrategy
)

checker = create_threshold_checker()
result = checker.check_threshold(...)  # ← This method doesn't exist in research/!
```

**Verdict:** ⚠️ **CONSOLIDATE** - These could be complementary but the broken import and overlapping functionality suggest they should be merged

---

## File Comparison

| Aspect | research/ (565 lines) | agents/research/ (339 lines) |
|--------|----------------------|------------------------------|
| **Input Type** | `Dict[str, Any]` (structured data) | `List[Dict[str, Any]]` (raw results) |
| **Main Method** | `check(research_data)` | `check_threshold(results, company_name)` |
| **Focus** | Section completeness | Source quality |
| **Stage** | Late (after processing) | Early (before processing) |
| **Validation** | Field-based per section | Pattern-based in raw content |
| **Complexity** | HIGH - Detailed section requirements | MEDIUM - Source counting & patterns |
| **Factory Function** | None | `create_threshold_checker()` ✅ |
| **Used By** | researcher.py (BROKEN import!) | Exported but unused correctly |

---

## Broken Import Analysis

### Current State (researcher.py lines 37-41)

```python
from ...research.data_threshold import (
    DataThresholdChecker,
    create_threshold_checker,  # ← ERROR: Doesn't exist!
    RetryStrategy
)
```

### researcher.py Usage (lines 307-328)

```python
checker = create_threshold_checker()  # ← ERROR: Not defined in research/

result = checker.check_threshold(  # ← ERROR: Method doesn't exist in research/
    content=combined_content,
    company_name=company_name,
    company_type=ctype
)
```

### What Methods Actually Exist

**research/data_threshold.py:**
- `DataThresholdChecker.check(research_data: Dict[str, Any])`  ✅
- `check_data_threshold(research_data: Dict[str, Any])`  ✅ (convenience function)
- `should_generate_report(research_data: Dict[str, Any])`  ✅
- `create_threshold_checker()`  ❌ **DOES NOT EXIST**

**agents/research/data_threshold.py:**
- `DataThresholdChecker.check_threshold(results: List[Dict], company_name: str)`  ✅
- `create_threshold_checker(custom_thresholds: Optional[Dict])`  ✅

**Impact:** researcher.py will crash at runtime when trying to use data_threshold!

---

## Detailed Feature Comparison

### research/data_threshold.py (Late-stage validation)

**Purpose:** Check if processed research data has sufficient information for report generation

**Key Classes:**
```python
class DataSufficiency(Enum):
    EXCELLENT = "excellent"  # 80%+ coverage
    GOOD = "good"  # 60-80%
    ADEQUATE = "adequate"  # 40-60%
    POOR = "poor"  # 20-40%
    INSUFFICIENT = "insufficient"  # <20%

class RetryStrategy(Enum):
    MULTILINGUAL = "multilingual"
    PARENT_COMPANY = "parent_company"
    ALTERNATIVE_SOURCES = "alternative_sources"
    RELAXED_QUERIES = "relaxed_queries"
    REGIONAL_SOURCES = "regional_sources"
    ARCHIVED_DATA = "archived_data"
    PRESS_RELEASES = "press_releases"
    NONE = "none"

@dataclass
class SectionCoverage:
    section_name: str
    expected_fields: int
    found_fields: int
    missing_fields: List[str]
    coverage_pct: float
    has_specific_data: bool  # Has actual numbers, not just text

@dataclass
class ThresholdResult:
    passes_threshold: bool
    sufficiency: DataSufficiency
    overall_coverage: float
    section_coverages: List[SectionCoverage]
    missing_critical: List[str]
    recommended_strategies: List[RetryStrategy]
    can_proceed: bool
    explanation: str
```

**Validation Approach:**
- Section-based: financial (30% weight), market (20%), company_info (15%), competitive (15%), products (10%), strategy (10%)
- Expected fields per section (e.g., financial: revenue, net_income, profit_margin, etc.)
- Pattern matching for specific data (currency values: `$123M`, percentages: `45%`)
- Missing data detection ("not available", "N/A", "unable to find")
- Weighted coverage calculation
- Critical fields must be present

**Thresholds:**
- Minimum overall: 25% coverage
- Minimum sections OK: 2 sections must be adequate
- Critical fields must have data

**Usage Pattern:**
```python
checker = DataThresholdChecker()
result = checker.check(research_data, strict_mode=False)

if not result.passes_threshold:
    print(f"Insufficient data: {result.explanation}")
    print(f"Missing critical: {result.missing_critical}")
    print(f"Recommended strategies: {result.recommended_strategies}")
```

---

### agents/research/data_threshold.py (Early-stage validation)

**Purpose:** Check if raw search results have enough data to proceed with analysis

**Key Classes:**
```python
class RetryStrategy(Enum):
    MULTILINGUAL = "multilingual"
    PARENT_COMPANY = "parent_company"
    ALTERNATIVE_NAMES = "alternative_names"  # ← Different from research/
    BROADER_QUERIES = "broader_queries"
    INDUSTRY_FOCUS = "industry_focus"

@dataclass
class ThresholdResult:
    passes_threshold: bool
    coverage_score: float  # 0-100
    source_count: int
    unique_domains: int
    content_richness: float  # 0-100
    has_financial_data: bool
    has_company_info: bool
    has_product_data: bool
    retry_strategies: List[RetryStrategy]
    issues: List[str]
    summary: str
```

**Validation Approach:**
- Source counting: minimum sources by company type
- Domain diversity: unique domains
- Content aggregation: total character count
- Category detection: financial, company_info, product, market patterns
- Coverage score calculation:
  - Source score (max 30 points)
  - Diversity score (max 20 points)
  - Content score (max 30 points)
  - Category score (max 20 points)

**Thresholds by Company Type:**
```python
"public": {
    "min_sources": 5,
    "min_unique_domains": 3,
    "min_content_chars": 2000,
    "required_categories": ["financial", "company_info"],
    "min_coverage_score": 40,
},
"private": {
    "min_sources": 3,
    "min_unique_domains": 2,
    "min_content_chars": 1000,
    "required_categories": ["company_info"],
    "min_coverage_score": 30,
},
# ... startup, subsidiary
```

**Category Detection Patterns:**
```python
"financial": [
    r"revenue|ingresos|receita|faturamento",
    r"(?:market\s*)?cap(?:italization)?|valorização",
    r"profit|lucro|beneficio|ganancia",
    r"(?:\$|€|£|R\$|MXN)\s*[\d.,]+\s*(?:billion|million|B|M|bn|mn|milhões|millones)",
],
"company_info": [
    r"founded|established|fundada|fundado|establecida",
    r"headquarter|based\s+in|sede|ubicada",
    r"employees?|empleados|funcionários|colaboradores",
],
# ... product, market
```

**Usage Pattern:**
```python
checker = DataThresholdChecker()
result = checker.check_threshold(
    results=search_results,  # List[Dict] from web search
    company_name="Company X",
    company_type="public"
)

if not result.passes_threshold:
    print(f"Coverage: {result.coverage_score:.1f}/100")
    print(f"Sources: {result.source_count}")
    print(f"Retry strategies: {result.retry_strategies}")
```

---

## Key Differences

### 1. Input Types

**research/:**
```python
def check(
    self,
    research_data: Dict[str, Any],  # ← Structured data
    strict_mode: bool = False
) -> ThresholdResult:
```

**agents/research/:**
```python
def check_threshold(
    self,
    results: List[Dict[str, Any]],  # ← Raw search results
    company_name: str,
    company_type: str = "public"
) -> ThresholdResult:
```

### 2. RetryStrategy Enums

**research/ (8 strategies):**
- MULTILINGUAL ✅
- PARENT_COMPANY ✅
- ALTERNATIVE_SOURCES ← Different
- RELAXED_QUERIES ← Different
- REGIONAL_SOURCES ← Unique
- ARCHIVED_DATA ← Unique
- PRESS_RELEASES ← Unique
- NONE ← Unique

**agents/research/ (5 strategies):**
- MULTILINGUAL ✅
- PARENT_COMPANY ✅
- ALTERNATIVE_NAMES ← Unique
- BROADER_QUERIES ← Different
- INDUSTRY_FOCUS ← Unique

### 3. ThresholdResult Structure

**research/ - Section-focused:**
```python
@dataclass
class ThresholdResult:
    passes_threshold: bool
    sufficiency: DataSufficiency  # ← Enum
    overall_coverage: float
    section_coverages: List[SectionCoverage]  # ← Detailed per section
    missing_critical: List[str]  # ← Field-level
    recommended_strategies: List[RetryStrategy]
    can_proceed: bool
    explanation: str
```

**agents/research/ - Source-focused:**
```python
@dataclass
class ThresholdResult:
    passes_threshold: bool
    coverage_score: float  # ← Simple score
    source_count: int  # ← Source metrics
    unique_domains: int  # ← Source metrics
    content_richness: float  # ← Content metric
    has_financial_data: bool  # ← Binary flags
    has_company_info: bool
    has_product_data: bool
    retry_strategies: List[RetryStrategy]
    issues: List[str]
    summary: str
```

### 4. Validation Focus

**research/ validates:**
- Section completeness (6 sections)
- Expected fields per section
- Specific data patterns (values, not just keywords)
- Critical field presence
- Weighted coverage by section importance

**agents/research/ validates:**
- Source quantity and diversity
- Total content volume
- Presence of data categories (pattern matching)
- Overall coverage score

---

## Workflow Analysis

### Intended Workflow (if complementary):

```
┌─────────────────────────────────────────────────────────────────┐
│                    Research Workflow                              │
└─────────────────────────────────────────────────────────────────┘

1. Web Search Phase
   └─ Execute searches, gather raw results

2. ⚡ EARLY-STAGE CHECK (agents/research/data_threshold.py)
   ├─ Check source count and diversity
   ├─ Check content volume
   ├─ Detect data category presence
   └─ Decision: Proceed or Retry with strategies

3. Data Processing Phase
   ├─ Extract facts from sources
   ├─ Structure data into sections
   └─ Compile research_data Dict

4. ✅ LATE-STAGE CHECK (research/data_threshold.py)
   ├─ Check section completeness
   ├─ Check field presence
   ├─ Check specific data values
   └─ Decision: Generate report or request more data

5. Report Generation
```

### Current Reality (BROKEN):

```
researcher.py:
    ├─ Imports from research/ ❌
    ├─ Calls create_threshold_checker() ❌ (doesn't exist)
    ├─ Calls check_threshold() ❌ (doesn't exist)
    └─ Will crash at runtime! 💥
```

---

## Consolidation Strategy

### Recommended Approach: Fix researcher.py + Keep Both (Option A)

**Rationale:**
- They validate different things at different stages (like quality_enforcer)
- Early-stage: raw search results (source quality)
- Late-stage: structured research data (section completeness)
- Both are needed in a complete workflow

**Steps:**
1. Fix researcher.py import to use agents/research/ instead of research/
2. Keep both implementations as complementary tools
3. Document when to use each one
4. Update __init__.py exports to clarify purposes

**Files to Modify:**
```python
# researcher.py (line 37)
# BEFORE (BROKEN):
from ...research.data_threshold import (
    DataThresholdChecker,
    create_threshold_checker,
    RetryStrategy
)

# AFTER (FIXED):
from ..research.data_threshold import (  # ← One less dot!
    DataThresholdChecker,
    create_threshold_checker,
    RetryStrategy
)
```

**Estimated Effort:** 15 minutes
- Update import path in researcher.py
- Test to ensure no crashes
- Update documentation

---

### Alternative Approach: Merge Into Single Implementation (Option B)

**Rationale:**
- Overlapping functionality causes confusion
- Both check data sufficiency
- Both recommend retry strategies
- researcher.py bug suggests unclear boundaries

**Design:**
```python
class DataThresholdChecker:
    def check_raw_results(
        self,
        results: List[Dict],
        company_name: str,
        company_type: str
    ) -> ThresholdResult:
        """Check raw search results (early stage)"""
        # Logic from agents/research/
        pass

    def check_research_data(
        self,
        research_data: Dict[str, Any],
        strict_mode: bool = False
    ) -> ThresholdResult:
        """Check structured research data (late stage)"""
        # Logic from research/
        pass
```

**Steps:**
1. Merge both into single class in research/
2. Add both `check_raw_results()` and `check_research_data()` methods
3. Unify RetryStrategy enums (combine all strategies)
4. Provide two ThresholdResult variants or unified structure
5. Update researcher.py to use unified version
6. Delete agents/research/data_threshold.py
7. Update __init__.py exports

**Estimated Effort:** 3-4 hours
- Merge implementations
- Unify enums and data structures
- Update imports (2 locations)
- Testing

---

## Comparison with quality_enforcer

| Aspect | quality_enforcer | data_threshold |
|--------|------------------|----------------|
| **Are they duplicates?** | NO - Complementary | UNCLEAR - Possibly complementary but broken |
| **Different purposes?** | YES - Pre-gen gate vs Post-gen analyzer | MAYBE - Early source check vs Late data check |
| **Usage clarity?** | Clear - Both used correctly | BROKEN - researcher.py has wrong import |
| **Recommendation** | KEEP BOTH | FIX IMPORT or CONSOLIDATE |

---

## Estimated Effort

### Option A (Fix Import - Keep Both)
| Task | Time | Risk |
|------|------|------|
| Fix researcher.py import | 5 min | LOW |
| Test data_threshold functionality | 10 min | LOW |
| Update documentation | 10 min | LOW |
| **TOTAL** | **25 min** | |

### Option B (Consolidate)
| Task | Time | Risk |
|------|------|------|
| Merge implementations | 1.5 hours | MEDIUM |
| Unify enums and structures | 30 min | LOW |
| Update imports (2 locations) | 15 min | LOW |
| Testing | 1 hour | MEDIUM |
| Delete duplicate | 5 min | LOW |
| **TOTAL** | **3-4 hours** | |

---

## Breaking Changes

### Option A (No Breaking Changes)
- Just fixes broken import
- Both versions remain available

### Option B (Minimal Breaking Changes)
- Import paths change from agents/research/ (but it was never used correctly anyway!)
- Method names change to `check_raw_results()` and `check_research_data()`

---

## Files to Modify

### Option A (Fix Import)
1. ⚠️ `src/company_researcher/agents/core/researcher.py` - Fix import path (line 37)

### Option B (Consolidate)
1. ✅ `src/company_researcher/research/data_threshold.py` - Add check_raw_results() method
2. ⚠️ `src/company_researcher/agents/core/researcher.py` - Update import
3. ⚠️ `src/company_researcher/research/__init__.py` - Update exports
4. ❌ `src/company_researcher/agents/research/data_threshold.py` - DELETE
5. ⚠️ `src/company_researcher/agents/research/__init__.py` - Remove exports

---

## Recommendation

**Priority:** HIGH - researcher.py is broken and will crash!

**Immediate Action:** Fix researcher.py import (Option A)
```python
# Change from:
from ...research.data_threshold import (...)
# To:
from ..research.data_threshold import (...)
```

**Long-term:** Consider Option B (consolidation) to:
- Eliminate confusion
- Provide clear unified interface
- Combine retry strategies
- Document when to use each check method

---

## Conclusion

**Status:** ⚠️ BROKEN CODE - Critical bug in researcher.py

**Issue:** researcher.py imports from research/ but calls methods from agents/research/

**Immediate Fix:** Change import path in researcher.py (15 minutes)

**Long-term Consideration:** These could be complementary (like quality_enforcer) OR consolidated into unified implementation

**Next Steps:**
1. Fix researcher.py import immediately
2. Test both data_threshold versions work correctly
3. Decide: Keep both OR consolidate?
4. Update documentation

---

**Analysis Date:** 2025-12-10
**Analyst:** Claude Code
**Status:** ⚠️ Critical Bug Found + Consolidation Plan Ready
