---
name: extract-templar-exemplar
description: "Please extract reusable templates (templars) or reference examples (exemplars) from any artifact type"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, templars, exemplars, extraction, patterns, maintenance
argument-hint: "Artifact file path (e.g., .cursor/rules/ticket/plan-rule.mdc) or folder to scan"
---

# Extract Templar or Exemplar

Please analyze existing artifacts (rules, prompts, tickets, etc.) to identify reusable template patterns (templars) or exceptional reference examples (exemplars) worth promoting to dedicated folders.

**Pattern**: Pattern Extraction Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: Essential for building reusable pattern library  
**Use When**: Found excellent artifact worth reusing, or noticing repeated patterns

---

## Purpose

This prompt helps maintain a curated collection of:
- **Templars**: Structural templates (format/section scaffolds) to be adapted and filled
- **Exemplars**: Filled content examples showing how to use the structure (and what to avoid)

Use this when you find an artifact with excellent structure or patterns worth reusing across the framework.

## Quick Reference

**Fast Decision Tree**:
```
Is structure reusable across multiple artifacts?
├─ YES → Extract as TEMPLAR
└─ NO → Is implementation exceptionally high-quality?
    ├─ YES → Extract as EXEMPLAR
    └─ NO → Don't extract (keep as regular artifact)

Can it be BOTH? → Extract as both if:
  ✓ Structure is reusable AND
  ✓ Implementation is exceptional
```

**Quick Comparison**:

| Aspect | Templar | Exemplar |
|--------|---------|----------|
| **Focus** | Structure (HOW organized) | Excellence (WHAT good looks like) |
| **Content** | Abstract with placeholders | Concrete implementation |
| **Use Case** | Copy and customize | Reference and learn from |
| **Reusability** | High (multiple domains) | Medium (similar domains) |
| **Maintenance** | Update when pattern evolves | Update when better found |

## Supported Artifact Types

This prompt works with:
- **Rules** (`.cursor/rules/**/*.mdc`)
- **Prompts** (`.cursor/prompts/**/*.prompt.md`)
- **Tickets** (`tickets/**/`)
- **Documentation** (`docs/**/*.md`)
- **Scripts** (`scripts/**/*.{ps1,sh,py}`)

## Expected Output

This prompt will produce:
1. **Analysis report** identifying templar/exemplar candidates
2. **Extracted templar/exemplar files** with proper documentation
3. **Placement recommendations** for where to save them
4. **Usage documentation** explaining how to apply the pattern

## Lean Extraction Rules (keep sources small)
- Move heavy examples and long narratives into the exemplar file; keep only links in the source.
- Move reusable structures into the templar file; keep only the essential sections in the source.
- Source artifact stays concise: purpose, context, process, expected output, and a pointer to the templar/exemplar.
- When in doubt: cut from the source, keep in exemplar, reference both.
- Final intent: source = concise instructions + links; templar = structure; exemplar = filled examples (good/bad, edge cases).
- Trimming is part of extraction: remove inline examples/narratives from the source while you extract them to exemplar; keep only the pointer in the source (DRY).
- Stageable workflow: you may run extraction/trimming in phases and track progress (e.g., tracker.md) so partial work is visible and auditable.
- Automation: reusable extraction/trimming scripts should live under `.cursor/scripts/housekeeping/` and be referenced from this prompt/rules when used.
- Keep inline (do not extract) when:
  - Pattern is one-off/domain-specific and not reusable elsewhere.
  - Removing it would lose essential quick-start context for the source.
  - A small, critical example is needed inline for clarity (leave one compact example).
  - Maintenance cost of a separate templar/exemplar outweighs benefit.

## Cross-References & Automation (for best results)

- **Scripts (place here)**: `.cursor/scripts/housekeeping/` — keep reusable extraction/trimming helpers here (e.g., extract + trim + link updater). Reference them when invoking this prompt so runs stay consistent.
- **Example invocation**:  
  ```powershell
  ./.cursor/scripts/housekeeping/extract-templar-exemplar.ps1 `
    -Source ".cursor/prompts/prompt/improve-prompt.prompt.md" `
    -ExemplarPath ".cursor/prompts/exemplars/prompt/prompt-quality-improvement-exemplar.md"
  ```
