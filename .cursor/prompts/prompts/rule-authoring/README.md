# Rule Authoring Prompts

Prompts for creating, validating, syncing, and extracting patterns from rules in the rule framework.

## Available Prompts

### Creation & Organization

- **`@create-new-rule`** - Create a new rule following the framework
  - Interactive rule creation wizard
  - Front-matter templates
  - Structure guidance
  - Validation checklists
  - Supporting artifacts (templars/exemplars)

- **`@sync-rules-between-repos`** - Sync rules between repositories
  - Automated comparison analysis
  - Categorized sync recommendations
  - Conflict resolution strategies
  - Post-sync validation
  - PowerShell automation scripts

### Quality & Validation

- **`@validate-rule-compliance`** - Validate rule against framework standards
  - Front-matter validation
  - Structure compliance checks
  - Contract verification
  - Quality assessment
  - Severity categorization (Critical/High/Medium/Low)

### Pattern Extraction

- **`@extract-prompts-from-conversation`** - Extract prompt patterns from transcripts
  - Analyze conversation effectiveness
  - Extract reusable templates
  - Meta-analysis of patterns
  - Generate prompt templates

**Note**: For extracting templars/exemplars from rules, use **`@extract-templar-exemplar`** from the housekeeping collection (works across all artifact types including rules)

## Quick Start

### Create a New Rule

```
@create-new-rule "validation" for "ticket workflow compliance"
```

### Validate Existing Rule

```
@validate-rule-compliance .cursor/rules/ticket/plan-rule.mdc
```

### Extract Reusable Pattern

```
@extract-templar-exemplar .cursor/rules/ticket/workflow-rule.mdc
```

**Note**: Now uses generalized housekeeping prompt that works for rules, prompts, tickets, docs, and scripts.

### Sync Rules Between Repos

```
@sync-rules-between-repos 
  source: eneve.ebase.foundation
  target: eneve.domain
  domain: ticket
```

## Workflow

### Standard Rule Creation Workflow

1. **Create**: `@create-new-rule` → generates rule file with structure
2. **Validate**: `@validate-rule-compliance` → check format and quality
3. **Refine**: Fix any validation issues
4. **Extract**: `@extract-templar-exemplar` → if pattern is reusable (housekeeping)

### Rule Improvement Workflow

1. **Validate**: `@validate-rule-compliance` → identify issues
2. **Fix**: Address validation errors and warnings
3. **Re-validate**: Confirm improvements
4. **Extract**: If now exemplary, extract as exemplar

### Pattern Extraction Workflow

1. **Identify**: Review rules for reusable patterns or exceptional quality
2. **Extract**: `@extract-templar-exemplar` → create templar/exemplar (housekeeping)
3. **Document**: Add usage guidance and learning points
4. **Reference**: Update original rules to link to extracted patterns
5. **Reuse**: Apply templars when creating new rules

### Repository Sync Workflow

1. **Compare**: `@sync-rules-between-repos` → automated analysis
2. **Review**: Examine generated sync report
3. **Execute**: Sync Categories A & B (add/update)
4. **Resolve**: Handle Category C conflicts manually
5. **Validate**: Run post-sync validation scripts

## Automation Scripts

The `scripts/` folder contains PowerShell automation for common tasks:

### Rule Comparison

```powershell
# Compare rules between two repositories
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\compare-rules.ps1
```

**Output**: CSV report with categorized sync recommendations

### Sync Validation

```powershell
# Validate rules after sync
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\validate-sync.ps1
```

**Output**: Validation report confirming integrity

### Bidirectional Sync

```powershell
# Two-way sync between repositories
powershell -ExecutionPolicy Bypass -File .cursor\prompts\rule-authoring\scripts\sync-rules-bidirectional.ps1
```

**Output**: Bidirectional sync with conflict resolution

## Folder Structure

```
.cursor/prompts/rule-authoring/
├── create-new-rule.prompt.md
├── validate-rule-compliance.prompt.md
├── sync-rules-between-repos.prompt.md
├── extract-prompts-from-conversation.prompt.md
├── scripts/
│   ├── compare-rules.ps1
│   ├── validate-sync.ps1
│   ├── sync-rules-bidirectional.ps1
│   ├── compare-complete.ps1
│   └── validate-complete-sync.ps1
└── README.md (you are here)

Note: For templar/exemplar extraction, see .cursor/prompts/housekeeping/
```

## Related Rules

