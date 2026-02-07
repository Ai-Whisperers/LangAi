---
name: architectural-question
description: "Ask respectful questions about design and architecture"
category: code-quality
tags: architecture, design, patterns, organization, structure
argument-hint: "@code/folders and your question about structure"
---

# Architectural Question (Pattern-Based)

This prompt asks respectful questions about design decisions, structure, or architecture.

**Pattern**: Architectural Question Pattern ⭐⭐⭐⭐
**Effectiveness**: Resolves design confusion, validates approaches
**Use When**: Unclear about design decisions, questioning structure, seeking guidance

---

## Required Context

- **Code/Folders**: Relevant files or directories to reference with @
- **Question**: What you're confused about or want to understand
- **Confusion** (Optional): What seems wrong or unexpected

---

## Reasoning Process

The AI should:
1. **Examine Structure**: Review referenced code/folders
2. **Identify Pattern**: Recognize the design pattern or architecture used
3. **Explain Rationale**: Provide reasoning for why it's organized that way
4. **Validate or Correct**: Confirm good design OR identify actual issues
5. **Suggest Alternatives**: Propose better approaches if appropriate
6. **Respect Humility**: Acknowledge that human may have understood correctly

---

## Basic Usage

```
@[RELEVANT_CODE_OR_FOLDERS] [QUESTION_ABOUT_STRUCTURE]

[OPTIONAL_WHAT_SEEMS_CONFUSING]
```

**Placeholder Conventions**:
- `[RELEVANT_CODE_OR_FOLDERS]` - @ reference to files/folders (e.g., @Adapters, @Services/ExportService.cs)
- `[QUESTION_ABOUT_STRUCTURE]` - Your question (use "why", "how", "is this")
- `[OPTIONAL_WHAT_SEEMS_CONFUSING]` - What seems off, or add "or do I misunderstand"

---

## Example Questions

### Question Folder Organization
```
@Adapters @bin @Commands @Models these folders look to be in the wrong place

compared to @Services and @Shared

or do I misunderstand
```

### Question Approach
```
@ExportService.cs

Is this the right way to implement parent reference resolution?

Seems like it could be simplified
```

### Question Design Decision
```
@CurrentImplementation.cs

Why is X organized this way?

Would approach Y be better?
```

### Compare Alternatives
```
Should we use approach A or B for the export implementation?

Approach A: [description]
Approach B: [description]
```

---

## Question Types

### 1. Organization/Structure
```
@[FOLDERS] why are these organized this way?
```

**Example:**
```
@src/Adapters @src/Commands

Why are these at the same level as Shared?

Shouldn't they be under a different folder?
```

---

### 2. Design Validation
```
@[CODE] is this the right approach for [GOAL]?
```

**Example:**
```
@ExportService.cs is this the right approach for resolving parent references?

Seems complex - is there a simpler pattern?
```

---

### 3. Alternative Comparison
```
Should we use [OPTION_A] or [OPTION_B]?

[Compare pros/cons]
```

**Example:**
```
Should we use in-memory caching or database queries for parent reference resolution?

In-memory: Fast but memory intensive
Database: Slower but lower memory footprint
```

---

### 4. Clarification
```
@[CODE] how does [COMPONENT] work?

Trying to understand [SPECIFIC_ASPECT]
```

**Example:**
```
@ExportOrchestrationService.cs how does the orchestration work?

Trying to understand the relationship between ExportService and ExportFactory
```

---

### 5. Rationale Request
```
@[CODE] why was [DECISION] made?

[What's confusing about it]
```

**Example:**
```
@ParentReferenceResolver.cs why do we resolve references at export time?

Why not pre-load them all at startup?
```

---

## What This Pattern Does

✅ Opens respectful dialogue about design
✅ Reveals assumptions and rationale
✅ Helps understand existing patterns
✅ Validates or corrects architecture
✅ Prevents wrong implementations

---

## Asking Respectfully

### ✅ Good Approaches:
```
- "or do I misunderstand"
- "Is this the right way..."
- "Why is X organized this way?"
- "Would Y be better?"
- "Trying to understand..."
```

### ❌ Avoid:
```
- "This is wrong"
- "You did this badly"
- "Fix this structure"
```

---

## Expected AI Response

AI will typically:
1. **Explain** current organization/rationale
2. **Clarify** any misconceptions
3. **Validate** good design or identify issues
4. **Propose** corrections if structure actually wrong
5. **Recommend** alternative if better approach exists

