---
name: setup-repository-standards
description: "Please configure repository-wide standards (structure, docs, tickets, build infrastructure)"
category: setup
tags: repository, standards, structure, build-infrastructure, cicd
argument-hint: "interactive|default|[repo-path]"
---

# Setup Repository Standards (Interactive)

Please check and configure an entire repository to follow Energy21 development standards, including solution structure, documentation architecture, ticket system, and CI/CD setup.

**Pattern**: Repository Standards Setup Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: 95% coverage of repository requirements
**Use When**: Initializing new repository, auditing existing repository, enforcing organizational standards

---

## Purpose

Configure repository-wide standards to ensure consistent structure and tooling across all repositories:
- **Build Infrastructure**: Central Package Management (Directory.Build.props), SDK pinning (global.json)
- **Repository Structure**: Standard folder layout (src, tst, docs, tickets, .cursor)
- **Git Configuration**: `.gitignore`, `.gitattributes`, branch structure documentation
- **Documentation Architecture**: Three-folder pattern (technical, implementation, rfcs)
- **Ticket System**: Standard ticket structure with templates
- **Cursor Configuration**: Complete rules and prompts setup
- **CI/CD**: Pipeline configuration with code coverage, security scanning, SBOM

Supports **Interactive Mode** (ask questions) or **Default Mode** (apply organizational best practices).

---

## Required Context

- **Repository Path**: Path to the repository root
- **Repository Type**: Solution with multiple projects, monorepo, or single project
- **Interactive Mode**: Whether to ask questions or apply defaults
- **Current Structure**: Existing folders, solution files, configuration

---

## Process

Follow this workflow to setup repository standards:

### Step 1: Analyze Repository Structure
Detect solution files, projects, existing standards.

### Step 2: Load Current Configuration
Read `.gitignore`, `.editorconfig`, solution structure.

### Step 3: Compare Against Standards
Identify gaps in structure, documentation, tooling.

### Step 4: Interactive or Default Mode
Ask user preferences (interactive) or apply defaults (non-interactive).

### Step 5: Apply Configuration
Create/update repository-wide files and structure.

### Step 6: Validate
Verify structure and build successfully.

---

## Reasoning Process (for AI Agent)

Before executing, the AI should:

1. **Analyze Repository Structure**: Detect solution files, projects, existing standards
2. **Load Current Configuration**: Read .gitignore, .editorconfig, Directory.Build.props, solution structure
3. **Compare Against Standards**: Identify gaps (missing folders, missing config files, outdated structure)
4. **Interactive or Default**: Determine mode from user input or default to interactive
5. **Apply Configuration**: Create/update repository-wide files (build props, docs folders, ticket structure)
6. **Sanitize Projects**: Remove version attributes from .csproj, consolidate to Directory.Build.props
7. **Validate**: Build solution, verify structure complete
8. **Report**: Show what was changed, what needs manual review

---

## What This Checks and Configures

### 0. Build Infrastructure (Professional Setup)

#### Central Package Management & Build Properties

**`Directory.Build.props`** (Consolidated build settings):
```xml
<Project>
  <PropertyGroup>
    <!-- Central Package Management -->
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>

    <!-- Shared Settings -->
    <TargetFramework>net9.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>

    <!-- Code Analysis -->
    <EnableNETAnalyzers>true</EnableNETAnalyzers>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>

    <!-- Documentation -->
    <GenerateDocumentationFile>true</GenerateDocumentationFile>

    <!-- Deterministic Builds -->
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>

    <!-- Package Metadata -->
    <Authors>Your Team</Authors>
    <Company>Your Company</Company>
    <Copyright>Copyright © Your Company</Copyright>
    <RepositoryUrl>https://dev.azure.com/org/repo</RepositoryUrl>

    <!-- Source Link -->
    <PublishRepositoryUrl>true</PublishRepositoryUrl>
    <EmbedUntrackedSources>true</EmbedUntrackedSources>
    <IncludeSymbols>true</IncludeSymbols>
    <SymbolPackageFormat>snupkg</SymbolPackageFormat>
  </PropertyGroup>

  <ItemGroup>
    <!-- Package Versions (Central) -->
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageVersion Include="FluentAssertions" Version="6.12.0" />
    <PackageVersion Include="xunit" Version="2.6.1" />
    <!-- Add all package versions here -->
  </ItemGroup>
</Project>
```

