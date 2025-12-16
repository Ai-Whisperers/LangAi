# Prompt Exemplars Index

This directory contains **exemplar** files - concrete examples of exceptional quality extracted from high-quality prompts. Exemplars demonstrate excellence and serve as reference standards.

## What is an Exemplar?

An **exemplar** is a concrete reference example that:
- Demonstrates exceptional implementation quality
- Shows best practices in action
- Serves as reference standard for similar work
- Focuses on SPECIFIC CONTENT demonstrating excellence
- Explains WHY it's exemplary (learning points)

**Exemplar vs Templar**: Exemplars are concrete examples; templars are abstract templates.

## Available Exemplars

### 1. Guided Creation Workflow Exemplar

**File**: `guided-creation-workflow-exemplar.md`
**Source**: `create-new-prompt.prompt.md`
**Quality Score**: 96/100 (Exceptional)

**Demonstrates**:
- Comprehensive guidance with decision trees at every step
- Complete walkthrough examples (not fragments)
- Clear good/bad pattern examples throughout
- Ready-to-use templates with annotations
- Progressive disclosure (basic → enhanced)
- Multiple invocation modes (interactive, direct, template)

**Key Excellence Points**:
1. **Outstanding Decision Support** ⭐⭐⭐⭐⭐
   - Decision trees at every choice point
   - User sees ALL options upfront with clear descriptions
   - No guesswork needed

2. **Good vs Bad Examples Throughout** ⭐⭐⭐⭐⭐
   - Visual distinction (✅/❌) instantly clear
   - Explanations show reasoning, not just rules
   - Multiple examples establish patterns

3. **Complete Walkthrough Examples** ⭐⭐⭐⭐⭐
   - Shows EVERY step with specific decisions
   - Real scenarios, not placeholders
   - User can follow as checklist

4. **Progressive Disclosure** ⭐⭐⭐⭐⭐
   - Minimum structure for beginners
   - Enhanced structure for experts
   - Clear path to mastery

5. **Ready-to-Use Templates** ⭐⭐⭐⭐⭐
   - Copy-paste ready
   - Inline annotations explain choices
   - Standards embedded

**When to Reference**:
- Creating setup/configuration wizards
- Building artifact creation workflows
- Designing multi-step guided processes
- Supporting both beginners and experts

