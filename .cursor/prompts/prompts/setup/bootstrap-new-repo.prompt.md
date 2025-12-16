---
name: bootstrap-new-repo
description: "Please bootstrap a new .NET repository using Gold Standard reference implementation"
category: setup
tags: bootstrap, setup, gold-standard, repository, initialization, dotnet
argument-hint: "New repository name (e.g., my-new-repo)"
---

# Bootstrap New Repository (Gold Standard)

Please bootstrap a new .NET repository using `eneve.domain` as the "Gold Standard" reference implementation, setting up build infrastructure, CI/CD pipeline, documentation architecture, and AI rules.

**Pattern**: Repository Bootstrap Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for consistent repo initialization
**Use When**: Creating new .NET repository from scratch

---

## Purpose

Bootstrap a new .NET repository with complete Gold Standard setup in one go:
- **Build Infrastructure**: Central Package Management, .editorconfig, build props
- **AI & Rules**: Complete `.cursor/` directory with rules, prompts, templars
- **CI/CD Pipeline**: Azure DevOps pipeline with validation scripts
- **Documentation**: Standard docs structure (technical/implementation/rfcs)
- **Project Structure**: Solution, projects, test structure

**Reference Implementation**: `eneve.domain` repository serves as the Gold Standard template.

---

## Required Context

- **Reference Repo**: Access to `eneve.domain` (Gold Standard)
- **New Repo**: Empty repository created in Azure DevOps
- **Prerequisites**: .NET 9 SDK installed, Git initialized
- **Customization Info**: Repository name, company, authors, package tags

---

## Process

Follow this workflow to bootstrap new repository:

### Step 1: Prepare Prerequisites
Verify requirements before starting.

### Step 2: Copy Build Infrastructure
Copy shared build configuration from Gold Standard.

### Step 3: Setup AI & Rules
Install complete `.cursor/` directory with all rules and prompts.

### Step 4: Configure CI/CD Pipeline
Copy and customize Azure DevOps pipeline and validation scripts.

### Step 5: Create Documentation Structure
Setup docs folders and ticket templates.

### Step 6: Initialize Solution
Create .NET solution with initial projects.

### Step 7: Validate Setup
Run build, tests, and pipeline validation.

---

## Reasoning Process (for AI Agent)

When bootstrapping new repository, the AI should:

1. **Verify Prerequisites**: Does user have access to Gold Standard repo? Is .NET SDK installed?
2. **Plan Customization**: What repository-specific values need updating? (name, company, URLs)
3. **Phase Order**: Which phase should be executed first? (build infrastructure → AI → CI/CD → docs → solution)
4. **Adaptation**: What files need customization vs blind copy? (Directory.Build.props needs edits, .gitignore can copy)
5. **Validation**: How to verify each phase completed successfully?
6. **Next Steps**: After bootstrap, what should user do? (commit, push, configure pipeline)

---

## Step-by-Step Implementation

### Phase 1: Build Infrastructure (The Foundation)

#### 1. Copy Configuration Files from `eneve.domain` root:

**Files to copy**:
- `Directory.Build.props` - Shared build settings
- `Directory.Packages.props` - Central Package Management (CPM)
- `global.json` - SDK version pinning
- `NuGet.Config` - Package sources configuration
- `.gitignore` - Standard .NET ignores + tickets/current.md
- `.editorconfig` - Code style rules

```bash
# From eneve.domain root
cp Directory.Build.props ../my-new-repo/
cp Directory.Packages.props ../my-new-repo/
cp global.json ../my-new-repo/
cp NuGet.Config ../my-new-repo/
cp .gitignore ../my-new-repo/
cp .editorconfig ../my-new-repo/
```

#### 2. Customize `Directory.Build.props`:

**Update these properties**:
```xml
<Authors>Your Name</Authors>
<Company>Your Company</Company>
<RepositoryUrl>https://dev.azure.com/org/my-new-repo</RepositoryUrl>
<PackageTags>your-tags</PackageTags>
```

