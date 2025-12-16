---
name: update-readme
description: "Please audit and improve an existing README.md to meet the README structure rule"
category: documentation
tags: documentation, readme, audit, structure, quality, improvement
argument-hint: "Path to the existing README.md (e.g., ./README.md or ./src/Module/README.md)"
templar: .cursor/prompts/templars/documentation/readme-update-templar.md
exemplar: .cursor/prompts/exemplars/documentation/readme-update-exemplar.md
rules:
  - .cursor/rules/readme-structure-rule.mdc
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Update README

Please audit and improve an existing README.md to meet the README structure rule.

**Pattern**: README Enhancement Pattern ⭐⭐⭐⭐⭐
**Effectiveness**: Essential for maintaining project documentation quality
**Use When**: README lacks required sections, has outdated content, or doesn't follow standards

---

## Purpose

Refine an existing `README.md` so it fully complies with `.cursor/rules/readme-structure-rule.mdc`, fills gaps without losing useful context, and stays copy-pasteable for contributors.

This prompt transforms incomplete or outdated READMEs into professional, standards-compliant documentation that helps contributors understand and use the project effectively.

## Required Context
- Path to the current README
- Project/module name, audience, and ownership
- Known gaps or pain points (e.g., unclear install, missing usage, no contribution guidance)
- Accurate setup commands, prerequisites, and usage examples
- Contribution expectations (branching, tests, style, required checks)
- Optional: badge/link sources (build, coverage, docs, license)

## Reasoning Process (for AI Agent)

Before updating the README, you should:

1. **Understand Audience & Scope**: Who will read this README? What do they need to know?
2. **Analyze Current State**: Map existing sections against the README structure rule, identify gaps and outdated content
3. **Preserve Value**: Keep accurate, useful content while improving clarity and structure
4. **Plan Improvements**: Decide what sections to add, update, or restructure based on project needs
5. **Validate Quality**: Ensure commands are copy-pasteable, links resolve, and no sensitive information is exposed
6. **Test Readability**: Verify the updated README flows logically and answers key contributor questions

---

## What to Analyze

Review the README against these quality standards:

### Required Sections (Must Have)
- **Title**: H1 with project/module name
- **Description**: Concise overview paragraph
- **Installation/Setup**: Prerequisites and setup commands
- **Usage**: Concrete examples and commands
- **Contribution**: Branch naming, testing, style requirements

### Optional but Recommended
- Requirements/Prereqs (if complex)
- Support/Contact information
- Links (docs, changelog, CI/CD)
- License/Badges
- Architecture overview
- Troubleshooting

### Quality Checks
- Commands are accurate and copy-pasteable
- No secrets, internal hosts, or credentials
- Links resolve to valid targets
- Formatting follows markdown standards
- Examples work with current codebase

## Process
1) **Assess current README**
   - Identify missing or weak required sections: Title, Description, Installation/Setup, Usage, Contribution.
   - Note outdated or redundant content to prune.
2) **Gather facts**
   - Confirm accurate setup commands, prerequisites, and usage flows.
   - Capture contribution expectations (PR checks, branch naming, coding standards).
3) **Plan updates**
   - Decide required additions: Usage examples, Contribution steps, Support/Contact, Links, License/Badges.
   - Keep commands actionable and copy-pasteable.
4) **Revise content**
   - Preserve good content; rewrite unclear parts.
   - Add missing required sections and optional helpful sections.
5) **Validate against the rule**
   - Check section completeness and heading levels (H1 for title, H2 for sections).
   - Run OPSEC scan: no secrets, internal hosts, credentials.
   - Ensure links/badges resolve to valid targets.
6) **Deliver**
   - Provide the updated README content ready to replace the original file.

## Output Format
- Full `README.md` content containing:
  - H1 Title and concise description paragraph
  - `## Installation/Setup` with prerequisites and commands
  - `## Usage` with concrete examples/commands
  - `## Contribution` with branch/test/style expectations
  - Optional: Requirements/Prereqs, Support/Contact, Links (docs/changelog), License/Badges

## Usage Modes

### Basic Mode
For standard README updates:
```
@update-readme ./README.md
```

### Advanced Mode
With specific guidance and context:
```
@update-readme ./README.md

Provide additional context:
- Audience: New contributors joining the team
- Focus areas: Setup instructions and contribution guidelines
- Known gaps: Missing usage examples and contact information
- Required badges: Build status, code coverage, license
```

### Batch Mode
For multiple READMEs in a project:
```
# Update all READMEs in project
foreach ($readme in Get-ChildItem -Recurse -Filter "README.md") {
    @update-readme $readme.FullName
}
```

---

## Examples

### Example 1: Basic Module README Enhancement

**Input**:
```
@update-readme ./src/Billing/README.md
```

**Context Provided**:
- Audience: Backend developers integrating billing features
- Focus: Setup and API usage
- Current gaps: Missing contribution guidelines

**Expected Output (excerpt)**:
```markdown
# Billing Module

Provides comprehensive billing APIs for invoice generation, payment processing, and subscription management.

## Installation/Setup

### Prerequisites
- .NET 8 SDK or later
- SQL Server 2019+ with billing database
- Valid connection string with read/write permissions

### Setup Steps
1. **Restore dependencies**:
   ```bash
   dotnet restore
   ```

2. **Configure database connection**:
   ```bash
   # Windows
   setx Billing__ConnectionString "Server=localhost;Database=BillingDB;Trusted_Connection=True;"

   # Linux/macOS
   export Billing__ConnectionString="Server=localhost;Database=BillingDB;User Id=sa;Password=YourPassword123!"
   ```

3. **Run database migrations**:
   ```bash
   dotnet ef database update --project src/Billing.Data
   ```

## Usage

### Basic Invoice Creation
```csharp
var invoiceService = new InvoiceService();
var invoice = await invoiceService.CreateInvoiceAsync(new InvoiceRequest {
    CustomerId = "CUST-001",
    Amount = 99.99m,
    Description = "Monthly subscription"
});
```

### API Endpoints
- `POST /api/invoices` - Create new invoice
- `GET /api/invoices/{id}` - Retrieve invoice details
- `PUT /api/invoices/{id}/pay` - Process payment

## Contribution

### Development Workflow
1. **Branch naming**: `feature/EPP-123-billing-enhancement`
2. **Code style**: Follow existing patterns in codebase
3. **Testing**: Add unit tests for new features

### Quality Checks
```bash
# Format code
dotnet format

