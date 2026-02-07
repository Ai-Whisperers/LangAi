---
name: Setup Project Documentation Standards
description: Configure .NET project documentation standards and validation for any maturity level
category: cicd
tags: [documentation, setup, configuration, standards, maturity-levels]
argument-hint: "[maturity-level: 1-3]"
---

# Setup Project Documentation Standards

## Overview

Configure a .NET project (new or existing) with comprehensive XML documentation standards, ensuring all public APIs are documented and ready for NuGet package consumers.

This prompt handles projects at any maturity level, from initial setup to enforcing strict documentation requirements.

---

## Task

Set up complete documentation infrastructure for this .NET project, including project configuration, validation tools, and documentation standards.

---

## Maturity Levels

Documentation requirements evolve as projects mature. This setup supports three levels:

### Level 1: Initial Setup (New Projects)
- Generate XML documentation files
- Basic project configuration
- Documentation encouraged but not enforced

### Level 2: Maturing Projects
- XML documentation required for all public APIs
- Build warnings for missing documentation
- Documentation validation in CI/CD (optional)

### Level 3: Production-Ready (Mature Projects)
- **Documentation warnings treated as errors**
- **CI/CD pipeline enforcement (required)**
- **Branch protection prevents undocumented code**
- **NuGet packages must include complete documentation**

**Default for this prompt:** Level 3 (Production-Ready)

To use a different level, specify it in your request.

---

## Requirements

### 1. Analyze Current State

Before making changes, analyze:

**Project Configuration:**
- Does `<GenerateDocumentationFile>` exist in `.csproj`?
- Are code analyzers enabled?
- Is this project packaged for NuGet?
- What's the current documentation coverage?

**Repository Structure:**
- Does `docs/` folder exist?
- Is there a `cicd/` folder with validation scripts?
- Are documentation standards documented?

**Maturity Assessment:**
- Is this a new project or existing?
- Does CI/CD already exist?
- Are there existing documentation standards?

### 2. Project File Configuration

Update `.csproj` files based on maturity level:

**Level 1 - Basic (Minimum):**
```xml
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
</PropertyGroup>
```

**Level 2 - Maturing (Recommended):**
```xml
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <EnableNETAnalyzers>true</EnableNETAnalyzers>
  <AnalysisLevel>latest</AnalysisLevel>
</PropertyGroup>
```

**Level 3 - Production (Strict):**
```xml
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <EnableNETAnalyzers>true</EnableNETAnalyzers>
  <AnalysisLevel>latest</AnalysisLevel>
  <!-- For NuGet packages only: -->
  <GeneratePackageOnBuild>true</GeneratePackageOnBuild>
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>
</PropertyGroup>
```

**When to apply:**
- **Source projects:** All levels apply
- **Test projects:** Level 1 only (no strict enforcement)
- **Sample/example projects:** Level 1 only

### 3. Documentation Standards File

Create or update `docs/DOCUMENTATION-STANDARDS.md`:

**Required Sections:**
1. **Overview** - Why documentation matters for this project
2. **XML Documentation Requirements**
   - What must be documented (public APIs, parameters, returns, exceptions)
   - Quality standards (minimum length, no redundancy, meaningful descriptions)
3. **Examples** - Good and bad documentation examples
4. **Project Configuration** - How to enable documentation in `.csproj`
5. **Local Validation** - How developers can test locally
6. **CI/CD Integration** - How documentation is enforced (if Level 3)

**Template Available:** Use existing `docs/DOCUMENTATION-STANDARDS.md` as reference if it exists.

### 4. Validation Tools (Level 2+)

If validation tools don't exist and maturity level is 2 or higher:

**Option A:** Create local validation script
- PowerShell script: `scripts/validate-documentation.ps1`
- Checks for CS1591 warnings
- Can be run manually by developers

**Option B:** Use existing CI/CD validation
- Reference `cicd/scripts/validate-documentation.ps1` if it exists
- Integrate into pre-commit hooks (optional)

