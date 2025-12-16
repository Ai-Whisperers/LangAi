---
name: Setup CI/CD Documentation Pipeline
description: Create a complete CI/CD pipeline for documentation validation and testing
category: cicd
tags: [pipeline, documentation, validation, testing, azure-devops]
---

# Setup CI/CD Documentation Pipeline

## Overview

Create a complete CI/CD pipeline for .NET projects that automatically validates XML documentation completeness, runs all unit tests, and generates documentation coverage reports.

## Task

Set up a comprehensive Azure DevOps CI/CD pipeline in this repository that:

1. **Builds** all .NET projects with documentation warnings as errors
2. **Validates** XML documentation files are generated
3. **Checks** all public APIs are documented
4. **Runs** all unit tests with code coverage
5. **Generates** documentation coverage reports
6. **Publishes** test results and NuGet packages

## Requirements

### 1. Create CI/CD Folder Structure

Create a `cicd/` folder in the repository root with:

```
cicd/
├── azure-pipelines.yml
├── QUICK-START.md
├── README.md
└── scripts/
    ├── validate-documentation.ps1
    ├── verify-xml-files.ps1
    └── generate-doc-report.ps1
```

### 2. Azure Pipeline Configuration

Create `cicd/azure-pipelines.yml` with:

**Pipeline Features:**
- Triggers on push to `main`, `develop`, and `feature/*` branches
- Triggers on PRs targeting `main` and `develop`
- Uses .NET 9.x SDK (adjust version as needed for your project)
- Runs on Windows agents

**Build Steps:**
1. Install .NET SDK
2. Restore NuGet packages
3. Build solution with `/p:TreatWarningsAsErrors=true`
4. Verify XML documentation files exist
5. Run all unit tests with code coverage
6. Validate documentation completeness
7. Publish test results and coverage
8. Pack NuGet packages (main/develop only)
9. Generate documentation coverage report

**Stages:**
- **Build_and_Validate** - Main build and validation
- **Documentation_Report** - Generate coverage report

### 3. PowerShell Validation Scripts

#### validate-documentation.ps1
**Purpose:** Validates XML documentation completeness and quality

**Features:**
- Scans all source projects (exclude test projects)
- Checks XML file exists and has content
- Builds projects to detect documentation warnings (CS1591)
- Reports undocumented members
- Exit code 0 = pass, 1 = fail

**Parameters:**
- `Configuration` - Build configuration (default: Release)

#### verify-xml-files.ps1
**Purpose:** Verifies XML documentation files were generated

**Features:**
- Checks each project's bin folder for XML files
- Reports file sizes
- Lists missing files with expected paths
- Exit code 0 = all found, 1 = missing files

**Parameters:**
- `Configuration` - Build configuration (default: Release)

#### generate-doc-report.ps1
**Purpose:** Generates documentation coverage report

**Features:**
- Analyzes XML documentation for all projects
- Calculates coverage percentages
- Creates markdown report with project details
- Identifies projects needing attention
- Outputs to `$(Build.ArtifactStagingDirectory)/docs-report/`

### 4. Documentation Files

#### QUICK-START.md
**Content:**
- Quick setup instructions (5-10 minutes)
- Local testing commands
- Azure DevOps setup steps
- Branch protection setup
- Common scenarios and troubleshooting

#### README.md
**Content:**
- Complete pipeline documentation
- Script descriptions and usage
- Setup instructions
- Branch policy configuration
- Troubleshooting guide
- Related documentation links

### 5. Update .gitignore

Add comment section explaining XML files are not committed:

```gitignore
# XML Documentation Files (auto-generated during build)
# These are not committed as they are build artifacts
# Included automatically in NuGet packages
```

**Note:** XML files should already be ignored by `bin/` and `obj/` patterns.

### 6. Project Configuration Verification

**Verify** all source projects have in their `.csproj`:

```xml
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <EnableNETAnalyzers>true</EnableNETAnalyzers>
  <AnalysisLevel>latest</AnalysisLevel>
</PropertyGroup>
```

**For NuGet packages, also include:**

```xml
<PropertyGroup>
  <GeneratePackageOnBuild>true</GeneratePackageOnBuild>
  <IncludeSymbols>true</IncludeSymbols>
  <SymbolPackageFormat>snupkg</SymbolPackageFormat>
</PropertyGroup>
```

**If missing:** Add these settings to each source project file.

## Implementation Details

### Pipeline Variables

```yaml
variables:
  buildConfiguration: 'Release'
  dotnetVersion: '9.x'  # Adjust to your .NET version
```

### Key Pipeline Tasks

**Build with strict warnings:**
```yaml
- task: DotNetCoreCLI@2
  displayName: 'Build Solution (Treat Doc Warnings as Errors)'
  inputs:
    command: 'build'
    projects: '**/*.sln'
    arguments: '--configuration $(buildConfiguration) --no-restore /p:TreatWarningsAsErrors=true'
```

**Run all tests:**
```yaml
- task: DotNetCoreCLI@2
  displayName: 'Run Unit Tests'
  inputs:
    command: 'test'
    projects: 'tst/**/*.Tests.csproj'
    arguments: '--configuration $(buildConfiguration) --no-build --collect:"XPlat Code Coverage"'
    publishTestResults: true
```

