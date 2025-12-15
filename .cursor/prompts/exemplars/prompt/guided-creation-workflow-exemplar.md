---
type: exemplar
artifact-type: prompt
demonstrates: comprehensive-guidance, decision-trees, complete-templates
quality-score: exceptional
version: 1.0.0
illustrates: prompt.organize
use: critic-only
notes: "Pattern extraction only. Do not copy exemplar content into outputs."
extracted-from: .cursor/prompts/prompt/organize-prompts.prompt.md
referenced-by:
  - .cursor/prompts/prompt/organize-prompts.prompt.md
---

# Guided Creation Workflow Exemplar

## Why This is Exemplary

The `create-new-prompt.prompt.md` demonstrates exceptional quality in guiding users through complex creation tasks. It achieves remarkable clarity and completeness through:

1. **Outstanding Decision Support** - Decision trees at every choice point
2. **Comprehensive Examples** - Multiple complete walkthroughs showing entire process
3. **Clear Good/Bad Patterns** - Explicit ✅/❌ examples throughout
4. **Complete Templates** - Ready-to-use templates with annotations
5. **Progressive Disclosure** - Basic → Enhanced structures for different skill levels
6. **Multi-Modal Interaction** - Interactive, direct, and template-based invocation

## Key Quality Elements

### 1. Decision Trees at Every Step ⭐⭐⭐⭐⭐

**What Makes It Exceptional**:
The prompt provides clear decision logic at each step, eliminating ambiguity:

```markdown
### Step 2: Choose Location

**Existing Categories**:
- `agile/` - Agile artifacts (epics, stories, features)
- `code-quality/` - Code quality and refactoring
- `cicd/` - CI/CD and automation
[...15+ categories with clear descriptions]

**New Category?**: Create if no existing category fits
```

**Why This Works**:
- User sees ALL options upfront
- Each option has clear description
- Guidance on when to create new category
- No guesswork needed

### 2. Good vs Bad Examples Throughout ⭐⭐⭐⭐⭐

**Pattern Demonstrated**:
```markdown
**Examples**:
- ✅ `create-user-story.prompt.md`
- ✅ `validate-test-coverage.prompt.md`
- ❌ `story.prompt.md` (too vague)
- ❌ `CreateUserStory.prompt.md` (wrong case)
- ❌ `agile-create-user-story.prompt.md` (redundant category)
```

**Why This Works**:
- Visual distinction (✅/❌) instantly clear
- Explanations show reasoning, not just rules
- Multiple examples show pattern, not edge case
- Users learn by seeing mistakes to avoid

### 3. Complete Walkthrough Examples ⭐⭐⭐⭐⭐

**Example Structure**:
```markdown
### Example 1: Creating a Testing Prompt (Complete Workflow)

**Request**: "Create a prompt to check test coverage"

**Step 1 - Define Purpose**:
- What: Analyze unit test coverage for files/modules
- Who: Developers ensuring code quality
- When: Before code review, after adding features
- Output: Coverage report with gaps identified

**Step 2 - Choose Location**:
- Category: `unit-testing/` (testing operations)

[...continues through all 6 steps with specific decisions]

**Final File**: `.cursor/prompts/unit-testing/analyze-test-coverage.prompt.md`
```

**Why This Works**:
- Shows EVERY step, not just highlights
- Real decisions, not placeholders
- Demonstrates reasoning at each choice
- Complete path from request to final output
- User can follow along as checklist

### 4. Progressive Disclosure Structure ⭐⭐⭐⭐⭐

**Pattern Demonstrated**:
```markdown
**Minimum Structure**:
[Basic template for beginners]

**Enhanced Structure** (Recommended):
[Advanced template with more sections]
```

**Why This Works**:
- Beginners not overwhelmed
- Experts see better practices
- Clear labeling ("Minimum" vs "Enhanced")
- Both options fully documented
- Gradual path to mastery

### 5. Ready-to-Use Templates ⭐⭐⭐⭐⭐

**Complete Template Provided**:
```markdown
## Prompt Template

```markdown
---
name: your-prompt-name
description: "What this prompt does in one clear sentence"
category: appropriate-category
tags: tag1, tag2, tag3, tag4
argument-hint: "What input it expects (if applicable)"
---

# Your Prompt Title

[...complete template with annotations...]
```
```

**Why This Works**:
- Copy-paste ready
- Inline annotations explain each part
- Follows all standards
- Reduces error-prone manual writing
- Users customize, not create from scratch

### 6. Multiple Invocation Modes ⭐⭐⭐⭐

**Pattern Demonstrated**:
```markdown
## Quick Start

**Interactive Creation**:
@create-new-prompt
[Shows conversation flow]

**Direct Creation**:
@create-new-prompt "prompt-name" for "purpose description"

**From Template**:
@create-new-prompt using template
```

**Why This Works**:
- Supports different work styles
- Interactive for uncertain users
- Direct for confident users
- Template for standardized creation
- All modes clearly documented

