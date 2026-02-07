---
name: Validate Documentation Setup
description: Comprehensive validation of .NET documentation configuration and maturity assessment
category: cicd
tags: [validation, documentation, quality-audit, maturity-assessment]
---

# Validate Documentation Setup

## Overview

Comprehensive validation of a .NET project's documentation configuration, standards compliance, and enforcement mechanisms. This prompt audits existing documentation setup and identifies gaps as projects mature from optional to required documentation.

Use this prompt to assess documentation readiness before releases, during maturity progression, or as part of quality audits.

---

## Task

Perform a thorough validation of the project's documentation setup, including:
1. Project configuration analysis
2. Documentation standards compliance
3. Validation tooling assessment
4. CI/CD enforcement verification
5. Maturity level assessment
6. Gap analysis and recommendations

---

## Validation Scope

### What This Validates

✅ **Project Configuration:**
- `.csproj` settings for XML generation
- Code analyzer configuration
- NuGet package settings (if applicable)

✅ **Documentation Files:**
- XML documentation generation
- File completeness and size
- Content quality (member coverage)

✅ **Standards Documentation:**
- `docs/DOCUMENTATION-STANDARDS.md` exists and is complete
- Developer guides include documentation section
- Team training materials available

✅ **Validation Tools:**
- Local validation scripts exist and work
- CI/CD pipeline validation configured
- Branch protection policies enforced

✅ **Maturity Assessment:**
- Current maturity level identification
- Readiness for next maturity level
- Gaps preventing progression

### What This Doesn't Validate

❌ **Code Quality:** Use code review tools
❌ **Test Coverage:** Use test coverage tools
❌ **Security:** Use security scanning tools
❌ **Performance:** Use performance profiling tools

This prompt focuses exclusively on documentation setup and enforcement.

---

## Maturity Levels Reference

Projects progress through documentation maturity:

### Level 1: Initial Setup (Basic)
- XML documentation files generated
- Documentation encouraged but not enforced
- Basic standards documented

### Level 2: Maturing Projects (Recommended)
- XML documentation required for public APIs
- Build warnings for missing documentation
- Validation tools available
- Standards well-documented

### Level 3: Production-Ready (Strict)
- **Documentation warnings are errors**
- **CI/CD pipeline enforcement mandatory**
- **Branch protection prevents undocumented code**
- **NuGet packages include complete documentation**
- **Zero tolerance for undocumented public APIs**

---

## Validation Steps

### Step 1: Project Configuration Analysis

**Scan all `.csproj` files:**

For each source project (in `src/` folder), check:

1. ✅ **GenerateDocumentationFile:**
   ```xml
   <GenerateDocumentationFile>true</GenerateDocumentationFile>
   ```
   - ❌ **Missing** = Level 0 (Not configured)
   - ✅ **Present** = Level 1 minimum

2. ✅ **EnableNETAnalyzers:**
   ```xml
   <EnableNETAnalyzers>true</EnableNETAnalyzers>
   <AnalysisLevel>latest</AnalysisLevel>
   ```
   - ❌ **Missing** = Level 1 (Basic only)
   - ✅ **Present** = Level 2+ capable

3. ✅ **NuGet Package Settings** (if project is packaged):
   ```xml
   <GeneratePackageOnBuild>true</GeneratePackageOnBuild>
   <IncludeSymbols>true</IncludeSymbols>
   <SymbolPackageFormat>snupkg</SymbolPackageFormat>
   ```
   - ❌ **Missing** = Documentation not in packages
   - ✅ **Present** = Level 3 capable

**Generate Report:**
```
Project Configuration Analysis
========================================
Source Projects Analyzed: X

✅ XML Documentation Generation: X/X projects
⚠️  Code Analyzers Enabled: X/X projects
⚠️  NuGet Package Settings: X/X projects

Details:
- ProjectName: [Level X] Missing: analyzer settings
- ProjectName: [Level 3] Complete
```

### Step 2: XML Documentation File Verification

**Build and verify XML files:**

1. **Clean build:**
   ```bash
   dotnet clean
   dotnet build --configuration Release
   ```

2. **Locate XML files:**
   ```bash
   Get-ChildItem -Path "src" -Filter "*.xml" -Recurse |
     Where-Object { $_.FullName -like "*Release*" }
   ```

3. **Verify each XML file:**
   - ✅ **Exists** - File was generated
   - ✅ **Non-empty** - File has content (> 0 bytes)
   - ✅ **Valid XML** - Can be parsed as XML
   - ✅ **Has members** - Contains documented members

**Generate Report:**
```
XML Documentation File Analysis
========================================
Expected Files: X
Generated Files: X
Empty Files: X
Invalid Files: X

Details:
- ProjectName.xml: ✅ 45.2 KB, 127 members documented
- ProjectName.xml: ❌ NOT FOUND
- ProjectName.xml: ⚠️  EMPTY (0 bytes)
```

### Step 3: Documentation Coverage Analysis

**Check for undocumented public APIs:**

1. **Build with strict warnings:**
   ```bash
   dotnet build --configuration Release /p:TreatWarningsAsErrors=true
   ```

