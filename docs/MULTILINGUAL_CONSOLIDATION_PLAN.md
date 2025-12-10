# Multilingual Search Consolidation - Implementation Plan

**Date:** 2025-12-10
**Target:** Merge `research/multilingual_search.py` (664 lines) into `agents/research/multilingual_search.py` (635 lines)
**Estimated Effort:** 4-6 hours
**Status:** Ready for approval

---

## Executive Summary

**Strategy:** Merge INTO `agents/research/multilingual_search.py` (keep this as primary)

**Rationale:**
- Used by 4 locations (workflows, tests) vs 1 (researcher.py)
- Has valuable PARENT_COMPANY_MAP (130+ subsidiaries)
- Better country detection (regex-based COUNTRY_INDICATORS)
- Only need to update 1 import location

**Add from research/ version:**
- 6 additional languages (French, German, Italian, Chinese, Japanese, Korean)
- RegionalSource dataclass
- Comprehensive query templates for all 9 languages
- REGIONAL_SOURCES data for market-specific sources

---

## Current State Analysis

### agents/research/ version (635 lines) - PRIMARY

**Strengths:**
- ✅ Used by workflows (critical path)
- ✅ Used by tests (validation)
- ✅ PARENT_COMPANY_MAP (130+ subsidiaries → parent mappings)
- ✅ Region enum (NORTH_AMERICA, LATAM_BRAZIL, LATAM_SPANISH, EUROPE, ASIA)
- ✅ COUNTRY_INDICATORS with regex patterns (sophisticated detection)
- ✅ Methods: detect_region(), get_parent_company(), get_parent_company_queries(), get_alternative_name_queries()

**Current Languages:** 3 (English, Spanish, Portuguese)

**Current Data Structures:**
```python
Language enum: 3 languages
Region enum: 6 regions
MultilingualQuery(query, language, topic, priority)
PARENT_COMPANY_MAP: 130+ entries
COUNTRY_INDICATORS: 20+ countries with regex patterns
QUERY_TEMPLATES: 6 topics × 3 languages
```

### research/ version (664 lines) - SECONDARY

**Strengths:**
- ✅ 9 languages total (adds 6 more)
- ✅ RegionalSource dataclass for source metadata
- ✅ COUNTRY_LANGUAGES mapping (50+ countries)
- ✅ REGIONAL_SOURCES: Market-specific data sources
- ✅ Query templates for all 9 languages

**Current Languages:** 9 (English, Spanish, Portuguese, French, German, Italian, Chinese, Japanese, Korean)

**Current Data Structures:**
```python
Language enum: 9 languages
RegionalSource(name, url, language, country, data_types, search_template)
MultilingualQuery(query, language, query_type, priority) # Note: query_type vs topic
COUNTRY_LANGUAGES: 50+ countries
REGIONAL_SOURCES: Dict[str, List[RegionalSource]]
QUERY_TEMPLATES: More comprehensive with all 9 languages
```

---

## Implementation Plan

### Phase 1: Add Missing Languages ✅

**File:** `src/company_researcher/agents/research/multilingual_search.py`

**Action:** Extend Language enum

```python
class Language(Enum):
    """Supported languages for search queries."""
    ENGLISH = "en"
    SPANISH = "es"
    PORTUGUESE = "pt"
    # ADD:
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
```

**Estimated Time:** 5 minutes

### Phase 2: Add RegionalSource Dataclass ✅

**Action:** Add new dataclass after MultilingualQuery

```python
@dataclass
class RegionalSource:
    """A regional data source."""
    name: str
    url: str
    language: Language
    country: str
    data_types: List[str]  # e.g., ["financial", "news", "regulatory"]
    search_template: Optional[str] = None  # e.g., "site:{url} {query}"
```

**Estimated Time:** 5 minutes

### Phase 3: Extend QUERY_TEMPLATES ✅

**Action:** Add query templates for 6 new languages

**Current topics in agents/research/:**
- overview
- financial
- products
- competitors
- news
- leadership

