# Cursor in this repo: what’s configured + how to use it

This repo uses Cursor’s project configuration features to make agent work **repeatable**, **safe**, and **fast**.

## What Cursor reads from the repo

- **Project rules**: `.cursor/rules/**/*.mdc`
- **High-level project overlay**: `.cursorrules`
- **Prompt library** (Prompt Registry-compatible):
  - Prompts: `.cursor/prompts/prompts/**/*.prompt.md`
  - Collections: `.cursor/prompts/collections/*.collection.yml`
- **Ignore controls**:
  - `.cursorignore` (block AI access + indexing)
  - `.cursorindexingignore` (block indexing only)
- **Cursor CLI/Agent permissions (optional)**: `.cursor/cli.json`
- **MCP (optional)**: create local `.cursor/mcp.json` (see `.cursor/MCP_SETUP.md`)

## Recommended setup (once per machine)

### 1) Enable prompt files in chat

In Cursor settings, enable **Copilot prompt files** (setting key often shown as `chat.promptFiles`).

### 2) Install Prompt Registry (optional, but best UX)

Install the “Prompt Registry” extension and add a **local source** pointing to:

- `./.cursor/prompts`

Then install one or more collections from `.cursor/prompts/collections/`.

### 3) Keep indexing fast

This repo ships:

- `.cursorindexingignore` to keep huge folders like `outputs/` out of search results
- `.cursorignore` to block secrets like `.env` from AI access

## Day-to-day workflows

### Use a prompt (fastest path)

1. In Cursor chat, type `/`
2. Pick a prompt (auto-complete)
3. Provide arguments if the prompt expects them

If you don’t use Prompt Registry, you can still open a prompt file and copy/paste or drag it into chat.

### Add a new prompt

1. Create a new `*.prompt.md` under `.cursor/prompts/prompts/<category>/`
2. Add it to a collection in `.cursor/prompts/collections/*.collection.yml`
3. Validate references:

```text
python .cursor/scripts/validate-prompt-collections.py
```

### Validate the whole Cursor setup (recommended before sharing changes)

Run the single entrypoint:

```text
python .cursor/scripts/validate-cursor-config.py
```

It validates:
- YAML under `.cursor/`
- Prompt Registry collections (`.collection.yml` → referenced prompt files exist)
- Rule index (`.cursor/rules/rule-index.yml` → referenced files exist)

### Add a new rule

1. Prefer adding a focused rule under `.cursor/rules/<domain>/`
2. If it’s a “router/meta-rule”, make it an **agent-application** rule (semantic trigger, no file writes)
3. If it’s file-specific behavior, use **globs/governs** (file-mask triggering)

This repo adds a Python entrypoint rule at:
- `.cursor/rules/python/agent-application-rule.mdc`

## Optional: MCP

MCP server config is typically org-specific.

1. Copy `.cursor/mcp.template.json` → `.cursor/mcp.json`
2. Edit server URLs
3. Restart Cursor

Details: `.cursor/MCP_SETUP.md`.

## Common improvements teams make (and why)

- **Ignore hygiene**: keep generated outputs out of indexing to prevent noisy search results.
- **Prompt collections**: group prompts by workflow so `/` autocomplete stays useful.
- **Rule granularity**: split “mega rules” into smaller, file-scoped rules (better triggering, less drift).
- **Validation scripts**: add small validators (like prompt collection checks) to prevent broken references.
- **Safety controls**: restrict dangerous shell operations via CLI permissions and Cursor settings.