- **Templars to use**: store structural patterns in `.cursor/prompts/templars/` (by domain). Link them from the source artifact after extraction.
- **Exemplars to use**: store filled examples in `.cursor/prompts/exemplars/` (by domain). Point source artifacts to these instead of embedding content.
- **Rules to observe**: apply `rule.authoring.templars-and-exemplars.v1`, `rule.authoring.cross-references.v1`, `rule.authoring.provenance-and-versioning.v1`, and prompt quality standards when updating references.
- **Frontmatter references**: when you create templars/exemplars, add frontmatter fields (`illustrates`/`implements`/`use`) and briefly note source/consumers in the body (e.g., “Extracted from [artifact]; referenced by [prompt/rule]”) to keep provenance clear without bloating source artifacts.

## Reasoning Process

Before extracting:
1. **Understand Pattern**: What makes this artifact special or reusable?
2. **Classify Type**: Is this a structural template (templar) or reference example (exemplar)?
3. **Identify Artifact Type**: Rule, prompt, ticket, doc, script?
4. **Identify Reusability**: Can this pattern benefit other artifacts?
5. **Abstract Appropriately**: What should be generalized vs kept specific?

## Templar vs Exemplar

### Side-by-Side Comparison

| Characteristic | Templar (Template) | Exemplar (Example) |
|----------------|-------------------|-------------------|
| **Primary Focus** | Structure (HOW to organize) | Excellence (WHAT good looks like) |
| **Content Type** | Abstract with placeholders | Concrete implementation |
| **Reusability** | Copy and customize | Reference and learn from |
| **Abstraction Level** | High (generic framework) | Low (specific implementation) |
| **Use Case** | Creating new similar artifacts | Improving existing artifacts |
| **Value Proposition** | Saves structural design time | Shows quality standards |
| **Maintenance** | Update when pattern evolves | Update when better found |
| **File Content** | `[PLACEHOLDER]` based | Full working artifact |
| **Applies To** | 3+ different domains | Similar domain/purpose |

### Templars (Templates)
**What They Are**:
- Reusable structural patterns
- Placeholder-based templates
- Abstract, adaptable frameworks
- Focus on STRUCTURE

**When to Extract**:
- ✅ Artifact has a structure useful for multiple domains
- ✅ Pattern can be parameterized with placeholders
- ✅ Framework applies to a category of artifacts
- ✅ Structure enforces quality standards

**Common Templar Patterns Worth Extracting**:
- ✅ **Validation patterns** (input → validate → report)
- ✅ **Workflow patterns** (define stages → enforce transitions)
- ✅ **Checklist patterns** (multi-level validation criteria)
- ✅ **Documentation patterns** (required sections → quality standards)
- ✅ **Naming convention patterns** (pattern → examples → validation)
- ✅ **Integration patterns** (define interface → specify contracts)

### Exemplars (Examples)
**What They Are**:
- Exceptional reference implementations
- High-quality concrete examples
- Best-in-class demonstrations
- Focus on EXCELLENCE

**When to Extract**:
- ✅ Artifact demonstrates exceptional quality
- ✅ Shows best practices in action
- ✅ Can guide others creating similar artifacts
- ✅ Solves a problem particularly well

**Common Exemplar Qualities Worth Preserving**:
- ✅ **Outstanding contract definitions** (inputs, outputs, preconditions, postconditions)
- ✅ **Exceptional validation checklists** (complete, specific, actionable)
- ✅ **Comprehensive examples** (good, bad, edge cases)
- ✅ **Excellent error handling** (anti-patterns, troubleshooting)
- ✅ **Perfect cross-referencing** (related artifacts, templars, exemplars)
- ✅ **Superior clarity** (zero ambiguity, crystal-clear requirements)

## Extraction Process

### Step 1: Analyze Artifact

Read the target artifact and identify:
- **Artifact type** (rule, prompt, ticket, etc.)
- **Structural patterns** worth templating
- **Quality elements** worth exemplifying
- **Reusability potential** for other artifacts
- **Unique approaches** worth preserving

### Step 2: Determine Type

