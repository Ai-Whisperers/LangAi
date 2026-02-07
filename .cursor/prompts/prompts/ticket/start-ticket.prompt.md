---
name: start-ticket
description: "Please initialize a new ticket with complete documentation structure and implementation plan"
category: ticket
tags: ticket, workflow, initialization, documentation, setup, planning
argument-hint: "Ticket ID and summary (e.g., EPP-192)"
---

# Start Working on Ticket

Please initialize complete ticket documentation and create an implementation plan for starting work.

**Pattern**: Ticket Initialization Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential foundation for all ticket work
**Use When**: Starting any new ticket, ensuring proper documentation and planning

---

## Purpose

This prompt establishes proper ticket foundation by:
- Creating structured ticket documentation folder
- Assessing complexity and determining implementation strategy
- Gathering relevant context and dependencies
- Planning work breakdown with milestones
- Setting up tracking mechanisms
- Enabling smooth handoff and continuity

Use this when beginning work on any new ticket.

---

## Required Context

```xml
<ticket>
  <id>[TICKET_ID]</id>
  <summary>[TICKET_SUMMARY]</summary>
  <requirements>[DETAILED_REQUIREMENTS]</requirements> <!-- optional -->
</ticket>
```

**Placeholder Conventions**:
- `[TICKET_ID]` - Full ticket identifier (e.g., EPP-192, EBASE-12345)
- `[TICKET_SUMMARY]` - Brief description of ticket objective (1-2 sentences)
- `[DETAILED_REQUIREMENTS]` - Optional detailed requirements or link to specification

---

## Process

Follow these steps to initialize a ticket:

### Step 1: Gather Ticket Information
Collect ticket ID, summary, and any available detailed requirements or specifications.

### Step 2: Formulate Start Request
Use pattern with XML delimiters:
```xml
<ticket>
  <id>[TICKET_ID]</id>
  <summary>[TICKET_SUMMARY]</summary>
</ticket>
<action>start ticket</action>
```

### Step 3: AI Creates Documentation Structure
AI generates complete ticket folder with plan.md, context.md, progress.md, and assesses complexity.

### Step 4: Review Generated Documentation
Check plan, complexity assessment, work breakdown, and implementation strategy.

### Step 5: Begin Implementation
Use activate-ticket or proceed with first task from plan.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Understand Objective**: What problem does this ticket solve? What's the desired outcome?
2. **Assess Complexity**: Simple fix or complex implementation? How many components involved?
3. **Identify Dependencies**: What existing code/systems does this touch? What could break?
4. **Plan Approach**: What's the logical sequence of work? What are the milestones?
5. **Surface Unknowns**: What questions need answers? What research is needed?
6. **Estimate Effort**: Based on complexity, how much work is this?
7. **Create Documentation**: Generate plan.md, context.md, progress.md following templates
8. **Update Tracking**: Set current.md to this ticket

---

## Complexity Assessment Criteria

### Simple Fix (1-2 days, <3 files, straightforward)
- Single responsibility change
- Clear requirements
- Minimal risk
- Few dependencies
- Focused scope

### Complex Implementation (>2 days, >3 files, uncertainty)
- Multiple components affected
- Architectural impact
- Unclear or evolving requirements
- Significant risk
- Many dependencies
- Multi-phase work

Document assessment in `plan.md` with rationale.

---

## Ticket Folder Structure

Initialize folder at `tickets/[TICKET_ID]/` with these files:

```
tickets/
  [TICKET_ID]/
    plan.md          # Objectives, approach, acceptance criteria
    context.md       # Technical state, dependencies, next steps
    progress.md      # Session-by-session work log
    references.md    # Static file and conversation references (optional)
```

---

## Plan.md Template

