# Documentation Validation Checklist

Checklist for validating all documentation for accuracy, completeness, and quality.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## Documentation Files to Validate

### Phase 1: Critical Documentation

- [ ] [README.md](../README.md)
- [ ] [INSTALLATION.md](../INSTALLATION.md)
- [ ] [QUICK_START.md](../QUICK_START.md)
- [ ] [docs/company-researcher/README.md](company-researcher/README.md)
- [ ] [docs/README.md](README.md)

### Phase 2: Technical Documentation

- [ ] [ARCHITECTURE.md](company-researcher/ARCHITECTURE.md)
- [ ] [IMPLEMENTATION.md](company-researcher/IMPLEMENTATION.md)
- [ ] [AGENT_DEVELOPMENT.md](company-researcher/AGENT_DEVELOPMENT.md)
- [ ] [API_REFERENCE.md](company-researcher/API_REFERENCE.md)

### Phase 3: Validation & Quality

- [ ] [TROUBLESHOOTING.md](company-researcher/TROUBLESHOOTING.md)
- [ ] [FAQ.md](company-researcher/FAQ.md)
- [ ] [PHASE_EVOLUTION.md](company-researcher/PHASE_EVOLUTION.md)

---

## Validation Criteria

### 1. Accuracy ✓

**Check**: Are all facts and code examples correct?

**For each document**:
- [ ] Technical details match actual code
- [ ] File paths are correct
- [ ] Function signatures match implementation
- [ ] Performance metrics are accurate
- [ ] No outdated information

**How to verify**:
```bash
# Check file paths
ls -la <path-mentioned-in-docs>

# Verify code snippets
python -c "<code-from-docs>"

# Test commands
<command-from-docs>
```

### 2. Completeness ✓

**Check**: Does documentation cover all necessary topics?

**For each document**:
- [ ] All stated objectives covered
- [ ] No TODO placeholders
- [ ] Examples provided where needed
- [ ] All sections filled out
- [ ] Cross-references complete

**Missing content indicators**:
- "TODO"
- "Coming soon" (without timeline)
- "[TBD]"
- Empty sections
- Broken internal links

### 3. Consistency ✓

**Check**: Are facts consistent across documents?

**Cross-document checks**:
- [ ] Same version numbers
- [ ] Same performance metrics
- [ ] Same file structure descriptions
- [ ] Same terminology
- [ ] Same examples (where applicable)

**Common inconsistencies**:
- Different quality scores
- Different cost figures
- Different directory structures
- Different agent names

### 4. Link Verification ✓

**Check**: Do all links work?

**Types of links**:
- [ ] Internal doc links (relative paths)
- [ ] Code file references
- [ ] External URLs
- [ ] Image references (if any)

**How to verify**:
```bash
# Check internal file links
for file in $(grep -r "\[.*\](.*.md)" docs/ | cut -d: -f2 | grep -o "(.*md)" | tr -d '()'); do
  test -f "docs/$file" && echo "✓ $file" || echo "✗ MISSING: $file"
done

# Check external URLs (manual)
# Visit each URL mentioned
```

### 5. Code Examples ✓

**Check**: Do code examples work?

**For each code example**:
- [ ] Syntax is correct
- [ ] Imports are valid
- [ ] Examples are runnable
- [ ] Output matches description
- [ ] No hardcoded secrets

**How to verify**:
```bash
# Extract and test code examples
# Run each example in isolation
python test_example.py
```

### 6. Formatting ✓

**Check**: Is markdown properly formatted?

