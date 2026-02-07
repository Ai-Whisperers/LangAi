---
id: prompt.setup.readme.v1
kind: documentation
version: 1.0.0
description: Documentation for Setup Prompts
provenance:
  owner: team-setup
  last_review: 2025-12-06
---

# Setup Prompts - Quick Reference

This folder contains interactive prompts for setting up and enforcing development standards across projects and repositories.

## Available Prompts

### 1. Setup Project Standards
**File**: `setup-project-standards.md`
**Use When**: Configuring individual project (`.csproj` level)
**Scope**: Single project configuration

**What it configures:**
- Project file settings (.csproj)
- EditorConfig (.editorconfig)
- Git ignore rules (.gitignore)
- Code analyzers (StyleCop, .NET Analyzers)
- Documentation generation
- Testing framework

**Quick Usage:**
```
setup project standards
```

**Interactive Mode:**
```
setup project standards (interactive)
```

---

### 2. Setup Repository Standards
**File**: `setup-repository-standards.md`
**Use When**: Initializing or auditing entire repository
**Scope**: Repository-wide configuration

**What it configures:**
- Directory structure (src/, docs/, tickets/, .cursor/)
- Git configuration (.gitignore, .gitattributes, branching strategy)
- Documentation architecture (three-folder pattern)
- Ticket tracking system
- Cursor rules and prompts
- CI/CD workflows
- Repository documentation (README, CONTRIBUTING)

**Quick Usage:**
```
setup repository standards
```

**Interactive Mode:**
```
setup repository standards (interactive)
```

**Audit Mode (Check Only):**
```
audit repository standards
```

---

## When to Use Which

### Use Project Standards When:
- Setting up a new project in existing repository
- Applying code quality standards to specific project
- Configuring analyzers and documentation for one project
- Ensuring .csproj settings match organizational standards

### Use Repository Standards When:
- Initializing a brand new repository
- Standardizing structure across organization
- Setting up ticket tracking and documentation
- Configuring Git strategy and CI/CD
- Creating consistent developer experience

### Use Both When:
Starting a new repository with one or more projects:
1. **First**: `setup repository standards (interactive)` - Creates structure
2. **Then**: `setup project standards` for each project - Configures individual projects

---

## Interactive vs Default Mode

### Interactive Mode
**When to use:**
- First time setup
- Need to customize standards
- Want to understand options
- Different requirements than defaults

**What it does:**
- Asks questions about each configuration area
- Explains recommendations
- Allows custom values
- Shows what will be changed before applying

**Example:**
```
setup repository standards (interactive)

> Repository Type: [Solution / Monorepo / Library]
> Git branching: [Git Flow / GitHub Flow]
> Setup CI/CD: [Yes / No]
> Platform: [GitHub Actions / Azure DevOps]
```

### Default Mode
**When to use:**
- Batch setup of multiple projects/repositories
- Accept organizational standards as-is
- Quick setup without customization
- Consistent configuration across teams

**What it does:**
- Applies Energy21 standard configuration
- No questions asked
- Fast execution
- Reports what was changed

**Example:**
```
setup repository standards

> Applying Energy21 standards...
> ✅ Created standard directory structure
> ✅ Applied Git configuration
> ✅ Setup ticket system
> Done!
```

---

## Common Workflows

### Workflow 1: New Repository from Scratch

```bash
# 1. Create repository on GitHub/Azure DevOps
# 2. Clone locally
git clone <repository-url>
cd <repository-name>

# 3. Setup repository structure (interactive first time)
setup repository standards (interactive)

# 4. Review changes
git status

# 5. Commit configuration
git add .
git commit -m "Setup repository standards"

# 6. Create develop branch
git checkout -b develop
git push --all origin

# 7. For each project in src/:
setup project standards

# 8. Build and verify
dotnet build
```

### Workflow 2: Standardize Existing Repository

```bash
# 1. Audit current state
audit repository standards

# 2. Review gaps and recommendations
# (AI shows what's missing/non-compliant)

# 3. Apply standards (interactive to customize)
setup repository standards (interactive)

# 4. Review changes carefully
git diff

# 5. Commit in stages
git add docs/
git commit -m "Add documentation architecture"

git add tickets/
git commit -m "Setup ticket tracking system"

git add .cursor/
git commit -m "Add Cursor rules and prompts"
```

### Workflow 3: Standardize Multiple Projects

```bash
# For each project in src/:

# 1. Navigate to project or reference it
cd src/ProjectName
# OR
@src/ProjectName/ProjectName.csproj

# 2. Apply standards (default mode for consistency)
setup project standards

# 3. Fix any new warnings
dotnet build
# (Fix warnings introduced by TreatWarningsAsErrors)

# 4. Commit when clean
git add src/ProjectName/
git commit -m "Apply project standards to ProjectName"
```

---

## What Gets Modified

