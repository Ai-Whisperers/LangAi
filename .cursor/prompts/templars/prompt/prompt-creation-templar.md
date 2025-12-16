---
type: templar
artifact-type: prompt
pattern-name: prompt-creation
version: 1.0.0
applies-to: prompt meta-work
implements: prompt.create
extracted-from: .cursor/prompts/prompt/create-new-prompt.prompt.md
consumed-by:
  - .cursor/prompts/prompt/create-new-prompt.prompt.md
---

# Prompt Creation Templar

## Pattern Purpose
Create a new reusable prompt that is registry-ready, concise, and standards-compliant.

## When to Use
- Formalizing an ad-hoc prompt into the library
- Creating a fresh prompt with clear scope and structure

## Inputs
- Prompt name (kebab-case), purpose, category
- Target audience and use cases
- Expected output shape; optional examples

## Deterministic Steps
1) Define Purpose & Scope (what/why/when; boundaries)
2) Choose Category & Name (kebab-case; avoid redundant prefixes)
3) Write Frontmatter (minimal required fields; YAML compliant)
4) Draft Body (Purpose, Required Context, Process, Examples, Expected Output, Quality Criteria, Related)
5) Validate (prompt-creation-rule + registry integration; YAML check)
6) Test (run once in chat; adjust)

## Structure to Produce
- Frontmatter: name, description (“Please …”), category, tags, argument-hint (if input needed)
- Purpose: short paragraph; state intent and when to use
- Required Context: bullets of inputs needed
- Process: 3–7 numbered steps, outcome-focused
- Reasoning Process (for AI): brief checklist
- Examples: 1–2 few-shots (happy + edge), concise
- Expected Output: clear format; avoid verbosity
- Quality Criteria: 4–7 checks tied to correctness and clarity
- Related Prompts/Rules: only high-value links

## Quality Bar
- YAML valid; no JSON arrays; polite description
- Sections present and minimal; no redundant horizontal rules
- Examples prove usage and expected format; stay short
- Output spec matches what examples show
- Tags specific (3–6); argument-hint present if needed

## Output
- A single `.prompt.md` ready for library/collection inclusion
- Optional note for which collection to add

## Usage Example
```
@create-new-prompt "validate-openapi" "Please validate OpenAPI specs" --category api-testing
```
