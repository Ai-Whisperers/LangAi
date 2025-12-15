---
name: enhance-prompt
description: "Please enhance a prompt with advanced features, examples, and better structure"
category: prompt
tags: prompts, enhancement, features, examples, structure
argument-hint: "Prompt file path and enhancement type (optional)"
templar: .cursor/prompts/templars/prompt/prompt-enhancement-workflow-templar.md
exemplar: .cursor/prompts/exemplars/prompt/prompt-enhancement-workflow-exemplar.md
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Enhance Prompt

Please take an existing prompt and enhance it with advanced features, better examples, improved structure, and additional capabilities.

**Pattern**: Enhancement Workflow Pattern ⭐⭐⭐⭐  
**Effectiveness**: Essential for maturing prompts from basic to production-ready  
**Use When**: Prompt works correctly but lacks examples, clarity, or advanced features

---

## Purpose

This prompt helps evolve working prompts into production-ready, highly usable prompts by:
- Adding comprehensive examples and use cases
- Improving structure and organization
- Adding validation and quality checks
- Enhancing documentation and references
- Adding multiple usage modes or configurations

Use this AFTER `/improve-prompt` has fixed any issues. This prompt assumes the base prompt works correctly and focuses on making it better, clearer, and more powerful.

---

## Required Context

- **Prompt File**: Path to existing `.prompt.md` file to enhance
- **Enhancement Type** (optional): Structure, Content, Feature, Documentation, or Comprehensive
- **Time Available** (optional): Quick (5-10min), Medium (15-30min), or Deep (30+min)

---

## Process

Follow these steps to enhance a prompt:

### Step 1: Analyze Current Prompt
Read the prompt and identify:
- What it does well (strengths to preserve)
- What's missing (gaps to fill)
- What could be clearer (improvements to make)

### Step 2: Select Enhancement Type
Choose based on primary gap:
- **Examples missing** → Add Examples Enhancement
- **Instructions unclear** → Structure Enhancement
- **No validation** → Feature Enhancement
- **Missing references** → Documentation Enhancement
- **Multiple gaps** → Comprehensive Enhancement

### Step 3: Plan Enhancements
Decide which improvements add most value without breaking existing functionality.

### Step 4: Apply Enhancements
Integrate improvements while preserving core purpose and working content.

### Step 5: Validate Enhanced Version
Test that enhanced prompt still works and improvements actually help.

---

## Reasoning Process (for AI Agent)

Before enhancing, the AI should:

1. **Read Current Prompt**: Understand what it currently does and how well it works
2. **Identify Core Value**: What makes this prompt useful? Preserve this at all costs
3. **Find Gaps**: What's missing or could be better? Examples? Clarity? Features?
4. **Select Enhancements**: Which improvements add most value without unnecessary complexity?
5. **Plan Integration**: How to add features without breaking existing functionality?
6. **Preserve Working Content**: Don't remove or break what already works well

---

## Enhancement Decision Tree

```
Does prompt work correctly?
├─ NO → Use improve-prompt.prompt.md first (fix issues)
└─ YES → Continue with enhancement

What's the primary gap?
├─ Missing examples → Add Examples Enhancement
├─ Unclear instructions → Add Structure Enhancement
├─ No validation → Add Feature Enhancement (validation)
├─ Lacks references → Add Documentation Enhancement
└─ Multiple gaps → Comprehensive Enhancement

How much time available?
├─ 5-10 min → Quick Enhancement (examples, tags)
├─ 15-30 min → Medium Enhancement (sections, validation)
└─ 30+ min → Deep Enhancement (restructure, multiple modes)
```

---

## Enhancement Categories

### 1. Structure Enhancement

**Add Missing Sections**:
- Clear objective statement
- Prerequisites and context
- Step-by-step instructions
- Expected output format
- Usage examples
- Related prompts/resources

**Improve Organization**:
- Logical section ordering
- Clear headings hierarchy
- Bullet points for lists
- Code blocks for examples
- Tables for comparisons

### 2. Content Enhancement

**Add Examples**:
- Before/after examples
- Multiple use case scenarios
- Good vs bad examples
- Edge case handling
- Real-world applications

**Improve Instructions**:
- More specific guidance
- Clearer action verbs
- Numbered steps for procedures
- Decision trees for complex flows
- Troubleshooting tips

### 3. Feature Enhancement

