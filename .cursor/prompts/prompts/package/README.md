# NuGet Package Metadata Prompts

Prompts for generating complete, high-quality NuGet package metadata following Microsoft best practices.

## When These Prompts Are Used

### Automatic Trigger
When `cicd/scripts/validate-package-metadata.ps1` fails validation, it displays:
```
Use prompt: .cursor/prompts/package/generate-package-metadata.prompt.md
```

### Manual Use
- Setting up new library project for NuGet
- Improving package quality and discoverability
- Adding missing metadata to existing packages
- Preparing for first public release

## Available Prompts

### [`generate-package-metadata.prompt.md`](./generate-package-metadata.prompt.md)
**Purpose**: Generate comprehensive NuGet package metadata for .NET projects

**Use when**:
- CI/CD pipeline fails: "Required package metadata missing"
- Creating new library project
- Need to add README, icon, or tags
- Want to improve package discoverability

**Generates**:
- Complete `Directory.Build.props` configuration
- Project-specific `.csproj` metadata
- Package description and tags
- License selection guidance
- README and icon integration

## Quick Use

```
Tell Cursor AI:
"Generate NuGet package metadata using the package prompt"

Or:
"Add missing package metadata to Directory.Build.props"

Or:
"Create complete NuGet metadata following best practices"
```

## Required Metadata Fields

✅ Must have:
- PackageId
- Version
- Authors
- Description (50+ chars)
- PackageLicenseExpression
- PackageProjectUrl
- RepositoryUrl
- RepositoryType
- Copyright

⭐ Recommended:
- PackageTags
- PackageReadmeFile
- PackageIcon
- PackageReleaseNotes

## Related

- **Project Setup**: `.cursor/rules/setup/project-setup-rule.mdc` - Full project standards
- **CI/CD Script**: `cicd/scripts/validate-package-metadata.ps1` - Validation
- **NuGet Docs**: https://learn.microsoft.com/nuget/create-packages/package-authoring-best-practices

## Common Scenarios

### Scenario 1: New Project Setup
```
"Generate complete NuGet package metadata for Eneve.Domain.Cache project"
```

### Scenario 2: Missing Required Fields
```
"Add missing package metadata: Authors, License, Repository URL"
```

### Scenario 3: Improve Discoverability
```
"Add package tags, README, and icon to improve NuGet discoverability"
```

## Example Output Structure

```
Repository Root/
├── Directory.Build.props     (Shared metadata)
│   ├── Authors, Company, Copyright
│   ├── Repository URLs
│   ├── License
│   └── Common settings
├── README.md                 (Included in package)
├── icon.png                  (Package icon, 64x64)
└── src/
    └── YourProject/
        └── YourProject.csproj  (Project-specific metadata)
            ├── PackageId
            ├── Description
            ├── Version
            └── Tags
```

---

**Last Updated**: 2025-12-06