**Choose Templar if**:
- Structure can be reused with different content
- Pattern applies to multiple domains
- Focus is on HOW the artifact is structured

**Choose Exemplar if**:
- Implementation demonstrates exceptional quality
- Serves as reference for similar artifacts
- Focus is on WHAT excellent looks like

**Can Be Both**:
- Some artifacts are both templates and examples
- Extract as both templar and exemplar if applicable

### Step 3: Extract and Document

**Lean rule**: Move bulky examples/narratives out of the source artifact. Put structure/format in the templar, and filled content (good/bad) in the exemplar. Keep the original artifact concise (purpose, context, process, expected output, quality criteria) with links to templar/exemplar.

For **Templars**:

```markdown
---
type: templar
artifact-type: [rule|prompt|ticket|doc|script]
applies-to: [domain or use-case]
pattern-name: descriptive-pattern-name
version: 1.0.0
---

# [Pattern Name] Templar

## Pattern Purpose

[What problem this template solves]

## Artifact Type

**For**: [Rules | Prompts | Tickets | Docs | Scripts | Multiple]

## When to Use

- [Scenario 1]
- [Scenario 2]

## Template Structure

[Provide the reusable structure with placeholders]

### Section 1: [Name]
[PLACEHOLDER_1]: [What to put here]

### Section 2: [Name]
[PLACEHOLDER_2]: [What to put here]

## Customization Points

- **[Placeholder 1]**: [Guidance on what to fill in]
- **[Placeholder 2]**: [Guidance on what to fill in]

## Example Usage

**For [Artifact Type]**:
[Show template filled in for a concrete use case]

## Related Templars

- [Other templates that work with this one]
```

For **Exemplars**:

```markdown
---
type: exemplar
artifact-type: [rule|prompt|ticket|doc|script]
demonstrates: [what pattern/practice it shows]
domain: [artifact domain]
quality-score: [high|exceptional]
version: 1.0.0
---

# [Artifact Name] Exemplar

## Artifact Type

**Type**: [Rule | Prompt | Ticket | Doc | Script]

## Why This is Exemplary

[Explain what makes this artifact exceptional]

## Key Quality Elements

1. **[Element 1]**: [Why it's excellent]
2. **[Element 2]**: [Why it's excellent]
3. **[Element 3]**: [Why it's excellent]

## Pattern Demonstrated

[Describe the pattern/approach this exemplifies]

## Full Exemplar Content

[Complete artifact content preserved as reference]

## Learning Points

- [Key takeaway 1]
- [Key takeaway 2]

## When to Reference

Use this exemplar when:
- [Scenario 1]
- [Scenario 2]

## Related Exemplars

- [Other examples demonstrating similar patterns]
```

### Step 4: Place Appropriately

**Templars** go to:
```
# For rules
.cursor/rules/templars/[domain]/[pattern-name]-templar.mdc

# For prompts
.cursor/prompts/templars/[category]/[pattern-name]-templar.md

# For tickets
tickets/templars/[category]/[pattern-name]-templar.md

# For docs/scripts (create templars/ folder as needed)
docs/templars/[pattern-name]-templar.md
scripts/templars/[pattern-name]-templar.{ps1|sh|py}
```

**Exemplars** go to:
```
# For rules
.cursor/rules/exemplars/[domain]/[artifact-name]-exemplar.mdc

# For prompts
.cursor/prompts/exemplars/[category]/[artifact-name]-exemplar.md

# For tickets
tickets/exemplars/[category]/[artifact-name]-exemplar.md

# For docs/scripts
docs/exemplars/[artifact-name]-exemplar.md
scripts/exemplars/[artifact-name]-exemplar.{ps1|sh|py}
```

### Step 5: Link Back

Update the original artifact to reference the templar/exemplar:

```markdown
## Pattern Used

This [artifact] follows: `[path-to-templar]`

## Reference Example

See exemplar: `[path-to-exemplar]`
```

## Output Format

