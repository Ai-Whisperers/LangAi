---
name: pre-commit-validation
description: "Comprehensive pre-commit validation using CI/CD scripts to detect issues before pushing"
category: git
tags: git, validation, CI/CD, quality, pre-commit
argument-hint: "Validation level (1=Quick, 2=Standard, 3=Full)"
---

# Pre-Commit Validation

Run comprehensive validation checks before committing to catch issues that would fail in CI/CD pipeline.

**Context**: Before claiming work is done and committing changes.

---

## Validation Levels

Choose validation level based on time available and change scope:

### Level 1: Quick Check (30 seconds)
**When**: Minor changes, documentation updates, simple fixes
**Run**: Code formatting only

### Level 2: Standard Check (2-3 minutes)
**When**: Normal feature work, bug fixes, refactoring
**Run**: Format + Build + Tests

### Level 3: Full Validation (5-10 minutes)
**When**: Before merge requests, after build failures, significant changes
**Run**: All CI/CD pipeline checks

---

## Level 1: Quick Check

```powershell
# Navigate to repo root
cd e:\WPG\Git\E21\GitRepos\eneve.domain

# Check code formatting
dotnet format --verify-no-changes --severity warn
```

**If formatting fails**:
```powershell
# Auto-fix formatting issues
dotnet format

# Verify fix
dotnet format --verify-no-changes --severity warn
```

✅ **Pass Criteria**: Exit code 0, no formatting changes needed

---

## Level 2: Standard Check

```powershell
# 1. Format check
dotnet format --verify-no-changes --severity warn

# 2. Build with warnings as errors
dotnet build --configuration Release /p:TreatWarningsAsErrors=true

# 3. Run all tests
dotnet test --configuration Release --no-build
```

✅ **Pass Criteria**: All commands exit code 0

---

## Level 3: Full Validation

Run all CI/CD pipeline validation steps locally:

### 3.1 Code Quality

```powershell
# Code formatting
dotnet format --verify-no-changes --severity warn

# Build with warnings as errors
dotnet build --configuration Release /p:TreatWarningsAsErrors=true

# Run all tests with coverage
dotnet test --configuration Release --no-build --collect:"XPlat Code Coverage"

# Check naming conventions
dotnet build /p:EnforceCodeStyleInBuild=true /p:TreatWarningsAsErrors=true
```

### 3.2 Documentation

```powershell
# Validate documentation quality
.\cicd\scripts\validate-documentation.ps1

# Verify XML files generated
.\cicd\scripts\verify-xml-files.ps1
```

### 3.3 Package Quality

```powershell
# Validate package metadata
.\cicd\scripts\validate-package-metadata.ps1

# Scan license compliance
.\cicd\scripts\scan-licenses.ps1 -OutputPath "./local-reports/licenses"

# Check for breaking changes (API compatibility)
.\cicd\scripts\check-breaking-changes.ps1 -OutputPath "./local-reports/compat"
```

### 3.4 Code Metrics (Optional but Recommended)

```powershell
# Calculate maintainability index and complexity
.\cicd\scripts\calculate-code-metrics.ps1 -OutputPath "./local-reports/metrics"
```

---

## Validation Execution

Please run the appropriate validation level and report:

1. **Which validation level are you running?**
   - Level 1: Quick Check
   - Level 2: Standard Check
   - Level 3: Full Validation

2. **Execute the commands**
   - Run each command in sequence
   - Capture exit codes
   - Note any failures

3. **Report Results**
   - ✅ PASS: Command succeeded (exit code 0)
   - ❌ FAIL: Command failed (exit code non-zero)
   - Include error messages for failures

4. **Fix Issues if Found**
   - Address any failures
   - Re-run validation
   - Confirm all checks pass

---

## Common Issues & Fixes

### Issue: Formatting Violations (IDE1006, etc.)

**Error**: `error IDE1006: Naming rule violation: Missing prefix: '_'`

**Fix**:
```powershell
# Auto-fix formatting
dotnet format

# Verify
dotnet format --verify-no-changes --severity warn
```

### Issue: Compiler Warnings

**Error**: `warning CS1591: Missing XML comment`

**Fix**: Add XML documentation to public members or suppress in `.csproj`:
```xml
<NoWarn>CS1591</NoWarn>
```

### Issue: Test Failures