**Add templates for each new language:**
- French: 6 topics × ~3 templates each
- German: 6 topics × ~3 templates each
- Italian: 6 topics × ~3 templates each
- Chinese: 6 topics × ~3 templates each
- Japanese: 6 topics × ~3 templates each
- Korean: 6 topics × ~3 templates each

**Source:** Copy from research/ version lines 176-271

**Estimated Time:** 30 minutes (copy + adapt formatting)

### Phase 4: Add REGIONAL_SOURCES ✅

**Action:** Add comprehensive regional data sources

**Copy from research/ version:**
- Mexico sources (BMV, Expansion MX, El Economista MX, CNBV)
- Brazil sources (B3, Valor Econômico, InfoMoney, Exame, CVM)
- Argentina sources
- Chile sources
- Colombia sources
- Peru sources
- Europe sources (France, Germany, Italy)
- Asia sources (China, Japan, Korea)

**Add as class attribute or module constant:**
```python
REGIONAL_SOURCES: Dict[str, List[RegionalSource]] = {
    "mexico": [...],
    "brazil": [...],
    # ... etc
}
```

**Estimated Time:** 45 minutes (copy + formatting + validation)

### Phase 5: Extend COUNTRY_INDICATORS (Optional) ⚠️

**Decision Point:** Should we add more countries?

**Current in agents/research/:** 20+ countries (Latin America focus)
**Available in research/:** 50+ countries (global coverage)

**Options:**
1. **Add global coverage** - extend with Europe, Asia, Africa
2. **Keep Latin America focus** - no changes needed

**Recommendation:** Add European and Asian countries since we're adding those languages

**Countries to add:**
- France, Germany, Italy (for new languages)
- China, Japan, Korea (for new languages)
- UK, Canada, Australia (English markets)

**Estimated Time:** 30 minutes

### Phase 6: Add Helper Methods (Optional) ⚠️

**Consider adding from research/ version:**
- `get_regional_sources(country: str) -> List[RegionalSource]`
- More comprehensive query generation using REGIONAL_SOURCES

**Estimated Time:** 30 minutes

### Phase 7: Update API Compatibility ⚠️

**Issue:** MultilingualQuery field naming

**agents/research/ has:**
```python
MultilingualQuery(query, language, topic, priority)
```

**research/ has:**
```python
MultilingualQuery(query, language, query_type, priority)
```

**Decision:** Keep `topic` (used by workflows/tests)
- research/__init__.py can alias during re-export if needed

**Estimated Time:** 10 minutes (verify no conflicts)

---

## Phase 8: Update Imports 🔧

### Files to Update: 1 file only!

**File 1:** `src/company_researcher/agents/core/researcher.py`

**Current:**
```python
from ...research.multilingual_search import (
    MultilingualSearchGenerator,
    create_multilingual_generator,
    Language
)
```

**Change to:**
```python
from ...agents.research.multilingual_search import (
    MultilingualSearchGenerator,
    create_multilingual_generator,
    Language
)
```

**Estimated Time:** 5 minutes

---

## Phase 9: Update Re-Exports 🔧

### File:** `src/company_researcher/research/__init__.py`

**Current:**
```python
from .multilingual_search import (
    MultilingualSearchGenerator,
    Language,
    RegionalSource,
    create_multilingual_generator,
)
```

**Change to:**
```python
from ..agents.research.multilingual_search import (
    MultilingualSearchGenerator,
    Language,
    RegionalSource,  # Now available!
    create_multilingual_generator,
)
```

**Estimated Time:** 5 minutes

---

## Phase 10: Delete Old File 🗑️

**File:** `src/company_researcher/research/multilingual_search.py`

**Action:** Delete after all changes complete and tested

**Estimated Time:** 2 minutes

---

## Phase 11: Testing & Validation ✅

### Tests to Run:

1. **Import Test:**
```bash
python -c "from src.company_researcher.agents.research.multilingual_search import MultilingualSearchGenerator, Language, RegionalSource"
```

