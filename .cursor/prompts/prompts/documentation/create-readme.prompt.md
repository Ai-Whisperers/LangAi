---
name: create-readme
description: "Generate a new README.md that follows the README structure rule"
agent: cursor-agent
model: GPT-4
tools:
  - search/codebase
  - fileSystem
argument-hint: "Target folder path for the new README (e.g., ./ or ./src/Module)"
category: documentation
tags: documentation, readme, onboarding, quality, generation
rules:
  - .cursor/rules/readme-structure-rule.mdc
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Create README

Please generate a complete `README.md` that complies with `.cursor/rules/readme-structure-rule.mdc` for the target project or module.

**Pattern**: Documentation Creation Pattern ⭐⭐⭐⭐
**Effectiveness**: Fast, compliant README generation
**Use When**: A project or module is missing a README or needs a full rewrite to match the README structure rule.

---

## Purpose

Create a complete `README.md` that complies with `.cursor/rules/readme-structure-rule.mdc` for the target project or module.

### Objectives

- Deliver a ready-to-commit README that meets required sections and formatting
- Provide copy-pasteable commands and links for setup and usage
- Keep content minimal yet sufficient for onboarding and contribution

---

## Required Context

- **Target folder path**: Relative to repository root (e.g., `./`, `./src/Module`)
- **Project/module name and purpose**: What the project/module does
- **Primary audience**: Users, contributors, operators, or all
- **Installation/Setup steps**: Commands, prerequisites, dependencies
- **Usage examples**: Common workflows, commands, API hints
- **Contribution expectations**: Branching, PR process, code style
- **Optional: badges/links**: Build status, coverage, license, docs
- **Optional: constraints**: Air-gapped environments, OS targets, offline restore

### Optional Parameters
- **Template**: `dotnet-library`, `dotnet-api`, `nodejs-module`, `python-package`, `react-component`
- **Audience emphasis**: users | contributors | operators
- **Badges**: list of CI/coverage/license badge URLs or leave out
- **Links**: docs, changelog, architecture, contributing, API reference

---

## Process

1. **Assess scope**
   - Confirm target folder and intended audience
   - Identify any existing docs to link (CHANGELOG, docs/, API docs)

2. **Plan structure** (per README rule)
   - Required sections: Title (H1), Description, Installation/Setup, Usage, Contribution
   - Optional sections: Requirements/Prereqs, Support/Contact, Links (docs, changelog), License/Badges

3. **Draft content**
   - Summarize purpose and key capabilities
   - Provide minimal, copy-pasteable setup/usage commands
   - State contribution expectations (branch naming, tests, style)

4. **Validate**
   - Ensure all required sections from `readme-structure-rule.mdc` are present and populated
   - Check OPSEC: no secrets, internal hosts, or credentials
   - Confirm markdown formatting (H1 for title, H2 for sections)
   - Verify links/badges point to valid targets

5. **Deliver**
   - Provide the full `README.md` content ready to save at the target path

---

## Reasoning Process (for AI Agent)

Before generating the README, you must:
1. **Understand the module's audience and scope** to keep content focused and appropriate
2. **Map inputs to required sections** from the README structure rule
3. **Prefer concise commands and concrete examples** over verbose prose
4. **Avoid assumptions** - leave placeholders only when unavoidable
5. **Re-check OPSEC and formatting** before presenting the final README

---

## Examples (Few-Shot)

### Example 1: Small .NET Library README

**Input Context**:
- Target: `./src/Acme.Logging`
- Audience: Contributors and users
- Setup: `dotnet add package Acme.Logging`
- Purpose: Lightweight logging helpers for .NET applications

**Expected Output**:
```markdown
# Acme.Logging

Lightweight logging helpers for .NET applications with structured logging and configurable sinks.

## Installation/Setup

```bash
dotnet add package Acme.Logging
```

Optional: Configure log level in `appsettings.json`:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

## Usage

```csharp
using Acme.Logging;

var logger = LoggerFactory.Create(builder =>
{
    builder.AddAcmeLogging();
});

logger.LogInformation("Application started");
logger.LogError("Database connection failed: {Error}", ex.Message);
```

### Example 2: Full Project README

**Input Context**:
- Target: `./`
- Audience: All (users, contributors, operators)
- Setup: Multi-step installation with prerequisites
- Purpose: Web API for order management

**Expected Output**:
```markdown
# Order Management API

