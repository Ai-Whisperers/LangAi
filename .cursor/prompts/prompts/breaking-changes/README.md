# Breaking Changes Documentation Prompts

Prompts for documenting breaking API changes with comprehensive migration guidance.

## When These Prompts Are Used

### Automatic Trigger
When `cicd/scripts/check-breaking-changes.ps1` detects breaking API changes, it displays:
```
Use prompt: .cursor/prompts/breaking-changes/document-breaking-changes.prompt.md
```

### Manual Use
- Planning a breaking change release
- Need to document API changes for consumers
- Creating migration guide for major version
- Reviewing breaking changes before release

## Available Prompts

### [`document-breaking-changes.prompt.md`](./document-breaking-changes.prompt.md)
**Purpose**: Generate complete breaking changes documentation with migration steps

**Use when**:
- CI/CD pipeline detects breaking changes
- Need to document API changes in CHANGELOG
- Creating major version release (X.0.0)
- Reviewing compatibility between versions

**Provides**:
- CHANGELOG.md format for breaking changes
- Before/after code examples
- Step-by-step migration guide
- Impact assessment
- Version increment guidance

## Quick Use

```
Tell Cursor AI:
"Document breaking changes using the breaking-changes prompt"

Or:
"Generate migration guide for API changes detected in pipeline"
```

## Related

- **CHANGELOG**: `.cursor/prompts/changelog/` - For release notes
- **Versioning**: `.cursor/rules/cicd/tag-based-versioning-rule.mdc` - Version rules
- **CI/CD Script**: `cicd/scripts/check-breaking-changes.ps1` - Detection

## Example Workflow

1. **Detection**: Pipeline runs `check-breaking-changes.ps1`
2. **Failure**: Breaking changes detected vs last release
3. **Documentation**: Use prompt to document changes
4. **Version**: Increment MAJOR version (1.x.x → 2.0.0)
5. **Release**: Follow RC workflow with proper documentation

---

**Last Updated**: 2025-12-06