### Project Standards Modifies:
- `*.csproj` - Adds properties and package references
- `.editorconfig` - Creates or updates formatting rules
- `.gitignore` - Adds project-specific entries
- `README.md` - Creates project README if missing

**Does NOT modify:**
- Source code files (*.cs)
- Test files
- Configuration files (appsettings.json)

### Repository Standards Creates/Modifies:
- **Creates**: docs/, tickets/, .cursor/, conversation/, directory structure
- **Creates**: README.md, CONTRIBUTING.md, documentation index files
- **Modifies**: .gitignore, .gitattributes
- **Creates**: .github/workflows/ or azure-pipelines.yml (if CI/CD enabled)

**Does NOT modify:**
- Existing source code
- Existing projects (.csproj)
- Existing documentation content

---

## Validation and Safety

Both prompts include validation steps:

### Before Applying Changes:
- Analyzes current state
- Identifies what will change
- In interactive mode: Shows changes before applying

### After Applying Changes:
- Verifies files created successfully
- Checks solution/project builds
- Reports any errors encountered
- Provides manual action checklist

### Safety Features:
- Never modifies source code
- Never commits changes automatically
- Always reports what was changed
- Provides rollback guidance if issues occur

---

## OPSEC and Security

Both prompts follow security best practices:

**Never Includes:**
- ❌ Connection strings
- ❌ API keys or credentials
- ❌ Internal server names or URLs
- ❌ Customer data or production identifiers

**Always Ensures:**
- ✅ Secrets documented as environment variables
- ✅ Sensitive files added to .gitignore
- ✅ Templates use placeholder values
- ✅ Configuration references Key Vault/environment

---

## Troubleshooting

### Build fails after applying project standards

**Issue**: `TreatWarningsAsErrors` causes build to fail
**Fix**:
1. Review warnings: `dotnet build`
2. Fix warnings incrementally
3. Or temporarily disable: `<TreatWarningsAsErrors>false</TreatWarningsAsErrors>`
4. Re-enable when code is clean

### Directory creation fails

**Issue**: Permission denied or conflicts
**Fix**:
1. Check file system permissions
2. Verify no conflicting files exist
3. Create directories manually: `mkdir -p docs/technical docs/implementation docs/rfcs`
4. Run setup again

### Git ignores expected files

**Issue**: .gitignore too aggressive
**Fix**:
1. Review .gitignore entries
2. Use `git add -f <file>` to force add specific files
3. Adjust .gitignore rules
4. Commit corrections

---

## Related Documentation

- **Cursor Rules**: `@/.cursor/rules/` - Standards enforced by these prompts
- **Ticket Workflow**: `@/.cursor/rules/ticket/ticket-workflow-rule.mdc`
- **Git Strategy**: `@/.cursor/rules/git/branching-strategy-overview.mdc`
- **Documentation**: `@/.cursor/rules/documentation/documentation-architecture-rule.mdc`

---

## Examples Output

### Project Standards Report
```markdown
## Project Standards Setup Complete

**Project**: Eneve.eBase.DataMigrator
**Type**: C# .NET 8.0
**Mode**: Default

### Changes Applied:
✅ Updated .csproj: Nullable, TreatWarningsAsErrors, Documentation
✅ Created .editorconfig with standard formatting rules
✅ Added code analyzers: Microsoft.CodeAnalysis.NetAnalyzers
✅ Updated .gitignore with .NET standard entries

### Manual Actions Required:
- [ ] Fix new warnings from TreatWarningsAsErrors
- [ ] Add XML documentation to undocumented public APIs
- [ ] Run `dotnet build` to verify configuration

### Next Steps:
1. Run: dotnet build
2. Fix any warnings
3. Commit changes: git add . && git commit -m "Apply project standards"
```

### Repository Standards Report
```markdown
## Repository Standards Setup Complete

**Repository**: eneve.ebase.datamigrator
**Type**: .NET Solution
**Mode**: Interactive

### Structure Created:
✅ docs/technical/ - Technical specifications
✅ docs/implementation/ - Implementation guides
✅ docs/rfcs/ - Design proposals
✅ tickets/ - Ticket tracking with templates
✅ .cursor/rules/ - Code quality rules
✅ .cursor/prompts/ - Reusable prompts

### Configuration Applied:
✅ .gitignore - Standard entries
✅ .gitattributes - Line ending normalization
✅ README.md - Repository overview template
✅ CONTRIBUTING.md - Contribution guidelines

### Manual Actions Required:
- [ ] Review and customize README.md
- [ ] Commit configuration changes
- [ ] Create 'develop' branch
- [ ] Setup branch protection rules on GitHub

### Next Steps:
1. git add . && git commit -m "Setup repository standards"
2. git checkout -b develop
3. git push --all origin
```

---

**Created**: 2025-12-02
**Maintained By**: Development Standards Team
**Related**: EBASE-TEMP-004 (Architectural improvements)
