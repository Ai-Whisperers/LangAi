---
name: Generate NuGet Package Metadata
description: Generate complete NuGet package metadata following Microsoft best practices
category: package
tags: [nuget, metadata, packaging, configuration]
---

# Generate NuGet Package Metadata

## Purpose

Generate comprehensive NuGet package metadata for .NET projects following Microsoft's packaging best practices.

## When to Use

- CI/CD pipeline fails: "Required package metadata missing"
- Setting up new library project for NuGet publishing
- Improving package discoverability and quality
- Preparing for first public release

## Input Requirements

Provide:
1. **Project Information**: Name, purpose, target audience
2. **Repository URL**: Git repository location
3. **Organization/Author**: Who maintains this package
4. **License**: Preferred license (or help choosing)

## Instructions

### Step 1: Analyze Project Structure

Determine:
- Project name and namespace
- Package purpose and functionality
- Target frameworks (.NET 6, 7, 8, 9, etc.)
- Existing metadata in `.csproj` and `Directory.Build.props`

### Step 2: Generate Required Metadata

Create or update `Directory.Build.props` (project root) with comprehensive metadata including:
- Package Identity (PackageId, Version)
- Package Information (Authors, Company, Description)
- Legal & Licensing (Copyright, PackageLicenseExpression)
- Repository Information (RepositoryUrl, RepositoryType)
- Discoverability (PackageTags, PackageReadmeFile)
- Build Configuration (Documentation generation, Source Link, Symbols)

### Step 3: Choose Appropriate License

**Common Licenses**:

| License | Best For | Permissions | Limitations |
|---------|----------|-------------|-------------|
| **MIT** | Most permissive, popular choice | Commercial use, modification, distribution | Must include license |
| **Apache-2.0** | Corporate-friendly with patent grant | Same as MIT + explicit patent grant | Must state changes |
| **BSD-3-Clause** | Simple permissive license | Commercial use, modification | Cannot use author name for promotion |

**Recommendation**: Use **MIT** for maximum adoption, **Apache-2.0** if patent protection matters.

More info: https://choosealicense.com/

### Step 4: Write Package Description

**Quality Description Format**:
```
[One-sentence summary of what it does]

[2-3 sentences explaining key features and use cases]

[Optional: Who should use this and why]
```

**Best Practices**:
- ✅ 50-200 characters optimal
- ✅ Start with what it does, not what it is
- ✅ Mention key benefits and use cases
- ✅ Use clear, non-technical language
- ❌ Don't use marketing fluff
- ❌ Don't just repeat the package name

### Step 5: Select Package Tags

**Tag Guidelines**:
- Use 5-10 relevant keywords
- Separate with semicolons
- Include: technology, domain, use case
- Use common search terms

**Tag Categories to Include**:
- **Platform**: `dotnet`, `csharp`, `netstandard`, `net9`
- **Domain**: `domain`, `business-logic`, `enterprise`
- **Patterns**: `ddd`, `clean-architecture`, `cqrs`, `event-sourcing`
- **Functionality**: `validation`, `caching`, `logging`, `security`

### Step 6: Validate Metadata

Check:
- [ ] All required fields present
- [ ] Description is meaningful (50+ chars)
- [ ] License is valid SPDX expression
- [ ] Tags are relevant and searchable
- [ ] URLs are accessible
- [ ] README.md exists and included
- [ ] Icon file exists (if specified)

## Related Documentation

- **NuGet Best Practices**: https://learn.microsoft.com/nuget/create-packages/package-authoring-best-practices
- **SPDX Licenses**: https://spdx.org/licenses/
- **Choose a License**: https://choosealicense.com/
- **Project Setup Rule**: `.cursor/rules/setup/project-setup-rule.mdc`

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-06  
**Triggered by**: `validate-package-metadata.ps1` failures