RESTful web API for managing customer orders, inventory, and fulfillment workflows.

## Requirements

- .NET 8.0 or later
- SQL Server 2019 or later
- Docker (for local development)

## Installation/Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/acme/order-api.git
   cd order-api
   ```

2. **Install dependencies**
   ```bash
   dotnet restore
   ```

3. **Configure database**
   ```bash
   # Update connection string in appsettings.json
   dotnet ef database update
   ```

4. **Run the application**
   ```bash
   dotnet run
   ```

## Usage

### Start the API
```bash
dotnet run --project src/OrderApi/OrderApi.csproj
```

### Create an order
```bash
curl -X POST https://localhost:5001/api/orders \
  -H "Content-Type: application/json" \
  -d '{"customerId": 123, "items": [{"productId": 456, "quantity": 2}]}'
```

### View API documentation
Navigate to `https://localhost:5001/swagger` for interactive API docs.

## Contribution

### Development Setup
1. Follow installation steps above
2. Run tests: `dotnet test`
3. Format code: `dotnet format`

### Branch Naming
Use pattern: `feature/EPP-123-description` or `fix/EPP-456-issue-name`

### Pull Requests
- Ensure all tests pass
- Update documentation if APIs change
- Add migration scripts for database changes

## Links

- [API Documentation](docs/api/)
- [Architecture Overview](docs/architecture.md)
- [Contributing Guide](CONTRIBUTING.md)
```

### Example 3: Node.js Module README

**Input Context**:
- Target: `./packages/utils`
- Audience: Contributors (internal package)
- Setup: `npm install @company/utils`
- Purpose: Shared utility functions for frontend applications

**Expected Output**:
```markdown
# @company/utils

Shared utility functions for frontend applications including validation, formatting, and HTTP helpers.

## Installation/Setup

```bash
npm install @company/utils
```

## Usage

```javascript
import { validateEmail, formatCurrency } from '@company/utils';

const isValid = validateEmail('user@company.com');
const price = formatCurrency(29.99, 'USD'); // "$29.99"
```

## Contribution

- Branch naming: `feature/EPP-123-description`
- Test changes: `npm test`
- Format code: `npm run format`
```

### Example 4: Python Package README

**Input Context**:
- Target: `./src/mypackage`
- Audience: Data scientists and ML engineers
- Setup: `pip install mypackage`
- Purpose: Machine learning utilities for data preprocessing

**Expected Output**:
```markdown
# MyPackage

Machine learning utilities for data preprocessing, feature engineering, and model evaluation.

## Installation/Setup

```bash
pip install mypackage
```

For development:
```bash
git clone https://github.com/company/mypackage.git
cd mypackage
pip install -e .
```

## Usage

```python
from mypackage.preprocessing import clean_data, encode_features
from mypackage.evaluation import calculate_metrics

# Clean and preprocess data
df_clean = clean_data(df, remove_outliers=True)
X_encoded = encode_features(df_clean, categorical_cols=['category'])

# Evaluate model
metrics = calculate_metrics(y_true, y_pred)
print(f"Accuracy: {metrics['accuracy']:.2f}")
```

## Contribution

### Setup Development Environment
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
```

### Branch Naming
- Features: `feature/EPP-123-add-new-preprocessing-method`
- Fixes: `fix/EPP-456-handle-edge-case-in-encoding`

### Code Quality
- All tests must pass: `pytest --cov=mypackage --cov-fail-under=90`
- Code formatted with black: `black . && isort .`
- Type hints required for new functions
```

---

## Output Format

A single markdown file containing:

**Required Sections**:
- `# {Project/Module Title}` - H1 heading with clear title
- Description paragraph(s) - What it does, key capabilities
- `## Installation/Setup` - Concrete, copy-pasteable steps
- `## Usage` - Examples and common workflows
- `## Contribution` - Expectations for contributors

**Optional Sections** (when relevant):
- `## Requirements` - Prerequisites and dependencies
- `## Support` - Contact info, issue tracking
- `## Links` - Documentation, changelog, related projects
- `## License` - License information and badges

---

## Validation Checklist

