---
name: validate-completion
description: "Please validate that a ticket is truly complete and ready to close"
category: ticket
tags: ticket, validation, completion, quality-check, done, discipline
argument-hint: "Ticket ID or 'current ticket'"
---

# Validate Ticket Completion

Please perform comprehensive validation to determine if a ticket is truly complete and ready to close.

**Pattern**: Completion Validation Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Critical quality gate - prevents premature "done" claims
**Use When**: Before claiming any ticket complete, before closing tickets

---

## Purpose

This prompt enforces completion discipline by:
- Systematically verifying all acceptance criteria met
- Checking code quality and testing standards
- Validating documentation completeness
- Ensuring no regressions or breaking changes
- Preventing premature "done" claims
- Acting as quality gate before closure

Use this before claiming any ticket complete or marking it ready to close.

---

## Required Context

```xml
<ticket>
  <id>[TICKET_ID]</id>
</ticket>
```

**Placeholder Conventions**:
- `[TICKET_ID]` - Ticket identifier (e.g., EPP-192, EBASE-12345) or "current ticket"

---

## Process

Follow these steps to validate ticket completion:

### Step 1: Identify Ticket to Validate
Determine which ticket to validate (current or specific ticket ID).

### Step 2: Formulate Validation Request
Use pattern with XML delimiters:
```xml
<ticket>
  <id>[TICKET_ID]</id>
</ticket>
<action>validate completion</action>
```

Or for current ticket:
```xml
<action>validate completion for current ticket</action>
```

### Step 3: Review Validation Report
AI will perform comprehensive 10-category validation and provide detailed report with evidence.

### Step 4: Address Issues (if any)
If validation fails:
- Fix blockers first (must be resolved)
- Address must-fix items (should be resolved)
- Consider nice-to-have items (can be follow-up tickets)

### Step 5: Re-Validate After Fixes
Run validation again after addressing issues.

### Step 6: Proceed to Closure (if validated)
Only after validation passes, proceed with close-ticket.

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Load Ticket Context**: Read plan.md (acceptance criteria), progress.md (what was done), context.md (current state)
2. **Verify Requirements**: Check each acceptance criterion against actual deliverables with evidence
3. **Assess Quality**: Review code, tests, documentation against standards (10 categories)
4. **Check for Gaps**: Look for incomplete work, missing tests, undocumented decisions
5. **Evaluate Readiness**: Can this be closed without follow-up work? (honest assessment)
6. **Surface Issues**: Identify and categorize by severity (BLOCKER/MUST-FIX/NICE-TO-HAVE)
7. **Generate Report**: Provide comprehensive validation report with evidence and recommendation
8. **Act as Responsible Colleague**: Would you confidently hand this to another developer saying "it's done"? If not, flag issues.

---

## Validation Categories (10 Total)

### Category 1: Requirements Met ✅❌

- [ ] **All acceptance criteria satisfied**: Each criterion from plan.md verified with evidence
- [ ] **Original problem fully solved**: Root cause addressed, not just symptoms
- [ ] **No scope creep**: Ticket scope respected, additional work ticketed separately
- [ ] **All edge cases handled**: Boundary conditions, null cases, error paths covered

**Evidence Required**: Specific code references, test coverage, manual verification

---

### Category 2: Code Quality ✅❌

- [ ] **Clean code principles followed**: Readable, maintainable, follows DRY/SOLID
- [ ] **No code smells**: No long methods (>50 lines), god classes, duplicated code
- [ ] **Error handling comprehensive**: Try-catch where appropriate, meaningful error messages
- [ ] **Performance considerations addressed**: No obvious performance issues introduced
- [ ] **Naming conventions**: Descriptive names, consistent style

**Evidence Required**: Code review, static analysis, linting passes

---

### Category 3: Testing ✅❌

- [ ] **Unit tests written and passing**: All new code has unit test coverage
- [ ] **Integration tests (if applicable)**: Cross-component interactions tested
- [ ] **Manual testing completed**: Actual usage verified
- [ ] **Edge cases tested**: Boundary conditions, null inputs, error scenarios
- [ ] **Regression tests**: Existing functionality still works
- [ ] **Test coverage meets standards**: Percentage meets project requirements

**Evidence Required**: Test execution results, coverage reports

---

### Category 4: Documentation ✅❌

