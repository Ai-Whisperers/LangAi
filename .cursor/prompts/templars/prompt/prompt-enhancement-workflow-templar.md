---
type: templar
artifact-type: prompt
pattern-name: prompt-enhancement-workflow
version: 1.0.0
applies-to: prompt meta-work
implements: prompt.enhance
extracted-from: .cursor/prompts/prompt/enhance-prompt.prompt.md
consumed-by:
  - .cursor/prompts/prompt/enhance-prompt.prompt.md
---

# Prompt Enhancement Workflow Templar

## Pattern Purpose
Enhance a working prompt without breaking core value: add structure, examples, validation, and documentation in a controlled pass.

## When to Use
- Base prompt works but lacks clarity, examples, or guardrails
- After fixes are done (post “improve” pass)
- When adding structured modes or richer documentation

## Inputs
- Prompt file path (existing `.prompt.md`)
- Primary gap (examples, structure, validation, docs, comprehensive)
- Time budget (quick / medium / deep)

## Deterministic Steps
1) Analyze: strengths to preserve, gaps to fill, risks of regressions
2) Choose enhancement type: examples | structure | feature/validation | documentation | comprehensive
3) Plan: smallest set of changes that improves the prompt without bloat
4) Apply: add only necessary sections, examples, and validation; preserve working parts
5) Validate: run against prompt-creation-rule and registry format; spot-check usage

## Structure to Produce
- Frontmatter: minimal, correct YAML; only needed fields (name, description, category, tags, argument-hint)
- Purpose: why and when to use; one short paragraph
- Required Context: bullets of inputs the user must supply
- Process: numbered steps tailored to the enhancement type
- Reasoning Process (for AI): short checklist of how to think; avoid verbosity
- Examples: 2–3 focused few-shots; no sprawling before/after dumps
- Expected Output: concise format spec; avoid over-detail
- Quality Criteria: 5–8 checklist items tied to gaps addressed
- Related: only high-value related prompts/rules

## Quality Bar (use to self-check)
- No redundant sections (combine Purpose/Use When; remove star ratings/effectiveness fluff)
- Examples are short, cover happy + edge; show input → output clearly
- Validation/quality criteria map to gaps fixed
- YAML compliant (no JSON arrays), polite description (“Please …”)
- File stays lean; cut horizontal-rule noise and repeated boilerplate

## Output
- A single enhanced prompt file, ready to use
- Brief change note (what was added, what was preserved)

## Usage Example
```
@enhance-prompt .cursor/prompts/prompt/example.prompt.md --type examples --time medium
```