2. **Unit Tests:**
```bash
pytest tests/test_quality_modules.py -v
pytest tests/test_enhanced_workflow_integration.py -v
```

3. **Integration Test:**
```bash
# Test researcher.py with new import
python -c "from src.company_researcher.agents.core.researcher import ResearcherAgent"
```

4. **Feature Test:**
```python
from src.company_researcher.agents.research.multilingual_search import (
    MultilingualSearchGenerator,
    Language,
    RegionalSource
)

gen = MultilingualSearchGenerator()

# Test new languages
queries = gen.generate_queries("Samsung", language=Language.KOREAN)
print(f"Korean queries: {len(queries)}")

# Test RegionalSource
assert RegionalSource is not None
```

**Estimated Time:** 30 minutes

---

## Detailed Time Breakdown

| Phase | Task | Time | Risk |
|-------|------|------|------|
| 1 | Add 6 languages to enum | 5 min | LOW |
| 2 | Add RegionalSource dataclass | 5 min | LOW |
| 3 | Extend QUERY_TEMPLATES (6 languages) | 30 min | LOW |
| 4 | Add REGIONAL_SOURCES data | 45 min | LOW |
| 5 | Extend COUNTRY_INDICATORS (optional) | 30 min | LOW |
| 6 | Add helper methods (optional) | 30 min | MEDIUM |
| 7 | Verify API compatibility | 10 min | LOW |
| 8 | Update researcher.py import | 5 min | LOW |
| 9 | Update research/__init__.py re-export | 5 min | LOW |
| 10 | Delete old file | 2 min | LOW |
| 11 | Testing & validation | 30 min | MEDIUM |
| **TOTAL** | **Core tasks (required)** | **2.5 hrs** | |
| **TOTAL** | **With optional enhancements** | **4-5 hrs** | |

---

## Risk Assessment

### LOW RISK ✅
- Adding languages to enum
- Adding dataclass
- Copying query templates
- Copying regional sources data
- Updating imports (only 1 location)
- Re-export changes

### MEDIUM RISK ⚠️
- Helper method additions (if any bugs in implementation)
- Testing coverage (need to ensure all features work)
- Field naming (topic vs query_type) - but we're keeping "topic"

### HIGH RISK ❌
- None identified

---

## Rollback Plan

If issues arise:

1. **Git revert** - All changes in single commit
2. **Restore old import** in researcher.py
3. **Tests will catch** - No breaking changes if tests pass

---

## Success Criteria

✅ All 9 languages work in Language enum
✅ RegionalSource dataclass available for import
✅ QUERY_TEMPLATES support all 9 languages
✅ REGIONAL_SOURCES provide market-specific sources
✅ researcher.py imports from agents/research/
✅ research/__init__.py re-exports work
✅ All existing tests pass
✅ New language features accessible
✅ research/multilingual_search.py deleted
✅ Zero breaking changes for existing code

---

## Approval Checklist

Before proceeding, confirm:

- [ ] Strategy approved (merge into agents/research/)
- [ ] Time commitment acceptable (2.5-5 hours)
- [ ] Optional enhancements desired? (Phase 5-6)
- [ ] Testing plan acceptable
- [ ] Backup/rollback strategy clear

---

## Next Steps

**Option A:** Proceed immediately with consolidation (2.5-5 hours)
**Option B:** Schedule for later (create branch, bookmark)
**Option C:** Modify plan based on feedback

**Recommendation:** Proceed if time permits, as this is HIGH priority and blocks cleanup progress.

---

## Post-Consolidation

After successful merge:

1. Update DUPLICATE_FILES_ANALYSIS.md (mark as resolved)
2. Update FINAL_DUPLICATE_SUMMARY.md (update status)
3. Update REFACTORING_TRACKER.md (add consolidation entry)
4. Move to next duplicate (quality_enforcer.py)

---

**Status:** ✅ READY FOR APPROVAL
**Confidence:** HIGH (clear plan, low risk, good testing strategy)
