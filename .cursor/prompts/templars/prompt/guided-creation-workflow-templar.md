---
type: templar
artifact-type: prompt
applies-to: creation, setup, configuration, initialization, onboarding
pattern-name: guided-creation-workflow
version: 1.0.0
implements: prompt.create
extracted-from: .cursor/prompts/prompt/create-new-prompt.prompt.md
consumed-by:
  - .cursor/prompts/prompt/create-new-prompt.prompt.md
---

# Guided Multi-Step Creation Workflow Templar

## Pattern Purpose

This template provides a structured, guided workflow for creation tasks where users need step-by-step assistance with decisions at each stage. It reduces cognitive load by breaking complex creation into manageable steps with clear decision points.

## When to Use

Use this pattern when creating prompts for:
- **Setup/initialization tasks** - Project setup, environment configuration
- **Artifact creation** - Creating structured documents, files, or objects
- **Wizard-style workflows** - Multi-step processes requiring decisions
- **Onboarding flows** - Guiding users through complex first-time tasks
- **Migration tasks** - Step-by-step migration with validation

**Criteria for This Pattern**:
- ✅ Task has 4+ distinct steps
- ✅ Users need guidance at each step
- ✅ Decisions required at multiple points
- ✅ Output quality depends on following structure
- ✅ Process can be templated/standardized

## Template Structure

```markdown
# [Action] [Subject]

[Brief description of what this workflow creates/accomplishes]

## Expected Output

This prompt will produce:
1. **[Primary Output]** - [Description]
2. **[Secondary Output]** - [Description]
3. **[Validation Output]** - [Description]
4. **[Usage Instructions]** - [Description]

## Reasoning Process

Before [action]:
1. **[Reasoning Step 1]**: [What to consider]
2. **[Reasoning Step 2]**: [What to analyze]
3. **[Reasoning Step 3]**: [What to plan]
4. **[Reasoning Step 4]**: [What to validate]

## [Action] Process

### Step 1: [Define/Identify Phase]

Answer these questions:
- **What**: [Question about core purpose]
- **Who**: [Question about target users]
- **When**: [Question about use cases]
- **Output**: [Question about expected result]

### Step 2: [Choose/Select Phase]

Determine [what needs to be chosen]:

**[Option Category 1]**:
- `[option-1]/` - [Description and when to use]
- `[option-2]/` - [Description and when to use]
- `[option-3]/` - [Description and when to use]

**[Option Category 2]**: [Description]

**Decision Tree Format** (if applicable):
```
[Question]?
├─ [Answer A] → [Recommendation]
├─ [Answer B] → [Recommendation]
└─ [Answer C] → [Recommendation]
```

### Step 3: [Name/Configure Phase]

**[Configuration Rules]**:
- [Rule 1 with format]
- [Rule 2 with constraint]
- [Rule 3 with convention]
- [Rule 4 with limitation]

**Examples**:
- ✅ `[good-example]` - [Why good]
- ✅ `[another-good-example]` - [Why good]
- ❌ `[bad-example]` - [Why bad]
- ❌ `[another-bad-example]` - [Why bad]

### Step 4: [Write/Configure Phase 1]

**[Configuration Aspect 1]**:
```[format]
[field-1]: [value-format]
[field-2]: [value-format]
[field-3]: [value-format]
```

**[Configuration Rules]**:
- ✅ [Best practice 1]
- ✅ [Best practice 2]
- ❌ [Anti-pattern 1]
- ❌ [Anti-pattern 2]

### Step 5: [Write/Configure Phase 2]

**[Content Structure]**:
```markdown
# [Section 1]

[Content guidance]

## [Section 2]

[Content guidance]

## [Section 3]

[Content guidance]
```

**Enhanced Structure** (Recommended):
```markdown
# [Section 1]

[Enhanced guidance]

## [Section 2]

[Enhanced guidance with subsections]

### [Subsection 2.1]
[Details]

### [Subsection 2.2]
[Details]

## [Section 3]

