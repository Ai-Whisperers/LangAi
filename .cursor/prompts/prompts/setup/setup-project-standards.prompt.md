---
name: setup-project-standards
description: "Please configure project-level standards (csproj, editorconfig) interactively or with defaults"
category: setup
tags: standards, project, configuration, quality, csproj, editorconfig
argument-hint: "interactive|default|[project-path]"
---

# Setup Project Standards (Interactive)

Please check and configure a project to follow Energy21 development standards, with optional interactive mode for customization.

**Pattern**: Project Standards Setup Pattern ⭐⭐⭐⭐  
**Effectiveness**: 90% coverage of standard requirements  
**Use When**: Starting new project, auditing existing project, ensuring standards compliance

---

## Purpose

Configure project-level standards to ensure consistent quality across all projects:
- **C#/.NET Projects**: `.csproj` settings, nullable types, warnings-as-errors, XML docs
- **EditorConfig**: Formatting, naming conventions, code style rules
- **Directory Structure**: Standard folder layout (src, tst, docs, tickets)
- **Git Configuration**: `.gitignore`, `.gitattributes`
- **Documentation**: README, XML docs enabled

Supports **Interactive Mode** (ask questions) or **Default Mode** (apply best practices).

---

## Required Context

- **Project Path**: Path to the project directory (current or specified)
- **Project Type**: C#/.NET, TypeScript, Python, etc. (auto-detect from files)
- **Interactive Mode**: Whether to ask questions or apply defaults
- **Current Settings**: Existing `.csproj`, `.editorconfig` if present

---

## Process

Follow this workflow to setup project standards:

### Step 1: Detect Project Type
Identify project type from file extensions and project files.

### Step 2: Load Current Configuration
Read existing settings (`.csproj`, `.editorconfig`, `.gitignore`).

### Step 3: Compare Against Standards
Identify gaps and non-compliant settings.

### Step 4: Interactive or Default Mode
Ask user preferences (interactive) or apply defaults (non-interactive).

### Step 5: Apply Configuration
Update project files with standard settings.

### Step 6: Validate
Verify settings applied correctly, build project.

---

## Reasoning Process (for AI Agent)

Before executing, the AI should:

1. **Identify Project Type**: Detect from file extensions (`.csproj` = .NET, `package.json` = Node, etc.)
2. **Load Current Configuration**: Read existing settings (csproj, editorconfig, gitignore)
3. **Compare Against Standards**: Identify gaps and non-compliant settings
4. **Interactive or Default**: Determine mode from user input or default to interactive
5. **Apply Configuration**: Update project files with standard settings (prompting if interactive)
6. **Validate**: Build project, check for new warnings/errors
7. **Report**: Show what was changed and validation results

---

## What This Checks and Configures

### For C#/.NET Projects

#### 1. Project File Settings (`.csproj`)

**Critical Settings**:
- ✅ `<Nullable>enable</Nullable>` - Nullable reference types enabled
- ✅ `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` - Warnings treated as errors
- ✅ `<GenerateDocumentationFile>true</GenerateDocumentationFile>` - XML documentation generation
- ✅ `<LangVersion>latest</LangVersion>` - Use latest C# version
- ✅ `<ImplicitUsings>enable</ImplicitUsings>` - Implicit usings for cleaner code

**Code Analysis Settings**:
- ✅ `<EnableNETAnalyzers>true</EnableNETAnalyzers>` - Enable .NET analyzers
- ✅ `<EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>` - Enforce code style
- ✅ StyleCop analyzers (optional, can enable in interactive mode)

#### 2. EditorConfig (`.editorconfig`)