**`global.json`** (SDK pinning):
```json
{
  "sdk": {
    "version": "9.0.100",
    "rollForward": "latestFeature"
  }
}
```

**`NuGet.Config`** (Package sources):
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="Azure Artifacts" value="https://pkgs.dev.azure.com/org/_packaging/feed/nuget/v3/index.json" />
  </packageSources>
</configuration>
```

#### After Creating Directory.Build.props
- **Update ALL .csproj files**: Remove `Version` attributes from `<PackageReference>`
- **Remove duplicated settings**: Delete `<TargetFramework>`, `<Nullable>`, etc. from .csproj (now in Directory.Build.props)
- **Delete Directory.Packages.props**: If exists, merge into Directory.Build.props

---

### 1. Repository Structure

**Standard Directory Layout**:
```
repository-root/
├── .cursor/                  # Cursor configuration
│   ├── rules/               # Code quality and development rules
│   └── prompts/             # Reusable prompt patterns
├── src/                     # Source code
│   ├── ProjectName/         # Main project(s)
│   └── ProjectName.Tests/   # Test project(s) (alternative: tst/)
├── tst/                     # Alternative test folder
├── docs/                    # Documentation
│   ├── technical/           # Technical specifications (WHAT)
│   ├── implementation/      # Implementation guides (HOW)
│   └── rfcs/                # Proposals and RFCs (FUTURE)
├── tickets/                 # Ticket tracking
│   ├── current.md          # Active ticket (local only, not committed)
│   ├── templates/          # Ticket templates
│   └── EPIC-###/           # Ticket folders
├── conversations/           # Conversation history (sanitized)
│   └── [INITIALS]/         # Per-developer conversations
├── cicd/                    # CI/CD configuration
│   ├── azure-pipelines.yml  # Azure DevOps pipeline
│   └── scripts/            # Build and validation scripts
├── .github/                 # GitHub configuration (if GitHub)
│   └── workflows/          # CI/CD workflows
├── .gitignore              # Git ignore rules
├── .gitattributes          # Git attributes
├── .editorconfig           # Editor configuration
├── README.md               # Repository overview
├── CHANGELOG.md            # Version history (Keep a Changelog format)
├── CONTRIBUTING.md         # Contribution guidelines (optional)
└── Solution.sln            # Solution file
```

---

### 2. Git Configuration

**`.gitignore`** (Standard entries):
```
# Build results
[Bb]in/
[Oo]bj/

# IDE
.vs/
.vscode/
.idea/
*.user
*.suo

# Ticket tracking (local only)
tickets/current.md

# NuGet
*.nupkg
*.snupkg
```

**`.gitattributes`** (Line ending normalization):
```
* text=auto
*.cs text eol=lf
*.md text eol=lf
*.json text eol=lf
*.yml text eol=lf
*.xml text eol=lf
```

**Branch Structure Documentation** (Git Flow):
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/PROJ-####-description` - Feature branches
- `fix/PROJ-####-description` - Bug fix branches
- `hotfix/PROJ-####-description` - Hotfix branches
- `release/vX.Y.Z` - Release branches

---

### 3. Documentation Architecture

**Three-Folder Pattern**:
- **`docs/technical/`** - WHAT exists (current system specs, domain documentation)
- **`docs/implementation/`** - HOW to build (implementation guides, architecture decisions)
- **`docs/rfcs/`** - FUTURE proposals (design decisions, proposals for future work)

**Standard Files**:
- **`README.md`** - Repository overview (purpose, build instructions, architecture)
- **`CONTRIBUTING.md`** - Contribution guidelines (optional)
- **`CHANGELOG.md`** - Version history (Keep a Changelog format)
- **`docs/technical/README.md`** - Technical documentation index
- **`docs/implementation/README.md`** - Implementation guide index
- **`docs/PROJECT-SETUP-TRACKER.md`** - Setup tracking document

---

### 4. Ticket System Setup

**Standard Structure**:
```
tickets/
├── current.md              # Active ticket (local, not committed)
├── templates/              # Ticket templates
│   ├── plan-template.md
│   ├── context-template.md
│   └── progress-template.md
├── EPP-###/               # Epic folder
│   ├── plan.md            # Epic plan
│   ├── progress.md        # Epic progress
│   └── TICKET-###/        # Individual tickets
│       ├── plan.md
│       ├── context.md
│       ├── progress.md
│       ├── timeline.md
│       ├── recap.md
│       └── references.md
```