**Keep as-is** (these are Gold Standard settings):
- `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`
- `<GenerateDocumentationFile>true</GenerateDocumentationFile>`
- `<EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>`

---

### Phase 2: AI & Rules Setup (The Brain)

#### 1. Copy `.cursor` Directory:

```bash
# Copy entire .cursor/ folder from eneve.domain
cp -r ../eneve.domain/.cursor ./
```

**This installs**:
- All rules (`.cursor/rules/**/*.mdc`)
- All prompts (`.cursor/prompts/**/*.prompt.md`)
- Templars and exemplars
- Rule-authoring framework
- Ticket management rules
- CI/CD validation rules

#### 2. Verify AI Setup:

```bash
# Check key files exist
ls .cursor/rules/cicd/tag-based-versioning-rule.mdc
ls .cursor/rules/setup/project-setup-rule.mdc
ls .cursor/prompts/ticket/activate-ticket.prompt.md
```

---

### Phase 3: CI/CD Setup (The Pipeline)

#### 1. Create Directory Structure:

```bash
mkdir -p cicd/scripts cicd/docs
```

#### 2. Copy Pipeline Assets:

```bash
# Copy main pipeline
cp ../eneve.domain/cicd/azure-pipelines.yml ./cicd/

# Copy ALL validation scripts (CRITICAL)
cp ../eneve.domain/cicd/scripts/*.ps1 ./cicd/scripts/
```

**Critical scripts** (ensure all copied):
- `verify-xml-files.ps1` - XML documentation validation
- `validate-documentation.ps1` - Documentation completeness
- `generate-doc-report.ps1` - Documentation reporting
- `scan-licenses.ps1` - License compliance checking
- `validate-release-notes.ps1` - CHANGELOG validation

#### 3. Configure Pipeline:

Edit `cicd/azure-pipelines.yml`:
```yaml
variables:
  solutionPath: 'MyNewRepo.sln'  # Update solution name
  publishVstsFeed: 'Test-Feed'   # Update for test feed
  prodVstsFeed: 'Production-Feed' # Update for production feed
```

---

### Phase 4: Documentation & Tickets (The Structure)

#### 1. Create Directories:

```bash
mkdir -p docs/technical docs/implementation docs/rfcs
mkdir -p tickets/templates
```

#### 2. Copy Templates:

```bash
# Copy ticket templates
cp -r ../eneve.domain/tickets/templates/* ./tickets/templates/

# Copy README structure (then customize content)
cp ../eneve.domain/README.md ./README.md
```

#### 3. Create Initial README:

Edit `README.md` to match your repository:
- Project name and description
- Architecture overview
- Build instructions
- Contributing guidelines

---

### Phase 5: Solution Setup (The Code)

#### 1. Create Solution:

```bash
dotnet new sln -n MyNewRepo
mkdir src tst
```

#### 2. Create Initial Projects:

```bash
# Create domain library
cd src
dotnet new classlib -n MyNewRepo.Domain

# Create unit tests
cd ../tst
dotnet new xunit -n MyNewRepo.Domain.Tests
cd ..
```

#### 3. Add Projects to Solution:

```bash
dotnet sln add src/MyNewRepo.Domain/MyNewRepo.Domain.csproj
dotnet sln add tst/MyNewRepo.Domain.Tests/MyNewRepo.Domain.Tests.csproj
```

#### 4. Sanitize Project Files (CRITICAL):

**Remove** `<PackageReference>` versions from `.csproj` files:

```xml
<!-- ❌ BAD: Version in project file -->
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />

<!-- ✅ GOOD: Version in Directory.Packages.props -->
<PackageReference Include="Newtonsoft.Json" />
```

**Add** package versions to `Directory.Packages.props` instead:

```xml
<ItemGroup>
  <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
  <PackageVersion Include="xunit" Version="2.6.1" />
  <PackageVersion Include="FluentAssertions" Version="6.12.0" />
</ItemGroup>
```