**Formatting**:
- ✅ Consistent indent size (4 spaces for C#)
- ✅ Line endings (CRLF for Windows, LF for Unix)
- ✅ Trim trailing whitespace
- ✅ Insert final newline

**Naming Conventions**:
- ✅ PascalCase for classes, methods, properties
- ✅ camelCase for local variables, parameters
- ✅ _camelCase for private fields (optional, configurable)

**Code Style Rules**:
- ✅ Braces required for blocks
- ✅ Spacing around operators
- ✅ Expression-bodied members preferences
- ✅ var usage preferences

#### 3. Directory Structure

**Standard Layout**:
```
/src                 ← Source code
/tst                 ← Unit tests (or /tests)
/docs                ← Documentation
  /technical         ← Technical specifications
  /implementation    ← Implementation docs
  /rfcs              ← RFCs for future changes
/tickets             ← Ticket tracking
  /templates         ← Ticket templates
/.cursor             ← AI rules and prompts
  /rules             ← Cursor rules
  /prompts           ← Cursor prompts
```

#### 4. Git Configuration

**`.gitignore`**:
```
# Build results
[Bb]in/
[Oo]bj/

# IDE
.vs/
.vscode/
.idea/

# Ticket tracking
tickets/current.md

# User-specific
*.user
*.suo
```

**`.gitattributes`**:
```
* text=auto
*.cs text eol=lf
*.md text eol=lf
*.json text eol=lf
```

#### 5. Documentation

**README.md** (minimum sections):
```markdown
# Project Name

Brief description

## Build
`dotnet build`

## Test
`dotnet test`

## Architecture
[Overview]
```

**XML Documentation**: Enabled with `<GenerateDocumentationFile>true</GenerateDocumentationFile>`

---

## Interactive Questions

When run in interactive mode, the AI asks:

### 1. Project Identity
```
Project Name: [Current or prompt]
Description: [Brief project description]
Target Framework: net9.0, net8.0, net7.0? [Current or prompt]
```

### 2. Code Quality Standards
```
Treat warnings as errors? [Yes (recommended) / No]
  → Enforces zero-warning policy

Enable nullable reference types? [Yes (recommended) / No]
  → Prevents null reference exceptions

Generate XML documentation? [Yes / No]
  → Required for public libraries, optional for applications
```

### 3. Code Analysis
```
Enable StyleCop analyzers? [Yes / No]
  → Enforces code style consistency

Enable Microsoft.CodeAnalysis.NetAnalyzers? [Yes (recommended) / No]
  → Provides additional code quality checks

Severity for undocumented public APIs? [Warning / Error / None]
  → CS1591 warning level
```

### 4. Testing Standards
```
Unit test framework: [xUnit (recommended) / NUnit / MSTest]
  → Test framework preference

Code coverage requirement: [80% / 70% / 60% / Custom]
  → Minimum code coverage threshold
```

### 5. Git Standards
```
Branch naming convention: [feature/PROJ-#### / custom]
  → Feature branch pattern

Commit message format: [Conventional Commits / Custom]
  → Commit message standard
```

---

## Examples (Few-Shot)

### Example 1: Setup New C# Project (Interactive Mode)

**User Input**:
```
@setup-project-standards interactive
```

**AI Reasoning**:
- **Mode**: Interactive (user requested)
- **Project Type**: .NET (detected `.csproj`)
- **Current State**: Minimal `.csproj`, no `.editorconfig`
- **Action**: Ask questions, apply settings

**Expected Interaction**:
```markdown
## Project Standards Setup (Interactive)

**Project Detected**: MyLibrary.csproj (.NET 9 Class Library)

### Current Settings Analysis

❌ Missing: `<TreatWarningsAsErrors>`
❌ Missing: `<Nullable>enable`
❌ Missing: `.editorconfig`
✅ Present: `<GenerateDocumentationFile>`

---

### Configuration Questions

**Q1: Treat warnings as errors?**
This enforces zero-warning policy for highest code quality.
> [Yes (recommended) / No]: Yes

**Q2: Enable nullable reference types?**
Prevents null reference exceptions at compile time.
> [Yes (recommended) / No]: Yes

**Q3: Generate XML documentation?**
Required for public libraries, optional for applications.
> [Yes / No]: Yes

**Q4: Enable StyleCop analyzers?**
Enforces consistent code style across team.
> [Yes / No]: Yes

**Q5: Unit test framework?**
> [xUnit (recommended) / NUnit / MSTest]: xUnit

---

### Applying Configuration ✅

**Updated MyLibrary.csproj**:
```xml
<PropertyGroup>
  <TargetFramework>net9.0</TargetFramework>
  <Nullable>enable</Nullable>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <LangVersion>latest</LangVersion>
  <ImplicitUsings>enable</ImplicitUsings>
  <EnableNETAnalyzers>true</EnableNETAnalyzers>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="StyleCop.Analyzers" Version="1.1.118" />
</ItemGroup>
```

**Created .editorconfig**:
```ini
root = true

[*.cs]
indent_style = space
indent_size = 4
end_of_line = lf
trim_trailing_whitespace = true
insert_final_newline = true

# Naming conventions
dotnet_naming_rule.classes_should_be_pascal_case.severity = error
dotnet_naming_rule.classes_should_be_pascal_case.symbols = classes
dotnet_naming_rule.classes_should_be_pascal_case.style = pascal_case

# Code style
csharp_prefer_braces = true:error
csharp_space_after_keywords_in_control_flow_statements = true
```

---

### Validation ✅

**Build Test**:
```bash
dotnet build
# Result: Build succeeded. 2 Warning(s) (undocumented members)
```

**Action Required**: Add XML documentation to 2 public members

---

**Setup Complete!** ✅

**Next Steps**:
1. Add XML docs to public members
2. Run `dotnet build` to verify zero warnings
3. Commit changes: `git commit -m "chore: apply project standards"`
```

---

### Example 2: Setup Existing Project (Default Mode)

**User Input**:
```
@setup-project-standards default
```

**AI Reasoning**:
- **Mode**: Default (apply best practices without questions)
- **Project Type**: .NET (detected `.csproj`)
- **Current State**: Existing project with some settings
- **Action**: Apply Gold Standard defaults

**Expected Output**:
```markdown
## Project Standards Setup (Default Mode)

**Project**: ExistingProject.csproj
**Mode**: Default (applying best practices)

### Analysis

**Current Settings**:
✅ `<TargetFramework>net8.0`
❌ Missing `<Nullable>enable`
❌ Missing `<TreatWarningsAsErrors>`
✅ `<GenerateDocumentationFile>true`
❌ `.editorconfig` not found

### Applying Default Standards ✅

**Changes to ExistingProject.csproj**:
```diff
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
+  <Nullable>enable</Nullable>
+  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
+  <LangVersion>latest</LangVersion>
+  <ImplicitUsings>enable</ImplicitUsings>
+  <EnableNETAnalyzers>true</EnableNETAnalyzers>
+  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
</PropertyGroup>
```

**Created .editorconfig**: [Standard C# editorconfig]

**Created .gitignore**: [Standard .NET gitignore]

### Validation

```bash
dotnet build
# Result: Build succeeded with 0 Warning(s), 0 Error(s) ✅
```

**Setup Complete!** All standards applied. Project is ready for Gold Standard compliance.

**Commit Changes**:
```bash
git add .csproj .editorconfig .gitignore
git commit -m "chore: apply project standards (default mode)"
```
```

---

### Example 3: Audit Existing Project (No Changes)

**User Input**:
```
@setup-project-standards --audit-only
```

**AI Reasoning**:
- **Mode**: Audit (report only, no changes)
- **Action**: Compare against standards, report gaps

**Expected Output**:
```markdown
## Project Standards Audit

**Project**: MyApp.csproj

### Compliance Report

✅ **COMPLIANT** (8/10):
- ✅ Nullable reference types enabled
- ✅ Warnings as errors enabled
- ✅ XML documentation enabled
- ✅ .editorconfig present
- ✅ .gitignore present
- ✅ README.md present
- ✅ Target framework current (net9.0)
- ✅ Code analyzers enabled

❌ **NON-COMPLIANT** (2/10):
- ❌ Missing `<ImplicitUsings>enable`
- ❌ StyleCop analyzers not installed

### Recommendations

**High Priority**:
1. Add `<ImplicitUsings>enable</ImplicitUsings>` to .csproj
   → Reduces using statement clutter

**Medium Priority**:
2. Install StyleCop.Analyzers package
   → Enforces consistent code style

### Compliance Score: 80% (Good)

**Apply Fixes**:
```
@setup-project-standards default  # Apply all recommendations
```
```

---

## Quality Criteria

After applying standards, verify:

- [ ] `.csproj` file valid XML and builds successfully
- [ ] `.editorconfig` present and properly formatted
- [ ] `.gitignore` includes standard entries (bin, obj, .vs, tickets/current.md)
- [ ] `README.md` exists with project overview
- [ ] Project builds without errors: `dotnet build`
- [ ] All new warnings addressed or documented
- [ ] Nullable reference types enabled (if supported)
- [ ] XML documentation generated
- [ ] Code analyzers enabled
- [ ] Git attributes configured (line endings)

---

## Common Pitfalls

### Pitfall 1: Enabling Warnings-as-Errors in Legacy Project

**Symptom**: Hundreds of warnings become errors, build fails

**Solution**: Enable gradually:
1. Start with `<WarningLevel>4</WarningLevel>`
2. Fix warnings incrementally
3. Then enable `<TreatWarningsAsErrors>true`

### Pitfall 2: Nullable Reference Types Break Existing Code

**Symptom**: Many null-related warnings after enabling

**Solution**:
1. Enable with `<Nullable>enable`
2. Add `#nullable disable` to legacy files
3. Fix incrementally, remove pragma as fixed

### Pitfall 3: StyleCop Too Strict for Team

**Symptom**: Team rejects StyleCop rules

**Solution**: Customize `.editorconfig` to team preferences, or use analyzers only without StyleCop

---

## Related Prompts

- `setup/bootstrap-new-repo.prompt.md` - Bootstrap entire repository from Gold Standard
- `setup/setup-repository-standards.prompt.md` - Repository-level standards (git, CI/CD)

---

## Related Rules

- `.cursor/rules/code-quality-and-best-practices.mdc` - Code quality standards
- `.cursor/rules/code-writing-standards.mdc` - Code writing guidelines
- `.cursor/rules/documentation/documentation-standards-rule.mdc` - Documentation requirements
- `.cursor/rules/git/branch-naming-rule.mdc` - Git branch naming standards

---

## Usage

**Non-interactive (apply defaults)**:
```
@setup-project-standards
@setup-project-standards default
```

**Interactive mode**:
```
@setup-project-standards interactive
```

**Specific project**:
```
@setup-project-standards ./path/to/project
```

**Audit only (no changes)**:
```
@setup-project-standards --audit-only
```

---

**Created**: 2025-12-02  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)  
**Pattern ID**: #7 Project Standards Setup
