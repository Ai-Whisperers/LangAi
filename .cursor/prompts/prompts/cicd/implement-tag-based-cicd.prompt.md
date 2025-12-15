---
name: Implement Tag-Based Versioning CI/CD Pipeline
description: Step-by-step guide to implementing 60/60 Gold Standard CI/CD pipeline with two-stage RC workflow
category: cicd
tags: [pipeline, versioning, deployment, azure-devops, rc-workflow]
argument-hint: "[repository-path]"
---

# Prompt: Implement Tag-Based Versioning CI/CD Pipeline

**Category:** CI/CD Implementation  
**Type:** Step-by-Step Implementation Prompt  
**Complexity:** Medium  
**Time Estimate:** 2-3 hours  
**Version:** 4.0.0 (60/60 Gold Standard with Two-Stage RC)

---

## Objective

Implement a production-ready CI/CD pipeline using git tag-based versioning with **two-stage RC workflow** support for .NET repositories.

**This prompt produces:** 60/60 implementation (Gold Standard)
- ✅ Full pipeline operational (Build, Security, Coverage, Package, Publish)
- ✅ Tag parsing and version extraction
- ✅ **Two-Stage RC Workflow**: `test-*-rcN` → `release-*-rcN` → `release-*`
- ✅ Automated publishing: `test-*` to TEST feed, `release-*` to PROD feed
- ✅ NuGet prerelease support: `release-*-rcN` published as prerelease
- ✅ Maintenance release support for older version lines
- ✅ All quality gates enforced

---

## Prerequisites

### Required
- [ ] Azure DevOps project access
- [ ] Repository admin rights (to configure pipeline)
- [ ] .NET 9 SDK installed locally for testing
- [ ] Internal test NuGet feed created in Azure Artifacts
- [ ] Production NuGet feed created (Azure Artifacts or nuget.org)

---

## Step-by-Step Implementation

### Phase 1: Preparation (30 minutes)

#### 1.1 Review Template

Read and understand:
```
.cursor/templars/cicd/azure-pipelines-unified-template.yml
.cursor/rules/cicd/tag-based-versioning-rule.mdc
cicd/docs/TAGGING-GUIDE.md
```

#### 1.2 Identify Repository-Specific Values

Document these for your repository:
- Solution file name: `_____________________`
- Test project glob pattern: `_____________________`
- Internal test feed name: `_____________________`
- Production feed name: `_____________________`
- Repository URL: `_____________________`

#### 1.3 Check Existing Scripts

Verify these scripts exist in `cicd/scripts/`:
- [ ] `verify-xml-files.ps1`
- [ ] `validate-documentation.ps1`
- [ ] `generate-doc-report.ps1`

If missing, copy from `eneve.domain` reference repository.

---

### Phase 2: Pipeline Configuration (45 minutes)

#### 2.1 Copy Template

```bash
# Copy unified template to your repository
copy .cursor\templars\cicd\azure-pipelines-unified-template.yml cicd\azure-pipelines.yml
```

#### 2.2 Customize Variables

Edit `cicd/azure-pipelines.yml`:

```yaml
variables:
  buildConfiguration: 'Release'
  dotnetVersion: '9.x'
  solutionPath: 'YourSolution.sln'  # <-- UPDATE THIS
```

#### 2.3 Configure Publishing

Update the `NuGetCommand@2` tasks with your feed names:

```yaml
# Test Feed
inputs:
  publishVstsFeed: 'YourTestFeedName' # <-- UPDATE THIS

# Production Feed
inputs:
  publishVstsFeed: 'YourProductionFeedName' # <-- UPDATE THIS
```

#### 2.4 Adjust Paths if Needed

If your repository uses non-standard paths:

```yaml
trigger:
  paths:
    include:
      - src/**      # <-- Adjust if needed
      - tst/**      # <-- Adjust if needed
```

---

### Phase 3: Azure DevOps Setup (15 minutes)

#### 3.1 Create Pipeline

1. Navigate to Azure DevOps → Pipelines
2. Click "New Pipeline"
3. Select "Azure Repos Git"
4. Select your repository
5. Choose "Existing Azure Pipelines YAML file"
6. Select `/cicd/azure-pipelines.yml`
7. Click "Run" (will fail first time if no tests yet, expected)

#### 3.2 Configure Tag Triggers

Azure DevOps UI:
1. Edit pipeline
2. Click "Triggers" tab
3. Enable "Tag triggers"
4. **Verify** tag patterns are included:
   - `release-*`
   - `test-*`
   - `coverage-*`

---

### Phase 4: Local Testing (45 minutes)

#### 4.1 Test Build Locally

```bash
# Clean and build
dotnet clean
dotnet restore
dotnet build --configuration Release /p:TreatWarningsAsErrors=true
```

**Expected:** Build succeeds with zero warnings

#### 4.2 Test Documentation Scripts

```powershell
# Verify XML files generated
.\cicd\scripts\verify-xml-files.ps1 -Configuration Release

# Validate documentation completeness
.\cicd\scripts\validate-documentation.ps1 -Configuration Release
```

