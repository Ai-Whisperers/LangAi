# Multilingual Search Duplicate Analysis

**Date:** 2025-12-10
**Status:** CONFIRMED DUPLICATE - Both versions actively used

---

## Summary

Both `multilingual_search.py` implementations exist and are **actively used** by different parts of the codebase. This is a **real duplicate** requiring consolidation.

---

## File Locations & Sizes

| File | Lines | Active Users |
|------|-------|--------------|
| `research/multilingual_search.py` | 664 | 1 (researcher.py) |
| `agents/research/multilingual_search.py` | 635 | 4 (workflows, tests) |

---

## Usage Analysis

### research/multilingual_search.py (664 lines)
**Used By:**
- `agents/core/researcher.py` (imports: MultilingualSearchGenerator, create_multilingual_generator, Language)
- `research/__init__.py` (re-exports for package API)

**Import Statement:**
```python
from ...research.multilingual_search import (
    MultilingualSearchGenerator,
    create_multilingual_generator,
    Language
)
```

### agents/research/multilingual_search.py (635 lines)
**Used By:**
- `workflows/nodes/search_nodes.py`
- `workflows/comprehensive_research.py`
- `tests/test_quality_modules.py`
- `tests/test_enhanced_workflow_integration.py`
- `agents/research/__init__.py` (re-exports)

**Import Statement:**
```python
from ...agents.research.multilingual_search import (
    MultilingualSearchGenerator,
    create_multilingual_generator,
    ...
)
```

---

## Feature Comparison

### Supported Languages

**research/** version (MORE COMPREHENSIVE):
- ✅ English
- ✅ Spanish
- ✅ Portuguese
- ✅ French
- ✅ German
- ✅ Italian
- ✅ Chinese
- ✅ Japanese
- ✅ Korean
- **Total: 9 languages**

**agents/research/** version (LIMITED):
- ✅ English
- ✅ Spanish
- ✅ Portuguese
- **Total: 3 languages** (focused on Latin America)

### Data Models

**research/** version:
```python
class Language(Enum): # 9 languages
class RegionalSource(dataclass):  # Regional data source metadata
class MultilingualQuery(dataclass):
    query: str
    language: Language
    query_type: str
    priority: int
```

**agents/research/** version:
```python
class Language(Enum): # 3 languages only
class Region(Enum):  # Geographic regions
class MultilingualQuery(dataclass):
    query: str
    language: Language
    topic: str  # Different field name
    priority: int
```

### Key Features

**research/** version UNIQUE features:
- ✅ RegionalSource dataclass for data source metadata
- ✅ COUNTRY_LANGUAGES mapping (extensive - 50+ countries)
- ✅ REGIONAL_SOURCES comprehensive list
- ✅ 9-language support
- ✅ `current_year` parameter in __init__
- ✅ More comprehensive country/language mappings

**agents/research/** version UNIQUE features:
- ✅ Region enum (NORTH_AMERICA, LATAM_BRAZIL, LATAM_SPANISH, etc.)
- ✅ PARENT_COMPANY_MAP (130+ subsidiary → parent mappings)
  - Telecom: América Móvil, Telefónica, Millicom
  - Banking: Itaú, Bradesco, BBVA
  - Retail: Grupo Bimbo, Walmart subsidiaries
- ✅ Parent company lookup functionality
- ✅ Focused on Latin America use cases

### Method Signatures

**research/** version:
```python
def __init__(self, current_year: int = 2024):

def generate_queries(
    company_name: str,
    headquarters_country: Optional[str] = None,
    languages: Optional[List[Language]] = None,
    query_types: Optional[List[str]] = None,
    include_parent_company: bool = True
) -> List[MultilingualQuery]:
```

**agents/research/** version:
```python
def __init__(self):

def generate_queries(
    company_name: str,
    language: Optional[Language] = None,
    topic: Optional[str] = None,
    ...
) -> List[MultilingualQuery]:
```

---

## Consolidation Complexity: HIGH

### Why This Is Complex

1. **Different API Signatures**
   - `query_type` vs `topic` field
   - Different __init__ parameters
   - Breaking change risk

2. **Different Feature Sets**
   - research/ version: More languages, regional sources
   - agents/research/ version: Parent company mappings, region enum

3. **Active Usage in Multiple Places**
   - Can't simply delete one without breaking code
   - Tests depend on agents/research/ version
   - Workflows depend on agents/research/ version
   - researcher.py depends on research/ version

4. **Both Have Valuable Features**
   - research/ version: Better for global companies
   - agents/research/ version: Better for Latin American subsidiaries

---

## Consolidation Recommendations

### Option 1: Merge Into agents/research/ (RECOMMENDED)

**Rationale:**
- More actively used (4 locations vs 1)
- Used by workflows (critical path)
- Used by tests (validation path)
- Only need to update 1 location (researcher.py)

**Steps:**
1. Add 6 more languages to agents/research/ version (French, German, Italian, Chinese, Japanese, Korean)
2. Add RegionalSource dataclass
3. Add REGIONAL_SOURCES data
4. Add comprehensive COUNTRY_LANGUAGES mapping
5. Update researcher.py to import from agents/research/
6. Delete research/multilingual_search.py
7. Update research/__init__.py to re-export from agents/research/
8. Run all tests to verify

**Estimated Effort:** 4-6 hours

### Option 2: Merge Into research/

**Rationale:**
- More comprehensive language support
- Better structure for global expansion

**Steps:**
1. Add PARENT_COMPANY_MAP and Region enum to research/ version
2. Update 4 locations (workflows, tests) to import from research/
3. Update agents/research/__init__.py to re-export from research/
4. Delete agents/research/multilingual_search.py
5. Run all tests to verify

**Estimated Effort:** 6-8 hours (more files to update)

### Option 3: Keep Both, Add Abstraction

**Rationale:**
- Preserve both feature sets without breaking changes
- Create unified interface

**Steps:**
1. Create base interface/protocol
2. Update both to implement interface
3. Add factory function to select version
4. No breaking changes

**Estimated Effort:** 3-4 hours
**Risk:** Maintains duplicate code, doesn't solve root problem

---

## Recommended Action

**MERGE INTO agents/research/** (Option 1)

**Priority:** HIGH (active duplicate causing confusion)

**Next Steps:**
1. Create backup branch
2. Add missing features from research/ to agents/research/
3. Update researcher.py import
4. Delete research/multilingual_search.py
5. Update research/__init__.py re-exports
6. Run full test suite
7. Commit with detailed message

**Benefits:**
- ✅ Single source of truth
- ✅ Best of both versions
- ✅ Minimal breaking changes (only 1 file to update)
- ✅ Maintains all existing tests
- ✅ Clear ownership (agents/research/)

**Risks:**
- ⚠️ Need to ensure all features preserved
- ⚠️ Need careful testing of researcher.py after change
- ⚠️ Verify factory functions still work

---

## Conclusion

This is a **confirmed duplicate** with both versions actively used. Consolidation is necessary but requires careful planning due to:
- Different feature sets
- Multiple active users
- Test dependencies

**Recommended approach:** Merge into agents/research/ version (used by 4 locations vs 1) with careful feature preservation.
