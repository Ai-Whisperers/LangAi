---
name: create-jira-recap
description: "Generate a JIRA-ready recap summary for a completed ticket"
category: ticket
tags: ticket, recap, jira, summary, multi-repo
argument-hint: "Ticket ID (e.g., EBASE-12259)"
---

# Create JIRA Ticket Recap

Generate a JIRA-ready recap summary for a completed ticket that can be pasted directly into JIRA comments or resolution field.

**Pattern**: JIRA Recap Generation Pattern ⭐⭐⭐⭐
**Effectiveness**: Essential for JIRA status reporting and ticket closure
**Use When**: Closing tickets in JIRA, generating status reports, documenting outcomes for external tracking

---

## Purpose

This prompt generates professional, JIRA-ready recap summaries that:
- Aggregate work across multiple repositories
- Focus on outcomes and delivered value
- Comply with OPSEC standards (no internal paths, credentials, sensitive info)
- Provide quantifiable metrics
- Are scannable and concise for stakeholders

Use this when you need to update JIRA with completed work or close JIRA tickets with proper documentation.

---

## Required Context

- **Ticket ID**: JIRA ticket identifier (e.g., EBASE-12259, EPP-192)
- **Workspace**: Full workspace with all repos (eneve.ebase.foundation, eneve.domain, eneve.ebase.datamigrator, etc.)
- **Completion State**: Work must be complete (recap.md files should exist in relevant repos)

---

## Multi-Repo Awareness

**CRITICAL**: Tickets may span multiple repositories. Always:

1. **Search the entire workspace** for the ticket ID across all repos
2. **Check each repo** for ticket folders: `tickets/**/[TICKET_ID]/`
3. **Identify where work was actually done** (presence of progress.md, context.md, recap.md indicates work)
4. **Create per-repo recaps** if work occurred in multiple repos (save as recap.md in each)
5. **Aggregate for JIRA** - single JIRA recap summarizing all repo work

### Indicators of Work Done in a Repo

**Strong Indicators (High Confidence):**
- `recap.md` already exists → Work completed
- Code changes (grep for ticket ID in commits) → Work was done
- README changes, .csproj changes for documentation tickets
- `GenerateDocumentationFile` enabled in projects
- Concrete deliverables (files created, configs changed, docs written)

**Weak Indicators (Verify with Evidence):**
- `progress.md` exists with entries → Suggests activity, but verify actual deliverables
- `context.md` exists with content → Suggests active work, but verify completion
- `references.md` exists → Suggests research/planning, but doesn't guarantee implementation
- `plan.md` only → May be just a plan copy, verify with other files

**Verification Required:**
- Presence of ticket folder files indicates *planning* or *activity*, NOT completion
- Always verify with actual code/documentation changes in the repo
- Check for concrete deliverables before claiming work done in that repo

---

## Process

Follow these steps to create a JIRA recap:

### Step 1: Verify Ticket Completion
Ensure work is complete across all repos (recap.md files exist, all acceptance criteria met).

### Step 2: Formulate Recap Request
Use pattern with XML delimiters:
```
<ticket>@[TICKET-ID]</ticket> <action>create jira recap</action> <scope>entire workspace</scope>
```

### Step 3: AI Searches Entire Workspace
AI will search all repos for ticket references and evidence of completed work.