2. **Capture CS1591 warnings:**
   - CS1591 = Missing XML documentation for publicly visible types/members
   - Count warnings per project
   - Identify specific undocumented members

3. **Calculate coverage:**
   - Load each XML file
   - Count documented members
   - Compare against expected (manual or via analyzer)

**Generate Report:**
```
Documentation Coverage Analysis
========================================
Projects: 3
Total Public APIs: ~450 (estimated)
Documented Members: 423

Warning Summary:
- ProjectName: ✅ 0 warnings (100% coverage)
- ProjectName: ⚠️  12 warnings (23 undocumented members)
- ProjectName: ❌ 45 warnings (critical gaps)

Maturity Assessment:
- Level 3 Ready: 1/3 projects
- Level 2 Ready: 2/3 projects
- Level 1 Only: 0/3 projects
```

### Step 4: Documentation Standards Validation

**Check for required documentation:**

1. ✅ **docs/DOCUMENTATION-STANDARDS.md:**
   - ❌ Missing = No standards documented
   - ✅ Present = Check completeness

2. **If present, verify sections:**
   - ✅ Overview / Purpose
   - ✅ XML Documentation Requirements
   - ✅ Quality Standards
   - ✅ Examples (good and bad)
   - ✅ Project Configuration Instructions
   - ✅ Local Validation Instructions
   - ✅ CI/CD Integration (if Level 3)

3. ✅ **Developer Guide:**
   - Check for documentation section in:
     - `docs/DEVELOPER-GUIDE.md`
     - `docs/CONTRIBUTING.md`
     - `README.md`
   - Should explain how to document code

4. ✅ **.gitignore:**
   - XML documentation files mentioned/ignored
   - Explanation comment present

**Generate Report:**
```
Documentation Standards Validation
========================================
Documentation Standards File: ✅ Present and complete
Developer Guide: ⚠️  Missing documentation section
.gitignore: ✅ XML files properly ignored

Completeness Score: 85%

Missing/Incomplete:
- Developer guide needs documentation section
- Standards file missing CI/CD integration section
```

### Step 5: Validation Tooling Assessment

**Check for validation mechanisms:**

1. ✅ **Local Validation Scripts:**
   - `scripts/validate-documentation.ps1` (lightweight)
   - `cicd/scripts/validate-documentation.ps1` (full validation)
   - `cicd/scripts/verify-xml-files.ps1` (XML verification)

2. ✅ **CI/CD Pipeline:**
   - `cicd/azure-pipelines.yml` or similar
   - GitHub Actions: `.github/workflows/*.yml`
   - GitLab CI: `.gitlab-ci.yml`

3. ✅ **Test each validation tool:**
   - Run local scripts
   - Verify they detect issues
   - Check exit codes work correctly

**Generate Report:**
```
Validation Tooling Assessment
========================================
Local Validation Scripts:
- ✅ verify-xml-files.ps1: Present and working
- ✅ validate-documentation.ps1: Present and working
- ⚠️  generate-doc-report.ps1: Not found

CI/CD Pipeline:
- ✅ azure-pipelines.yml: Present with doc validation
- ✅ Documentation stage: Configured
- ✅ Treats warnings as errors: Yes

Branch Protection:
- ⚠️  Not configured (manual verification required)

Tooling Maturity: Level 3 (Strict enforcement capable)
```

### Step 6: CI/CD Integration Verification

**Validate CI/CD enforcement:**

1. ✅ **Pipeline Configuration:**
   - Documentation validation step exists
   - Treats warnings as errors: `/p:TreatWarningsAsErrors=true`
   - Fails build on undocumented APIs
   - Runs on all relevant branches

2. ✅ **Branch Protection** (manual check required):
   - Main/master branch protected
   - Build must pass before merge
   - Documentation validation required

3. ✅ **Test Pipeline:**
   - Review recent pipeline runs
   - Check if documentation validation runs
   - Verify failures are caught

**Generate Report:**
```
CI/CD Integration Verification
========================================
Pipeline Type: Azure DevOps / GitHub Actions / GitLab CI
Documentation Validation: ✅ Configured

Pipeline Features:
- ✅ Build with TreatWarningsAsErrors
- ✅ XML file verification
- ✅ Documentation completeness check
- ✅ Runs on PRs to main/develop
- ✅ Blocks merge on failure

Branch Protection:
- ⚠️  Cannot verify programmatically (check Azure DevOps manually)
- Recommendation: Enable on main branch

Enforcement Level: Level 3 (Strict) ✅
```

### Step 7: Maturity Assessment

**Determine current and target maturity:**

**Scoring Criteria:**

| Criteria | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| XML Generation | ✅ | ✅ | ✅ |
| Code Analyzers | ❌ | ✅ | ✅ |
| Validation Scripts | ❌ | ✅ | ✅ |
| CI/CD Validation | ❌ | Optional | ✅ Required |
| Warnings as Errors | ❌ | ❌ | ✅ |
| Branch Protection | ❌ | ❌ | ✅ |
| Zero Warnings | ❌ | Goal | ✅ Enforced |

