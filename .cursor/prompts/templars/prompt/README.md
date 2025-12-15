# Prompt Templars Index

This directory contains **templar** files - abstract, reusable patterns extracted from high-quality prompts. Templars define structure and customization points for creating new prompts that follow proven patterns.

## What is a Templar?

A **templar** is a structural template that:
- Defines reusable patterns with placeholders
- Shows customization points for adaptation
- Applies across multiple similar use cases
- Focuses on STRUCTURE over specific content
- Includes guidance on when to use the pattern

**Templar vs Exemplar**: Templars are abstract templates; exemplars are concrete examples demonstrating excellence.

## Available Templars

### 1. Guided Creation Workflow Templar

**File**: `guided-creation-workflow-templar.md`  
**Extracted From**: `create-new-prompt.prompt.md`  
**Pattern**: Multi-step guided workflow with decision trees

**Applies To**:
- Setup/initialization tasks
- Artifact creation workflows
- Wizard-style processes
- Onboarding flows
- Configuration tasks

**Key Features**:
- 6-step structure (Define → Choose → Name → Configure → Write → Validate)
- Decision trees at choice points
- Good/bad example pairs
- Complete templates
- Progressive disclosure (basic → enhanced)

**Use When**:
- Task has 4+ distinct steps
- Users need guidance at each step
- Decisions required at multiple points
- Output quality depends on following structure

**Example Applications**:
- Setup development environment
- Create deployment configuration
- Initialize new project
- Configure CI/CD pipeline

---

### 2. Multi-Level Validation Templar

**File**: `multi-level-validation-templar.md`  
**Extracted From**: `validate-prompt.prompt.md`  
**Pattern**: Weighted validation with severity levels and scoring

**Applies To**:
- Code validation (linting, quality checks)
- Document validation (format, completeness)
- Configuration validation (settings, deployments)
- Data validation (schema, business rules)
- Artifact validation (builds, packages)

**Key Features**:
- 4-level validation (Critical 40% / Important 20% / Quality 30% / Best Practice 10%)
- Severity categorization (ERROR / WARNING / INFO)
- Pass/fail thresholds (≥90% = PASS, 70-89% = WARNING, <70% = FAIL)
- Actionable feedback with fix instructions
- Weighted quality scoring

**Use When**:
- Multiple validation criteria exist
- Different severity levels needed
- Objective pass/fail determination required
- Users need prioritized fix guidance
- Quality scoring helps track improvements

**Example Applications**:
- Validate API responses
- Check code quality before commit
- Verify configuration files
- Audit documentation completeness

---

### 3. Enhancement Workflow Templar

**File**: `enhancement-workflow-templar.md`  
**Extracted From**: `enhance-prompt.prompt.md`  
**Pattern**: Categorized enhancement with decision trees and time-scoping

**Applies To**:
- Code refactoring
- Document improvement
- Configuration optimization
- Process enhancement
- Feature enrichment

**Key Features**:
- 4 enhancement categories (Structure / Content / Features / Documentation)
- Decision tree for gap analysis
- Time-based scoping (Quick 5-10min / Medium 15-30min / Deep 30+min)
- Before/after comparison with impact assessment
- Preservation of working functionality

**Use When**:
- Artifact exists and works
- Multiple improvement dimensions possible
- Need to prioritize which improvements to make
- Different enhancement levels needed
- Before/after comparison helps communicate value

**Example Applications**:
- Refactor legacy code
- Enhance documentation quality
- Improve test coverage
- Optimize configuration files

---

### 4. Categorization Workflow Templar

**File**: `categorization-workflow-templar.md`  
**Extracted From**: `organize-prompts.prompt.md`  
**Pattern**: Inventory → Categorize → Move → Validate workflow

**Applies To**:
- File organization
- Code restructuring
- Documentation categorization
- Artifact cleanup
- Migration/reorganization tasks

**Key Features**:
- 4-phase workflow (Inventory → Categorize → Move → Validate)
- Comprehensive decision tree for categorization
- Batch operation support
- Metadata update patterns
- Organization report generation

**Use When**:
- Multiple artifacts need categorization
- Clear category system exists (or needs definition)
- Decision criteria can be articulated
- Batch operations more efficient
- Validation confirms proper organization

**Example Applications**:
- Organize test files by type
- Categorize documentation by audience
- Restructure code into modules
- Clean staging/temp directories

---

## Choosing the Right Templar

### By Task Type

| Task Type | Recommended Templar |
|---|---|
| Creating new artifacts | Guided Creation Workflow |
| Checking quality/compliance | Multi-Level Validation |
| Improving existing artifacts | Enhancement Workflow |
| Organizing/categorizing items | Categorization Workflow |

### By Characteristics

**Use Guided Creation when**:
- Multi-step process with decisions
- Users need guidance at each phase
- Quality depends on following structure

**Use Multi-Level Validation when**:
- Need objective pass/fail decisions
- Multiple severity levels exist
- Prioritized feedback required

**Use Enhancement Workflow when**:
- Artifact works but could be better
- Multiple improvement dimensions
- Need to scope by time available

**Use Categorization Workflow when**:
- Many items need organization
- Clear categorization criteria exist
- Batch operations beneficial

## How to Use Templars

### Step 1: Select Appropriate Templar
Choose based on task type and characteristics above.

### Step 2: Read Customization Points
Each templar lists placeholders and guidance for adaptation.

### Step 3: Replace Placeholders
Substitute domain-specific content:
- `[Artifact Type]` → your artifact (code, document, config, etc.)
- `[Enhancement Category N]` → your categories (structure, tests, docs, etc.)
- `[Question N]` → your decision criteria

### Step 4: Adapt Examples
Update Few-Shot examples with domain-specific scenarios.

### Step 5: Test and Iterate
Create prompt from templar, test with real scenarios, refine.

## Combining Templars

Templars can be composed for complex workflows:

**Creation + Validation**:
- Use Guided Creation for artifact creation
- Use Multi-Level Validation as Step 6 (validation phase)

**Enhancement + Validation**:
- Use Multi-Level Validation to identify gaps
- Use Enhancement Workflow to address identified issues

**Organization + Validation**:
- Use Categorization Workflow to move artifacts
- Use Multi-Level Validation to confirm quality after moves

## Contributing New Templars

To add a new templar:

1. **Identify pattern** in existing high-quality prompts
2. **Extract structure** (not specific content)
3. **Define customization points** with clear guidance
4. **Document applicability** (when to use, example applications)
5. **Add to this index** with description

See `extract-templar-exemplar.prompt.md` for extraction guidance.

## Related Directories

- **`.cursor/prompts/exemplars/prompt/`** - Concrete examples of excellence
- **`.cursor/prompts/prompt/`** - Actual prompts (sources for templars)
- **`.cursor/rules/rule-authoring/`** - Rules for creating rules/prompts

## Metadata

**Last Updated**: 2025-12-08  
**Templar Count**: 4  
**Extraction Source**: `.cursor/prompts/prompt/` folder analysis  
**Related Prompt**: `extract-templar-exemplar.prompt.md`