**Learning Points**:
- Decision support is critical (don't assume users know)
- Examples must be complete (show entire workflow)
- Good/bad pairs teach effectively
- Templates reduce friction significantly
- Progressive disclosure serves all skill levels

---

### 2. Comprehensive Documentation Exemplar

**File**: `comprehensive-documentation-exemplar.md`
**Source**: Multiple prompt sources (pattern compilation)
**Quality Score**: 95/100 (Exceptional)

**Demonstrates**:
- Few-Shot examples throughout with complete workflows
- Decision trees for complex choices
- Before/after comparison patterns
- Comprehensive troubleshooting sections
- Good/bad example pairs
- Ready-to-use templates
- Progressive disclosure
- Reasoning process sections
- Quality checklists
- Multi-mode usage patterns

**Key Excellence Points**:
1. **Few-Shot Examples** ⭐⭐⭐⭐⭐
   - Complete workflows from request to final output
   - Reasoning at each decision point
   - Real scenarios with specific outcomes

2. **Decision Trees** ⭐⭐⭐⭐⭐
   - Visual structure instantly clear
   - Covers all decision branches
   - Multi-level trees for complex decisions

3. **Before/After Comparisons** ⭐⭐⭐⭐⭐
   - Shows actual transformation
   - Analysis explains WHY changes needed
   - Quantified impact demonstrates value

4. **Troubleshooting Sections** ⭐⭐⭐⭐
   - Issue → Cause → Solution structure
   - Multiple possible causes addressed
   - Verification steps for diagnosis

5. **Reasoning Sections** ⭐⭐⭐⭐⭐
   - Primes thinking before action (CoT)
   - Makes implicit reasoning explicit
   - Improves output quality

**When to Reference**:
- Creating documentation for complex processes
- Building guides that serve multiple skill levels
- Documenting transformations/improvements
- Providing comprehensive troubleshooting

**Learning Points**:
- Few-Shot examples must show complete workflows
- Decision trees prevent users from getting stuck
- Before/after with quantified impact communicates value
- Reasoning sections improve output quality
- Multiple patterns combined create gold standard

**Pattern Combinations**:
This exemplar shows how to combine multiple documentation patterns for maximum clarity and usability.

---

## Quality Scoring

Exemplars are evaluated on:

| Dimension | Weight | Description |
|---|----|----|
| **Clarity** | 20% | How clearly the content communicates |
| **Completeness** | 20% | How thoroughly it covers the topic |
| **Examples** | 20% | Quality and completeness of examples |
| **Reusability** | 20% | How easily patterns can be applied elsewhere |
| **Innovation** | 20% | Novel approaches or exceptional execution |

**Scores**:
- **90-100**: Exceptional (reference standard)
- **80-89**: Excellent (worth studying)
- **70-79**: Good (solid implementation)
- **<70**: Not exemplar quality

## When to Reference Exemplars

### By Documentation Need

| Need | Recommended Exemplar |
|---|---|
| Multi-step guided workflows | Guided Creation Workflow |
| Comprehensive documentation | Comprehensive Documentation |
| Decision support patterns | Both (complementary) |
| Before/after transformations | Comprehensive Documentation |
| Template design | Guided Creation Workflow |

### By Learning Goal

**To learn**:
- **Decision tree design** → Both exemplars show patterns
- **Few-Shot example structure** → Comprehensive Documentation
- **Progressive disclosure** → Guided Creation Workflow
- **Troubleshooting sections** → Comprehensive Documentation
- **Template design** → Guided Creation Workflow

## How to Use Exemplars

### Step 1: Identify Need
Determine what aspect of quality you want to improve.

### Step 2: Study Exemplar
Read the "Why This is Exemplary" section to understand excellence criteria.

### Step 3: Review Key Elements
Examine specific patterns demonstrated with high ratings (⭐⭐⭐⭐⭐).

### Step 4: Extract Pattern
Identify the structural pattern you want to apply.

### Step 5: Adapt to Context
Apply pattern to your specific domain with appropriate customization.

### Step 6: Validate Quality
Compare your implementation to exemplar quality criteria.

## Learning from Exemplars

### Pattern: Few-Shot Examples

**From**: Comprehensive Documentation Exemplar

**Structure**:
```markdown
### Example 1: [Scenario] (Complete Workflow)
**Request**: [User request]
**Step 1**: [Decisions made]
**Step 2**: [Actions taken]
[...all steps...]
**Final Output**: [Result]
```

**Apply**: Show ENTIRE workflow, not fragments. Include reasoning.

### Pattern: Decision Trees

**From**: Both Exemplars

**Structure**:
```
[Question]?
├─ [Condition A] → [Action A]
├─ [Condition B] → [Action B]
└─ [Condition C] → [Action C]
```

**Apply**: Visual structure for complex choices. Cover all branches.

### Pattern: Before/After Comparison

**From**: Comprehensive Documentation Exemplar

**Structure**:
```markdown
**Before**: [Initial state]
**Analysis**:
- **Strengths**: [Good parts]
- **Gaps**: [Missing parts]

**After**: [Improved state]
**Impact**:
- **Quality**: ⬆️ X%
```

**Apply**: Show transformation with quantified impact.

## Exemplar Anti-Patterns

### What Makes Something NOT Exemplary

❌ **Incomplete Examples**
- Showing only highlights, not complete workflows
- Leaving user to "figure out the rest"

❌ **Vague Guidance**
- "Choose the appropriate option" without criteria
- No decision support provided

❌ **Abstract Placeholders**
- `[Your content here]` without structure
- No concrete examples to learn from

❌ **Missing Reasoning**
- Steps without explanation of WHY
- No decision rationale provided

## Contributing New Exemplars

To add a new exemplar:

1. **Identify exceptional quality** in existing prompts
2. **Document WHAT makes it exceptional** (specific elements)
3. **Explain WHY it's exemplary** (learning points)
4. **Rate quality dimensions** (clarity, completeness, etc.)
5. **Provide usage guidance** (when to reference, how to apply)
6. **Add to this index** with summary

**Quality Bar**: Only prompts scoring ≥90/100 should become exemplars.

See `extract-templar-exemplar.prompt.md` for extraction guidance.

## Exemplar vs Source Prompt

**Source Prompt**: The actual working prompt file
**Exemplar**: Documentation explaining WHY it's exceptional and HOW to learn from it

**Relationship**: Exemplars reference source prompts but add meta-analysis explaining excellence.

## Related Directories

- **`.cursor/prompts/templars/prompt/`** - Abstract structural templates
- **`.cursor/prompts/prompt/`** - Actual prompts (sources for exemplars)
- **`.cursor/rules/rule-authoring/`** - Rules for creating rules/prompts

## Metadata

**Last Updated**: 2025-12-08
**Exemplar Count**: 2
**Average Quality Score**: 95.5/100
**Extraction Source**: `.cursor/prompts/prompt/` folder analysis
**Related Prompt**: `extract-templar-exemplar.prompt.md`

## Recognition

These exemplars represent the gold standard for prompt engineering quality in this codebase. They demonstrate what "comprehensive," "clear," and "well-structured" mean in practice.
