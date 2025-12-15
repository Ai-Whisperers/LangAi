---
type: templar
artifact-type: prompt
pattern-name: prompt-quality-improvement
version: 1.0.0
applies-to: prompt meta-work
implements: prompt.improve
extracted-from: .cursor/prompts/prompt/improve-prompt.prompt.md
consumed-by:
  - .cursor/prompts/prompt/improve-prompt.prompt.md
---

# Prompt Quality Improvement Templar

## Pattern Purpose
Diagnose and fix prompt quality issues before enhancement. Produce a corrected, standard-compliant prompt plus a brief change log.

## When to Use
- Prompt has unclear instructions, missing sections, or format issues
- Before any enhancement pass
- When aligning to prompt-creation-rule and registry format

## Inputs
- Prompt file path or raw content
- Access to prompt-creation-rule and registry integration rule

## Deterministic Steps
1) Read & Understand Intent  
2) Analyze against five lenses: Frontmatter, Structure, Clarity, Reusability, Documentation  
3) Identify Issues with severity (critical / important / nice-to-have)  
4) Rewrite: produce a complete improved prompt fixing all issues  
5) Document Changes: short list of what changed and why  
6) Validate: YAML correctness, required sections present, examples usable  

## Structure to Produce
- Frontmatter: required fields only; correct YAML; polite description
- Purpose: single paragraph (what/why/when)
- Required Context: concise bullets
- Process/Instructions: numbered, actionable
- Reasoning Process (for AI): short checklist, not narrative
- Examples: 1–2 targeted few-shots; show input → output; keep brief
- Expected Output: compact format spec
- Quality Criteria: checklist tied to fixed issues
- Related Prompts/Rules: only high-value links

## Issue Categories (fast rubric)
- Frontmatter: missing fields, bad YAML, vague description, weak tags
- Structure: missing Purpose/Process/Output
- Clarity: ambiguity, missing scope, unclear outputs
- Reusability: hardcoded specifics, no argument-hint
- Documentation: no examples, no quality criteria, missing related refs

## Output
- Improved prompt content (replacement-ready)
- Issue list (optional brief) and change log (1–5 bullets)

## Usage Example
```
@improve-prompt .cursor/prompts/prompt/example.prompt.md
```