These prompts follow standards from:

- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Canonical structure
- `.cursor/rules/rule-authoring/rule-contracts-and-scope.mdc` - Contracts
- `.cursor/rules/rule-authoring/rule-invocation-strategies.mdc` - When rules apply
- `.cursor/rules/rule-authoring/rule-validation-and-checklists.mdc` - Validation
- `.cursor/rules/rule-authoring/rule-naming-conventions.mdc` - Naming
- `.cursor/rules/rule-authoring/rule-templars-and-exemplars.mdc` - Patterns
- `.cursor/rules/rule-authoring/rule-sync-rule.mdc` - Sync process

## Examples

### Example 1: Creating a New Validation Rule

```
@create-new-rule "database-validation" in database-standards

Purpose: Validate database schema against standards
Output: Validation report with pass/fail criteria
```

### Example 2: Validating an Existing Rule

```
@validate-rule-compliance .cursor/rules/git/branch-lifecycle-rule.mdc

Result: Pass with 2 warnings
- Warning: Missing exemplar references
- Warning: Could add more anti-pattern examples
```

### Example 3: Extracting Reusable Pattern

```
@extract-templar-exemplar .cursor/rules/ticket/validation-before-completion-rule.mdc

Analysis: Found comprehensive validation checklist pattern
Type: Templar (structure is highly reusable)

Extracted: validation-checklist-templar.mdc
Save to: .cursor/rules/templars/ticket/
```

**Note**: Uses housekeeping prompt that works across artifact types

### Example 4: Syncing Rules Between Repos

```
@sync-rules-between-repos
  source: eneve.ebase.foundation
  target: eneve.domain
  scope: ticket domain

Result: 
- 3 rules to add
- 5 rules to update
- 1 rule to review (conflict)
- 12 rules already in sync
```

## Best Practices

### When Creating Rules

- Start with clear purpose and scope
- Choose appropriate invocation strategy
- Follow naming conventions (lowercase-with-hyphens-rule.mdc)
- Include comprehensive validation checklists
- Provide good and bad examples
- Validate before committing

### When Validating Rules

- Run validation for all changed rules
- Fix Critical and High severity issues first
- Address Medium issues before committing
- Document reasons for any Low severity exceptions

### When Extracting Patterns

- Be selective - only extract high-value patterns
- Document WHY the pattern is valuable
- Provide clear usage guidance
- Cross-reference related patterns
- Keep templars abstract, exemplars concrete

### When Syncing Rules

- Always review analysis report before executing
- Handle conflicts (Category C) manually
- Validate after sync completes
- Document sync in log file
- Test synced rules in target context

## Tips

- **Use `@validate-rule-compliance` frequently** - Catch issues early
- **Extract patterns proactively** - Don't wait until you copy a rule 3 times
- **Leverage automation scripts** - Save time with PowerShell tools
- **Keep sync logs** - Maintain audit trail of changes
- **Reference templars** - Link new rules to patterns they follow
- **Update exemplars** - When better examples are created

## Troubleshooting

### Issue: Rule Validation Fails

**Solution**: 
1. Check front-matter syntax (YAML must be valid)
2. Verify rule_id follows naming convention
3. Ensure all required sections present
4. Run `@validate-rule-compliance` for detailed report

### Issue: Sync Conflicts (Category C)

**Solution**:
1. Review both versions side-by-side
2. Identify which changes are more valuable
3. Choose: keep source, keep target, or manual merge
4. Document decision in sync log

### Issue: Extracted Templar Too Complex

**Solution**:
1. Simplify to 3-5 key customization points
2. Consider creating "Basic" and "Advanced" versions
3. Add concrete usage example
4. May be multiple simpler patterns combined

### Issue: No One Uses Extracted Pattern

**Solution**:
1. Verify discoverability (README updated?)
2. Add more usage examples
3. Present pattern to team
4. Archive if unused after 3 months

## Support

For issues with rule authoring:
- Check validation errors carefully
- Review rule authoring framework rules
- Reference templars/exemplars for patterns
- Use automation scripts for efficiency

## Related Folders

- `.cursor/rules/` - All rule files
- `.cursor/rules/templars/` - Reusable rule templates
- `.cursor/rules/exemplars/` - Reference rule examples
- `.cursor/prompts/prompt/` - Similar prompts for prompt management
- `.cursor/prompts/housekeeping/` - Maintenance prompts including pattern extraction