```markdown
## Extraction Analysis

### Artifact Analyzed
**File**: [path to artifact]
**Type**: [rule|prompt|ticket|doc|script]
**Domain**: [artifact domain]
**Purpose**: [what it does]

### Pattern Identified
**Type**: [Templar | Exemplar | Both]
**Pattern Name**: [descriptive name]
**Reusability**: [High | Medium | Low]
**Applies To**: [domains/categories]

### Why Extract?
[Specific reasons this is worth extracting]

## Extracted Templar

[If applicable, complete templar content]

**Save to**: [appropriate path based on artifact type]

## Extracted Exemplar

[If applicable, complete exemplar content]

**Save to**: [appropriate path based on artifact type]

## Usage Recommendations

### For Templar
When creating [artifact type] for [use case], start with this template and customize:
- [Customization 1]
- [Customization 2]

### For Exemplar
Reference this example when creating [artifact type] that:
- [Scenario 1]
- [Scenario 2]

## Related Patterns

- [Other templars/exemplars in same domain]
- [Complementary patterns]
```

## Examples (Few-Shot)

### Example 1: Extract Validation Templar from Rule

**Input**: Analyze `.cursor/rules/ticket/validation-before-completion-rule.mdc`

**Reasoning**:
- Has clear multi-level validation checklist structure
- Pattern applies to ANY validation scenario (code, docs, tickets, prompts)
- Structure is reusable: Critical → Standard → Quality → Best Practices
- Should be extracted as TEMPLAR

**Output**:
```markdown
## Extraction Analysis

### Artifact Analyzed
**File**: `.cursor/rules/ticket/validation-before-completion-rule.mdc`
**Type**: rule
**Domain**: ticket
**Purpose**: Validates ticket completion requirements

### Pattern Identified
**Type**: Templar
**Pattern Name**: multi-level-validation-checklist-pattern
**Reusability**: High
**Applies To**: tickets, prompts, rules, docs, scripts

### Why Extract?
- Multi-level validation structure applies to many artifact types
- Checklist pattern enforces completeness
- Severity categorization (Critical/Standard/Quality/Best) is universal
- Can validate tickets, code, docs, configs, processes, etc.

## Extracted Templar

[Creates validation-checklist-templar.mdc showing:]
- Level 1: Critical compliance checks
- Level 2: Standard requirements
- Level 3: Quality standards
- Level 4: Best practices
- Severity categorization framework
- Pass/Fail/Pass-with-Issues reporting

**Save to**: `.cursor/rules/templars/validation/multi-level-checklist-templar.mdc`

### Usage Recommendations

**For Rules**: Validation rules for any domain
**For Prompts**: Validation prompts for code/doc quality
**For Tickets**: Completion validation checklists
**For Scripts**: Validation script output formats
```

### Example 2: Extract Exemplar from Prompt

**Input**: Analyze `.cursor/prompts/rule-authoring/extract-prompts-from-conversation.prompt.md`

**Reasoning**:
- Shows excellent Few-Shot examples
- Demonstrates comprehensive Chain-of-Thought reasoning
- Includes specific before/after patterns
- Should be extracted as EXEMPLAR

**Output**:
```markdown
## Extraction Analysis

### Artifact Analyzed
**File**: `.cursor/prompts/rule-authoring/extract-prompts-from-conversation.prompt.md`
**Type**: prompt
**Domain**: rule-authoring
**Purpose**: Extract reusable prompts from conversations

### Pattern Identified
**Type**: Exemplar
**Pattern Name**: comprehensive-extraction-with-cot-and-few-shot
**Quality**: Exceptional
**Applies To**: extraction, analysis, transformation prompts

### Why Extract?
- Exemplary use of Few-Shot learning (multiple examples)
- Shows both success and failure cases
- Excellent Chain-of-Thought reasoning structure
- Clear before/after format with specific instructions

## Extracted Exemplar

[Creates extraction-pattern-exemplar.md showing:]
- Outstanding Few-Shot examples structure
- Chain-of-Thought integration
- Clear input/reasoning/output format
- Comprehensive troubleshooting section

**Save to**: `.cursor/prompts/exemplars/rule-authoring/extraction-pattern-exemplar.md`

### Usage Recommendations

**For Prompts**: Creating extraction/analysis prompts
**For Rules**: Rules requiring analysis workflows
**For Docs**: Documentation about extraction patterns
```

