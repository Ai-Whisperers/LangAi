# MCP setup for Cursor (optional)

Cursor can load MCP server definitions from a project-local file named:

- `\.cursor/mcp.json`

This repository does not commit `mcp.json` by default because MCP server URLs are often organization-specific and may include credentials.

## How to enable MCP for this repo

1. Copy the template:
   - From: `.cursor/mcp.template.json`
   - To: `.cursor/mcp.json`

2. Edit `.cursor/mcp.json` and replace the example server with your real MCP server(s).

3. Restart Cursor.

## Notes

- Keep `mcp.json` **free of secrets**. If your MCP provider requires tokens, prefer environment-variable based configuration or a local-only file that is git-ignored.
- If you also use Claude Code, compare with `.claude/mcp/*.json` to reuse the same server endpoints where appropriate.
