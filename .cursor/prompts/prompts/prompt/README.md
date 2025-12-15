# Prompt Meta-Tools

Meta-prompts for managing, creating, and improving prompts themselves.

## Available Prompts

### Creation & Organization

- **`@create-new-prompt`** - Create a new prompt following standards
  - Interactive prompt creation wizard
  - Templates and best practices built-in
  - Automatic validation

- **`@organize-prompts`** - Organize prompts into proper categories
  - Scan for miscategorized prompts
  - Move to appropriate folders
  - Clean up staging areas

### Quality & Improvement

- **`@validate-prompt`** - Validate prompt format and quality
  - Check Prompt Registry format compliance
  - Verify naming conventions
  - Assess content quality
  - Generate validation report

- **`@improve-prompt`** - Improve existing prompt quality
  - Analyze against best practices
  - Identify specific issues
  - Provide concrete improvements
  - Highlight changes made

- **`@enhance-prompt`** - Add advanced features to prompts
  - Add examples and use cases
  - Improve structure
  - Add validation checklists
  - Add troubleshooting guides

### Pattern Extraction

**Note**: For extracting templars/exemplars, use **`@extract-templar-exemplar`** from the housekeeping collection (works across all artifact types including prompts, rules, tickets, docs, scripts)

## Quick Start

### Create a New Prompt

```
@create-new-prompt "validate-api-response" for API testing
```

### Validate Existing Prompt

```
@validate-prompt .cursor/prompts/category/my-prompt.prompt.md
```

### Improve Prompt Quality

```
@improve-prompt .cursor/prompts/category/my-prompt.prompt.md
```

### Organize Uncategorized Prompts

```
@organize-prompts extracted/
```

## Workflow

### Standard Prompt Creation Workflow

1. **Create**: `@create-new-prompt` → generates prompt file
2. **Validate**: `@validate-prompt` → check format and quality
3. **Improve**: `@improve-prompt` → fix any issues
4. **Enhance**: `@enhance-prompt` → add examples and features
5. **Organize**: `@organize-prompts` → ensure proper location

### Prompt Improvement Workflow

1. **Validate**: `@validate-prompt` → identify issues
2. **Improve**: `@improve-prompt` → fix issues
3. **Enhance**: `@enhance-prompt` → add features
4. **Validate**: `@validate-prompt` → confirm improvements

### Pattern Extraction Workflow

1. **Identify**: Review prompts for reusable patterns or exceptional quality
2. **Extract**: `@extract-templar-exemplar` → create templar/exemplar (housekeeping)
3. **Document**: Add usage guidance and learning points
4. **Reference**: Update original prompts to link to extracted patterns
5. **Reuse**: Apply templars when creating new prompts

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format
- `.cursor/rules/prompts/prompt-extraction-rule.mdc` - Extracting prompts

## Best Practices

### When Creating Prompts

- Start with clear purpose and use cases
- Choose appropriate category
- Follow naming conventions (kebab-case)
- Include examples and usage instructions
- Validate before committing

### When Improving Prompts

- Run validation first to identify issues
- Fix format errors before content improvements
- Add examples to clarify usage
- Reference related prompts and rules
- Test improvements work correctly

### When Organizing Prompts

- Keep extracted/ folder empty (temporary staging only)
- Use existing categories when possible
- Update frontmatter category when moving
- Validate after moving files
- Keep special folders (exemplars/, templars/) curated

## Folder Structure

```
.cursor/prompts/
├── prompt/                   # Meta-prompts (you are here)
│   ├── create-new-prompt.prompt.md
│   ├── validate-prompt.prompt.md
│   ├── improve-prompt.prompt.md
│   ├── enhance-prompt.prompt.md
│   └── organize-prompts.prompt.md
│
├── housekeeping/            # Maintenance prompts
│   └── extract-templar-exemplar.prompt.md  # Works across all artifact types
│
├── [category]/              # Category folders
│   └── *.prompt.md
│
├── extracted/               # Temporary staging (to be organized)
├── exemplars/              # Example prompts (reference implementations)
│   └── [category]/
│       └── *-exemplar.md
└── templars/               # Template prompts (reusable structures)
    └── [category]/
        └── *-templar.md
```

## Examples

### Example 1: Creating a New Testing Prompt

```
@create-new-prompt "check-test-coverage" in unit-testing category

Purpose: Analyze test coverage for a specific file or module
Output: Coverage report with missing tests identified
```

### Example 2: Improving Existing Prompt

```
@improve-prompt .cursor/prompts/git/create-branch.prompt.md

Analysis: Missing usage examples, tags too generic
Improvements: Added examples, specific tags, argument hints
```

### Example 3: Batch Validation

```
@validate-prompt .cursor/prompts/cicd/*.prompt.md

Result: 8 prompts validated
  - 5 passed completely
  - 2 warnings (missing argument-hint)
  - 1 error (invalid YAML)
```

### Example 4: Extract Reusable Pattern

```
@extract-templar-exemplar .cursor/prompts/prompt/validate-prompt.prompt.md

Analysis: Found multi-level validation checklist pattern
Reusability: High (applies to any validation task)
Type: Templar

Extracted: validation-checklist-templar.md
Save to: .cursor/prompts/templars/prompt/
```

**Note**: Extraction prompt now in housekeeping collection, works for all artifact types

## Tips

- **Use `@validate-prompt` frequently** - Catch issues early
- **Extract patterns from conversations** - Real usage creates best prompts
- **Identify reusable patterns** - Use `@extract-templar-exemplar` when you find great structures
- **Keep prompts focused** - One clear purpose per prompt
- **Include examples** - Shows how to use effectively
- **Reference related content** - Links to prompts/rules and templars/exemplars
- **Reuse templars** - Start with proven patterns when creating new prompts

## Support

For issues with these meta-prompts:
- Check validation errors carefully
- Review Prompt Registry format rules
- Reference related rule files
- Look at exemplars/ for examples