### Example 3: Extract Both from Ticket Structure

**Input**: Analyze `tickets/EPP-192/plan.md` (hypothetical excellent ticket)

**Reasoning**:
- Has reusable ticket structure (templar candidate)
- Implementation shows exceptional documentation (exemplar candidate)
- Both the structure AND execution are valuable
- Should be extracted as BOTH

**Output**:
```markdown
## Extraction Analysis

### Artifact Analyzed
**File**: `tickets/EPP-192/plan.md`
**Type**: ticket
**Domain**: feature development
**Purpose**: Ticket plan documentation

### Pattern Identified
**Type**: Both (Templar + Exemplar)
**Pattern Name**: comprehensive-ticket-plan
**Reusability**: High (structure), Exceptional (implementation)

### Why Extract Both?
- **Templar**: Ticket plan structure applies to all tickets
  - Objectives → Requirements → Approach → Validation
- **Exemplar**: Shows best-in-class ticket documentation
  - Complete requirement tracing
  - Comprehensive validation checklists
  - Excellent cross-referencing

## Extracted Templar

[Creates ticket-plan-templar.md showing:]
- Standard ticket plan structure
- Required sections with placeholders
- Optional sections for different ticket types
- Quality checklist pattern

**Save to**: `tickets/templars/ticket-plan-templar.md`

## Extracted Exemplar

[Creates ticket-plan-exemplar.md showing:]
- Complete ticket preserved as reference
- Highlighting exceptional elements:
  - Clear objective statements
  - Comprehensive requirements
  - Well-structured approach
  - Complete validation criteria

**Save to**: `tickets/exemplars/EPP-192-plan-exemplar.md`

### Usage Recommendations

**Use Templar when**: Creating any new ticket plan
**Use Exemplar when**: Want to see best-in-class ticket documentation
```

## Extraction Criteria

### High-Value Templars
Extract when artifact has:
- [ ] Reusable structural pattern
- [ ] Clear placeholder positions
- [ ] Applies to 3+ different domains/artifact types
- [ ] Enforces quality standards
- [ ] Novel or particularly effective structure

### High-Value Exemplars
Extract when artifact has:
- [ ] Exceptional quality across dimensions
- [ ] Demonstrates best practices clearly
- [ ] Solves a problem particularly well
- [ ] Can guide others effectively
- [ ] Represents best-in-class implementation

### Don't Extract If
- ❌ Pattern is too specific to one domain/artifact type
- ❌ Quality is average (not exemplary)
- ❌ Structure is common/obvious
- ❌ Would duplicate existing templars/exemplars
- ❌ Not worth the maintenance overhead

## Batch Extraction

**Analyze folder for patterns**:
```
@extract-templar-exemplar .cursor/rules/category/ --scan
@extract-templar-exemplar .cursor/prompts/category/ --scan
@extract-templar-exemplar tickets/TICKET-ID/ --scan
```

**Extract from specific artifact**:
```
@extract-templar-exemplar .cursor/rules/category/specific-rule.mdc
@extract-templar-exemplar .cursor/prompts/category/prompt.prompt.md
@extract-templar-exemplar tickets/TICKET-ID/plan.md
```

**Extract as specific type**:
```
@extract-templar-exemplar artifact.ext --type templar
@extract-templar-exemplar artifact.ext --type exemplar
@extract-templar-exemplar artifact.ext --type both
```

## Troubleshooting

### Issue: Unsure if Pattern is Reusable Enough

**Symptom**: Artifact seems well-structured but not sure if it's worth extracting

**Solution**:
1. List 3 concrete domains where pattern would be useful
2. If you struggle to list 3 different domains, it's probably too specific
3. Check if existing templars already cover this pattern
4. When in doubt, wait - extract after you find yourself copying it

**Example**:
- ❌ "This ticket validation checks plan.md" - Too specific to tickets
- ✅ "Multi-file validation pattern" - Applies to tickets, agile, docs, etc.

### Issue: Pattern is Both Templar and Exemplar

**Symptom**: Artifact has great structure AND exceptional implementation

