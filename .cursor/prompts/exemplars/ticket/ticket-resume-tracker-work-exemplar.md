# Ticket Resume-Tracker-Work Exemplar

## Examples (Few-Shot)

### Example 1: Resume Unit Test Implementation

**Input**:
```
<tracker>@UNIT-TEST-IMPLEMENTATION-TRACKER.md</tracker> <action>lets continue with the remaining tasks please</action>
```

**Reasoning**:
AI loads tracker, identifies 12 of 20 components have tests (60% complete), next priority is `ValidationService` component. Resumes by implementing tests for ValidationService using same pattern as completed components.

**Expected Output**:
```markdown
## Resuming Work from UNIT-TEST-IMPLEMENTATION-TRACKER.md

**Current Progress**:
- Completed: 12/20 components (60%)
- Remaining: 8 components (40%)
- Next Priority: ValidationService, AuthenticationService, CacheManager

---

### Continuing with ValidationService Tests

**Creating**: ValidationServiceTests.cs

```csharp
// ValidationService unit tests implementation
// (AI implements comprehensive test suite following established pattern)
```

✅ **ValidationService Tests Complete**
- 15 tests created
- 95% code coverage
- All edge cases covered
- XML documentation added

---

### Updated Progress

**UNIT-TEST-IMPLEMENTATION-TRACKER.md updated**:

```markdown
## Progress: 13/20 (65%)

### Completed ✅
- [Previous 12 components]
- ValidationService (15 tests, 95% coverage) ← NEW

### Remaining ⏳
- AuthenticationService (HIGH PRIORITY)
- CacheManager
- [6 more components]
```

---

### Next Session

**To continue**:
```
<tracker>@UNIT-TEST-IMPLEMENTATION-TRACKER.md</tracker> <action>lets continue</action>
```

**Next Priority**: AuthenticationService (8 remaining components, est. 3-4 sessions to 100%)
```

### Example 2: Push to Completion Goal

**Input**:
```
<tracker>@UNIT-TEST-IMPLEMENTATION-TRACKER.md</tracker> <action>lets get all to 100%</action>
```

**Reasoning**:
User wants to complete ALL remaining work. AI identifies 5 remaining components, works through them systematically in batch until tracker reaches 100%.

**Expected Output**:
```markdown
## Pushing to 100% Completion: UNIT-TEST-IMPLEMENTATION-TRACKER.md

**Starting State**: 15/20 components complete (75%)  
**Goal**: 20/20 components complete (100%)  
**Remaining**: 5 components

---

### Batch Processing Remaining Components

#### 1. AuthenticationService Tests ✅
- 12 tests created (login, token, session, refresh)
- 98% coverage
- Edge cases: expired tokens, invalid credentials, session timeout

#### 2. CacheManager Tests ✅
- 8 tests created (set, get, invalidate, expiry)
- 100% coverage
- Edge cases: null keys, memory pressure, concurrent access

#### 3. LoggingService Tests ✅
- 6 tests created (log levels, formatting, sinks)
- 92% coverage
- Edge cases: log rotation, sink failures

#### 4. ConfigurationManager Tests ✅
- 10 tests created (load, save, validation, environment)
- 95% coverage
- Edge cases: missing config, invalid values, environment overrides

#### 5. MetricsCollector Tests ✅
- 7 tests created (collect, aggregate, export)
- 90% coverage
- Edge cases: metric overflow, export failures

---

### Final Progress

**UNIT-TEST-IMPLEMENTATION-TRACKER.md updated**:

```markdown
## Progress: 20/20 (100%) ✅ COMPLETE

### All Components Complete ✅
[List of all 20 components with test counts and coverage]

**Overall Metrics**:
- Total Tests: 187
- Average Coverage: 94.5%
- All Edge Cases Covered: Yes
- XML Documentation: 100%

**Completion Date**: 2025-12-08

## Status
✅ **100% COMPLETE** - All components have comprehensive unit tests
```

---

### 🎉 Tracker Work Complete

**Achievement**: All 20 components now have comprehensive unit test coverage.

**Next Steps**:
1. Run full test suite: `dotnet test`
2. Validate coverage: `dotnet test /p:CollectCoverage=true`
3. Mark ticket complete if this was final requirement
```

### Example 3: Priority-Based Continuation

**Input**:
```
<tracker>@IMPLEMENTATION-TRACKER.md</tracker> <action>continue with high-priority items only</action>
```

**Reasoning**:
User wants to focus on high-priority items only. AI loads tracker, filters for HIGH PRIORITY items, works through them ignoring lower-priority items.

**Expected Output**:
```markdown
## Resuming High-Priority Items from IMPLEMENTATION-TRACKER.md

**Priority Filtering**: HIGH PRIORITY ONLY

**Current Progress**:
- High Priority Completed: 3/7 items (43%)
- High Priority Remaining: 4 items
- (Low/Medium priority items: 15 remaining, skipped this session)

---

### High-Priority Work

#### 1. User Authentication (HIGH PRIORITY) ✅
**Status**: Complete
- OAuth2 implementation
- Session management
- Token refresh mechanism
**Completion**: 2025-12-08

#### 2. Database Migration Tool (HIGH PRIORITY) ✅
**Status**: Complete
- Migration script generator
- Rollback support
- Version tracking
**Completion**: 2025-12-08

---

### Updated Progress (High-Priority Only)

**IMPLEMENTATION-TRACKER.md updated**:

```markdown
## High-Priority Items: 5/7 (71%)

### Completed ✅
- [Previous 3 items]
- User Authentication (OAuth2, session, token refresh)
- Database Migration Tool (scripts, rollback, versioning)

### Remaining HIGH PRIORITY ⏳
- API Rate Limiting (next)
- Security Audit Fixes
```

---

### Next Session

**To continue high-priority work**:
```
<tracker>@IMPLEMENTATION-TRACKER.md</tracker> <action>continue with high-priority items</action>
```

**Next Priority**: API Rate Limiting (2 high-priority items remaining)
```

### Example 4: Scoped Continuation (Skip Specific Items)

**Input**:
```
<tracker>@tracker.md</tracker> <action>continue but skip the skipped items</action>
```

**Reasoning**:
Tracker has some items marked SKIPPED (intentionally deferred). AI continues with pending items but respects SKIPPED markers.

**Expected Output**:
```markdown
## Resuming Work from tracker.md (Skipping SKIPPED Items)

**Current Progress**:
- Completed: 18 items
- Pending: 5 items
- Skipped: 3 items (will respect and skip)

---

### Continuing with Pending Items Only

(AI works through pending items, ignores items marked SKIPPED)

---

### Updated Progress

**tracker.md updated**:

```markdown
## Progress: 20/23 (87%) + 3 SKIPPED

### Completed ✅
- [18 previous items]
- [2 newly completed items]

### Pending ⏳
- [3 remaining pending items]

### Skipped (Intentionally Deferred) ⏭️
- [3 skipped items - not included in completion percentage]
```

**Note**: SKIPPED items excluded from completion percentage calculation.
```

---