```markdown
# [TICKET_ID]: [Title]

**Ticket**: [TICKET_ID]
**Created**: [Date]
**Status**: 🔄 In Progress

---

## Objective

[Clear statement of what this ticket accomplishes]

## Requirements

### Acceptance Criteria

1. [Specific, testable criterion]
2. [Specific, testable criterion]
3. [Specific, testable criterion]

### Constraints

- [Technical constraint]
- [Business constraint]
- [Timeline constraint]

---

## Complexity Assessment

**Classification**: [Simple Fix | Complex Implementation]

**Rationale**: [Why this classification - reference criteria]

**Estimated Effort**: [X] days/hours

**Risk Level**: [Low | Medium | High]

---

## Implementation Approach

### Strategy

[High-level approach - what pattern/architecture will be used]

### Work Breakdown

#### Phase 1: [Phase Name]
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

#### Phase 2: [Phase Name]
- [ ] Task 1
- [ ] Task 2

### Dependencies

- [Dependency 1]: [Why needed]
- [Dependency 2]: [Why needed]

### Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | [High/Med/Low] | [High/Med/Low] | [How to address] |

---

## Testing Strategy

- [ ] Unit tests for [components]
- [ ] Integration tests for [workflows]
- [ ] Manual testing for [edge cases]

---

## Questions / Unknowns

- [ ] [Question 1 needing resolution]
- [ ] [Question 2 needing research]

---

## Related

- **Jira**: [Link to JIRA ticket]
- **Related Tickets**: [List related tickets]
- **Documentation**: [Links to relevant docs]
```

---

## Context.md Template

```markdown
# [TICKET_ID]: Context

**Last Updated**: [Timestamp]

---

## Current Technical State

### Relevant Components

- **Component 1** (`path/to/component`): [Current state, what exists]
- **Component 2** (`path/to/component`): [Current state, what exists]

### Key Files

- `path/to/file1.cs` - [What this file contains, why relevant]
- `path/to/file2.cs` - [What this file contains, why relevant]

### Architecture Context

[Brief overview of architecture in affected area]

---

## Dependencies

### Internal Dependencies

- [System/Component 1]: [Why needed, what it provides]
- [System/Component 2]: [Why needed, what it provides]

### External Dependencies

- [Library/Service 1]: [Version, purpose]
- [Library/Service 2]: [Version, purpose]

### Integration Points

- [System A] integrates via [mechanism]
- [System B] depends on [interface]

---

## Technical Considerations

### Constraints

- [Performance requirement]
- [Compatibility requirement]
- [Security requirement]

### Patterns to Follow

- [Pattern 1]: [Why applicable]
- [Pattern 2]: [Why applicable]

### Patterns to Avoid

- [Anti-pattern 1]: [Why not applicable]

---

## Current Focus

### Immediate Next Steps

1. [Next action to take]
2. [Following action]
3. [Third action]

### Blockers

- [Blocker 1 if any]: [Impact and resolution plan]

---

## Notes

[Any additional context, discoveries, or considerations]
```

---

## Progress.md Template

```markdown
# [TICKET_ID]: Progress Log

**Ticket**: [TICKET_ID]
**Started**: [Date]

---

## Work Sessions

### [Timestamp] - Ticket Initialized

#### Session Summary
Ticket documentation created, complexity assessed, implementation plan defined.

#### Accomplished
- Ticket folder structure created
- Plan.md with objectives and approach
- Context.md with technical landscape
- Complexity assessment: [Simple Fix | Complex Implementation]
- Work breakdown created with [N] phases

#### Decisions
- **Implementation strategy**: [Chosen approach with rationale]
- **Complexity classification**: [Classification with reasoning]

#### Next Steps
- [First actual implementation task from plan]
- [Second task]
- [Research or clarification needed]
```

---

## Examples (Few-Shot)

### Example 1: Simple Fix Ticket

**Input**:
```xml
<ticket>
  <id>EPP-198</id>
  <summary>Fix memory leak in CacheManager</summary>
</ticket>
<action>start ticket</action>
```

**Reasoning**:
- Single component (CacheManager)
- Clear problem (memory leak)
- Focused change (disposal logic)
- Estimated 1-2 days
→ Classification: Simple Fix

**Expected Output**:
```markdown
## ✅ Ticket Initialized: EPP-198

**Ticket**: EPP-198
**Summary**: Fix memory leak in CacheManager
**Complexity**: Simple Fix

---

### 📁 Folder Structure Created

```
tickets/EPP-198/
  ├── plan.md          ✅ Created
  ├── context.md       ✅ Created
  ├── progress.md      ✅ Created
  └── references.md    ⚠️ Optional (create as needed)