**Option C:** Recommend full CI/CD setup
- Suggest using `setup-documentation-pipeline.md` prompt
- Full pipeline with automated validation

### 5. Developer Workflow Documentation

Create `docs/DEVELOPER-GUIDE-DOCUMENTATION.md` or add section to existing developer guide:

**Content:**
- How to add XML documentation comments
- Required tags: `<summary>`, `<param>`, `<returns>`, `<exception>`
- Optional tags: `<remarks>`, `<example>`, `<seealso>`
- How to test locally before committing
- What to do when validation fails
- Links to documentation standards

### 6. .gitignore Configuration

Ensure XML documentation files are ignored (they're build artifacts):

```gitignore
# XML Documentation Files (auto-generated during build)
# These are not committed as they are build artifacts
# Generated during build when <GenerateDocumentationFile>true</GenerateDocumentationFile>
# Included automatically in NuGet packages via bin/ and obj/ patterns
# To generate locally: dotnet build --configuration Release
```

**Note:** XML files should already be ignored by `bin/` and `obj/` patterns, but add this comment for clarity.

---

## Implementation Steps

### Step 1: Assess Current State

1. **Scan all `.csproj` files:**
   ```bash
   # Find all project files
   Get-ChildItem -Path . -Filter "*.csproj" -Recurse
   ```

2. **Check for existing documentation:**
   - Does `docs/DOCUMENTATION-STANDARDS.md` exist?
   - Do projects have `<GenerateDocumentationFile>` already?
   - Are there existing validation scripts?

3. **Determine maturity level:**
   - Ask user if not specified
   - Default to Level 3 for production code
   - Consider Level 1-2 for internal tools or prototypes

### Step 2: Update Project Files

For each source project (not test projects):

1. Read existing `.csproj` file
2. Locate or create `<PropertyGroup>` section
3. Add missing documentation settings based on maturity level
4. Preserve existing settings (don't remove anything)
5. Validate XML syntax before saving

**Projects to Update:**
- ✅ All projects in `src/` folder
- ✅ Any projects that produce NuGet packages
- ❌ Test projects (only basic settings)
- ❌ Sample/example projects (only basic settings)

### Step 3: Create Documentation Standards

If `docs/DOCUMENTATION-STANDARDS.md` doesn't exist:

1. Create `docs/` folder if needed
2. Create comprehensive standards document
3. Include examples specific to this project's domain
4. Reference existing rule files if they exist (`.cursor/rules/documentation/`)

If it already exists:
1. Review for completeness
2. Add missing sections
3. Update to match chosen maturity level

### Step 4: Create Developer Guide

If not already documented:

1. Create or update developer documentation
2. Include section on XML documentation
3. Provide clear examples
4. Link to validation tools
5. Show common error messages and how to fix

### Step 5: Setup Validation (Level 2+)

**For Level 2 (Maturing):**
- Create simple validation script developers can run manually
- Document how to use it
- Make it optional but recommended

**For Level 3 (Production):**
- Ensure CI/CD validation exists (or recommend setup)
- Configure build to fail on documentation warnings
- Setup branch protection (if Azure DevOps/GitHub)
- Make validation mandatory

### Step 6: Update .gitignore

1. Add XML documentation comment section if not present
2. Verify bin/ and obj/ patterns exist
3. Commit .gitignore changes

### Step 7: Test Configuration

Before completing:

1. **Build test:**
   ```bash
   dotnet clean
   dotnet build --configuration Release
   ```

2. **Verify XML files generated:**
   ```bash
   Get-ChildItem -Path "src" -Filter "*.xml" -Recurse
   ```

3. **Check for documentation warnings:**
   ```bash
   dotnet build --configuration Release /p:TreatWarningsAsErrors=true
   ```

4. **Run validation script** (if Level 2+):
   ```bash
   .\scripts\validate-documentation.ps1  # or cicd\scripts\...
   ```

---

## Maturity Progression Strategy

Projects should evolve through maturity levels:

### When to Move from Level 1 → Level 2

**Triggers:**
- Project has multiple contributors
- Code is being reused in other projects
- Public APIs are stabilizing
- Project approaching first release

**Actions:**
- Enable code analyzers
- Add validation scripts
- Update documentation standards
- Train team on requirements

### When to Move from Level 2 → Level 3

**Triggers:**
- Project is production-ready or released
- NuGet package is published
- External teams consuming APIs
- Documentation debt is minimal

**Actions:**
- Treat warnings as errors in CI/CD
- Require validation in branch policies
- Make documentation a release requirement
- Enforce through automated gates

### Preventing Regression

Once at Level 3:
- ✅ CI/CD prevents undocumented code from merging
- ✅ Build fails on documentation warnings
- ✅ Branch protection enforces validation
- ✅ NuGet packages include XML documentation

---

## Project Type Considerations

### Library/SDK Projects
**Recommended Level:** 3 (Strict)
- Public APIs consumed by external teams
- IntelliSense critical for developer experience
- Documentation is part of the product

### Application Projects
**Recommended Level:** 2 (Recommended)
- Internal team consumption
- Documentation helpful but not critical
- Focus on public contracts and utilities

### Internal Tools
**Recommended Level:** 1-2 (Basic to Recommended)
- Small team usage
- Documentation nice-to-have
- Can evolve as tool matures

### Proof of Concept / Prototypes
**Recommended Level:** 1 (Basic)
- Rapid iteration
- May be discarded
- Documentation optional

---

## Output Checklist

After completing setup, verify:

- [ ] All source `.csproj` files have `<GenerateDocumentationFile>true</GenerateDocumentationFile>`
- [ ] Code analyzers enabled (Level 2+)
- [ ] NuGet package settings configured (if applicable)
- [ ] `docs/DOCUMENTATION-STANDARDS.md` exists with complete standards
- [ ] Developer guide includes documentation section
- [ ] `.gitignore` has XML documentation comment
- [ ] Clean build succeeds: `dotnet build --configuration Release`
- [ ] XML files generated for all source projects
- [ ] Documentation validation passes (Level 2+)
- [ ] No CS1591 warnings (Level 3) or acceptable warnings documented (Level 2)
- [ ] CI/CD integration verified (Level 3)

---

## Success Criteria

**Level 1 (Basic):**
- ✅ XML files generated during build
- ✅ Documentation standards documented
- ✅ Team aware of expectations

**Level 2 (Recommended):**
- ✅ All above
- ✅ Code analyzers enabled
- ✅ Validation script available
- ✅ Minimal documentation warnings

**Level 3 (Strict):**
- ✅ All above
- ✅ Zero documentation warnings
- ✅ CI/CD enforcement active
- ✅ Branch protection configured
- ✅ NuGet packages include XML documentation

---

## Related Documentation

- **CI/CD Pipeline Setup:** `.cursor/prompts/cicd/setup-documentation-pipeline.md`
- **Validation Prompt:** `.cursor/prompts/cicd/validate-documentation-setup.md`
- **Documentation Standards:** `docs/DOCUMENTATION-STANDARDS.md` (after creation)
- **Documentation Rules:** `.cursor/rules/documentation/`

---

## Notes for AI Agents

- **Always assess current state first** - Don't assume project structure
- **Ask about maturity level** if not specified in request
- **Preserve existing settings** - Only add/update, never remove
- **Test before completing** - Verify builds and XML generation work
- **Provide next steps** - Guide user on progression path
- **Be pragmatic** - Level 1 is valid for early-stage projects

---

**Prompt Version:** 1.0.0
**Created:** 2025-11-30
**Target:** .NET Projects (any maturity level)
**Default Maturity:** Level 3 (Production-Ready)
