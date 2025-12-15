---
id: prompt.cicd.readme.v1
kind: documentation
version: 1.0.0
description: Documentation for CI/CD Prompts
provenance:
  owner: team-cicd
  last_review: 2025-12-06
---

# CI/CD and Documentation Prompts

This directory contains AI-assisted prompts for setting up and maintaining CI/CD pipelines and documentation infrastructure for .NET projects.

---

## Available Prompts

### Fix Prompts (Zero Warnings, Zero Errors Initiative)

#### fix-missing-documentation.md
**File:** `fix-missing-documentation.md`  
**Purpose:** Fix missing XML documentation warnings (CS1591)  
**Auto-Fix Script:** `cicd/scripts/fix-warnings.ps1 -Fix MissingDocumentation`  
**Use When:** CS1591 warnings detected, documentation coverage incomplete  
**Goal:** Zero warnings - complete XML documentation coverage

#### fix-incomplete-metadata.md
**File:** `fix-incomplete-metadata.md`  
**Purpose:** Complete NuGet package metadata  
**Auto-Fix Script:** `cicd/scripts/fix-warnings.ps1 -Fix IncompleteMetadata`  
**Use When:** Package metadata validation warns about missing properties  
**Goal:** Professional-quality NuGet packages

#### fix-missing-changelog.md
**File:** `fix-missing-changelog.md`  
**Purpose:** Generate CHANGELOG entries for releases  
**Auto-Fix Script:** `cicd/scripts/fix-errors.ps1 -Fix MissingChangelog`  
**Use When:** Release tag validation fails due to missing CHANGELOG entry  
**Goal:** Complete release documentation

---

### Setup Prompts

### 1. Setup Documentation Pipeline
**File:** `setup-documentation-pipeline.md`  
**Purpose:** Create a complete CI/CD pipeline for XML documentation validation  
**Use When:** Setting up automated documentation validation in Azure DevOps

**What It Creates:**
- `cicd/azure-pipelines.yml` - Two-stage pipeline
- `cicd/scripts/*.ps1` - Validation scripts
- `cicd/README.md` & `QUICK-START.md` - Documentation
- Project configuration updates
- `.gitignore` updates

**Target:** Mature projects ready for strict enforcement (Level 3)

**Time Required:** 10-15 minutes (AI-assisted)

---

### 2. Setup Project Documentation
**File:** `setup-project-documentation.md`  
**Purpose:** Configure a .NET project with documentation standards  
**Use When:** Setting up documentation in new or existing projects at any maturity level

**What It Creates:**
- Project file (`.csproj`) configuration
- `docs/DOCUMENTATION-STANDARDS.md`
- Developer documentation
- Local validation scripts (optional)
- `.gitignore` configuration

**Maturity Levels Supported:**
- **Level 1 (Basic):** XML generation enabled, documentation encouraged
- **Level 2 (Recommended):** Analyzers enabled, validation tools available
- **Level 3 (Strict):** CI/CD enforcement, zero-tolerance for undocumented code

**Target:** Any .NET project, with progressive maturity support

**Time Required:** 5-10 minutes (AI-assisted)

---

### 3. Validate Documentation Setup
**File:** `validate-documentation-setup.md`  
**Purpose:** Comprehensive audit of documentation configuration and compliance  
**Use When:** Pre-release validation, maturity assessment, or quality audits

**What It Validates:**
- Project configuration analysis
- XML file generation and completeness
- Documentation coverage (CS1591 warnings)
- Standards documentation compliance
- Validation tooling functionality
- CI/CD integration verification
- Maturity level assessment
- Gap analysis with recommendations

**Output:** Comprehensive validation report with action items

**Target:** Any .NET project with documentation setup

**Time Required:** 2-5 minutes (AI-assisted)

---

## Documentation Maturity Framework

All prompts support a three-level maturity progression:

### Level 1: Initial Setup (Basic)
**Characteristics:**
- XML documentation files generated
- Basic project configuration
- Documentation encouraged but not enforced
- Suitable for: New projects, prototypes, internal tools

**Requirements:**
- `<GenerateDocumentationFile>true</GenerateDocumentationFile>`
- Documentation standards documented

### Level 2: Maturing Projects (Recommended)
**Characteristics:**
- XML documentation required for all public APIs
- Build warnings for missing documentation
- Validation tools available for manual use
- Code analyzers enabled

**Requirements:**
- Level 1 requirements
- `<EnableNETAnalyzers>true</EnableNETAnalyzers>`
- Local validation scripts
- Minimal documentation warnings

**Suitable for:** Active projects, internal libraries, maturing applications

### Level 3: Production-Ready (Strict)
**Characteristics:**
- **Documentation warnings treated as errors**
- **CI/CD pipeline enforcement (mandatory)**
- **Branch protection prevents undocumented code**
- **Zero tolerance for undocumented public APIs**
- **NuGet packages include complete documentation**

**Requirements:**
- Level 1 & 2 requirements
- CI/CD validation pipeline
- `/p:TreatWarningsAsErrors=true` in builds
- Branch protection configured
- Zero CS1591 warnings

**Suitable for:** Published libraries, public APIs, production applications, NuGet packages

---

## Maturity Progression Strategy

Projects should evolve through maturity levels as they mature:

```
Level 1          Level 2              Level 3
(Basic)    →    (Recommended)    →    (Strict)
  ↓                   ↓                   ↓
Start          Stabilizing         Production
Documentation  Public APIs         Released/Public
```

**Triggers for Progression:**

**Level 1 → Level 2:**
- Multiple contributors
- Code reuse across projects
- Public APIs stabilizing
- Approaching first release