```

---

### 📊 Complexity Assessment

**Classification**: Simple Fix

**Rationale**:
- Single component affected (CacheManager.cs)
- Clear problem scope (memory leak from WeakReference not cleared)
- Focused solution (add explicit Dispose cleanup)
- Low risk (isolated change, comprehensive tests exist)
- Estimated effort: 1-2 days (investigation + fix + testing)

**Estimated Effort**: 1-2 days
**Risk Level**: Low
**Components Affected**: 1 component (CacheManager)

---

### 📋 Implementation Plan

**Strategy**: Identify root cause via memory profiler, implement explicit cleanup in Dispose method, add validation to prevent recurrence.

**Work Breakdown**:

**Phase 1**: Investigation (Day 1)
- Profile memory usage with diagnostics tools
- Identify WeakReference retention points
- Document root cause in RCA

**Phase 2**: Fix Implementation (Day 1-2)
- Add explicit WeakReference.SetTarget(null) in Dispose
- Verify cleanup with memory profiler
- Add unit test for disposal behavior

**Phase 3**: Prevention (Day 2)
- Add CI validation for proper Dispose implementations
- Update code review checklist
- Document WeakReference best practices

**Total Tasks**: 7 tasks across 3 phases

---

### 🔗 Dependencies Identified

**Internal**:
- CacheManager (existing component to modify)

**External**:
- Memory profiler tools (for diagnosis)
- Existing test suite (for regression validation)

---

### ⚠️ Risks & Questions

**Risks**:
- Risk: Fix may not fully resolve leak → Mitigation: Use memory profiler to verify
- Risk: Disposal timing may affect existing code → Mitigation: Comprehensive regression testing

**Questions Needing Resolution**:
- [ ] Are there other WeakReference usages in codebase with similar issue?
- [ ] What memory profiler tools are available for diagnosis?

---

### 🌿 Git Branch Suggestion

```bash
# Create branch
git checkout -b fix/EPP-198-cache-manager-memory-leak develop

# Branch naming
fix/EPP-198-cache-manager-memory-leak
```

---

### ⏭️ Ready to Start

**Next Steps**:
1. Profile current memory usage to identify leak pattern
2. Document root cause findings in tickets/EPP-198/rca.md
3. Implement Dispose cleanup fix

**Start with**:
```xml
<ticket>@EPP-198</ticket> <action>please start with Phase 1: Investigation</action>
```

---

**Files Created**:
- `tickets/EPP-198/plan.md`
- `tickets/EPP-198/context.md`
- `tickets/EPP-198/progress.md`
- `tickets/current.md` (updated)
```

### Example 2: Complex Implementation Ticket

**Input**:
```xml
<ticket>
  <id>EBASE-12345</id>
  <summary>Implement repository pattern for 14 configuration entities across 5 domains</summary>
</ticket>
<action>start ticket</action>
```

**Reasoning**:
- Multiple entities (14 repositories)
- Multiple domains (5: Markets, Products, Profiles, Calendars, Units)
- Pattern implementation (repository + UnitOfWork)
- Multi-phase work (infrastructure, then domains)
- Estimated 5-7 days
→ Classification: Complex Implementation

**Expected Output**:
```markdown
## ✅ Ticket Initialized: EBASE-12345

**Ticket**: EBASE-12345
**Summary**: Implement repository pattern for 14 configuration entities across 5 domains
**Complexity**: Complex Implementation

---

### 📁 Folder Structure Created

```
tickets/EBASE-12345/
  ├── plan.md          ✅ Created
  ├── context.md       ✅ Created
  ├── progress.md      ✅ Created
  ├── tracker.md       ✅ Created (for systematic work tracking)
  └── references.md    ⚠️ Optional (create as needed)