**Calculate Overall Maturity:**
```
Maturity Assessment
========================================
Current Maturity: Level X

Level 1 (Basic): [✅/⚠️/❌]
- XML Generation: ✅
- Standards Documented: ✅

Level 2 (Recommended): [✅/⚠️/❌]
- Code Analyzers: ✅
- Validation Scripts: ✅
- Minimal Warnings: ⚠️  (12 warnings remain)

Level 3 (Strict): [✅/⚠️/❌]
- Warnings as Errors: ✅
- CI/CD Enforcement: ✅
- Branch Protection: ⚠️  (not verified)
- Zero Warnings: ❌ (12 warnings in 1 project)

Readiness: Can achieve Level 3 after fixing 12 warnings
```

### Step 8: Gap Analysis and Recommendations

**Identify gaps preventing maturity progression:**

**For Each Gap:**
1. Describe the issue
2. Assess impact (Critical / High / Medium / Low)
3. Provide fix instructions
4. Estimate effort (Small / Medium / Large)

**Generate Report:**
```
Gap Analysis and Recommendations
========================================

CRITICAL GAPS (Blocking Level 3):
1. [HIGH] 12 undocumented public APIs in ProjectName
   Impact: CI/CD will fail when enforcement enabled
   Fix: Add XML comments to identified members
   Effort: Medium (2-4 hours)
   Files: See detailed list below

2. [MEDIUM] Code analyzers not enabled in ProjectName
   Impact: Can't detect documentation issues at build time
   Fix: Add <EnableNETAnalyzers>true</EnableNETAnalyzers>
   Effort: Small (5 minutes)

NON-CRITICAL GAPS (Quality improvements):
3. [LOW] Developer guide missing documentation section
   Impact: New developers may not know documentation standards
   Fix: Add section to docs/DEVELOPER-GUIDE.md
   Effort: Small (30 minutes)

RECOMMENDATIONS:
- Fix critical gaps before enabling Level 3 enforcement
- Review undocumented members list (attached)
- Consider gradual rollout: enable per-project
- Schedule team training on documentation standards
```

---

## Output Format

### Comprehensive Validation Report

Generate a markdown report with all findings:

```markdown
# Documentation Setup Validation Report

**Project:** Project Name
**Date:** YYYY-MM-DD
**Validated By:** AI Agent / Developer Name
**Current Maturity:** Level X
**Target Maturity:** Level Y

---

## Executive Summary

[2-3 sentences summarizing overall state]

**Key Findings:**
- ✅ X/Y projects fully documented
- ⚠️  X warnings remaining across Y projects
- ❌ X critical gaps identified

**Recommendation:** [Ready for Level X / Fix Y issues before progression]

---

## Detailed Findings

### 1. Project Configuration
[Results from Step 1]

### 2. XML Documentation Files
[Results from Step 2]

### 3. Documentation Coverage
[Results from Step 3]

### 4. Documentation Standards
[Results from Step 4]

### 5. Validation Tooling
[Results from Step 5]

### 6. CI/CD Integration
[Results from Step 6]

### 7. Maturity Assessment
[Results from Step 7]

### 8. Gap Analysis
[Results from Step 8]

---

## Action Items

**Immediate (Before Next Release):**
1. [Critical gap fix]
2. [Critical gap fix]

**Short Term (Next Sprint):**
1. [High priority improvement]
2. [High priority improvement]

**Long Term (Next Quarter):**
1. [Quality improvement]
2. [Process improvement]

---

## Appendix

### A. Undocumented Members List
[Detailed list of CS1591 warnings]

### B. Project Configuration Details
[Per-project configuration status]

### C. Validation Script Test Results
[Script execution outputs]

---

*Report generated by documentation validation prompt v1.0.0*
```

---

## Success Criteria

Validation is successful when:

✅ **Completeness:**
- All 8 validation steps executed
- All source projects analyzed
- All documentation files checked
- All tooling verified

✅ **Accuracy:**
- No false positives (incorrectly flagged issues)
- No false negatives (missed issues)
- Maturity level correctly assessed
- Gap analysis is actionable

✅ **Actionability:**
- Report clearly explains findings
- Gaps have specific fix instructions
- Effort estimates provided
- Prioritization clear

---

## Notes for AI Agents

- **Run actual validation** - Don't just check files exist, verify they work
- **Test validation scripts** - Execute them and check output
- **Build the project** - Actually run `dotnet build` to find warnings
- **Be specific** - List exact files, line numbers, member names
- **Provide commands** - Give copy-paste-ready fix commands
- **Consider context** - Adjust recommendations based on project type
- **Save report** - Write validation report to `docs/validation-report-YYYY-MM-DD.md`

---

## Related Prompts

- **Setup Project Documentation:** `.cursor/prompts/cicd/setup-project-documentation.md`
- **Setup CI/CD Pipeline:** `.cursor/prompts/cicd/setup-documentation-pipeline.md`
- **Documentation Standards:** `docs/DOCUMENTATION-STANDARDS.md`
- **Documentation Rules:** `.cursor/rules/documentation/`

---

**Prompt Version:** 1.0.0
**Created:** 2025-11-30
**Target:** .NET Projects (any maturity level)
**Validation Depth:** Comprehensive (8-step process)
