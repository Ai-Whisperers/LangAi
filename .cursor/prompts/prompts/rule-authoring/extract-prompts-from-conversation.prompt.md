---
name: extract-prompts-from-conversation
description: "Please analyze conversation transcripts to extract reusable prompt patterns and techniques"
category: rule-authoring
tags: prompts, extraction, analysis, patterns
argument-hint: "Conversation source file or path"
---

# Extract Prompts from Conversation

Please analyze the conversation transcript below and extract all reusable prompts following the prompt extraction rule framework:

**Conversation Source**: `[REPLACE WITH SOURCE FILE/PATH]`
**Extraction Goal**: `[REPLACE WITH: pattern-discovery/template-creation/technique-analysis]`

**Applies Rules**:
- `.cursor/rules/prompts/prompt-extraction-rule.mdc` - Full extraction process
- `.cursor/rules/prompts/prompt-creation-rule.mdc` - For creating templates

## Extraction Process

### 1. Identify and Categorize Prompts

For each user prompt found in the conversation, assign:

- **ID**: PROMPT-001, PROMPT-002, etc.
- **Type**: 
  - Initial Request
  - Refinement
  - Exploration
  - Implementation
  - Validation
  - Documentation
- **Stage**: beginning/middle/end of conversation
- **Context**: What led to this prompt

### 2. Extract Details

For each prompt capture:

```markdown
### PROMPT-XXX: [Descriptive Title]

**Type**: [prompt type]
**Stage**: [conversation stage]
**Problem Addressed**: [what issue this solved]
**Prerequisites**: [what was needed before this]

**Original Prompt**:
```
[Exact text as written by user]
```

**Outcome**: [what resulted - success/partial/needs-refinement]

**Effectiveness Rating**: ⭐⭐⭐⭐⭐ (1-5 stars)

**Pattern Analysis**:
- Structure: [how it was organized]
- Key Elements: [what made it effective/ineffective]
- Context Dependencies: [what implicit context influenced this]
- Reusability: [how broadly applicable is this]

**Reusable Template**:
```
[Generic version with placeholders]
```
```

### 3. Meta-Analysis

After extracting all prompts:

**Conversation Strategy**:
- Overall approach taken
- How prompts built on each other
- Evolution of understanding through prompts

**Effective Patterns**:
1. [Pattern name]: [description and why it worked]
2. [Pattern name]: [description and why it worked]
...

**Iteration Patterns**:
- How prompts were refined
- What triggered refinements
- Success indicators used

**Challenges Encountered**:
- Where prompts needed clarification
- What information was missing
- How challenges were overcome

### 4. Generate Reusable Templates

Create 3-5 generic prompt templates:

```markdown
#### Template: [Name]

**Use When**: [specific scenario or goal]

**Prerequisites**: [what must exist/be known first]

**Template**:
```
[Generic prompt with [REPLACE WITH ...] placeholders]
```

**Expected Outcome**: [what this should produce]

**Follow-up Actions**: [typical next steps]
```

## Analysis Guidelines

**Focus On**:
- User prompts only (not AI responses)
- Both successful and unsuccessful prompts
- Exact wording that reveals technique
- Implicit context that influenced effectiveness
- How prompts built on previous interactions

**Ignore**:
- Simple acknowledgments ("ok", "thanks")
- Pure questions without action request
- Conversational filler

**Rating Criteria** (1-5 stars):
- ⭐ Failed to produce useful result
- ⭐⭐ Produced partial result, needed significant refinement
- ⭐⭐⭐ Produced good result with minor adjustments
- ⭐⭐⭐⭐ Produced excellent result, minimal refinement
- ⭐⭐⭐⭐⭐ Perfect prompt, produced exactly what was needed

## Output Structure

```markdown
# Prompt Extraction Report

**Source**: [conversation source]
**Date**: [date]
**Domain**: [what domain/area this conversation covered]

## Executive Summary
[2-3 sentences on what this conversation accomplished and key patterns]

---

## Extracted Prompts

[All prompts following format above]

---

## Meta-Analysis

### Conversation Strategy
[Overall approach description]

### Effective Patterns
[List of patterns with examples]

### Iteration Patterns
[How prompts evolved]

### Challenges and Solutions
[Problems encountered and how they were resolved]

---

## Reusable Templates

[3-5 templates following format above]

---

## Recommendations

### For Similar Conversations
[Specific advice for similar scenarios]

### General Prompt Techniques
[Broader lessons learned]

### Avoid These Patterns
[Anti-patterns observed]

---

## Statistics

- Total prompts extracted: [N]
- Highly effective (4-5 stars): [N]
- Required refinement (2-3 stars): [N]
- Ineffective (1 star): [N]
- Most common type: [type]
- Average effectiveness: [X.X stars]
```

## Deliverables

Provide:

1. **Complete extraction report** following output structure
2. **All prompts** with ratings and analysis
3. **3-5 reusable templates** with placeholders
4. **Recommendations** for similar conversations
5. **Statistics summary**

Save to: `conversations/JP/extracted/[conversation-name]-prompt-extraction.md`

## Related Resources

- `.cursor/rules/rule-authoring/rule-extraction-from-practice.mdc` - Similar extraction process
- `.cursor/rules/rule-authoring/rule-templars-and-exemplars.mdc` - Template patterns
- `conversations/JP/` - Source conversations

---

## 📋 Conversation Transcript

[PASTE FULL CONVERSATION TRANSCRIPT HERE]

---

## Complete Framework

For full details on extraction process, see:
- `.cursor/rules/prompts/prompt-extraction-rule.mdc` - Complete 6-phase extraction process
- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Standards for creating prompt templates
- `.cursor/rules/prompts/prompts-rules-index.mdc` - Overview and navigation

**Note**: This extraction helps identify successful prompt patterns to reuse in future conversations and improves overall interaction effectiveness.

