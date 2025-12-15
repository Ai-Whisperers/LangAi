---
name: fix-incomplete-metadata
description: "AI-assisted prompt for fixing incomplete NuGet package metadata"
category: cicd
tags: cicd, nuget, metadata, package, quality
argument-hint: "Project file path"
---

# Fix Incomplete Package Metadata

**Pattern**: Error Resolution Helper | **Effectiveness**: High | **Use When**: CI/CD validation reports incomplete NuGet package metadata

## Purpose

Guide developers through fixing incomplete NuGet package metadata issues flagged by CI/CD validation, providing multiple resolution paths (automated, AI-assisted, manual) with clear steps and quality standards.

## User Process

When you encounter incomplete metadata errors from CI/CD:

1. **Identify the Issue**: Review error message specifying which metadata fields are missing
2. **Choose Fix Method**: Select automated (quick defaults), AI-assisted (quality), or manual (full control)
3. **Apply Fix**: Execute chosen method to add missing metadata properties
4. **Customize Values**: Replace defaults with accurate, project-specific information
5. **Validate**: Run validation script to confirm all metadata is complete and correct
6. **Commit**: Add fixed `.csproj` file to version control

## Context

Your project is missing required NuGet package metadata. For published packages and professional projects, complete metadata is mandatory.

## What's Wrong

Missing or incomplete properties in your `.csproj` file that are required for high-quality NuGet packages.

## Automated Fix

Run this command to add missing metadata with defaults:

```powershell
cd cicd/scripts
.\fix-warnings.ps1 -Fix IncompleteMetadata -Path "<PROJECT_FILE>.csproj"
```

**What it does:**
- Adds missing required properties
- Uses sensible defaults
- **You must review and customize values!**

## AI-Assisted Fix (Recommended)

Ask me (Cursor AI) to add complete, accurate metadata:

### Prompt Template

```
Complete the NuGet package metadata in <PROJECT_FILE>.csproj.

Add these properties to the first <PropertyGroup>:

Required:
- Authors: <YOUR_ORGANIZATION>
- Company: <YOUR_COMPANY>
- Description: <MEANINGFUL_DESCRIPTION>
- PackageLicenseExpression: <LICENSE> (MIT, Apache-2.0, etc.)
- Copyright: Copyright (c) 2025 <YOUR_ORGANIZATION>

Recommended:
- PackageProjectUrl: <GITHUB_URL>
- RepositoryUrl: <GITHUB_URL>
- RepositoryType: git
- PackageTags: <TAG1;TAG2;TAG3>
- PackageReadmeFile: README.md
- PackageIcon: <ICON_FILE>.png

Ensure values are accurate and professional.
```

## Manual Fix

1. **Open your `.csproj` file**
2. **Locate the first `<PropertyGroup>`** (or create one)
3. **Add required properties:**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    
    <!-- Package Metadata -->
    <Authors>Your Organization</Authors>
    <Company>Your Company</Company>
    <Description>
      Brief description of what this package does.
      Be specific and helpful.
    </Description>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <Copyright>Copyright (c) 2025 Your Organization</Copyright>
    
    <!-- Optional but Recommended -->
    <PackageProjectUrl>https://github.com/yourorg/yourrepo</PackageProjectUrl>
    <RepositoryUrl>https://github.com/yourorg/yourrepo</RepositoryUrl>
    <RepositoryType>git</RepositoryType>
    <PackageTags>tag1;tag2;tag3</PackageTags>
    <PackageReadmeFile>README.md</PackageReadmeFile>
    <PackageIcon>icon.png</PackageIcon>
  </PropertyGroup>