**Markdown checks**:
- [ ] Headers hierarchical (#, ##, ###)
- [ ] Code blocks have language specified
- [ ] Lists formatted correctly
- [ ] Tables render properly
- [ ] No excessive line length (>120 chars)

**How to verify**:
```bash
# Use markdown linter
npm install -g markdownlint-cli
markdownlint docs/**/*.md
```

### 7. User Perspective ✓

**Check**: Can users follow the documentation?

**Usability checks**:
- [ ] Instructions are clear
- [ ] Steps are in logical order
- [ ] Prerequisites stated upfront
- [ ] Common errors addressed
- [ ] Examples are relevant

**Test**: Have someone unfamiliar follow the docs

### 8. Versioning ✓

**Check**: Is version info accurate?

**Version checks**:
- [ ] "Last Updated" dates current
- [ ] Version numbers match (0.4.0)
- [ ] Phase numbers correct (Phase 4)
- [ ] Deprecated info removed or marked

---

## Validation Process

### Step 1: Initial Review

**Read through each document**:
1. Check table of contents matches sections
2. Verify all links clickable
3. Look for obvious errors
4. Note any questions

### Step 2: Technical Verification

**Verify technical accuracy**:
1. Compare code examples with actual code
2. Test commands and scripts
3. Verify file paths exist
4. Check function signatures
5. Validate performance metrics

### Step 3: Cross-Document Review

**Check consistency**:
1. Compare version numbers
2. Verify metrics match
3. Check terminology
4. Verify file structures
5. Check cross-references

### Step 4: User Testing

**Test from user perspective**:
1. Follow QUICK_START.md steps
2. Try troubleshooting solutions
3. Test API examples
4. Verify installation works

### Step 5: Final Review

**Polish and finalize**:
1. Fix all identified issues
2. Update "Last Updated" dates
3. Spell check
4. Format check
5. Final read-through

---

## Per-Document Checklists

### README.md

- [ ] System status accurate (Phase 4 Complete)
- [ ] Performance metrics current
- [ ] Quick start commands work
- [ ] Architecture diagram accurate
- [ ] All links work
- [ ] Phase progression correct

### INSTALLATION.md

- [ ] Prerequisites list complete
- [ ] Installation steps tested
- [ ] Commands work on Windows
- [ ] Commands work on Mac/Linux
- [ ] .env.example references correct (env.example)
- [ ] Directory structure matches reality
- [ ] Troubleshooting covers common issues

### QUICK_START.md

- [ ] Can complete in 5 minutes
- [ ] Commands work as written
- [ ] Example output realistic
- [ ] Scenarios cover common cases
- [ ] Quality score explanations accurate

### ARCHITECTURE.md

- [ ] Phase evolution accurate
- [ ] Workflow diagrams correct
- [ ] State definitions match code
- [ ] Reducer explanations accurate
- [ ] Agent descriptions current
- [ ] Performance metrics correct

### IMPLEMENTATION.md

- [ ] Code structure matches actual files
- [ ] Function examples work
- [ ] Agent patterns accurate
- [ ] State update examples correct
- [ ] Cost tracking explanations accurate

### AGENT_DEVELOPMENT.md

- [ ] Agent template works
- [ ] Example agent (News) complete
- [ ] Integration steps accurate
- [ ] Testing approach valid
- [ ] Best practices applicable

### API_REFERENCE.md

- [ ] Function signatures match code
- [ ] Type definitions accurate
- [ ] Return values correct
- [ ] Examples runnable
- [ ] All public APIs documented

### TROUBLESHOOTING.md

- [ ] Common errors listed
- [ ] Solutions actually work
- [ ] Windows-specific issues covered
- [ ] Error messages accurate
- [ ] Links to resources valid

### FAQ.md

- [ ] Questions represent actual FAQs
- [ ] Answers accurate
- [ ] Code examples work
- [ ] Metrics current
- [ ] Comparisons fair

### PHASE_EVOLUTION.md

- [ ] Phase descriptions accurate
- [ ] Timelines realistic (retrospective)
- [ ] Learnings valuable
- [ ] Metrics progression correct
- [ ] Future phases align with master plan

---

## Issue Tracking

### Found Issues

Use this template to track issues:

```markdown
**Document**: <filename>
**Section**: <section name>
**Issue**: <description>
**Severity**: High/Medium/Low
**Fix**: <how to fix>
**Status**: Open/Fixed
```

### Example

**Document**: INSTALLATION.md
**Section**: Directory Structure
**Issue**: Mentions `workflow.py` but actual file is `parallel_agent_research.py`
**Severity**: Medium
**Fix**: Update directory tree to show actual workflow files
**Status**: Fixed ✓

---

## Validation Report

After completing validation, create [VALIDATION_REPORT.md](VALIDATION_REPORT.md) with:

1. **Summary**: Overall status
2. **Issues Found**: List of all issues
3. **Issues Fixed**: What was corrected
4. **Remaining Issues**: What's outstanding
5. **Recommendations**: Improvements for next phase
6. **Sign-Off**: Validation complete

---

## Tools

### Markdown Linter

```bash
npm install -g markdownlint-cli
markdownlint docs/**/*.md
```

### Link Checker

```bash
npm install -g markdown-link-check
find docs -name "*.md" -exec markdown-link-check {} \;
```

### Spell Checker

```bash
npm install -g cspell
cspell "docs/**/*.md"
```

---

## Sign-Off Criteria

Documentation is validated when:

- [ ] All checklist items completed
- [ ] All critical issues fixed
- [ ] All high/medium issues addressed or documented
- [ ] Cross-references verified
- [ ] User testing successful
- [ ] Validation report created
- [ ] Sign-off obtained

---

**Last Updated**: December 5, 2025
**Validation Status**: IN PROGRESS
