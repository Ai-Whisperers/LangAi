# Ticket Activation Exemplar

## Examples (Few-Shot)

### Example 1: Start Work on Ticket

**Input**:
```
<ticket>@EBASE-12345</ticket> <action>please start</action>
```

**Reasoning**:
AI loads ticket context, identifies this is a fresh start, should initialize workspace and propose approach.

**Expected Output**:
```markdown
## Activating Ticket EBASE-12345

**Loaded Context**:
- ✓ Plan: Implement OAuth login feature
- ✓ Complexity: Complex Implementation
- ✓ Current State: Not started

**Acceptance Criteria** (from plan.md):
1. [ ] User can log in with OAuth2 provider
2. [ ] Session management implemented
3. [ ] Token refresh mechanism in place

**Proposed Approach**:
1. Create authentication service
2. Implement OAuth2 flow
3. Add session management
4. Create unit tests

Ready to proceed? Please confirm or adjust approach.
```

### Example 2: Create Feature Documentation

**Input**:
```
<ticket>@EPP-192</ticket> <action>please make the feature md</action>
```

**Reasoning**:
AI loads ticket context, understands this is about creating feature.md artifact, should generate structured feature documentation.

**Expected Output**:
```markdown
## Creating Feature Documentation for EPP-192

**Feature**: YAML Format Standardization

I'll create `tickets/EPP-192/feature.md` with:

## Feature: YAML Format Standardization

### Business Value
Consistent YAML formatting across all rule and prompt files...

[Complete feature.md content]

**Created**: tickets/EPP-192/feature.md (285 lines)
**Next**: Review and update progress.md
```

### Example 3: Test Implementation

**Input**:
```
<ticket>@EBASE-12345</ticket> <action>please test</action>
```

**Reasoning**:
AI loads ticket, identifies this is a test request, should execute tests and verify acceptance criteria.

**Expected Output**:
```markdown
## Testing Ticket EBASE-12345

**Test Results**:

### Unit Tests
✅ All 15 tests passing
- AuthenticationService: 8/8 pass
- SessionManager: 5/5 pass
- TokenRefresh: 2/2 pass

### Acceptance Criteria
✅ Criterion 1: OAuth login works - PASS
✅ Criterion 2: Session management - PASS
✅ Criterion 3: Token refresh - PASS

**Validation**: All acceptance criteria met, ready for closure.
```

### Example 4: Validate and Execute

**Input**:
```
<ticket>@EBASE-12263</ticket> <context>@database-migration-spec.md</context> <action>please validate and when ok, execute</action>
```

**Reasoning**:
AI loads ticket and spec, validates migration plan against database schema, confirms safety, then executes migration.

**Expected Output**:
```markdown
## Validating EBASE-12263 with database-migration-spec.md

**Validation Results**:
✓ Migration script syntax valid
✓ Rollback script present
✓ No data loss scenarios
✓ Foreign key constraints maintained
✓ Index strategy sound

**Preconditions Met**: All clear for execution.

**Executing Migration**:
1. Backup current schema...✓
2. Apply migration script...✓
3. Verify data integrity...✓
4. Update schema version...✓

**Result**: Migration successful. Updated progress.md with execution log.
```

---