- [ ] **XML documentation complete**: All public APIs documented
- [ ] **Code comments for complex logic**: Non-obvious code explained
- [ ] **README or docs updated**: If public-facing changes made
- [ ] **API changes documented**: Breaking changes, new endpoints, deprecated features
- [ ] **Architecture decisions recorded**: Significant design choices documented

**Evidence Required**: Generated documentation, doc files reviewed

---

### Category 5: Ticket Documentation ✅❌

- [ ] **progress.md up to date**: Final session documented
- [ ] **context.md reflects final state**: Current technical state accurate
- [ ] **All decisions documented**: Why choices were made
- [ ] **Timeline recorded (if applicable)**: Work sessions captured

**Evidence Required**: Review ticket documentation files

---

### Category 6: No Regressions ✅❌

- [ ] **Existing tests still passing**: No broken tests
- [ ] **No breaking changes to APIs**: Backward compatibility maintained
- [ ] **No unintended side effects**: Changes isolated to intended scope
- [ ] **Dependencies still compatible**: No version conflicts

**Evidence Required**: Full test suite execution, integration tests

---

### Category 7: Code Review Ready ✅❌

- [ ] **No debug code left behind**: Console.WriteLine, debug flags removed
- [ ] **No commented-out code**: Dead code removed
- [ ] **No TODOs or FIXMEs without tickets**: All TODOs either resolved or ticketed
- [ ] **Formatting and style consistent**: Follows project conventions
- [ ] **No OPSEC violations**: No secrets, credentials, internal paths exposed

**Evidence Required**: Code scan, manual review

---

### Category 8: Integration Points ✅❌

- [ ] **Dependencies updated if needed**: NuGet packages, library versions
- [ ] **Integration tests passing**: Cross-system interactions work
- [ ] **Database migrations (if applicable)**: Schema changes applied and tested
- [ ] **Configuration changes documented**: New settings, environment vars

**Evidence Required**: Integration test results, deployment checklist

---

### Category 9: Build & Deployment ✅❌

- [ ] **Solution builds successfully**: No compilation errors
- [ ] **No compiler warnings introduced**: Warning count not increased
- [ ] **Deployment considerations addressed**: Scripts updated, deployment docs reviewed
- [ ] **Environment-specific configs handled**: Dev, staging, prod configurations

**Evidence Required**: Build logs, deployment dry-run

---

### Category 10: Git Status ✅❌

- [ ] **All changes committed**: Working directory clean
- [ ] **Commit messages follow standards**: Clear, conventional commit format
- [ ] **Branch is clean and up to date**: Rebased/merged with target branch
- [ ] **Ready to merge**: No conflicts, CI passing

**Evidence Required**: Git status, branch comparison

---

## Issue Severity Levels

For each failing criterion, categorize:

- **🔴 BLOCKER**: Must be fixed before closing (prevents functionality, breaks contracts, high risk)
- **🟡 MUST-FIX**: Should be fixed before closing (quality/maintainability issue, moderate risk)
- **🟢 NICE-TO-HAVE**: Can be addressed in follow-up (minor improvements, low risk)

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/ticket/ticket-closure-exemplar.md`

## Output Format

```markdown
## [✅ | ❌] Validation Report: [TICKET-ID]

**Ticket**: [TICKET-ID] - [Title]
**Status**: [✅ READY TO CLOSE | ❌ NOT READY TO CLOSE]
**Validation Date**: [Date]

---

### Validation Summary

**Overall**: [✅ PASS | ❌ FAIL] ([X]/10 categories passing)
**Blockers**: [N] 🔴
**Must-Fix**: [N] 🟡
**Nice-to-Have**: [N] 🟢

---

### Category Results

[For each of 10 categories: ✅ PASS or ❌ FAIL with specific details and evidence]

---

### Issues Found (if any)

#### 🔴 BLOCKERS (Must Fix Before Closing)
[List with impact, issue description, fix description, estimated time, files affected]

#### 🟡 MUST-FIX (Should Fix Before Closing)
[List with impact, issue description, fix description, estimated time, files affected]

#### 🟢 NICE-TO-HAVE (Can Address in Follow-up)
[List with follow-up recommendation, not blocking]

---

### [✅ | ❌] RECOMMENDATION

[READY TO CLOSE | NOT READY TO CLOSE]

