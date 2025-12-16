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

| Folder | Purpose |
|---|---|
| `collections/` | Prompt Registry collections (`*.collection.yml`) |
| `prompts/` | Prompt files (`*.prompt.md`) organized by category |
| `prompts/agile/` | Agile artifacts |
| `prompts/code-quality/` | Code review/refactoring/quality |
| `prompts/database-standards/` | SQL and database workflows |
| `prompts/documentation/` | Documentation workflows |
| `prompts/git/` | Git operations and release workflows |
| `prompts/migration/` | Migration workflows |
| `prompts/rule-authoring/` | Rule authoring workflows |
| `prompts/technical/` | Technical docs workflows |
| `prompts/technical-specifications/` | Technical specifications workflows |
| `prompts/ticket/` | Ticket management workflows |
| `prompts/unit-testing/` | Test generation and coverage workflows |

## Usage

You have two good ways to run prompts:

| Method | How | Notes |
|---|---|---|
| Slash command (`/`) | Install collections via Prompt Registry, then run prompts from Cursor chat | Fastest UX |
| Drag/Copy | Drag a `*.prompt.md` file into Cursor chat | Works without Prompt Registry |

## Recommended collections to install

Start with the curated core bundle, then add domain bundles as needed:

| Collection | Path | Notes |
|---|---|---|
| Core Workflows | `.cursor/prompts/collections/core.collection.yml` | Small, curated default |
| Ticket Workflows | `.cursor/prompts/collections/ticket.collection.yml` | Ticket + tracker workflows |
| Code Quality | `.cursor/prompts/collections/code-quality.collection.yml` | Review/refactor/debug workflows |
| Git Workflow | `.cursor/prompts/collections/git.collection.yml` | Branch/commit/release workflows |

## Prompt Naming Convention

Prompts follow this pattern:

| Pattern | Meaning |
|---|---|
| `check-*.prompt.md` | Analysis and validation prompts |
| `create-*.prompt.md` | Generation prompts |
| `validate-*.prompt.md` | Compliance and verification prompts |
| `refactor-*.prompt.md` | Improvement and restructuring prompts |
| `generate-*.prompt.md` | Documentation and artifact generation |

## Best Practices

Treat prompts like scripts: review them, fill placeholders, and keep them up to date.

| Practice | Why |
|---|---|
| Review and customize prompts before use | Prompts are templates; make intent and scope explicit |
| Keep prompts aligned with rules | Prompts are designed to match the corresponding rule sets |
| Fill path placeholders carefully | Many prompts take file/folder paths and globs |
| Prefer small, composable prompts | Easier iteration and better reproducibility |

## Contributing

When creating new prompts:

| Step | Action |
|---|---|
| 1 | Place prompts in the appropriate category folder |
| 2 | Use clear, descriptive filenames |
| 3 | Include all necessary context and instructions |
| 4 | Follow the prompt structure pattern in existing files |