**Expected:** Scripts run successfully, no errors

---

### Phase 5: Pipeline Testing (45 minutes)

#### 5.1 Test Branch CI

```bash
# Create test feature branch
git checkout -b feature/test-cicd
git commit --allow-empty -m "test: trigger CI"
git push origin feature/test-cicd
```

**Expected:**
- Pipeline triggers automatically
- Stages 1-3 run (Build, Security, Coverage)
- No packaging or publishing
- Pipeline passes

#### 5.2 Test Internal RC Tag (Stage 1: TEST feed)

```bash
# Create internal RC tag
git tag -a test-0.0.1-rc1 -m "Internal RC1 for 0.0.1"
git push origin test-0.0.1-rc1
```

**Expected:**
- Pipeline triggers on tag
- All 5 stages run
- Package `YourPackage.0.0.1-rc1.nupkg` published to TEST feed
- Pipeline passes

#### 5.3 Verify Package in Test Feed

Azure DevOps → Artifacts → [YourTestFeed]:
- [ ] Package `YourPackage` version `0.0.1-rc1` appears

#### 5.4 Test External RC Tag (Stage 2: PROD feed as prerelease)

After internal QA passes:

```bash
# Create external RC tag (SAME commit as test-0.0.1-rc1)
git tag -a release-0.0.1-rc1 -m "Pre-prod RC1 for 0.0.1"
git push origin release-0.0.1-rc1
```

**Expected:**
- Pipeline triggers on tag
- Package `YourPackage.0.0.1-rc1.nupkg` published to PROD feed (as NuGet prerelease)
- Consumers can test with: `dotnet add package YourPackage --prerelease`

#### 5.5 Test GA Release Tag (Stage 3: PROD feed as stable)

After external testing passes:

```bash
# Merge to main (for current release line)
git checkout main
git merge release/0.0 --no-ff
git tag -a release-0.0.1 -m "Production release 0.0.1"
git push origin main release-0.0.1
```

**Expected:**
- Pipeline triggers on tag
- Package `YourPackage.0.0.1.nupkg` published to PROD feed (as stable)
- `dotnet add package YourPackage` now installs 0.0.1

---

### Phase 6: Documentation (30 minutes)

#### 6.1 Update Repository README

Add section to README.md:

```markdown
## Release Process

This repository uses tag-based versioning with **two-stage RC workflow**.

### Two-Stage Release Candidate Process

**Stage 1: Internal Testing (TEST feed)**
```bash
git tag -a test-X.Y.Z-rc1 -m "Internal RC1 for vX.Y.Z"
git push origin test-X.Y.Z-rc1
```
- Package published to TEST feed
- Internal QA team tests

**Stage 2: External Testing (PROD feed as prerelease)**
```bash
# After internal QA passes (SAME commit)
git tag -a release-X.Y.Z-rc1 -m "Pre-prod RC1 for vX.Y.Z"
git push origin release-X.Y.Z-rc1
```
- Package published to PROD feed as NuGet prerelease
- Consumers test with: `dotnet add package MyPackage --prerelease`

**Stage 3: GA Release (PROD feed as stable)**
```bash
# After external testing passes (SAME commit)
git checkout main
git merge release/X.Y --no-ff
git tag -a release-X.Y.Z -m "Production release vX.Y.Z"
git push origin main release-X.Y.Z
```
- Package published to PROD feed as stable
- Consumers get with: `dotnet add package MyPackage`
```

#### 6.2 Copy Tagging Guide

If not already present:
```bash
# Copy tagging guide to your repository
copy .cursor\templars\cicd\TAGGING-GUIDE.md cicd\docs\TAGGING-GUIDE.md
```

---

## Validation Checklist

### For 60/60 (Gold Standard with Two-Stage RC)

- [ ] Pipeline triggers on tags (`release-*`, `test-*`)
- [ ] Builds succeed with warnings-as-errors
- [ ] `test-*` tags publish to TEST feed
- [ ] `release-*-rcN` tags publish to PROD feed as NuGet prerelease
- [ ] `release-*` (no suffix) tags publish to PROD feed as stable
- [ ] Two-stage RC workflow followed: test-rc → release-rc → release
- [ ] Code immutability enforced: same commit between stages
- [ ] SBOM generated for all packages
- [ ] Security scanning fails on Critical/High vulnerabilities
- [ ] Documentation updated

---

## Troubleshooting

### Issue: "Feed not found"
**Check:** Feed name in `azure-pipelines.yml` matches Azure Artifacts exactly.

### Issue: "409 Conflict"
**Check:** You are trying to publish a version that already exists. Increment version (e.g., `rc1` -> `rc2`).

---

**Prompt Version:** 4.0.0  
**Last Updated:** 2025-12-05  
**Implementation Target:** 60/60 (Gold Standard with Two-Stage RC)  
**Reference:** eneve.domain  
**Related Rule:** `rule.cicd.tag-based-versioning.v2`