Before delivering the README:
- [ ] All required sections from `readme-structure-rule.mdc` are present
- [ ] Commands are copy-pasteable and accurate for the target environment
- [ ] No secrets, internal hosts, or credentials included (OPSEC compliant)
- [ ] Heading levels: H1 for title, H2 for main sections, H3 for subsections
- [ ] Links and badges point to valid, accessible targets
- [ ] Content is appropriate for the specified audience
- [ ] Examples are concrete and realistic for the project type
- [ ] Project/module name clearly reflects its purpose
- [ ] Installation steps work in the specified environment
- [ ] Usage examples are functional and complete
- [ ] Contribution guidelines match project workflow

---

## Troubleshooting

### Common Issues

**Issue**: "README not generating required sections"
**Cause**: Missing context information or incomplete rule compliance
**Solution**:
1. Verify all required context is provided
2. Check that `readme-structure-rule.mdc` is accessible
3. Provide more specific audience/setup information

**Issue**: "Commands not working in target environment"
**Cause**: Platform-specific commands or missing prerequisites
**Solution**:
1. Specify target OS/platform in context
2. Include prerequisite installation steps
3. Test commands in the actual environment

**Issue**: "Links/badges not displaying correctly"
**Cause**: Invalid URLs or missing CI/CD setup
**Solution**:
1. Verify all URLs are accessible and correct
2. Remove badges for services not yet configured
3. Use relative links for internal documentation

**Issue**: "Content too verbose or too sparse"
**Cause**: Incorrect audience assessment or unclear purpose
**Solution**:
1. Re-evaluate primary audience (users vs contributors vs operators)
2. Clarify the project/module's core purpose
3. Adjust content depth based on audience needs

### Quality Gates

**Before committing the README**:
1. **Technical accuracy**: All commands work as written
2. **Completeness**: All required sections populated
3. **Security**: No sensitive information exposed
4. **Accessibility**: Works in specified environment/constraints
5. **Consistency**: Follows project conventions and standards

---

## Usage Modes

### Quick Mode (5 minutes)
For simple projects with standard setup:
```
@create-readme ./

Context:
- Audience: All
- Setup: npm install (or dotnet restore, pip install)
- Purpose: [Brief description]
```

### Detailed Mode (15-30 minutes)
For complex projects with custom workflows:
```
@create-readme ./src/MyModule

Context:
- Audience: [users/contributors/operators]
- Setup: [Detailed installation steps]
- Purpose: [Comprehensive description]
- Prerequisites: [List requirements]
- Examples: [Specific usage examples]
- Branch pattern: [Naming convention]
```

### Template Mode
For projects following specific patterns:
```
@create-readme ./packages/my-package --template dotnet-library

Templates available:
- dotnet-library: .NET class libraries
- dotnet-api: ASP.NET Core Web APIs
- nodejs-module: Node.js packages
- python-package: Python packages
- react-component: React component libraries
```

### Template Library (Cheat Sheet)
- **dotnet-library**: Requires `dotnet add package` example, optional `appsettings.json` snippet
- **dotnet-api**: Needs `dotnet ef database update`, Swagger link, run command with project path
- **nodejs-module**: Uses `npm install` and sample import block
- **python-package**: Includes `pip install` plus editable install for contributors
- **react-component**: Show `npm install` and JSX usage snippet

---

## Usage

**Basic usage**:
```
@create-readme ./
```

**Module-specific README**:
```
@create-readme ./src/MyModule
```

**With inline context**:
```
@create-readme ./src/MyModule

Context:
- Audience: Contributors only
- Setup: dotnet add package MyModule
- Purpose: Data validation utilities
- Branch pattern: feature/EPP-123-description
```

**Advanced usage with templates**:
```
@create-readme ./packages/utils --template nodejs-module --audience contributors
```

---

## Related Prompts

- `documentation/update-readme.prompt.md` - Refresh an existing README with new features/changes
- `documentation/validate-documentation-quality.prompt.md` - Verify documentation quality and completeness
- `prompt/improve-prompt.prompt.md` - Fix issues in existing prompts before enhancing
- `prompt/enhance-prompt.prompt.md` - Add advanced features after fixing basic issues
- `git/create-branch.prompt.md` - Create feature branches for documentation updates

---

## Related Rules

- `.cursor/rules/readme-structure-rule.mdc` - Required README structure and sections
- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry integration standards
- `.cursor/rules/general-coding-rules.mdc` - General quality standards
- `.cursor/rules/code-writing-standards.mdc` - Language-specific standards