# Run tests
dotnet test --collect:"XPlat Code Coverage"

# Build solution
dotnet build --configuration Release
```
```

### Example 2: Legacy Code Documentation Overhaul

**Input**:
```
@update-readme ./legacy/ImportProcessor/README.md

Additional context:
- Audience: Migration team modernizing legacy system
- Current state: Outdated batch file commands, missing architecture info
- Pain points: Unclear data flow, no troubleshooting guide
- Required: Architecture diagram links, error handling examples
```

**Key Improvements Made**:
- Updated obsolete batch commands to PowerShell equivalents
- Added architecture section with data flow diagram
- Included troubleshooting section for common import failures
- Added performance considerations and monitoring guidance

### Example 3: Open Source Library README

**Input**:
```
@update-readme ./README.md

Context:
- Audience: External developers using the library
- Focus: Quick start and integration examples
- Add: Installation via NuGet, usage examples, contribution guidelines
- Include badges: NuGet version, build status, license
```

**Enhancements**:
- Added badge section with dynamic links
- Included multiple installation methods (NuGet, source)
- Added comprehensive usage examples with before/after code
- Included contribution section with PR template references

---

## Troubleshooting

### Common Issues

**Issue**: Commands fail with "command not found"
**Cause**: Missing prerequisites or PATH configuration
**Solution**:
1. Verify .NET SDK installation: `dotnet --version`
2. Check PATH includes .NET tools
3. Reinstall .NET SDK if needed

**Issue**: Database connection fails
**Cause**: Invalid connection string or database permissions
**Solution**:
1. Validate connection string format
2. Test database connectivity: `sqlcmd -S server -d database`
3. Check firewall and authentication settings

**Issue**: Build succeeds but README looks wrong
**Cause**: Markdown rendering differences or encoding issues
**Solution**:
1. Preview in GitHub's markdown renderer
2. Check for special characters or encoding issues
3. Use consistent heading levels (H1 → H2 → H3)

### Validation Failures

**Issue**: "Missing required sections" error
**Solution**: Compare against `.cursor/rules/readme-structure-rule.mdc` and add missing sections

**Issue**: "Commands not copy-pasteable" warning
**Solution**: Test all commands in a clean environment and fix any that fail

**Issue**: "Links don't resolve" error
**Solution**: Update URLs to current valid endpoints or remove broken links

## Quality Criteria

Enhanced READMEs should meet these standards:

- [ ] **Structure**: Follows README structure rule with all required sections
- [ ] **Accuracy**: All commands tested and working in current environment
- [ ] **Security**: No secrets, internal hosts, or sensitive credentials exposed
- [ ] **Usability**: Commands are copy-pasteable with minimal modification
- [ ] **Completeness**: Covers setup, usage, and contribution for target audience
- [ ] **Clarity**: Language appropriate for audience (technical vs business)
- [ ] **Links**: All badges and links resolve to valid targets
- [ ] **Formatting**: Consistent markdown formatting and heading hierarchy
- [ ] **Flow**: Logical progression from overview to deep usage
- [ ] **Maintenance**: Easy to keep updated as project evolves

---

## Enhancement Features

### Interactive Elements
- **Argument Hints**: Clear guidance for required inputs
- **Context Gathering**: Adapts based on audience and project type
- **Validation Feedback**: Real-time checks during generation
- **Multiple Output Formats**: Standard markdown or with additional features

### Advanced Capabilities
- **Audience Adaptation**: Tailors content for different reader types
- **Project Type Recognition**: Different structures for libraries vs applications
- **Integration Detection**: Includes relevant CI/CD, testing, and deployment info
- **Badge Generation**: Automatic creation of status and version badges

### Decision Support
- **Gap Analysis**: Identifies missing information automatically
- **Priority Ordering**: Suggests most important improvements first
- **Compatibility Checking**: Ensures suggestions work with existing setup

---

## Success Metrics

**Good Enhancement**: README now serves its audience effectively
- Contributors can set up and use the project without asking questions
- External users understand the project's value and capabilities
- Maintenance burden reduced through better documentation
- Project appears more professional and trustworthy

**Quality Indicators**:
- Time to onboard new contributors reduced by 50%+
- Support questions about setup/usage decreased
- Positive feedback on documentation clarity
- README remains current with project changes

---

## Related Prompts

- `documentation/create-readme.prompt.md` - Create READMEs from scratch
- `documentation/validate-documentation-quality.prompt.md` - Check documentation quality
- `documentation/check-folder-documentation.prompt.md` - Audit folder-level docs
- `documentation/generate-missing-docs.prompt.md` - Generate missing documentation

---

## Related Rules

- `.cursor/rules/readme-structure-rule.mdc` - README structure requirements
- `.cursor/rules/documentation/documentation-standards-rule.mdc` - Documentation quality standards

---

**Created**: 2025-12-06
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Updated**: 2025-12-13 (via improve-prompt enhancement)
