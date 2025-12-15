---
name: condense-prompts
description: "Please condense enhanced prompts by trimming icing while preserving core effectiveness"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, condensation, prompts, templars, exemplars
argument-hint: "Prompt path(s) or a candidate report to drive condensation"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---

# Condense Prompts

Condense enhanced prompts (with heavy examples/reasoning) using a keep/condense/remove checklist, time-scoped modes, and a consistent example policy.

## Purpose

Reduce prompt size and redundancy while keeping effectiveness, clarity, and required structure. Apply especially to “iced” prompts with many examples or verbose reasoning.

## Required Context

- Target prompt(s) to condense, or a candidate report (e.g., from `find-extraction-candidates`)
- Destination rules for templars/exemplars if splitting content
- Applicable standards: prompt creation + registry integration

## Modes

- **Quick (5-10 min)**: Light trim, reduce repetitions, keep core sections intact.
- **Standard (15-30 min)**: Apply full checklist, move overflow examples to exemplars, tighten reasoning.
- **Deep (30+ min)**: Restructure sections for clarity, split reusable patterns into templars, refresh usage and validation.

## Keep / Condense / Remove Checklist

- **Keep**: Frontmatter, purpose, required context, concise process, expected output, validation checklist, 3–5 key examples (max).  
- **Condense**: Reasoning sections (shorten), duplicate Purpose/Description, repetitive separators, verbose example narratives (summarize).  
- **Remove/Extract**: Star ratings, effectiveness claims, duplicate “Use When,” excessive `---`, long AI reasoning, large before/after blocks → move to exemplars; reusable structure → move to templars.

### Extraction & Removal Verification
- Validate before removal/condensing: ensure target content qualifies as templar/exemplar material.
- Use `extract-templar-exemplar` to perform the actual extraction (this prompt does not extract); only condense after the extraction is saved and linked.
- After extraction, replace removed blocks with a short pointer to the templar/exemplar.
- Keep ≤5 inline examples in source; move overflow to exemplar.
- Confirm source still has required sections and valid frontmatter.
- Keep inline (do not extract) when the pattern is one-off/domain-specific, when removing it would lose essential quick-start context, or when the example is small and critical for immediate clarity (leave 1 compact example inline).

## Example Policy

- Limit inline examples to 3–5 concise cases.  
- Move long or numerous examples into an exemplar file and link to it.  
- Preserve one compact “golden” example inline if needed for quick orientation.

## Reasoning Process (for AI Agent)

1. Identify icing signals (examples, verbose reasoning, stars, duplicated sections).  
2. Decide what to keep vs extract (templar/exemplar) vs remove.  
3. Rewrite the prompt to be concise, preserving structure and required sections.  
4. If extracting, note destination paths for templar/exemplar and update links.  
5. Validate against the checklist and standards.

## Process

1. **Select Targets**  
   - Use the candidate list (or specific paths).  
   - Confirm destinations for extracted pieces (templars/exemplars).

2. **Plan Condensation**  
   - Apply the keep/condense/remove checklist.  
   - Decide which examples stay inline vs move to exemplar.

3. **Condense**  
   - Trim duplicate sections and verbose reasoning.  
   - Reduce examples to 3–5 concise ones.  
   - Move reusable structure to a templar; rich examples to an exemplar.

4. **Link & Update**  
   - Add pointers to extracted templars/exemplars.  
   - Ensure frontmatter and body still meet prompt rules.

5. **Validate**  
   - Run through the Validation Checklist.  
   - Spot-check for clarity, completeness, and registry readiness.

## Troubleshooting

- **Inline examples still exceed 5**: Move excess to an exemplar and keep one compact “golden” example inline.
- **Frontmatter YAML errors**: Reformat lists with `- item` syntax; avoid JSON arrays.
- **Lost links after extraction**: Add explicit references under Related Prompts/Rules to the new templar/exemplar paths.

## Output Format

```markdown
## Condensed Prompt
- Source: [path]
- Size: [before] → [after] lines
- Actions:
  - Kept: [list]
  - Condensed: [list]
  - Extracted: [templar/exemplar paths if any]
- Inline Examples: [count kept]
- Links: [templar/exemplar references]
```

## Validation Checklist

- [ ] Required sections intact (purpose, context, process, output, validation)  
- [ ] Frontmatter valid for registry (YAML, fields, no JSON arrays)  
- [ ] Inline examples ≤ 5 and concise  
- [ ] Long examples moved to exemplar (if present)  
- [ ] Reusable structure moved to templar (if applicable)  
- [ ] No stars/effectiveness claims/duplicate “Use When”  
- [ ] Excessive separators/verbosity removed  
- [ ] Links to extracted templar/exemplar added (if created)  
- [ ] Tone and clarity match prompt standards  

## Usage

```text
@condense-prompts .cursor/prompts/ticket/activate-ticket.prompt.md
@condense-prompts .cursor/prompts/ticket/catchup-on-ticket.prompt.md
@condense-prompts candidates.json
```

## Related Prompts

- `housekeeping/find-extraction-candidates.prompt.md`
- `housekeeping/extract-templar-exemplar.prompt.md`
- `prompt/improve-prompt.prompt.md`
- `prompt/enhance-prompt.prompt.md`

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc`
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc`
