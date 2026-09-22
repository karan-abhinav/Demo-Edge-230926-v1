# edge-ai-toolkit

Everything built in Modules 1-3, packaged so a second repository gets the same
setup with one install.

## What is inside

| Component | Path | Loads as |
|---|---|---|
| Reviewer subagent | `agents/telemetry-reviewer.md` | `edge-ai-toolkit:telemetry-reviewer` |
| Test runner subagent | `agents/test-runner.md` | `edge-ai-toolkit:test-runner` |
| Security scanner subagent | `agents/security-scanner.md` | `edge-ai-toolkit:security-scanner` |
| Lab report skill | `skills/lab-report/SKILL.md` | `/edge-ai-toolkit:lab-report` |
| Pipeline audit skill | `skills/pipeline-audit/SKILL.md` | `/edge-ai-toolkit:pipeline-audit` |
| Format-on-edit hook | `hooks/hooks.json` -> `scripts/format_python.py` | PostToolUse |
| Write guard hook | `hooks/hooks.json` -> `scripts/protect_paths.py` | PreToolUse |
| Telemetry MCP server | `.mcp.json` | `mcp__plugin_edge-ai-toolkit_telemetry__*` |

## Install

```bash
# from the repository that contains solutions/marketplace
/plugin marketplace add ./solutions/marketplace
/plugin install edge-ai-toolkit@edge-ai-training
/reload-plugins
```

## Develop

```bash
claude --plugin-dir ./solutions/marketplace/plugins/edge-ai-toolkit
claude plugin validate ./solutions/marketplace/plugins/edge-ai-toolkit
```

`/reload-plugins` picks up edits without restarting the session.

## Path placeholders

- `${CLAUDE_PLUGIN_ROOT}` — this plugin's install directory. Changes on every
  plugin update, so never hard-code a path to it.
- `${CLAUDE_PROJECT_DIR}` — the project the session started in. The MCP server
  lives in the project, not the plugin, so `.mcp.json` uses this one.
- `${CLAUDE_PLUGIN_DATA}` — persistent per-plugin data that survives updates.

## Two things that bite

1. Only `plugin.json` goes inside `.claude-plugin/`. `agents/`, `skills/`,
   `hooks/` and `.mcp.json` all sit at the plugin root.
2. Plugin subagents ignore `hooks`, `mcpServers` and `permissionMode`. If an
   agent needs one of those, keep it in `.claude/agents/` instead of packaging it.
