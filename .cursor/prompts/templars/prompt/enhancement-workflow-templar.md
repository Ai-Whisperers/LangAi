---
type: templar
artifact-type: prompt
applies-to: improvement, enhancement, refactoring, optimization, enrichment
pattern-name: enhancement-categorization-workflow
version: 1.0.0
implements: prompt.enhance
extracted-from: .cursor/prompts/prompt/enhance-prompt.prompt.md
consumed-by:
  - .cursor/prompts/prompt/enhance-prompt.prompt.md
---

# Enhancement Categorization Workflow Templar

## Pattern Purpose

This template provides a structured approach to improving existing artifacts by categorizing enhancements into clear buckets (Structure, Content, Features, Documentation) and providing decision trees for selecting appropriate improvements based on gaps and time available.

## When to Use

Use this pattern when creating improvement/enhancement prompts for:
- **Code refactoring** - Improving existing code quality
- **Document enhancement** - Adding missing sections, improving clarity
- **Configuration optimization** - Enhancing config files with better practices
- **Process improvement** - Streamlining existing workflows
- **Feature enrichment** - Adding capabilities to existing artifacts

**Criteria for This Pattern**:
- ✅ Artifact already exists and works
- ✅ Multiple possible improvement dimensions
- ✅ Need to prioritize which improvements to make
- ✅ Different enhancement levels (quick vs deep)
- ✅ Before/after comparison helps communicate value

## Template Structure

```markdown
# Enhance [Artifact Type]

Please take an existing [artifact] and enhance it with [enhancement types].

## Expected Output

This prompt will produce:
1. **Enhancement analysis** identifying current gaps and opportunities
2. **Complete enhanced [artifact]** with all improvements integrated
3. **Enhancement summary** listing specific additions and improvements
4. **Impact assessment** showing [quality dimensions] gains

## Reasoning Process

Before enhancing:
1. **Read Current [Artifact]**: Understand what it currently does
2. **Identify Core Value**: What makes this [artifact] useful?
3. **Find Gaps**: What's missing or could be better?
4. **Select Enhancements**: Which improvements add most value without complexity?
5. **Plan Integration**: How to add features without breaking existing functionality?

## Enhancement Decision Tree

```
Does [artifact] work correctly?
├─ NO → Use @[fix-prompt] first (fix issues)
└─ YES → Continue with enhancement

What's the primary gap?
├─ [Gap Type 1] → [Enhancement Category 1]
├─ [Gap Type 2] → [Enhancement Category 2]
├─ [Gap Type 3] → [Enhancement Category 3]
├─ [Gap Type 4] → [Enhancement Category 4]
└─ Multiple gaps → Comprehensive Enhancement

How much time available?
├─ [Short timeframe] → Quick Enhancement ([specific items])
├─ [Medium timeframe] → Medium Enhancement ([specific items])
└─ [Long timeframe] → Deep Enhancement ([specific items])
```

## Enhancement Categories

### 1. [Enhancement Category 1]

**Add [Missing Elements]**:
- [Element type 1]
- [Element type 2]
- [Element type 3]
- [Element type 4]
- [Element type 5]

**Improve [Existing Elements]**:
- [Improvement type 1]
- [Improvement type 2]
- [Improvement type 3]
- [Improvement type 4]

### 2. [Enhancement Category 2]

**Add [Missing Elements]**:
- [Element type 1]
- [Element type 2]
- [Element type 3]
- [Element type 4]
- [Element type 5]

**Improve [Existing Elements]**:
- [Improvement type 1]
- [Improvement type 2]
- [Improvement type 3]
- [Improvement type 4]

### 3. [Enhancement Category 3]

**Add [Missing Elements]**:
- [Element type 1]
- [Element type 2]
- [Element type 3]
- [Element type 4]
- [Element type 5]

**Improve [Existing Elements]**:
- [Improvement type 1]
- [Improvement type 2]
- [Improvement type 3]
- [Improvement type 4]

### 4. [Enhancement Category 4]

**Improve [Aspect 1]**:
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]
- [Improvement 4]

**Add [Aspect 2]**:
- [Addition 1]
- [Addition 2]
- [Addition 3]
- [Addition 4]

## Enhancement Process

1. **Analyze** current [artifact] capabilities
2. **Identify** enhancement opportunities
3. **Select** appropriate enhancements
4. **Implement** enhancements with care
5. **Validate** enhanced version works correctly

## Enhancement Patterns

### Pattern 1: Add [Section Type]

```[format]
## [Section Name]

