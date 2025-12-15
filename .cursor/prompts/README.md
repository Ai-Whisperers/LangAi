---
id: prompt.library.readme.v1
kind: documentation
version: 1.0.0
description: Documentation for Cursor Prompts Library
provenance:
  owner: team-prompts
  last_review: 2025-12-06
---

# Cursor Prompts Library

This folder contains ready-to-use, advanced prompts organized by rule category. Simply drag these prompts into your conversation with Cursor to execute common tasks efficiently.

## Structure

The prompt library is organized to mirror the `.cursor/rules/` structure, and to support Prompt Registry (`/` slash command) workflows:

- **`collections/`** - Prompt Registry collections (`*.collection.yml`)
- **`prompts/`** - Prompt files (`*.prompt.md`) organized by category:
  - **`prompts/agile/`** - Agile artifacts
  - **`prompts/code-quality/`** - Code review/refactoring/quality
  - **`prompts/database-standards/`** - SQL and database workflows
  - **`prompts/documentation/`** - Documentation workflows
  - **`prompts/git/`** - Git operations and release workflows
  - **`prompts/migration/`** - Migration workflows
  - **`prompts/rule-authoring/`** - Rule authoring workflows
  - **`prompts/technical/`** - Technical docs workflows
  - **`prompts/technical-specifications/`** - Technical specifications workflows
  - **`prompts/ticket/`** - Ticket management workflows
  - **`prompts/unit-testing/`** - Test generation and coverage workflows

## Usage

You have two good ways to run prompts:

1. **Slash command (`/`)**: Install collections via Prompt Registry, then run prompts from Cursor chat (fastest).
2. **Drag/Copy**: Drag a `*.prompt.md` file into Cursor chat (works even without Prompt Registry).

## Prompt Naming Convention

Prompts follow this pattern:
- `check-*.prompt.md` - Analysis and validation prompts
- `create-*.prompt.md` - Generation prompts
- `validate-*.prompt.md` - Compliance and verification prompts
- `refactor-*.prompt.md` - Improvement and restructuring prompts
- `generate-*.prompt.md` - Documentation and artifact generation

## Best Practices

- Review and customize prompts before use if needed
- Prompts are designed to work with the corresponding rule sets
- Some prompts may require file/folder paths - update them before use
- Advanced prompts include context gathering and validation steps

## Contributing

When creating new prompts:
1. Place them in the appropriate category folder
2. Use clear, descriptive filenames
3. Include all necessary context and instructions
4. Follow the prompt structure pattern in existing files