**Validate documentation:**
```yaml
- task: PowerShell@2
  displayName: 'Validate Documentation Quality'
  inputs:
    targetType: 'filePath'
    filePath: 'cicd/scripts/validate-documentation.ps1'
    arguments: '-Configuration $(buildConfiguration)'
```

### Script Implementation Notes

**validate-documentation.ps1:**
- Use `Get-ChildItem -Path "src" -Filter "*.csproj" -Recurse` to find source projects
- Dynamically detect target framework from project file (e.g., `net8.0`, `net9.0`, `netstandard2.0`)
- Check for XML file at `bin/$Configuration/$TargetFramework/$ProjectName.xml`
- Use `dotnet build` to capture documentation warnings
- Parse output for `warning CS1591:` patterns
- Colorize output: Green = pass, Red = fail, Yellow = warnings

**verify-xml-files.ps1:**
- Similar project discovery as validate script
- Simply verify file existence and size
- Report all missing files before exiting

**generate-doc-report.ps1:**
- Load XML files as `[xml]` objects
- Count total members vs documented members
- Calculate coverage percentage per project
- Generate markdown table with results
- Add recommendations for projects < 75% coverage

### Local Testing Commands

Provide these commands for developers:

```powershell
# Build solution
dotnet build YourSolution.sln --configuration Release

# Verify XML files exist
.\cicd\scripts\verify-xml-files.ps1 -Configuration Release

# Validate documentation completeness
.\cicd\scripts\validate-documentation.ps1 -Configuration Release

# Generate coverage report
.\cicd\scripts\generate-doc-report.ps1
```

## Expected Outputs

### On Successful Run

- ✅ Build succeeds
- ✅ All XML files generated
- ✅ No documentation warnings
- ✅ All tests pass
- ✅ Code coverage published
- ✅ Documentation report generated
- ✅ NuGet packages created (main/develop)

### On Failed Documentation

- ❌ Build fails with CS1591 warnings
- 📋 Lists undocumented members
- 📊 Shows which projects failed
- 🔍 Provides file paths to fix

### Artifacts Published

1. **Test Results** - Viewable in Tests tab
2. **Code Coverage** - Viewable in Coverage tab
3. **NuGet Packages** - Downloadable artifacts
4. **Documentation Report** - Markdown report with coverage stats

## Verification Checklist

After implementation, verify:

- [ ] `cicd/` folder created with all files
- [ ] Azure pipeline YAML is syntactically valid
- [ ] All three PowerShell scripts are present
- [ ] Scripts run successfully locally
- [ ] README and QUICK-START guides created
- [ ] `.gitignore` updated with XML comment
- [ ] All source `.csproj` files have `<GenerateDocumentationFile>true</GenerateDocumentationFile>`
- [ ] Local test build succeeds
- [ ] Local XML verification succeeds
- [ ] Local documentation validation succeeds

## Azure DevOps Setup Steps

After files are committed:

1. Navigate to Azure DevOps → Pipelines → Create Pipeline
2. Select repository
3. Choose "Existing Azure Pipelines YAML file"
4. Select `/cicd/azure-pipelines.yml`
5. Run pipeline to verify it works
6. (Optional) Set up branch protection on `main`

## Branch Protection Setup

1. Go to Repos → Branches
2. Click `main` → Branch policies
3. Enable "Require a minimum number of reviewers"
4. Add Build Validation:
   - Build pipeline: Your new pipeline
   - Trigger: Automatic
   - Policy requirement: Required
5. Save

**Result:** All PRs must pass documentation validation before merge.

## Troubleshooting

### Pipeline Fails: "XML file NOT FOUND"

**Fix:** Add to project file:
```xml
<GenerateDocumentationFile>true</GenerateDocumentationFile>
```

### Pipeline Fails: "Documentation warnings (CS1591)"

**Fix:** Add XML comments to undocumented public members

### Scripts Don't Run Locally

**Fix:** Ensure PowerShell execution policy allows scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Related Documentation

- Documentation standards (if exists): `docs/DOCUMENTATION-STANDARDS.md`
- Documentation rules (if exists): `.cursor/rules/documentation/`
- Unit testing rules (if exists): `.cursor/rules/unit-testing/`

## Notes for AI Agents

- **Adjust .NET version** in pipeline to match project target framework
- **Adjust solution name** in build tasks to match repository
- **Adjust test project pattern** if different from `tst/**/*.Tests.csproj`
- **Check NuGet.Config** location if restore fails
- **Preserve existing** pipeline configurations if any
- **Don't commit** XML documentation files (they're build artifacts)

## Success Criteria

✅ Pipeline created and runs successfully
✅ Documentation validation catches missing docs
✅ All tests run and results published
✅ Code coverage collected and published
✅ NuGet packages include XML documentation
✅ Documentation report generated
✅ Local testing scripts work
✅ Quick start guide helps developers

---

**Template Version:** 1.0.0
**Created:** 2025-11-30
**Target:** Azure DevOps Pipelines
**Framework:** .NET 9.x (adaptable)