**Fix**: 
1. Run tests locally to identify failures
2. Debug and fix failing tests
3. Ensure all tests pass before committing

### Issue: Missing Documentation

**Error**: Documentation validation fails

**Fix**: Add XML comments to public APIs, then regenerate docs

### Issue: Breaking Changes Detected

**Warning**: API compatibility check shows breaking changes

**Fix**: 
- If intentional: Document in CHANGELOG and plan version bump
- If unintentional: Refactor to maintain compatibility

---

## Pre-Commit Checklist

Before claiming "done" and committing:

- [ ] **Validation passed** at appropriate level
- [ ] **All tests passing** (local and new tests)
- [ ] **No compiler warnings** introduced
- [ ] **No linter errors** (formatting clean)
- [ ] **Documentation complete** (XML comments on public APIs)
- [ ] **No debug code** left in (Console.WriteLine, etc.)
- [ ] **No commented-out code** (remove or explain)
- [ ] **Commit message ready** (follows conventional commit format)
- [ ] **Changes staged** (only relevant files)
- [ ] **No breaking changes** (or documented if intentional)

---

## Validation Summary Template

After running validation, provide summary:

```
## Validation Results

**Level**: [1/2/3]
**Date**: [YYYY-MM-DD HH:MM]

### Results
- [ ] Code Formatting: PASS/FAIL
- [ ] Build: PASS/FAIL
- [ ] Tests: PASS/FAIL
- [ ] Documentation: PASS/FAIL (Level 3 only)
- [ ] Package Metadata: PASS/FAIL (Level 3 only)
- [ ] License Scan: PASS/FAIL (Level 3 only)
- [ ] API Compatibility: PASS/FAIL (Level 3 only)

### Issues Found
[List any issues and how they were resolved]

### Status
✅ READY TO COMMIT
❌ NEEDS WORK - [list remaining tasks]
```

---

## Integration with Workflow

**Use this prompt**:
- After completing a ticket (see `.cursor/prompts/ticket/validate-completion.md`)
- Before running `.cursor/prompts/git/prepare-commit.md`
- After fixing a failed CI/CD build
- Before creating a merge request

**Rule References**:
- `.cursor/rules/cicd/pre-build-validation-rule.mdc`
- `.cursor/rules/ticket/validation-before-completion-rule.mdc`
- `.cursor/rules/ticket/ai-completion-discipline.mdc`
- `.cursor/rules/development-commit-message.mdc`

---

## Quick Copy-Paste Commands

### Level 1: Quick
```powershell
cd e:\WPG\Git\E21\GitRepos\eneve.domain && dotnet format --verify-no-changes --severity warn
```

### Level 2: Standard
```powershell
cd e:\WPG\Git\E21\GitRepos\eneve.domain
dotnet format --verify-no-changes --severity warn
dotnet build --configuration Release /p:TreatWarningsAsErrors=true
dotnet test --configuration Release --no-build
```

### Level 3: Full (PowerShell script)
```powershell
cd e:\WPG\Git\E21\GitRepos\eneve.domain

# Core checks
dotnet format --verify-no-changes --severity warn
if ($LASTEXITCODE -ne 0) { Write-Error "Format failed"; exit 1 }

dotnet build --configuration Release /p:TreatWarningsAsErrors=true
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }

dotnet test --configuration Release --no-build
if ($LASTEXITCODE -ne 0) { Write-Error "Tests failed"; exit 1 }

# Documentation
.\cicd\scripts\validate-documentation.ps1
if ($LASTEXITCODE -ne 0) { Write-Error "Documentation validation failed"; exit 1 }

.\cicd\scripts\verify-xml-files.ps1
if ($LASTEXITCODE -ne 0) { Write-Error "XML verification failed"; exit 1 }

# Package quality
.\cicd\scripts\validate-package-metadata.ps1
if ($LASTEXITCODE -ne 0) { Write-Error "Metadata validation failed"; exit 1 }

Write-Host "✅ All validation checks passed!" -ForegroundColor Green
```

---

## Notes

- **Run in correct directory**: Always navigate to repo root first
- **PowerShell execution policy**: May need `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- **Time estimates**: Based on repository size; may vary
- **CI/CD scripts**: Located in `cicd/scripts/` directory
- **Full documentation**: See `cicd/scripts/README.md`

**Remember**: It's better to spend 5 minutes validating locally than 30 minutes debugging a failed CI/CD build!

