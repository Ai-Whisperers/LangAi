---
type: exemplar
artifact-type: prompt
demonstrates: prompt-quality-improvement
domain: prompt meta-work
quality-score: exceptional
version: 1.0.0
illustrates: prompt.improve
use: critic-only
notes: "Pattern extraction only. Do not copy exemplar content into outputs."
extracted-from: .cursor/prompts/prompt/improve-prompt.prompt.md
referenced-by:
  - .cursor/prompts/prompt/improve-prompt.prompt.md
  - .cursor/prompts/prompt/validate-prompt.prompt.md
---

# Prompt Quality Improvement Exemplar

## Why This Is Exemplary
- Runs the full diagnose → fix → validate loop
- Uses the five-lens rubric and fixes only what matters
- Delivers a ready-to-use improved prompt plus a crisp change log

## Key Quality Elements
1. Issue list grouped by lens with severity
2. Replacement prompt that is concise and standard-compliant
3. Minimal but complete sections (Purpose, Context, Process, Examples, Output, Quality Criteria)
4. YAML is clean, polite, and EPP-192 compliant
5. Examples are short, realistic, and testable

## Pattern Demonstrated (abridged)
- Lens findings:
  - Frontmatter: missing category and argument-hint; description not polite
  - Structure: no Purpose, no Expected Output
  - Clarity: instructions vague
  - Reusability: no argument-hint, too specific wording
  - Documentation: no examples, no quality criteria
- Fix:
  - Add clean frontmatter (category, tags, argument-hint)
  - Add Purpose and Expected Output
  - Rewrite Process into 4 clear steps
  - Add 2 brief examples (happy + edge)
  - Add 5-item quality checklist tied to fixes
- Validate: YAML ok; required sections present; examples align with output spec

## Exemplar Content (abridged)
```markdown
---
name: sample-check-status
description: "Please summarize current ticket status from context, progress, and timeline"
category: ticket
tags: ticket, status, summary
argument-hint: "Ticket ID or prompt path"
---

# Check Ticket Status (Improved)

Use to produce a concise status snapshot from existing ticket docs.

## Required Context
- ticket ID (or open files: context, progress, timeline)

## Process
1) Gather: read context.md, progress.md, timeline.md (if present)
2) Extract: current focus, blockers, latest actions
3) Summarize: status + blockers + next 3 steps
4) Validate: ensure sources cited; keep it concise

## Examples
### Example 1: Happy Path
Input: ticket files present  
Output: brief status + blockers + next steps

### Example 2: Missing Timeline
Input: context/progress only  
Output: status + note timeline missing + next steps

## Expected Output
- Status summary (1–2 lines)
- Blockers (if any)
- Next 3 steps
- Sources noted (context/progress/timeline)

## Quality Criteria
- [ ] YAML valid; polite description
- [ ] Purpose clear; instructions actionable
- [ ] Examples: happy + edge
- [ ] Expected Output matches summary format
- [ ] Mentions sources used
```

## Learning Points
- Quality pass is targeted: fix only what’s broken, keep it lean
- Examples stay short; they prove format and behavior
- Quality checklist mirrors the issues that were fixed

## When to Reference
Use when you need a concrete model of a full “improve” pass that keeps prompts small, compliant, and maintainable.