**Configuration**:
- Ticket templates in `tickets/templates/`
- `.gitignore` entry for `tickets/current.md` (local-only tracking)

---

### 5. Cursor Configuration

**Rules Setup**:
```
.cursor/
└── rules/
    ├── clean-code.mdc
    ├── code-quality-and-best-practices.mdc
    ├── ticket/
    │   ├── ticket-workflow-rule.mdc
    │   ├── plan-rule.mdc
    │   ├── context-rule.mdc
    │   └── progress-rule.mdc
    ├── git/
    │   ├── branching-strategy-overview.mdc
    │   ├── branch-naming-rule.mdc
    │   └── branch-lifecycle-rule.mdc
    └── documentation/
        ├── documentation-standards-rule.mdc
        └── documentation-architecture-rule.mdc
```

**Prompts Setup**:
```
.cursor/
└── prompts/
    ├── ticket/
    │   ├── activate-ticket.prompt.md
    │   ├── complete-ticket.prompt.md
    │   └── switch-ticket.prompt.md
    ├── setup/
    │   ├── bootstrap-new-repo.prompt.md
    │   ├── setup-project-standards.prompt.md
    │   └── setup-repository-standards.prompt.md
    └── housekeeping/
        ├── archive-obsolete-artifacts.prompt.md
        └── consolidate-duplicates.prompt.md
```

---

### 6. CI/CD Configuration

#### Azure DevOps Pipeline

**`cicd/azure-pipelines.yml`**:
```yaml
trigger:
  branches:
    include:
      - main
      - develop
      - release/*

variables:
  solution Path: '**/*.sln'
  buildConfiguration: 'Release'

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: DotNetCoreCLI@2
            displayName: 'Restore'
            inputs:
              command: 'restore'

          - task: DotNetCoreCLI@2
            displayName: 'Build'
            inputs:
              command: 'build'
              arguments: '--configuration $(buildConfiguration) --no-restore'

          - task: DotNetCoreCLI@2
            displayName: 'Test'
            inputs:
              command: 'test'
              arguments: '--configuration $(buildConfiguration) --no-build --collect:"XPlat Code Coverage"'

          - script: |
              dotnet list package --vulnerable --include-transitive
            displayName: 'Security Scan'
```

#### CI/CD Enhancements (Professional Setup)

**1. Code Coverage Thresholds (per branch)**:
- `main`: 80% minimum coverage
- `develop`: 75% minimum coverage
- `feature/*`: 70% minimum coverage
- Fail build if coverage drops below threshold
- Use ReportGenerator for coverage analysis

**2. Security Scanning**:
- Run `dotnet list package --vulnerable --include-transitive`
- Report vulnerable packages
- Warn on any vulnerabilities
- Option to fail on Critical/High severity

**3. SBOM Generation (Software Bill of Materials)**:
- Install CycloneDX tool
- Generate `sbom.json` for the solution
- Publish SBOM as build artifact
- Only run on `main`/`develop` branches

---

## Examples (Few-Shot)

### Example 1: Setup New Repository (Interactive Mode)

**User Input**:
```
@setup-repository-standards interactive
```

**AI Reasoning**:
- **Mode**: Interactive (user requested)
- **Repository**: Detected empty repository with .git
- **Current State**: No structure, no configuration
- **Action**: Ask questions, create complete structure