**Optionally remove** `<TargetFramework>` if it matches `Directory.Build.props`:
- If all projects target `net9.0`, define in `Directory.Build.props`
- Remove from individual `.csproj` files for cleaner code

---

## Validation Checklist (Quality Criteria)

### Build Validation
- [ ] Solution builds: `dotnet build`
- [ ] No warnings in build output
- [ ] Tests run successfully: `dotnet test`
- [ ] All projects reference CPM correctly (no version attributes in PackageReference)

### CI/CD Validation
- [ ] Pipeline scripts execute locally: `.\cicd\scripts\validate-documentation.ps1`
- [ ] Pipeline YAML parses correctly
- [ ] Feed variables configured

### AI & Rules Validation
- [ ] `.cursor/rules/` directory exists with rules
- [ ] `.cursor/prompts/` directory exists with prompts
- [ ] Cursor AI recognizes rules (check Cursor "Rules" tab)
- [ ] `@activate-ticket` prompt works

### Documentation Validation
- [ ] `docs/` structure created (technical, implementation, rfcs)
- [ ] `tickets/templates/` exists
- [ ] README updated with project-specific content

### Git Validation
- [ ] `.gitignore` ignores `bin/`, `obj/`, `tickets/current.md`
- [ ] All Gold Standard files committed
- [ ] No untracked critical files

---

## Examples (Few-Shot)

### Example 1: Bootstrap New Domain Library Repository

**User Input**:
```
Bootstrap new repository called "eneve.billing.domain" using Gold Standard
```

**AI Reasoning**:
- **Repo Name**: eneve.billing.domain
- **Type**: Domain library (.NET class library)
- **Gold Standard**: Copy from eneve.domain
- **Customization Needed**: Company, Authors, RepositoryUrl, PackageTags
- **Follow 5-phase workflow**

**Expected Output**:
```markdown
## Bootstrapping eneve.billing.domain

**Reference**: eneve.domain (Gold Standard)

### Phase 1: Build Infrastructure ✅

**Files Copied**:
- Directory.Build.props (customization required)
- Directory.Packages.props
- global.json
- NuGet.Config
- .gitignore
- .editorconfig

**Customization Applied to Directory.Build.props**:
```xml
<PropertyGroup>
  <Authors>Energy21 Team</Authors>
  <Company>Energy21</Company>
  <RepositoryUrl>https://dev.azure.com/energy21/eneve.billing.domain</RepositoryUrl>
  <PackageTags>billing;domain;eneve;energy21</PackageTags>