```

---

### 📊 Complexity Assessment

**Classification**: Complex Implementation

**Rationale**:
- Multiple entities: 14 repositories across 5 domains (Markets, Products, Profiles, Calendars, Units)
- Architectural pattern: Implementing repository pattern + UnitOfWork integration
- Multi-phase work: Infrastructure setup, then domain-by-domain implementation
- Medium risk: Affects data access layer, requires careful transaction management
- Estimated effort: 5-7 days (infrastructure + 14 repositories + testing)

**Estimated Effort**: 5-7 days
**Risk Level**: Medium
**Components Affected**: 14 entities, 5 domains, UnitOfWork pattern, data access layer

---

### 📋 Implementation Plan

**Strategy**: Implement generic repository base classes and UnitOfWork pattern first, then systematically create concrete repositories for each domain. Use Dapper for data access with async throughout.

**Work Breakdown**:

**Phase 1**: Core Infrastructure (Day 1-2)
- [ ] Create IRepository<T> interface
- [ ] Implement RepositoryBase<T> with Dapper
- [ ] Create IUnitOfWork interface
- [ ] Implement UnitOfWork with transaction management
- [ ] Create entity mappers (domain ↔ database)
- [ ] Unit tests for base infrastructure

**Phase 2**: Markets Domain (Day 3)
- [ ] Country repository
- [ ] Market repository
- [ ] GridPointType repository
- [ ] MarketParty repository
- [ ] MarketRole repository
- [ ] UnitOfWork implementation for Markets

**Phase 3**: Products Domain (Day 4)
- [ ] MeterProduct repository
- [ ] MeterPictogram repository
- [ ] PhysicalProduct repository
- [ ] UnitOfWork implementation for Products

**Phase 4**: Profiles Domain (Day 4-5)
- [ ] Profile repository
- [ ] ProfileClass repository
- [ ] UnitOfWork implementation for Profiles

**Phase 5**: Calendars Domain (Day 5-6)
- [ ] Calendar repository
- [ ] CalendarEntry repository
- [ ] CalendarDate repository
- [ ] UnitOfWork implementation for Calendars

**Phase 6**: Units Domain (Day 6)
- [ ] MeasurementUnit repository
- [ ] UnitOfWork implementation for Units

**Phase 7**: Testing & Integration (Day 6-7)
- [ ] Integration tests for each repository
- [ ] Transaction rollback testing
- [ ] Performance validation
- [ ] Documentation updates

**Total Tasks**: 35+ tasks across 7 phases

---

### 🔗 Dependencies Identified

**Internal**:
- Domain entities (existing models for 14 configuration tables)
- Database schema (configuration tables in MSSQL)
- Connection management (existing ADO.NET infrastructure)

**External**:
- Dapper (ORM for data access) - current version
- System.Data.SqlClient (MSSQL provider)

---

### ⚠️ Risks & Mitigations

**Risks**:
- **Risk**: Transaction management complexity → **Mitigation**: Comprehensive UnitOfWork tests with rollback scenarios
- **Risk**: Performance impact from N+1 queries → **Mitigation**: Use Dapper multi-mapping, validate with profiler
- **Risk**: Breaking existing data access code → **Mitigation**: Incremental rollout, maintain backward compatibility initially

**Questions Needing Resolution**:
- [ ] Should we support both sync and async operations or async-only?
- [ ] What's the transaction isolation level requirement?
- [ ] Are there existing conventions for entity mapping?

---

### 🌿 Git Branch Suggestion

```bash
# Create branch
git checkout -b feature/EBASE-12345-repository-pattern-config-entities develop

# Branch naming
feature/EBASE-12345-repository-pattern-config-entities
```

---

### ⏭️ Ready to Start

**Next Steps**:
1. Create core repository interfaces (IRepository<T>, IUnitOfWork)
2. Implement RepositoryBase<T> with Dapper
3. Create first concrete repository (Country) as pattern

**Start with**:
```xml
<ticket>@EBASE-12345</ticket> <action>please start with Phase 1: Core Infrastructure</action>
```

**Tracking Strategy**: Use tracker.md for systematic progress across 14 repositories

---

**Files Created**:
- `tickets/EBASE-12345/plan.md`
- `tickets/EBASE-12345/context.md`
- `tickets/EBASE-12345/progress.md`
- `tickets/EBASE-12345/tracker.md` (for systematic work)
- `tickets/current.md` (updated)
```

---

## Output Format

When starting a ticket, AI must respond with:

```markdown
## ✅ Ticket Initialized: [TICKET-ID]

**Ticket**: [TICKET-ID]
**Summary**: [Brief summary]
**Complexity**: [Simple Fix | Complex Implementation]

---

### 📁 Folder Structure Created

```
tickets/[TICKET-ID]/
  ├── plan.md          ✅ Created
  ├── context.md       ✅ Created
  ├── progress.md      ✅ Created
  └── [tracker.md]     ✅ Created (if Complex Implementation)
```

---

### 📊 Complexity Assessment

**Classification**: [Simple Fix | Complex Implementation]

**Rationale**: [Detailed reasoning based on criteria]

**Estimated Effort**: [X days/hours]
**Risk Level**: [Low | Medium | High]
**Components Affected**: [N components]

---

### 📋 Implementation Plan

**Strategy**: [High-level approach]

**Work Breakdown**:

**Phase 1**: [Phase name]
- Task 1
- Task 2

[More phases...]

**Total Tasks**: [N tasks across M phases]

---

### 🔗 Dependencies Identified

**Internal**: [List]
**External**: [List]

---

### ⚠️ Risks & Questions

**Risks**: [List with mitigations]
**Questions Needing Resolution**: [List]

---

### 🌿 Git Branch Suggestion

```bash
git checkout -b [type]/[TICKET-ID]-[description] [base-branch]
```

---

### ⏭️ Ready to Start

**Next Steps**: [List first 3 actions]

**Start with**: [Command to begin work]

---

**Files Created**: [List of generated files]
```