**Add Interactivity**:
- Argument hints for inputs
- Variable placeholders
- Template sections
- Configurable options
- Multiple modes/variations

**Add Validation**:
- Input validation rules
- Output quality checks
- Success criteria
- Failure scenarios
- Recovery strategies

### 4. Documentation Enhancement

**Improve Metadata**:
- Better tags (more specific)
- Clearer description
- Version information
- Author/ownership info
- Last updated date

**Add References**:
- Related prompts
- Related rules
- External documentation
- Best practices links
- Tool documentation

---

## Enhancement Patterns

### Pattern 1: Add Examples Section

```markdown
## Examples

### Example 1: [Scenario Name]
**Input**:
[Input example]

**Expected Output**:
[Output example]

### Example 2: [Another Scenario]
[Similar structure]
```

### Pattern 2: Add Usage Modes

```markdown
## Usage Modes

### Basic Mode
For simple [use case]:
@prompt-name [basic-arg]

### Advanced Mode
For complex [use case]:
@prompt-name [detailed-args] --option value

### Batch Mode
For multiple items:
@prompt-name [pattern] --batch
```

### Pattern 3: Add Validation Checklist

```markdown
## Validation Checklist

Before claiming output is complete:
- [ ] [Validation point 1]
- [ ] [Validation point 2]
- [ ] [Validation point 3]
```

### Pattern 4: Add Troubleshooting

```markdown
## Troubleshooting

**Issue**: [Common problem]
**Cause**: [Why it happens]
**Solution**: [How to fix]

**Issue**: [Another problem]
[Similar structure]
```

---

## Examples (Few-Shot)

See exemplar for complete worked examples:
- `.cursor/prompts/exemplars/prompt/prompt-enhancement-workflow-exemplar.md`

## Enhancement Types by Time

### Quick Enhancements (5-10 min)
- Add usage examples
- Improve description
- Add better tags
- Add argument hints
- Fix formatting

### Medium Enhancements (15-30 min)
- Add multiple examples
- Add troubleshooting section
- Add validation checklist
- Improve instructions
- Add related prompts

### Deep Enhancements (30+ min)
- Add multiple usage modes
- Add comprehensive examples
- Add decision trees
- Add interactive features
- Complete restructure

---

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

---

## Quality Criteria

- [ ] Core purpose preserved
- [ ] All enhancements add clear value
- [ ] Examples are complete and realistic
- [ ] Instructions are actionable
- [ ] Related prompts/rules referenced
- [ ] Enhanced version tested and works

---

## Usage

**Basic Enhancement**:
```
@enhance-prompt .cursor/prompts/category/my-prompt.prompt.md
```

**Specific Enhancement**:
```
@enhance-prompt .cursor/prompts/category/my-prompt.prompt.md --add-examples
```

**Full Enhancement**:
```
@enhance-prompt .cursor/prompts/category/my-prompt.prompt.md --comprehensive
```

---

## Related Prompts

- `prompt/improve-prompt.prompt.md` - Fix issues before enhancing
- `prompt/validate-prompt.prompt.md` - Check quality after enhancing
- `prompt/create-new-prompt.prompt.md` - Create prompts from scratch
- `rule-authoring/extract-prompts-from-conversation.prompt.md` - Extract patterns
- `templars/prompt/prompt-enhancement-workflow-templar.md` - Reusable enhancement structure
- `exemplars/prompt/prompt-enhancement-workflow-exemplar.md` - Reference enhanced prompt

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

## Extracted Patterns

This prompt demonstrates exceptional quality and has been extracted into:

**Templar**:
- `.cursor/prompts/templars/prompt/prompt-enhancement-workflow-templar.md` - Abstract pattern for categorized enhancement with decision trees and time-scoping

**Exemplar**:
- `.cursor/prompts/exemplars/prompt/prompt-enhancement-workflow-exemplar.md` - Reference implementation showing lean enhancement

**Why Extracted**: Demonstrates outstanding enhancement categorization (Structure/Content/Features/Documentation), decision tree for gap analysis, time-based scoping (quick/medium/deep 5-10min/15-30min/30+min), before/after comparisons with quantified impact assessment, and preservation of working functionality.

**Reuse**: Use the templar when creating improvement prompts for code refactoring, document enhancement, configuration optimization, or any artifact that works but could be better. Especially valuable when multiple improvement dimensions exist and time-scoping helps prioritize.

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)