</PropertyGroup>
```

### Phase 2: AI & Rules Setup ✅

**Copied**:
- Complete `.cursor/` directory (rules, prompts, templars)

**Verified**:
✓ Tag-based versioning rule exists
✓ Project setup rule exists
✓ Ticket prompts available

### Phase 3: CI/CD Setup ✅

**Created**:
- `cicd/` directory structure
- `cicd/azure-pipelines.yml` (from Gold Standard)
- `cicd/scripts/*.ps1` (all 15 scripts copied)

**Customized Pipeline**:
```yaml
variables:
  solutionPath: 'Eneve.Billing.Domain.sln'
  publishVstsFeed: 'Eneve-Test'
  prodVstsFeed: 'Eneve-Production'
```

### Phase 4: Documentation & Tickets ✅

**Created**:
- `docs/technical/`
- `docs/implementation/`
- `docs/rfcs/`
- `tickets/templates/` (copied from Gold Standard)

**README Updated**:
```markdown
# Eneve Billing Domain

Billing domain models and business logic for eNeve platform.

## Architecture
Domain-Driven Design with clean architecture principles.

## Build
`dotnet build`

## Test
`dotnet test`
```

### Phase 5: Solution Setup ✅

**Created Solution**:
```bash
dotnet new sln -n Eneve.Billing.Domain
```

**Created Projects**:
- `src/Eneve.Billing.Domain/` - Domain library
- `tst/Eneve.Billing.Domain.Tests/` - Unit tests

**Sanitized Projects**: Versions moved to `Directory.Packages.props`

### Validation Results ✅

```bash
# Build: SUCCESS
dotnet build
# Result: Build succeeded. 0 Warning(s), 0 Error(s)

# Tests: SUCCESS
dotnet test
# Result: Total tests: 2, Passed: 2

# Pipeline Validation: SUCCESS
.\cicd\scripts\validate-documentation.ps1
# Result: Documentation validation passed

# AI Rules: ACTIVE
# Cursor recognized 120 rules and 85 prompts
```

### Next Steps

```bash
# 1. Commit initial setup
git add .
git commit -m "chore: bootstrap repository from eneve.domain gold standard"

# 2. Push to remote
git push origin main

# 3. Configure Azure DevOps pipeline
# Point to: cicd/azure-pipelines.yml

# 4. Verify CI/CD pipeline runs successfully
```

**Repository is now ready for development!** ✅
```

---

## Common Pitfalls

### Pitfall 1: Forgot to Customize Directory.Build.props

**Symptom**: Package metadata still says "eneve.domain"

**Fix**: Update `<Authors>`, `<Company>`, `<RepositoryUrl>`, `<PackageTags>`

### Pitfall 2: Package Versions in .csproj Files

**Symptom**: Build warnings about version conflicts

**Fix**: Remove all `Version="X.Y.Z"` from `<PackageReference>`, add to `Directory.Packages.props`

### Pitfall 3: Missing CI/CD Scripts

**Symptom**: Pipeline fails with "script not found"

**Fix**: Ensure ALL scripts copied from `cicd/scripts/` (use `cp *.ps1`)

### Pitfall 4: .gitignore Missing tickets/current.md

**Symptom**: `tickets/current.md` appears in git status

**Fix**: Ensure `.gitignore` contains `tickets/current.md` (Gold Standard has this)

---

## Prerequisites Checklist

Before starting:

- [ ] New empty repository created in Azure DevOps
- [ ] Access to `eneve.domain` repository (Gold Standard)
- [ ] .NET 9 SDK installed (`dotnet --version`)
- [ ] Git initialized (`git init` in new repo)
- [ ] Azure DevOps pipeline permissions
- [ ] NuGet feed access (Test and Production)

---

## Post-Bootstrap Tasks

After completing bootstrap:

1. **Commit and Push**:
   ```bash
   git add .
   git commit -m "chore: bootstrap repository from eneve.domain gold standard"
   git push origin main
   ```

2. **Configure Azure DevOps Pipeline**:
   - Create new pipeline
   - Point to `cicd/azure-pipelines.yml`
   - Run initial build to verify

3. **Verify CI/CD**:
   - Check build passes
   - Verify validation scripts execute
   - Confirm package feeds configured

4. **Create Initial Ticket**:
   ```bash
   @activate-ticket EPP-XXX
   ```

5. **Start Development**:
   - Create feature branch
   - Begin implementing domain logic

---

## Related Prompts

- `setup/setup-project-standards.prompt.md` - Apply Gold Standard to existing project
- `setup/setup-repository-standards.prompt.md` - Configure repository standards
- `ticket/activate-ticket.prompt.md` - Start first ticket

---

## Related Rules

- `.cursor/rules/setup/project-setup-rule.mdc` - Gold Standard project structure
- `.cursor/rules/cicd/tag-based-versioning-rule.mdc` - Versioning and release strategy
- `.cursor/rules/git/branching-strategy-overview.mdc` - Git workflow

---

## Usage

**Basic bootstrap**:
```
@bootstrap-new-repo my-new-repo
```

**With explicit path to Gold Standard**:
```
@bootstrap-new-repo my-new-repo --gold-standard /path/to/eneve.domain
```

**Dry run (show what would be copied)**:
```
@bootstrap-new-repo my-new-repo --dry-run
```

---

**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
**Reference**: eneve.domain (Gold Standard Implementation)