### [Subsection 1]
[Content structure]

### [Subsection 2]
[Content structure]
```

### Pattern 2: Add [Feature Type]

```[format]
## [Feature Name]

### [Mode 1]
For [use case]:
[Usage pattern]

### [Mode 2]
For [use case]:
[Usage pattern]
```

### Pattern 3: Add [Validation Type]

```[format]
## [Validation Section Name]

Before [action]:
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]
```

### Pattern 4: Add [Guidance Type]

```[format]
## [Guidance Section Name]

**[Issue Type]**: [Common problem]
**[Cause Type]**: [Why it happens]
**[Solution Type]**: [How to fix]
```

## Output Format

```markdown
## Enhancement Analysis

### Current State
- **Strengths**: [What's already good]
- **Gaps**: [What's missing]
- **Opportunities**: [What could be added]

### Proposed Enhancements
1. **[Enhancement Type]**: [What to add and why]
2. **[Enhancement Type]**: [What to add and why]
3. **[Enhancement Type]**: [What to add and why]

## Enhanced Version

[Complete enhanced artifact with all improvements]

## Enhancement Summary

### Additions
- [New section/feature added]
- [New section/feature added]
- [New section/feature added]

### Improvements
- [Existing part improved]
- [Existing part improved]
- [Existing part improved]

### Impact
- **[Quality Dimension 1]**: [How it's improved] (e.g., +300%)
- **[Quality Dimension 2]**: [How it's improved] (e.g., +500%)
- **[Quality Dimension 3]**: [How it's improved] (e.g., +400%)
```

## Enhancement Types

### Quick Enhancements ([Short Timeframe])
- [Quick enhancement 1]
- [Quick enhancement 2]
- [Quick enhancement 3]
- [Quick enhancement 4]
- [Quick enhancement 5]

### Medium Enhancements ([Medium Timeframe])
- [Medium enhancement 1]
- [Medium enhancement 2]
- [Medium enhancement 3]
- [Medium enhancement 4]
- [Medium enhancement 5]

### Deep Enhancements ([Long Timeframe])
- [Deep enhancement 1]
- [Deep enhancement 2]
- [Deep enhancement 3]
- [Deep enhancement 4]
- [Deep enhancement 5]

## Examples (Few-Shot)

### Example 1: Comprehensive Enhancement (Before/After)

**Before** ([Basic artifact description]):
```[format]
[Show minimal/basic version]
```

**Analysis**:
- **Strengths**: [What works]
- **Gaps**:
  - [Gap 1 with explanation]
  - [Gap 2 with explanation]
  - [Gap 3 with explanation]
  - [Gap 4 with explanation]

**After** ([Enhanced artifact description] - abbreviated):
```[format]
[Show enhanced version with improvements highlighted]
```

**Enhancement Summary**:
- ✅ [Enhancement 1 added]
- ✅ [Enhancement 2 added]
- ✅ [Enhancement 3 added]
- ✅ [Enhancement 4 added]
- ✅ [Enhancement 5 added]

**Impact**:
- **[Dimension 1]**: ⬆️ [Percentage]% - [Explanation]
- **[Dimension 2]**: ⬆️ [Percentage]% - [Explanation]
- **[Dimension 3]**: ⬆️ [Percentage]% - [Explanation]

## Related [Artifact Types]

- `@[related-prompt-1]` - For [purpose]
- `@[related-prompt-2]` - For [purpose]
- `@[related-prompt-3]` - For [purpose]

## Usage

**Basic Enhancement**:
```
@[prompt-name] [artifact-path]
```

**Specific Enhancement**:
```
@[prompt-name] [artifact-path] --add-[feature]
```

**Full Enhancement**:
```
@[prompt-name] [artifact-path] --comprehensive
```

## Enhancement Guidelines

### DO
- ✅ Keep the core purpose unchanged
- ✅ Add value through clarity and examples
- ✅ Maintain consistent formatting
- ✅ Test enhanced version works
- ✅ Preserve existing good content

### DON'T
- ❌ Change the fundamental purpose
- ❌ Add unnecessary complexity
- ❌ Remove working content
- ❌ Introduce breaking changes
- ❌ Add irrelevant information
```

## Customization Points

### Enhancement Categories
**Placeholder**: `[Enhancement Category N]`
**Guidance**: Define 3-4 enhancement dimensions relevant to your artifact type. Common patterns:
- **Structure** (organization, sections, hierarchy)
- **Content** (completeness, examples, clarity)
- **Features** (capabilities, modes, interactions)
- **Documentation** (references, metadata, guides)

Adjust based on what artifacts you're enhancing.

### Decision Tree
**Placeholder**: `[Gap Type N]`, `[Enhancement Category N]`
**Guidance**: Map common gaps to enhancement categories. Include time-based scoping (quick/medium/deep).

### Patterns
**Placeholder**: `[Section Type]`, `[Feature Type]`, etc.
**Guidance**: Provide concrete examples of common enhancement patterns users can apply. Show actual structure, not just descriptions.

### Before/After Example
**Placeholder**: `[Basic artifact]` / `[Enhanced artifact]`
**Guidance**: Show real transformation with impact quantification. Use percentages to demonstrate improvement magnitude.

### Impact Assessment
**Placeholder**: `[Quality Dimension N]`
**Guidance**: Define how to measure improvement. Examples: Usability, Clarity, Capability, Completeness, Maintainability.

## Example Usage (Applying This Templar)

### Creating "Enhance Unit Test" Prompt

**Category 1 - Structure**: Add AAA sections, group related tests
**Category 2 - Content**: Add edge cases, error scenarios
**Category 3 - Features**: Add parameterized tests, test fixtures
**Category 4 - Documentation**: Add XML docs, inline comments

**Decision Tree**: Missing coverage → Content | Poor organization → Structure | No assertions → Content

**Time Scoping**: Quick (5min) = add comments | Medium (15min) = restructure + edge cases | Deep (30min) = complete overhaul

**Result**: Enhancement prompt that analyzes existing tests and systematically improves them across all dimensions.

## Related Templars

- `multi-level-validation-templar.md` - Validation identifies what to enhance
- `guided-creation-workflow-templar.md` - Similar step-by-step structure
- `troubleshooting-guide-templar.md` - Enhancements address issues found

## Best Practices

### DO
- ✅ Categorize enhancements by dimension (structure, content, features, docs)
- ✅ Provide decision tree for selecting enhancements
- ✅ Scope by time available (quick, medium, deep)
- ✅ Show before/after with quantified impact
- ✅ Preserve working functionality
- ✅ Test enhanced version

### DON'T
- ❌ Change fundamental purpose
- ❌ Apply all enhancements blindly
- ❌ Skip impact assessment
- ❌ Forget validation after changes
- ❌ Make enhancements that add complexity without value
- ❌ Remove content that works

## Success Metrics

Good application of this pattern achieves:
- **Clarity**: Users understand what gaps exist and why
- **Prioritization**: Most valuable enhancements selected
- **Measurability**: Impact quantified with before/after comparison
- **Preservation**: Core value maintained while improving
- **Efficiency**: Time-scoped approach fits available effort

---

**Pattern Provenance**: Extracted from `enhance-prompt.prompt.md` which demonstrates exceptional enhancement categorization with decision trees, time-based scoping, comprehensive before/after examples, and quantified impact assessment.