[Enhanced guidance]
```

### Step 6: [Validate/Test Phase]

1. **[Validation 1]**: [How to validate]
2. **[Validation 2]**: [How to validate]
3. **[Validation 3]**: [How to validate]
4. **[Validation 4]**: [How to validate]

## [Artifact] Template

[Provide complete template showing all sections filled with placeholders]

```[format]
[Complete example template with placeholders and annotations]
```

## Examples (Few-Shot)

### Example 1: [Scenario 1 - Complete Workflow]

**Request**: "[Example user request]"

**Step 1 - [Phase 1 Name]**:
- [Decision 1]: [Result]
- [Decision 2]: [Result]
- [Decision 3]: [Result]

**Step 2 - [Phase 2 Name]**:
- [Decision]: [Result with reasoning]

**Step 3 - [Phase 3 Name]**:
- [Configuration]: [Result]
- [Rationale]: [Why this choice]

**Step 4 - [Phase 4 Name]**:
```[format]
[Configuration example filled in]
```

**Step 5 - [Phase 5 Name]** (abbreviated):
```markdown
[Content example showing structure]
```

**Step 6 - [Phase 6 Name]**:
```
[Validation commands/checks shown]

Result: [Pass/Fail with details]
```

**Final Output**: `[path/to/created/artifact]`

### Example 2: [Scenario 2 - Alternative Path]

[Similar structure showing different decisions leading to different outcome]

## Quick Start

**Interactive [Action]**:
```
@[prompt-name]

AI: [First question]
You: [User provides input]

AI: [Second question based on answer]
You: [User provides input]

[AI generates complete artifact]
```

**Direct [Action]**:
```
@[prompt-name] "[parameters]" with [options]
```

## Quality Checklist

Before finalizing:
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]
- [ ] [Check 4]
- [ ] [Check 5]
- [ ] [Check 6]
- [ ] [Check 7]
- [ ] [Check 8]
- [ ] [Check 9]
- [ ] [Check 10]
```

## Customization Points

### Step 1: Define Phase
**Placeholder**: `[Reasoning Step N]`
**Guidance**: Replace with specific questions users should answer about their creation task. Focus on purpose, audience, use cases, and expected output.

### Step 2: Choose Phase
**Placeholder**: `[Option Category]`, `[option-1]`, etc.
**Guidance**: Replace with actual options/categories users choose from. Include decision trees if choices are complex.

### Step 3: Name/Configure Phase
**Placeholder**: `[Configuration Rules]`
**Guidance**: Replace with specific naming conventions, formatting rules, or configuration constraints for your domain.

### Step 4-5: Write/Configure Phases
**Placeholder**: `[Configuration Aspect]`, `[Section N]`
**Guidance**: Replace with actual configuration fields or content sections users need to complete.

### Step 6: Validate Phase
**Placeholder**: `[Validation N]`
**Guidance**: Replace with specific validation checks, quality gates, or testing steps.

### Examples Section
**Placeholder**: `[Scenario N]`
**Guidance**: Provide 2-3 concrete walkthroughs showing complete workflows from request to final output.

## Example Usage (Applying This Templar)

### Creating a "Setup Development Environment" Prompt

**Step 1 - Define**: Environment setup for new developers
**Step 2 - Choose**: Category = `setup/`, Platform = Windows/Linux/Mac
**Step 3 - Name**: `setup-dev-environment.prompt.md`
**Step 4 - Configure Frontmatter**: Add platform detection logic
**Step 5 - Write Content**: Installation steps, verification commands
**Step 6 - Validate**: Test on fresh machine

**Result**: Guided workflow helping new developers set up their environment step-by-step with platform-specific instructions.

## Related Templars

- `multi-level-validation-templar.md` - Use for Step 6 validation
- `enhancement-workflow-templar.md` - Use to improve created artifacts
- `categorization-workflow-templar.md` - Use for organizing created artifacts

## Best Practices

### DO
- ✅ Provide clear decision criteria at each step
- ✅ Include good/bad examples throughout
- ✅ Offer both interactive and direct invocation modes
- ✅ Validate output at the end
- ✅ Include complete template users can copy
- ✅ Show 2+ full workflow examples

### DON'T
- ❌ Skip steps or compress too much
- ❌ Make users guess at decisions
- ❌ Provide vague examples
- ❌ Skip validation step
- ❌ Assume users know the conventions

## Success Metrics

Good application of this pattern achieves:
- **Completion rate**: >90% of users complete all steps
- **Quality**: Outputs meet standards without iteration
- **Efficiency**: Clear path reduces time to completion
- **Confidence**: Users feel guided, not lost
- **Reusability**: Template works across similar creation tasks

---

**Pattern Provenance**: Extracted from `create-new-prompt.prompt.md` which demonstrates exceptional guided workflow implementation with decision trees, examples, and comprehensive templates.