**Expected Interaction**:
```markdown
## Repository Standards Setup (Interactive)

**Repository Detected**: Empty repository (initialized with git)

### Configuration Questions

**Q1: Repository type?**
> [Solution with multiple projects (recommended) / Single project / Monorepo]: Solution

**Q2: Test folder name?**
> [tst (Energy21 standard) / tests]: tst

**Q3: Include conversations folder?**
> [Yes / No]: Yes

**Q4: CI/CD platform?**
> [Azure DevOps / GitHub Actions / Both]: Azure DevOps

**Q5: Enable security scanning?**
> [Yes (recommended) / No]: Yes

**Q6: Generate SBOM?**
> [Yes (recommended) / No]: Yes

---

### Creating Repository Structure ✅

**Folders Created**:
```
✓ .cursor/rules/
✓ .cursor/prompts/
✓ src/
✓ tst/
✓ docs/technical/
✓ docs/implementation/
✓ docs/rfcs/
✓ tickets/templates/
✓ conversations/
✓ cicd/scripts/
```

**Files Created**:
```
✓ Directory.Build.props (Central Package Management)
✓ global.json (SDK pinning to 9.0.100)
✓ NuGet.Config (Package sources)
✓ .gitignore (Standard .NET ignores)
✓ .gitattributes (Line ending normalization)
✓ .editorconfig (Code style rules)
✓ README.md (Repository overview template)
✓ CHANGELOG.md (Keep a Changelog format)
✓ docs/PROJECT-SETUP-TRACKER.md
✓ cicd/azure-pipelines.yml (with security scanning + SBOM)
```

**Cursor Configuration**:
```
✓ Copied .cursor/rules/ from Gold Standard
✓ Copied .cursor/prompts/ from Gold Standard
✓ Total: 120 rules, 85 prompts
```

---

### Validation ✅

**Structure Verification**:
```
✓ All required folders exist
✓ All configuration files present
✓ .gitignore includes tickets/current.md
✓ Directory.Build.props valid XML
```

**Next Steps**:
1. Create solution: `dotnet new sln -n MyRepo`
2. Create projects: `dotnet new classlib -n MyRepo.Domain`
3. Add to solution: `dotnet sln add src/MyRepo.Domain/MyRepo.Domain.csproj`
4. Commit: `git commit -m "chore: setup repository standards"`

**Repository is ready for development!** ✅
```

---

## Quality Criteria

After applying standards, verify:

- [ ] All required folders exist (src, tst, docs, tickets, .cursor, cicd)
- [ ] `Directory.Build.props` created with Central Package Management
- [ ] `global.json` pins SDK version
- [ ] `NuGet.Config` configured with package sources
- [ ] `.gitignore` includes standard entries + `tickets/current.md`
- [ ] `.gitattributes` normalizes line endings
- [ ] `.editorconfig` defines code style
- [ ] README.md exists with project overview
- [ ] CHANGELOG.md created (Keep a Changelog format)
- [ ] Documentation folders created (technical, implementation, rfcs)
- [ ] Ticket templates exist
- [ ] Cursor rules and prompts installed
- [ ] CI/CD pipeline configured (Azure DevOps or GitHub Actions)
- [ ] Security scanning enabled (if requested)
- [ ] SBOM generation configured (if requested)
- [ ] Solution builds successfully
- [ ] All .csproj files sanitized (no version attributes)

---

## Related Prompts

- `setup/bootstrap-new-repo.prompt.md` - Complete repository bootstrap from Gold Standard
- `setup/setup-project-standards.prompt.md` - Project-level standards (csproj, editorconfig)
- `ticket/activate-ticket.prompt.md` - Start first ticket

---

## Related Rules

- `.cursor/rules/git/branching-strategy-overview.mdc` - Git branch structure and workflow
- `.cursor/rules/ticket/ticket-workflow-rule.mdc` - Ticket management workflow
- `.cursor/rules/documentation/documentation-architecture-rule.mdc` - Three-folder documentation pattern
- `.cursor/rules/code-quality-and-best-practices.mdc` - Code quality standards
- `.cursor/rules/setup/project-setup-rule.mdc` - Gold Standard project structure

---

## Usage

**Non-interactive (apply defaults)**:
```
@setup-repository-standards
@setup-repository-standards default
```

**Interactive mode**:
```
@setup-repository-standards interactive
```

**Specific repository**:
```
@setup-repository-standards /path/to/repo
```

**Audit only (no changes)**:
```
@setup-repository-standards --audit-only
```

---

**Created**: 2025-12-02
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
**Updated**: 2025-12-04 (Added professional setup items - Directory.Build.props, security scanning, SBOM)
**Pattern ID**: #8 Repository Standards Setup

---

## Changelog

### 2025-12-08 - Comprehensive Improvement (PROMPTS-OPTIMIZE)
- Added Purpose section
- Added User Process section
- Added Few-Shot examples
- Renamed validation to Quality Criteria
- Fixed Related Standards format
- Updated provenance footer

### 2025-12-04 - Professional Setup Items Added
Based on eneve.ebase.foundation implementation:
- Added Section 0: Build Infrastructure (Directory.Build.props, global.json, NuGet.Config)
- Added CI/CD enhancements (coverage thresholds, security scanning, SBOM)
- Added CHANGELOG.md and PROJECT-SETUP-TRACKER.md to standard files
- Expanded validation checklist
- Source: Foundation setup session with complete implementation