**Solution**:
- Extract as BOTH (see Example 3 in Few-Shot section)
- Templar focuses on structure (abstract with placeholders)
- Exemplar preserves full implementation (concrete reference)
- Cross-reference them in documentation

### Issue: Extracted Pattern Already Exists

**Symptom**: After extracting, realize similar templar/exemplar already exists

**Solution**:
1. Compare with existing pattern - which is better?
2. If new one is better: Replace old, update references
3. If old one is better: Discard new extraction
4. If both valuable: Keep both, document differences and use cases
5. Update index/README to clarify when to use each

### Issue: Templar Too Abstract/Complex

**Symptom**: Extracted templar has too many placeholders or configuration points

**Solution**:
- Simplify by identifying the core 3-5 customization points
- Provide "Basic" and "Advanced" templar versions
- Add concrete example usage showing template applied
- Consider if pattern is actually 2-3 simpler patterns combined

**Example**:
- ❌ 15 placeholders, complex decision tree, 10 optional sections
- ✅ 5 key placeholders, clear customization points, 3 optional sections, example provided

### Issue: Exemplar Becomes Outdated

**Symptom**: Extracted exemplar no longer represents best practices

**Solution**:
1. Check if original artifact has been improved since extraction
2. Update exemplar with latest best practices
3. Increment version number in frontmatter
4. Add changelog note explaining updates
5. If significantly different, consider creating v2 as alternative

### Issue: No One Uses Extracted Pattern

**Symptom**: Pattern sits unused after extraction

**Solution**:
1. Verify pattern is discoverable (README, index files updated?)
2. Check if pattern solves real problems (survey team)
3. Add more usage examples showing value
4. Present pattern in team meeting/documentation
5. If still unused after 3 months, consider archiving

## Anti-Patterns

### What NOT to Extract

#### Anti-Pattern 1: Domain-Specific Structure

**Bad Extraction**:
```markdown
# Ticket-Plan-Validation Templar

## Template Structure
1. Check if plan.md has [TICKET_ID] in filename
2. Validate plan.md sections (specific to tickets only)
3. Check progress.md links to plan.md
```

**Why Bad**: Too specific to ticket domain, not reusable for other artifact types

**Better Approach**: Extract "Multi-File Validation Templar" with `[PRIMARY_FILE]` and `[RELATED_FILES]` placeholders

#### Anti-Pattern 2: Average Quality Exemplar

**Bad Extraction**:
```markdown
# Basic-Artifact Exemplar

This artifact works fine and follows the framework requirements.
```

**Why Bad**: "Works fine" ≠ "Exemplary". Exemplars must be exceptional, not just adequate

**Better Approach**: Only extract as exemplar if it demonstrates best-in-class quality

#### Anti-Pattern 3: Overly Abstract Templar

**Bad Extraction**:
```markdown
# Universal-Artifact Templar

1. [DEFINE_PURPOSE]
2. [SET_SCOPE]
3. [WRITE_CONTENT]
4. [ADD_EXAMPLES]
```

**Why Bad**: So abstract it provides no guidance. Not useful as template

**Better Approach**: Templars should have clear structure with meaningful placeholders

#### Anti-Pattern 4: Duplicate Existing Pattern

**Bad Extraction**:
```markdown
# Validation-Pattern-V2 Templar

[Same structure as existing validation-pattern-templar.mdc]
```

**Why Bad**: Creates confusion, maintenance overhead, duplication

**Better Approach**: Check existing templars first. Update existing or document differences

#### Anti-Pattern 5: Mixing Templar and Exemplar

**Bad Extraction**:
```markdown
# Mixed-Pattern Templar

Uses placeholders [HERE] but also shows concrete implementation there.
```

**Why Bad**: Unclear whether to copy structure or implementation

**Better Approach**: Keep templars abstract, exemplars concrete. Extract as both if needed

### Red Flags Checklist

**Don't extract if**:
- [ ] Can't list 3 different domains/artifact types where applicable
- [ ] Pattern is obvious/common sense
- [ ] Quality is average (not exceptional)
- [ ] Very similar pattern already exists
- [ ] Too complex to reuse (15+ customization points)
- [ ] Specific to one project/domain/artifact type
- [ ] Would rarely be referenced