</Project>
```

4. **Customize all values** - don't leave defaults!
5. **Validate:**

```powershell
.\validate-package-metadata.ps1
```

## Required Properties

### Authors
**Purpose**: Who created/maintains the package  
**Format**: Comma-separated names or organization name  
**Example**: `Energy21 Development Team`

### Company
**Purpose**: Company/organization name  
**Example**: `Energy21`

### Description
**Purpose**: What the package does (appears on NuGet.org)  
**Requirements**:
- Clear and concise
- Explain purpose and key features
- 100-200 characters ideal
**Example**: `Domain models and core business logic for the Energy21 eBase platform, including entities, value objects, and domain services.`

### PackageLicenseExpression
**Purpose**: License under which package is distributed  
**Common Values**:
- `MIT` - Most permissive
- `Apache-2.0` - With patent grant
- `GPL-3.0-or-later` - Copyleft
**Note**: Must be valid SPDX identifier

### Copyright
**Purpose**: Copyright notice  
**Format**: `Copyright (c) YEAR OWNER`  
**Example**: `Copyright (c) 2025 Energy21`

## Recommended Properties

### PackageProjectUrl
**Purpose**: Project homepage or documentation site  
**Example**: `https://github.com/yourorg/yourrepo`

### RepositoryUrl
**Purpose**: Source code repository URL  
**Example**: `https://github.com/yourorg/yourrepo`

### RepositoryType
**Purpose**: Type of repository  
**Common Values**: `git`, `svn`, `tfvc`

### PackageTags
**Purpose**: Searchable tags on NuGet.org  
**Format**: Semicolon-separated  
**Example**: `domain;ddd;energy;utilities;business-logic`

### PackageIcon
**Purpose**: Icon displayed on NuGet.org  
**Requirements**:
- PNG file
- Recommended: 128x128px
- Must be packed in package
**Setup**:
```xml
<PackageIcon>icon.png</PackageIcon>
<ItemGroup>
  <None Include="..\..\icon.png" Pack="true" PackagePath="\" />
</ItemGroup>
```

### PackageReadmeFile
**Purpose**: README displayed on NuGet.org  
**Requirements**:
- Markdown file
- Must be packed in package
**Setup**:
```xml
<PackageReadmeFile>README.md</PackageReadmeFile>
<ItemGroup>
  <None Include="..\..\README.md" Pack="true" PackagePath="\" />
</ItemGroup>
```

## Validation

After updating metadata:

```powershell
# Validate metadata completeness
cd cicd/scripts
.\validate-package-metadata.ps1

# Test package creation
dotnet pack

# Inspect generated .nupkg
# Should contain all metadata, icon, README
```

## Quality Checklist

- [ ] All required properties present
- [ ] Description is clear and helpful (not generic)
- [ ] License is appropriate and valid SPDX ID
- [ ] Copyright year is current
- [ ] URLs are correct and accessible
- [ ] Tags are relevant and searchable
- [ ] Icon file exists and is packed (if specified)
- [ ] README is packed (if specified)
- [ ] No placeholder/default values remain
- [ ] Validation passes without warnings

## Related Resources

- **Standards**: `.cursor/rules/setup/project-setup-rule.mdc`
- **Validation**: `cicd/scripts/validate-package-metadata.ps1`
- **NuGet Docs**: https://docs.microsoft.com/nuget/create-packages/package-authoring-best-practices

## Success Criteria

✅ All required metadata complete  
✅ All values customized (no defaults)  
✅ Validation passes  
✅ Professional quality package  
✅ Ready for NuGet publishing

## Related Prompts

- `fix-missing-documentation.prompt.md` - Fix missing XML documentation warnings
- `fix-missing-changelog.prompt.md` - Fix missing CHANGELOG entries

## Related Rules

- `.cursor/rules/setup/project-setup-rule.mdc` - Project metadata standards
- `.cursor/rules/quality/zero-warnings-zero-errors-rule.mdc` - Quality enforcement

---

**Goal**: Zero Warnings, Zero Errors - Professional Package Quality

---

**Created**: 2024-11-15 (Original prompt creation)  
**Updated**: 2025-12-08 (PROMPTS-OPTIMIZE: Added Pattern metadata, Purpose, User Process, Related Prompts/Rules)  
**Rule**: `rule.prompts.creation.v1`, `rule.prompts.registry-integration.v1`