[If not ready:]
**Estimated Remaining Work**: [X hours]
**Priority Fix Order**: [Numbered list]

**Next Steps**: [What to do next]
```

---

## Quality Criteria

For the validation itself to be complete:

- [ ] All 10 categories evaluated systematically
- [ ] Each criterion has clear pass/fail status
- [ ] Evidence cited for each category (not just opinion)
- [ ] Issues categorized by severity (Blocker/Must-Fix/Nice-to-Have)
- [ ] Estimated fix time provided for issues (realistic)
- [ ] Clear recommendation (Ready or Not Ready to close)
- [ ] Next steps provided with priority order
- [ ] No false positives (claiming pass when criteria not met)
- [ ] No false negatives (claiming fail for actually met criteria)
- [ ] Honest assessment (act as responsible colleague)

---

## Anti-Patterns

### ❌ DON'T: Claim complete with known issues
```markdown
Status: Ready to close
(But 2 repositories missing, no edge case tests)
```
**Why bad**: Premature completion creates technical debt, misleads stakeholders, damages trust

✅ **DO: Honest assessment with remaining work**
```markdown
Status: NOT ready to close
Blockers: 2 repositories missing (CalendarEntry, CalendarDate)
Blockers: Edge case tests needed (null IDs, concurrent access)
Estimated work: 3 hours
```

### ❌ DON'T: Vague validation
```markdown
Looks good, ready to close.
[No details, no evidence]
```
**Why bad**: No evidence of systematic check, can't catch real issues

✅ **DO: Systematic validation with evidence**
```markdown
Category 1: Requirements Met ✅ PASS
- ✅ All 14 repositories implemented
- ✅ UnitOfWork pattern integrated
Evidence: Code review shows all files present, functional tests passing
```

### ❌ DON'T: Ignore objective blockers
```markdown
2 repositories missing, but good enough to close
```
**Why bad**: Acceptance criteria explicitly not met, unprofessional

✅ **DO: Respect acceptance criteria**
```markdown
2 repositories missing → BLOCKER
Acceptance criteria requires 14, only 12 present
NOT READY TO CLOSE until all 14 implemented
```

---

## Critical Rules

**🚫 DO NOT claim completion if**:
- Any acceptance criteria unmet (even one)
- Blockers exist (high-risk issues)
- Tests failing (any test failures)
- Documentation incomplete (required docs missing)
- Code quality issues present (linting errors, code smells)

**✅ Act as responsible colleague**:
If you wouldn't feel confident handing this to another developer saying "it's done", it's NOT done. Be honest about remaining work.

---

## Usage

**Validate current ticket**:
```xml
<action>validate completion for current ticket</action>
```

**Validate specific ticket**:
```xml
<ticket>
  <id>EBASE-12345</id>
</ticket>
<action>validate completion</action>
```

**Before closing (recommended workflow)**:
```xml
<!-- Step 1: Validate -->
<ticket><id>EPP-192</id></ticket> <action>validate completion</action>

<!-- Step 2: Review validation report -->
<!-- Step 3: If passes, close -->
<ticket><id>EPP-192</id></ticket> <action>close ticket</action>
```

---

## Related Prompts

- `ticket/close-ticket.prompt.md` - Close ticket after validation passes
- `ticket/check-status.prompt.md` - Check progress before validation
- `ticket/update-progress.prompt.md` - Update progress if issues found, then re-validate
- `templars/ticket/ticket-closure-templar.md` - Closure structure after validation
- `exemplars/ticket/ticket-closure-exemplar.md` - Reference closure output

---

## Extracted Patterns

- **Templar**: `.cursor/prompts/templars/ticket/ticket-closure-templar.md`
- **Exemplar**: `.cursor/prompts/exemplars/ticket/ticket-closure-exemplar.md`

---

## Related Rules

Apply validation standards from:
- `.cursor/rules/ticket/validation-before-completion-rule.mdc` - Comprehensive validation requirements
- `.cursor/rules/ticket/ai-completion-discipline.mdc` - Completion discipline and responsible colleague behavior
- `.cursor/rules/ticket/ticket-workflow-rule.mdc` - Overall workflow standards

---

**Pattern**: Completion Validation Pattern
**Use When**: Before claiming any ticket complete
**Critical**: Quality gate - prevents premature "done" claims
**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