**Level 2 → Level 3:**
- Production-ready or released
- NuGet package published
- External teams consuming APIs
- Documentation debt is minimal

**Preventing Regression:**
- Once at Level 3, enforcement prevents backsliding
- CI/CD blocks undocumented code
- Branch protection mandatory

---

## Usage Guide

### Scenario 1: New Project Setup

**Goal:** Start a new .NET project with documentation from day one

**Prompt to Use:** `setup-project-documentation.md`

**Request Example:**
```
"Set up documentation for this new project at Level 1 (Basic).
We'll progress to stricter levels as the project matures."
```

**Outcome:** Basic XML generation enabled, standards documented

---

### Scenario 2: Existing Project Documentation

**Goal:** Add documentation to existing project without CI/CD

**Prompt to Use:** `setup-project-documentation.md`

**Request Example:**
```
"Set up documentation for this existing project at Level 2.
Enable analyzers and create validation scripts we can run manually."
```

**Outcome:** Full configuration, local validation, ready for Level 3 when needed

---

### Scenario 3: CI/CD Pipeline Setup

**Goal:** Add automated documentation validation to mature project

**Prompt to Use:** `setup-documentation-pipeline.md`

**Prerequisites:** Project should be at Level 2 or have minimal documentation warnings

**Request Example:**
```
"Set up the full CI/CD documentation pipeline with strict enforcement.
This project is ready for Level 3."
```

**Outcome:** Complete pipeline, scripts, branch protection guidance

---

### Scenario 4: Pre-Release Validation

**Goal:** Validate documentation setup before major release

**Prompt to Use:** `validate-documentation-setup.md`

**Request Example:**
```
"Validate our documentation setup before the v2.0 release.
We want to ensure we're at Level 3 compliance."
```

**Outcome:** Comprehensive report with release readiness assessment

---

### Scenario 5: Maturity Assessment

**Goal:** Determine if project is ready to progress to next level

**Prompt to Use:** `validate-documentation-setup.md`

**Request Example:**
```
"We're currently at Level 2. Assess if we're ready for Level 3
and provide a roadmap for any gaps."
```

**Outcome:** Gap analysis with specific action items and effort estimates

---

### Scenario 6: Combined Setup

**Goal:** Full documentation infrastructure for new production project

**Prompts to Use (in order):**
1. `setup-project-documentation.md` (Level 3)
2. `setup-documentation-pipeline.md`
3. `validate-documentation-setup.md` (verification)

**Request Example:**
```
"This is a new production library that will be published to NuGet.
Set up complete Level 3 documentation infrastructure with CI/CD."
```

**Outcome:** Fully configured project with strict enforcement

---

## Prompt Selection Guide

**Choose `setup-project-documentation.md` if you:**
- ✅ Starting a new project
- ✅ Adding documentation to existing project
- ✅ Want to progress through maturity levels
- ✅ Don't need CI/CD yet
- ✅ Want local validation only

**Choose `setup-documentation-pipeline.md` if you:**
- ✅ Have existing project with good documentation
- ✅ Ready for automated enforcement (Level 3)
- ✅ Need Azure DevOps pipeline
- ✅ Want branch protection
- ✅ Publishing to NuGet

**Choose `validate-documentation-setup.md` if you:**
- ✅ Want to audit existing setup
- ✅ Preparing for release
- ✅ Assessing maturity progression readiness
- ✅ Identifying documentation technical debt
- ✅ Creating onboarding documentation

**Use multiple prompts if you:**
- ✅ Need complete setup from scratch
- ✅ Want to verify setup after configuration
- ✅ Building comprehensive documentation infrastructure

---

## Integration with Existing Rules

These prompts integrate with the `.cursor/rules/documentation/` framework:

**Related Rules:**
- `documentation-standards-rule.mdc` - Standards for XML documentation
- `documentation-testing-rule.mdc` - Testing documentation completeness
- `unit-test-documentation-rule.mdc` - Test documentation standards

**Coordination:**
- Rules define standards and agent behavior
- Prompts provide actionable setup and validation workflows
- Both reference `docs/DOCUMENTATION-STANDARDS.md` as source of truth

---

## Success Criteria

### For Setup Prompts
✅ Project configured with appropriate maturity level  
✅ Documentation standards documented  
✅ Validation tools created and tested  
✅ Developer documentation provided  
✅ Clean build with no errors  

### For Validation Prompt
✅ All validation steps completed  
✅ Accurate maturity assessment  
✅ Comprehensive gap analysis  
✅ Actionable recommendations provided  
✅ Report saved for future reference  

---

## Maintenance

### When to Update These Prompts

**Update when:**
- .NET version changes (update SDK versions)
- Azure DevOps pipeline syntax changes
- New documentation requirements added
- Maturity framework evolves
- New validation tools available

**Version History:**
- v1.0.0 (2025-11-30): Initial prompts created
  - setup-documentation-pipeline.md
  - setup-project-documentation.md
  - validate-documentation-setup.md

---

## Support

**Questions about prompts:**
- Review this README
- Check individual prompt files for detailed instructions
- See `docs/DOCUMENTATION-STANDARDS.md` for standards
- Review `.cursor/rules/documentation/` for agent rules

**Questions about documentation standards:**
- See `docs/DOCUMENTATION-STANDARDS.md`
- Review `.cursor/rules/documentation/documentation-standards-rule.mdc`

**Questions about CI/CD:**
- See `cicd/README.md` (after pipeline setup)
- Review `cicd/QUICK-START.md` (after pipeline setup)

---

**Framework Version:** 1.0.0  
**Last Updated:** 2025-11-30  
**Maintainers:** Development Team  
**Target Framework:** .NET 9.x (adaptable)