## Quality Checklist

Before finalizing extraction:

### For Templars
- [ ] Pattern is truly reusable (3+ use cases identified)
- [ ] Placeholders clearly marked and documented
- [ ] Customization points explained
- [ ] Example usage showing application provided
- [ ] Related templars cross-referenced
- [ ] Artifact type(s) specified
- [ ] Required vs optional sections specified

### For Exemplars
- [ ] Excellence clearly articulated (why exemplary?)
- [ ] Learning points extracted
- [ ] Demonstrates specific best practices
- [ ] Context provided for when to reference
- [ ] Related exemplars cross-referenced
- [ ] Full artifact content preserved
- [ ] Quality elements highlighted

### For Both
- [ ] Proper frontmatter with type/version/artifact-type
- [ ] Clear documentation
- [ ] Saved in correct location
- [ ] Original artifact links back (if updated)
- [ ] No duplication of existing patterns

---

## Related Prompts

- `rule-authoring/create-new-rule.prompt.md` - Use templars when creating new rules
- `prompt/create-new-prompt.prompt.md` - Use templars when creating new prompts
- `housekeeping/sync-improvements.prompt.md` - Sync extracted patterns between repos
- `housekeeping/consolidate-duplicates.prompt.md` - May identify patterns worth extracting

## Related Rules

- `.cursor/rules/rule-authoring/rule-templars-and-exemplars.mdc` - Templar/exemplar concepts
- `.cursor/rules/rule-authoring/rule-file-structure.mdc` - Structure standards
- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt quality standards

## Usage

**Basic extraction**:
```
@extract-templar-exemplar .cursor/rules/ticket/plan-rule.mdc
@extract-templar-exemplar .cursor/prompts/script/add-caching.prompt.md
@extract-templar-exemplar tickets/EPP-192/plan.md
```

**Scan folder for patterns**:
```
@extract-templar-exemplar .cursor/rules/ticket/ --scan
@extract-templar-exemplar .cursor/prompts/housekeeping/ --scan
```

**Extract specific type**:
```
@extract-templar-exemplar my-artifact --templar
@extract-templar-exemplar my-artifact --exemplar
@extract-templar-exemplar my-artifact --both
```

## Maintenance Guidelines

### When to Update Templars
- Pattern proves useful and gets refined through use
- New best practices emerge
- Feedback shows customization points need clarification
- Version changes (increment version number)
- Framework standards evolve

### When to Update Exemplars
- Better examples are found (replace or add as alternative)
- Standards evolve (update to reflect current best practices)
- Original artifact improves significantly (update exemplar)
- Learning points become clearer through use
- New quality dimensions identified

### When to Archive
- Pattern no longer used (archive with reason)
- Better alternative exists (migrate references)
- Standard practices change (document obsolescence)
- Framework changes make pattern invalid

## Best Practices

### DO
- ✅ Extract patterns that benefit multiple artifact types
- ✅ Document WHY the pattern is valuable
- ✅ Provide clear usage guidance
- ✅ Cross-reference related patterns
- ✅ Keep templars abstract, exemplars concrete
- ✅ Update originals to reference extracted patterns
- ✅ Specify artifact types clearly
- ✅ Include cross-artifact examples

### DON'T
- ❌ Extract every artifact (be selective for quality)
- ❌ Create overly complex templars
- ❌ Make exemplars too abstract (keep concrete)
- ❌ Duplicate existing patterns
- ❌ Extract without clear use cases
- ❌ Forget to document context
- ❌ Ignore artifact type specificity

## Success Metrics

Good extraction achieves:
- **Reuse**: Pattern/example gets referenced by other artifacts
- **Clarity**: Others understand and apply the pattern
- **Quality**: Artifacts using it improve measurably
- **Efficiency**: Reduces time to create quality artifacts
- **Learning**: Team understands best practices better
- **Consistency**: Artifacts across types follow patterns

---

**Note**: This prompt itself demonstrates comprehensive documentation patterns - it could serve as an exemplar for housekeeping prompt documentation! 🎯

---

**Created**: 2025-12-06  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Improved**: 2025-12-08 (PROMPTS-OPTIMIZE ticket)