---

## Response Scenarios

### Scenario 1: Your Understanding is Correct
```
You're right - this structure is intentional because [REASON]

[Explanation of the design]
```

### Scenario 2: Misconception Cleared
```
Good question! The confusion is understandable. Here's why:

[Explanation that resolves confusion]
```

### Scenario 3: Actual Issue Found
```
You've identified a real issue. This should be organized differently:

[Explanation + Fix proposal]
```

### Scenario 4: Better Alternative
```
The current approach works, but there's a better way:

[Alternative explanation]
```

---

## Follow-up Patterns

### After Understanding
```
Thanks, that makes sense now. Let's proceed with [NEXT_STEP]
```

### After Issue Identified
```
OK, please reorganize as you suggested
```

### After Alternative Proposed
```
Let's go with approach [CHOICE] - please implement
```

---

## Examples by Domain

### Code Organization
```
@src/ folder structure - is this standard for this type of project?
```

### Class Design
```
@Service.cs why is this both a service and factory?

Seems to violate single responsibility
```

### Data Flow
```
@Export/ how does data flow from repository to Excel?

Trying to understand the transformation pipeline
```

### Pattern Usage
```
@Factory/ are we using factory pattern correctly here?

Seems like some factories are also doing transformation
```

---

## Comparing to Existing Patterns

```
@NewImplementation should this follow the same pattern as @ExistingFeature?

They seem similar but are structured differently
```

---

## Tips

- **Reference specific code** with @ mentions
- **Be humble** - "or do I misunderstand"
- **Explain confusion** - what seems off
- **Suggest alternatives** if you have ideas
- **Listen to rationale** - there may be good reasons
- **Ask before changing** - don't assume structure is wrong

---

## Learning Opportunity

These questions are great for:
- **Onboarding** to new codebase
- **Understanding patterns** used
- **Validating assumptions** before big changes
- **Learning** architectural decisions
- **Preventing** wrong implementations

---

## Multi-Part Questions

Break complex questions:

```
Question 1: Why are Adapters at this level?
[Get answer]

Question 2: Should Commands be grouped with Adapters?
[Get answer]

Question 3: Is there a standard pattern we should follow?
```

---

## Anti-Pattern (Don't Do This)

❌ **Assertive without understanding**:
```
This structure is wrong, fix it
```

❌ **Too many questions at once**:
```
Why is this here, why is that there, should we change A, B, C, D, and E?
```

✅ **Respectful and focused**:
```
@Adapters @Commands these seem to be in an unexpected place

or do I misunderstand the folder organization pattern?
```

---

## Expected AI Response

When you ask an architectural question, the AI should:

1. **Review Referenced Code**
   ```
   Examining @[files/folders]...
   ```

2. **Provide Context**
   ```
   The current structure is organized this way because:
   [Clear explanation of rationale]
   ```

3. **Address Confusion**
   ```
   Your observation about [issue] is:
   - Correct: [Confirm + explain]
   - A misconception: [Clarify + explain]
   - Valid concern: [Acknowledge + propose fix]
   ```

4. **Suggest if Needed**
   ```
   Alternative approach (if applicable):
   [Better way to organize/implement]

   Pros: [Benefits]
   Cons: [Trade-offs]
   ```

5. **Be Humble**
   ```
   Let me know if this explanation helps, or if you'd like me to reorganize.
   ```

---

## Quality Criteria

For effective architectural questions:

- [ ] Specific code/folders referenced with @
- [ ] Clear question stated (not just "this seems wrong")
- [ ] Humble tone ("or do I misunderstand")
- [ ] Context about what's confusing
- [ ] Open to learning (not asserting)

For AI responses:

- [ ] Code/structure actually examined
- [ ] Rationale explained clearly
- [ ] Admits if structure is suboptimal
- [ ] Proposes alternatives if better approaches exist
- [ ] Respectful of both human insight and existing design

---

## Related Prompts

- `code-quality/request-feature.md` - After understanding, request changes
- `ticket/validate-before-action.md` - Before making architectural changes

---

**Source**: Pattern Discovery Analysis (48 conversations, Nov 22 - Dec 01, 2025)
**Pattern ID**: #10 Architectural Question Pattern
**Evidence**: conversations/JP/extracted/pattern-discovery-report.md
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