---

## Quality Criteria

Before marking ticket initialization complete:

- [ ] Ticket folder created with all required files
- [ ] Plan.md includes objectives, acceptance criteria, work breakdown
- [ ] Complexity assessment done with rationale
- [ ] Context.md documents relevant components and dependencies
- [ ] Progress.md initialized with first entry
- [ ] Current.md updated to reflect active ticket
- [ ] Implementation strategy defined and clear
- [ ] Risks identified with mitigation plans
- [ ] Questions surfaced for resolution
- [ ] Git branch naming follows conventions (if applicable)
- [ ] Estimated effort is reasonable based on complexity
- [ ] Tracker.md created if Complex Implementation with many tasks

---

## Anti-Patterns

### ❌ DON'T: Skip complexity assessment
```markdown
# Plan
Let's implement this feature.
[No complexity assessment]
```
**Why bad**: Can't determine appropriate implementation strategy, effort estimation, or risk level

✅ **DO: Assess and document complexity**
```markdown
## Complexity Assessment
**Classification**: Complex Implementation
**Rationale**: Affects 14 entities across 5 domains, requires UnitOfWork pattern integration, estimated 5-7 days work
```

### ❌ DON'T: Vague work breakdown
```markdown
## Tasks
- Implement feature
- Test it
- Done
```
**Why bad**: No actionable tasks, no milestones, no way to track progress

✅ **DO: Specific, phased breakdown**
```markdown
## Work Breakdown

### Phase 1: Core Infrastructure (Day 1-2)
- [ ] Create repository base classes
- [ ] Implement UnitOfWork pattern
- [ ] Create entity mappers

### Phase 2: Domain Repositories (Day 3-5)
- [ ] Markets domain (5 repositories)
- [ ] Products domain (3 repositories)
...
```

### ❌ DON'T: Generic context
```markdown
## Context
This ticket is about adding repositories.
[No technical detail]
```
**Why bad**: Future developers have no context, can't resume work effectively

✅ **DO: Detailed technical context**
```markdown
## Current Technical State

### Relevant Components
- **Data Access Layer** (`src/DataAccess/`): Currently uses ADO.NET directly
- **Domain Entities** (`src/Domain/Configuration/`): 14 entities need repositories
- **Connection Management** (`src/Infrastructure/Database/`): Existing connection pooling

### Architecture Context
Currently using direct ADO.NET calls scattered across service layer. Implementing repository pattern to centralize data access, enable unit testing with mocks, and prepare for future ORM migration.
```

---

## Usage

**Start new ticket**:
```xml
<ticket>
  <id>EPP-192</id>
  <summary>Implement unit test coverage for Calendar domain</summary>
</ticket>
<action>start ticket</action>
```

**Start with detailed requirements**:
```xml
<ticket>
  <id>EBASE-12345</id>
  <summary>Implement repository pattern for configuration tables</summary>
  <requirements>
    14 entities across 5 domains need repositories:
    - Markets: Country, Market, GridPointType, MarketParty, MarketRole
    - Products: MeterProduct, MeterPictogram, PhysicalProduct
    - Profiles: Profile, ProfileClass
    - Calendars: Calendar, CalendarEntry, CalendarDate
    - Units: MeasurementUnit
  </requirements>
</ticket>
<action>start ticket</action>
```

---

## Related Prompts

- `ticket/activate-ticket.prompt.md` - Resume work on existing ticket
- `ticket/update-progress.prompt.md` - Document session progress
- `ticket/check-status.prompt.md` - Review ticket status
- `ticket/close-ticket.prompt.md` - Complete and close ticket
- `ticket/catchup-on-ticket.prompt.md` - Catch up on ticket history

---

## Related Rules

Follows workflow from:
- `.cursor/rules/ticket/ticket-workflow-rule.mdc` - Overall ticket workflow
- `.cursor/rules/ticket/complexity-assessment-rule.mdc` - Complexity classification criteria
- `.cursor/rules/ticket/plan-rule.mdc` - Plan documentation standards
- `.cursor/rules/ticket/context-rule.mdc` - Context documentation standards
- `.cursor/rules/git/branch-naming-rule.mdc` - Branch naming conventions

---

**Pattern**: Ticket Initialization Pattern
**Use When**: Starting any new ticket
**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