### Step 4: Review Generated Recaps
Check both:
- Per-repo recap.md files (saved in each repo's ticket folder)
- Aggregated JIRA recap (for pasting into JIRA)

### Step 5: Paste into JIRA
Copy aggregated recap into JIRA comment or resolution field, update ticket status.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Search Entire Workspace**: Find ticket references across ALL repos (grep, file search)
2. **Identify Repos with Work**: Distinguish planned vs. completed work using strong/weak indicators
3. **Locate Evidence**: Find ticket details in roadmap.md or ticket documentation per repo
4. **Extract Accomplishments**: What was actually delivered in each repo (specific deliverables)
5. **Identify Key Metrics**: Files created/modified, tests passing, coverage achieved, documentation lines
6. **Summarize Value**: Business and technical impact across all repos
7. **Format for JIRA**: Clean, professional, OPSEC-compliant format suitable for pasting
8. **Generate Per-Repo Recaps**: Create recap.md in each repo's ticket folder where work was done
9. **Generate Aggregated Recap**: Single JIRA-ready summary covering all repo work

---

## Search Strategy

```
1. Search all repos: grep -r "[TICKET_ID]" across workspace
2. Check ticket folders in each repo:
   - eneve.ebase.foundation/tickets/**/[TICKET_ID]/
   - eneve.domain/tickets/**/[TICKET_ID]/
   - eneve.ebase.datamigrator/tickets/**/[TICKET_ID]/
3. Review roadmap.md files for completion status
4. Check for code changes associated with ticket (git log, grep)
5. Verify deliverables exist (README changes, .csproj mods, new files)
```

---

## Basic Usage

```
<ticket>@[TICKET-ID]</ticket> <action>create jira recap</action> <scope>entire workspace</scope>
```

**Placeholder Conventions**:
- `[TICKET-ID]` - Full JIRA ticket ID (e.g., EBASE-12259, EPP-192, EBASE-13017)

---

## Output Format

### Per-Repo Recaps (save as recap.md in each repo's ticket folder)

```markdown
# Recap: [TICKET-ID] - [Title]

**Story ID:** [TICKET-ID]
**Feature:** [Parent feature if applicable]
**Epic:** [Parent epic if applicable]
**Repo:** [Repository name]
**Status:** ✅ Complete
**Completed:** [Date]

---

## Summary
[2-3 sentence repo-specific outcome]

## What Was Accomplished
- [Repo-specific deliverable 1]
- [Repo-specific deliverable 2]
- [Repo-specific deliverable 3]

## Metrics
- [Repo-specific metrics: files, lines, coverage, etc.]

## Status
✅ Complete - [Date]
```

### Aggregated JIRA Recap (for pasting into JIRA)

```
## Summary
[2-3 sentence high-level outcome covering ALL repos]

## Work by Repository

### [Repo 1 Name]
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

### [Repo 2 Name]
- [Deliverable 1]
- [Deliverable 2]

## Technical Details
- [Key technical achievement 1]
- [Key technical achievement 2]

## Metrics (if applicable)
- [Repo 1]: [count and types]
- [Repo 2]: [count and types]

## Status
✅ Complete - [Completion date]
```

---

## Examples (Few-Shot)

### Example 1: Multi-Repo Documentation Ticket

**Input**:
```
<ticket>@EBASE-13017</ticket> <action>create jira recap</action> <scope>entire workspace</scope>
```

**Reasoning**:
AI searches entire workspace for EBASE-13017, finds ticket folders in eneve.domain, eneve.ebase.foundation, and eneve.ebase.datamigrator. Identifies strong indicators (recap.md exists, README changes, .csproj GenerateDocumentationFile enabled) in all three repos. Aggregates accomplishments across repos.

**Expected Output**:

**Per-Repo Recaps Created**:
- `eneve.domain/tickets/EBASE-13017/recap.md`
- `eneve.ebase.foundation/tickets/EBASE-13017/recap.md`
- `eneve.ebase.datamigrator/tickets/EBASE-13017/recap.md`

**Aggregated JIRA Recap (for pasting)**:
```
## Summary
Delivered comprehensive XML documentation and README improvements across 3 repositories: Domain packages (Eneve.Domain), Foundation packages (Eneve.eBase.Foundation), and CLI tool (Eneve.eBase.DataMigrator). Enabled XML documentation generation, created detailed READMEs, and configured DocFX for API reference generation.

## Work by Repository

### Eneve.Domain
- XML documentation enabled for 3 projects (.csproj GenerateDocumentationFile)
- README expanded from 127 to 600+ lines
- 10 source files with complete XML docs
- Private/protected members documented (100% coverage)
- NuGet package documentation enhanced

### Eneve.eBase.Foundation
- XML documentation for 63+ files (100% public API coverage)
- Architecture documentation (800+ lines)
- Usage examples and getting started guide (960+ lines)
- DocFX configuration for API reference generation
- Cross-reference documentation between packages

### Eneve.eBase.DataMigrator
- XML documentation enabled for 8 projects
- Root README (308 lines) with CLI command documentation
- Individual project READMEs for shared libraries
- Architecture diagram with Mermaid
- Configuration guide for multi-environment deployment

## Technical Details
- Comprehensive XML comments following .NET conventions
- DocFX integration for automated API documentation
- Mermaid diagrams for architecture visualization
- Cross-repository documentation references
- NuGet package metadata updates

## Metrics
- Domain: 3 projects, 10 files documented, 600+ README lines
- Foundation: 63+ files, 100% public API coverage, 1700+ doc lines
- DataMigrator: 8 projects, 308 README lines, architecture diagrams

## Status
✅ Complete - 2025-11-25
```

### Example 2: Single-Repo Implementation Ticket

**Input**:
```
<ticket>@EBASE-12259</ticket> <action>create jira recap</action> <scope>entire workspace</scope>
```

**Reasoning**:
AI searches workspace, finds ticket only in eneve.ebase.foundation with strong indicators (recap.md exists, code changes, tests passing). Single-repo work, so simplified format.

**Expected Output**:

**Per-Repo Recap Created**:
- `eneve.ebase.foundation/tickets/EBASE-12259/recap.md`

**Aggregated JIRA Recap (for pasting)**:
```
## Summary
Implemented concrete repositories for 14 configuration tables with full CRUD operations, transaction support via UnitOfWork pattern, and async capabilities throughout. Covered 5 domain areas: Markets, Products, Profiles, Calendars, and Units.

## What Was Accomplished
- 14 concrete repository implementations with Dapper-based data access
- Bidirectional entity mappers for all domain objects
- Transaction support via UnitOfWork pattern (5 implementations)
- Async operations throughout (no synchronous blocking)
- Comprehensive unit tests for repository operations

## Technical Details

**Markets Domain (5 repositories)**:
- Country, Market, GridPointType, MarketParty, MarketRole

**Products Domain (3 repositories)**:
- MeterProduct, MeterPictogram, PhysicalProduct

**Profiles Domain (2 repositories)**:
- Profile, ProfileClass

**Calendars Domain (3 repositories)**:
- Calendar, CalendarEntry, CalendarDate

**Units Domain (1 repository)**:
- MeasurementUnit

## Metrics
- 14 repository classes implemented
- 5 UnitOfWork implementations
- 14 bidirectional entity mappers
- Dapper-based data access with async/await throughout

## Status
✅ Complete - 2025-11-22
```

### Example 3: Multi-Repo with Partial Work (Edge Case)

**Input**:
```
<ticket>@EBASE-12346</ticket> <action>create jira recap</action> <scope>entire workspace</scope>
```

**Reasoning**:
AI searches workspace, finds ticket folders in eneve.domain and eneve.ebase.foundation. However, eneve.domain only has plan.md (weak indicator), while eneve.ebase.foundation has recap.md and code changes (strong indicators). AI correctly identifies only foundation has completed work.

**Expected Output**:

**Analysis Report**:
```markdown
## Workspace Search Results: EBASE-12346

**Ticket folders found**:
1. eneve.domain/tickets/EBASE-12346/ (WEAK indicators only - plan.md exists, no deliverables)
2. eneve.ebase.foundation/tickets/EBASE-12346/ (STRONG indicators - recap.md, code changes, tests)

**Work completed in**: eneve.ebase.foundation only

**Note**: eneve.domain ticket folder appears to be planning only. No concrete deliverables found.
```

**Per-Repo Recap Created**:
- `eneve.ebase.foundation/tickets/EBASE-12346/recap.md` (only)

**Aggregated JIRA Recap**:
```
## Summary
Implemented validation framework in Foundation library with rule-based validation, fluent API, and async support.

## Work by Repository

### Eneve.eBase.Foundation
- Validation framework with 12 built-in validators
- Fluent API for composable validation rules
- Async validation support for database checks
- Comprehensive unit tests (95% coverage)

## Technical Details
- ValidationRule base class with chainable syntax
- Built-in validators: Required, Range, Email, Phone, etc.
- Custom validator support via IValidator interface
- Integration with existing entity mappers

## Metrics
- Foundation: 12 validators, 95% test coverage, async throughout

## Status
✅ Complete - 2025-12-05
```

---

## JIRA Formatting Notes

- Use markdown that JIRA accepts (headers with ##, bullets with -, bold with **)
- Keep it concise - JIRA comments should be scannable (aim for < 50 lines)
- No internal paths, sensitive info, or OPSEC violations
- Focus on outcomes and delivered value, not process details
- Include date of completion if available from ticket metadata
- **Show work breakdown by repo** for multi-repo tickets (critical for traceability)
- Use quantifiable metrics (files, lines, tests, coverage, not vague "some/many")

---

## Quality Criteria

Before marking JIRA recap complete:

- [ ] All repos with work identified and included (strong indicators verified)
- [ ] Repos with only weak indicators excluded or noted as "planning only"
- [ ] Work breakdown by repository clear and specific
- [ ] Metrics quantify accomplishments (files, lines, tests, coverage)
- [ ] Technical details specific and verifiable
- [ ] Business value communicated (not just technical implementation details)
- [ ] Format is JIRA-compatible (markdown JIRA supports: ##, -, **)
- [ ] No OPSEC violations (internal paths, credentials, emails, sensitive URLs)
- [ ] Concise and scannable (target < 50 lines for JIRA comment)
- [ ] Completion date included
- [ ] Per-repo recaps saved in respective repo ticket folders

---

## Anti-Patterns

### ❌ DON'T: Include internal paths or OPSEC violations

```markdown
## Work Completed
- Modified E:\WPG\Git\E21\GitRepos\eneve.domain\src\file.cs
- Credential: john.doe@company.com updated configs
- Internal URL: http://internal-server.local/docs
- Developer machine: DEV-WORKSTATION-01
```

**Why bad**: OPSEC violation, exposes internal structure, credentials, developer info

✅ **DO: Generic, safe descriptions**

```markdown
## Work Completed
- Modified Domain entity classes for improved validation
- Updated configuration handling for multi-environment support
- Enhanced documentation with architecture diagrams
```

### ❌ DON'T: Vague metrics

```markdown
## Metrics
- Some files updated
- Tests added
- Documentation improved
```

**Why bad**: Not quantifiable, no sense of scope or effort

✅ **DO: Specific, quantifiable metrics**

```markdown
## Metrics
- Domain: 3 projects, 10 classes, 600+ README lines
- Foundation: 63+ files, 100% public API coverage, 1700+ doc lines
- DataMigrator: 8 projects, 308 README lines, architecture diagrams
```

### ❌ DON'T: Single-repo format for multi-repo work

```markdown
## Summary
Added documentation to the codebase.

## What Was Accomplished
- Updated files
- Added docs
[No repo breakdown]
```

**Why bad**: Obscures scope, no traceability per repo, loses context

✅ **DO: Multi-repo breakdown**

```markdown
## Summary
Delivered comprehensive documentation across 3 repositories.

## Work by Repository

### Eneve.Domain
- XML documentation for 10 files
- README expanded to 600+ lines

### Eneve.eBase.Foundation
- XML documentation for 63+ files
- Architecture guide (800+ lines)

### Eneve.eBase.DataMigrator
- CLI documentation (308 lines)
- Architecture diagrams
```

### ❌ DON'T: Process details in JIRA recap

```markdown
## Work Completed
- Had 3 debugging sessions
- Tried approach A, then approach B
- Rewrote code 2 times
- Had discussion with team about design
- Spent time researching best practices
```

**Why bad**: JIRA recap focuses on outcomes delivered, not development process

✅ **DO: Outcomes and value delivered**

```markdown
## Work Completed
- Implemented repository pattern for 14 entities
- Achieved 100% async operation coverage
- Integrated transaction support via UnitOfWork
- Delivered full CRUD operations with error handling
```

### ❌ DON'T: Claim work without strong indicators

```markdown
## Work by Repository

### Eneve.Domain
- Implemented feature X
[But only plan.md exists, no code changes found]
```

**Why bad**: Inaccurate, misleading stakeholders

✅ **DO: Verify strong indicators before claiming**

```markdown
## Work by Repository

### Eneve.eBase.Foundation
- Implemented feature X (verified: code changes, tests passing, recap.md exists)

**Note**: Eneve.Domain ticket folder found but appears to be planning only (no deliverables).
```

---

## Related Prompts

- `ticket/validate-completion.prompt.md` - Validate before marking done
- `ticket/check-status.prompt.md` - Review current ticket status across repos
- `ticket/close-ticket.prompt.md` - Close ticket (includes recap generation)
- `ticket/catchup-on-ticket.prompt.md` - Understand ticket history for recap context

---

## Related Rules

- `.cursor/rules/ticket/recap-rule.mdc` - Recap documentation standards
- `.cursor/rules/ticket/ticket-workflow-rule.mdc` - Overall workflow standards
- `.cursor/rules/ticket/validation-before-completion-rule.mdc` - Validation before closure

**OPSEC**: No internal paths, credentials, emails, or sensitive URLs in output. All generated recaps must be safe for external JIRA systems.

---

**Pattern**: JIRA Recap Generation Pattern
**Use When**: Closing tickets, generating status reports for JIRA, documenting outcomes
**Critical**: Multi-repo awareness - scan entire workspace, verify strong indicators
**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