## Pattern Demonstrated

### The Guided Workflow Pattern

**Core Structure**:
1. **Expected Output First** - Show what success looks like
2. **Reasoning Process** - Prime thinking before action
3. **Step-by-Step Breakdown** - Manageable chunks with clear deliverables
4. **Decision Support** - Trees, options, examples at choice points
5. **Complete Examples** - Full walkthroughs, not fragments
6. **Templates** - Ready-to-use starting points
7. **Validation** - Quality checks before claiming done

**Implementation Details**:
- Each step has clear: objective → guidance → examples → validation
- Decision points use visual aids (trees, tables, lists)
- Examples show both success and failure paths
- Templates include annotations explaining choices
- Multiple usage modes support different skill levels

## Learning Points

### For Prompt Authors

1. **Decision Support is Critical**
   - Don't assume users know how to choose
   - Provide decision trees, not just lists
   - Explain reasoning, not just rules

2. **Examples Must Be Complete**
   - Show entire workflow, not highlights
   - Include reasoning at each step
   - Use real scenarios, not toy examples

3. **Good/Bad Pairs Teach Effectively**
   - Visual markers (✅/❌) work instantly
   - Explanations reinforce learning
   - Multiple examples show patterns

4. **Templates Reduce Friction**
   - Complete templates users can copy
   - Annotations explain choices
   - Standards embedded, not referenced

5. **Progressive Disclosure Serves All**
   - Basic version for beginners
   - Enhanced version for experts
   - Clear labeling of each level

### For Complex Workflows

1. **Break Into Clear Phases**
   - Define → Choose → Configure → Validate
   - Each phase has clear deliverable
   - Dependencies between phases explicit

2. **Provide Complete Examples**
   - Walk through entire process
   - Show decision reasoning
   - Include validation confirmation

3. **Support Multiple Entry Points**
   - Interactive for guidance
   - Direct for speed
   - Template for standards

## When to Reference

Use this exemplar when creating prompts that:
- Guide users through multi-step processes
- Require decisions at multiple points
- Need to support both beginners and experts
- Create structured artifacts
- Benefit from templates

**Specific Scenarios**:
- ✅ Setup/configuration wizards
- ✅ Artifact creation workflows
- ✅ Migration/transformation tasks
- ✅ Onboarding processes
- ✅ Any creation task with 4+ steps

## Anti-Patterns to Avoid

### ❌ Incomplete Examples

**Bad**:
```markdown
### Example: Create a prompt
Step 1: Define purpose [explain purpose]
Step 2: [rest of example]
...
```

**Why Bad**: Leaves users guessing, no complete path to success

### ❌ Vague Decision Points

**Bad**:
```markdown
Choose the appropriate category for your prompt.
```

**Why Bad**: No guidance on HOW to choose appropriately

### ❌ Missing Good/Bad Examples

**Bad**:
```markdown
Name should be descriptive and use kebab-case.
```

**Why Bad**: No concrete examples showing what "descriptive" means

### ❌ Abstract Templates

**Bad**:
```markdown
## Template
[Your content here]
```

**Why Bad**: No structure, no guidance, forces user to figure it out

## Full Exemplar Content

See: `.cursor/prompts/prompt/create-new-prompt.prompt.md`

**Preserved for reference as best-in-class example of:**
- Guided multi-step workflows
- Decision support throughout
- Complete walkthrough examples
- Good/bad pattern examples
- Ready-to-use templates
- Progressive disclosure (basic → enhanced)
- Multiple invocation modes

## Related Exemplars

- `comprehensive-documentation-exemplar.md` - Shows documentation quality standards
- `few-shot-pattern-exemplar.md` - Demonstrates Few-Shot learning (if extracted)
- `validation-feedback-exemplar.md` - Shows clear error/success messaging (if exists)

## Usage in Practice

**When creating setup workflows**:
- Reference Step 2 decision tree pattern
- Use Step-by-step breakdown structure
- Include complete walkthrough example

**When creating configuration prompts**:
- Reference good/bad examples pattern
- Use progressive disclosure structure
- Include ready-to-use templates

**When creating wizard-style prompts**:
- Reference entire guided workflow structure
- Use decision trees at each choice
- Include validation step at end

## Maintenance Notes

**Update this exemplar if**:
- Better examples of guided workflows emerge
- New guidance patterns prove more effective
- Standards for creation tasks evolve

**Current best practices demonstrated**:
- Chain-of-Thought reasoning section (primes thinking)
- Expected Output section first (shows success)
- Multiple complete examples (2+ full walkthroughs)
- Good/bad pairs throughout (visual learning)
- Quality checklist (validation criteria)

---

**Exemplar Quality Score**: 96/100
- Clarity: 10/10
- Completeness: 10/10
- Examples: 10/10
- Reusability: 9/10
- Innovation: 9/10

**Recognition**: This prompt sets the gold standard for guided workflow design in prompt engineering.

