# Claude Code: Extending the Agent
## Subagents, MCP, Hooks and Plugins — topic list

One day, six sessions, roughly 6h30 of contact time. Every session is
30–40% talk and 60–70% keyboard. Prerequisite: participants can already run a
Claude Code session, edit `CLAUDE.md`, and use plan mode.

---

## Module 0 — The extension layer (30 min, no lab)

| # | Topic |
|---|---|
| 0.1 | Where each extension plugs into the agentic loop |
| 0.2 | The five primitives: CLAUDE.md, skills, subagents, hooks, MCP — and plugins as the packaging layer |
| 0.3 | Context-cost model: what loads at session start, what loads on use, what costs nothing |
| 0.4 | Choosing between them: the trigger table (a rule missed twice → CLAUDE.md; a prompt retyped → skill; noisy side task → subagent; must-happen-every-time → hook; data Claude can't see → MCP; a second repo needs it → plugin) |
| 0.5 | Tour of the sandbox repository and the day's finish line |

---

## Module 1 — Subagents (100 min, Labs A1–A3)

### 1A. Built-in subagents
| # | Topic |
|---|---|
| 1.1 | Why isolation: the context-window economics of a noisy side task |
| 1.2 | `Explore` — read-only search; inherits the session model, capped at Opus on the Claude API; thoroughness levels |
| 1.3 | `Plan` — research during plan mode; read-only |
| 1.4 | `general-purpose` — exploration plus modification |
| 1.5 | The helper agents: `claude`, `statusline-setup`, `claude-code-guide` |
| 1.6 | What Explore and Plan skip: CLAUDE.md and git status — and what that implies for your rules |
| 1.7 | Turning built-ins off: `permissions.deny`, `Agent(Explore)`, `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS` |

### 1B. Custom subagents
| # | Topic |
|---|---|
| 1.8 | Anatomy: YAML frontmatter + Markdown body as the system prompt |
| 1.9 | Scope and precedence: managed › `--agents` CLI › `.claude/agents/` › `~/.claude/agents/` › plugin |
| 1.10 | Required fields (`name`, `description`) and how `description` drives automatic delegation |
| 1.11 | Capability control: `tools` allowlist, `disallowedTools` denylist, MCP server patterns |
| 1.12 | `model` (`sonnet`/`opus`/`haiku`/`fable`/`inherit`) and the resolution order |
| 1.13 | `permissionMode`, `maxTurns`, `effort`, `color`, `isolation: worktree` |
| 1.14 | `skills:` preloading vs on-demand skill discovery |
| 1.15 | `mcpServers:` — scoping a server to one subagent so the main context never pays for it |
| 1.16 | `hooks:` in frontmatter for conditional rules the `tools` field can't express |
| 1.17 | `memory:` — persistent per-agent knowledge at user, project or local scope |
| 1.18 | Files Claude Code silently skips, and `claude plugin validate` on an agents directory |

### 1C. Working with subagents
| # | Topic |
|---|---|
| 1.19 | Three ways to invoke: natural language, `@`-mention, `claude --agent` for a whole session |
| 1.20 | Foreground vs background; the reduced background tool set |
| 1.21 | Nesting depth, the concurrent limit, and resuming a finished subagent |
| 1.22 | Forks (`/subtask`): inherit the whole conversation, keep the output out of it |
| 1.23 | Patterns: isolate high-volume output, parallel research, chained specialists |
| 1.24 | Subagent output scanning, and why a subagent report is untrusted input |
| 1.25 | The 15,000-token description budget |

**Labs:** A1 read-only reviewer · A2 chained test-runner + docs-writer · A3 `db-reader` with a frontmatter guard hook

---

## Module 2 — MCP (80 min, Labs B1–B3)

| # | Topic |
|---|---|
| 2.1 | What MCP is for: tools and data access, not knowledge — MCP vs skill |
| 2.2 | Transports: `stdio`, `http`, `ws`, and why `sse` is deprecated |
| 2.3 | Scopes and precedence: local (`~/.claude.json`) › project (`.mcp.json`) › user |
| 2.4 | `claude mcp add`, `add-json`, `list`, `remove`; the `--` separator for stdio args |
| 2.5 | `.mcp.json` as configuration-as-code: commit it, teammates get the approval prompt |
| 2.6 | `/mcp` for connection status, `/context all` for token cost per tool |
| 2.7 | Tool naming `mcp__<server>__<tool>`; plugin-scoped `mcp__plugin_<plugin>_<server>__<tool>` |
| 2.8 | Permissions and allowlists: pre-approving a server, `requiresUserInteraction` |
| 2.9 | Context cost: tool names at startup, schemas deferred, tool search on by default |
| 2.10 | Secrets: environment interpolation, why tokens never go in a committed file |
| 2.11 | Building a server: FastMCP, tool signatures, and why the docstring *is* the interface |
| 2.12 | Read-only by construction: SQLite `mode=ro`, parameter allowlists, bounded limits |
| 2.13 | Scoping a server to a subagent instead of the whole session |
| 2.14 | Enterprise controls: `--strict-mcp-config`, managed MCP, allow/deny lists |

**Labs:** B1 add and commit a project-scope server · B2 build `telemetry_mcp.py` · B3 scope it to one subagent

---

## Module 3 — Hooks (85 min, Labs C1–C4)

| # | Topic |
|---|---|
| 3.1 | The core distinction: a prompt instruction is a request, a hook is a guarantee |
| 3.2 | Hook vs skill vs CLAUDE.md — determinism, context cost, and where each belongs |
| 3.3 | The lifecycle: session, turn, and per-tool-call cadences |
| 3.4 | Event catalogue — the ones you will actually use: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `SubagentStart`/`Stop`, `Stop`, `PreCompact`, `SessionEnd`, `Notification` |
| 3.5 | Three levels of nesting: event → matcher group → handler |
| 3.6 | Matcher semantics: exact string vs unanchored JavaScript regex, and the hyphen trap |
| 3.7 | Matching MCP tools: `mcp__server__.*` and why the bare prefix never fires |
| 3.8 | The `if` field: permission-rule syntax to filter before spawning a process |
| 3.9 | Five handler types: `command`, `http`, `mcp_tool`, `prompt`, `agent` |
| 3.10 | Exec form vs shell form; when you need `args` |
| 3.11 | Input JSON on stdin: common fields, `agent_id`/`agent_type` inside subagents |
| 3.12 | Exit codes: 0 = no decision, 2 = block, anything else = non-blocking error |
| 3.13 | Per-event blocking table — which events can actually stop something |
| 3.14 | JSON output: `permissionDecision`, `decision`/`reason`, `continue`, `systemMessage` |
| 3.15 | `additionalContext`: feeding state back to Claude, and phrasing it so it isn't read as injection |
| 3.16 | `terminalSequence` for notifications, because hooks have no controlling terminal |
| 3.17 | Hook locations and merge behaviour; skill and subagent frontmatter hooks |
| 3.18 | Workspace trust: what runs before you trust a folder |
| 3.19 | Operations: `/hooks`, `disableAllHooks`, `async`, timeouts, `--debug` |
| 3.20 | Loop safety: `stop_hook_active`, and why a mistyped path fails open |

**Labs:** C1 format-on-edit · C2 write guard over fixture data · C3 SessionStart context injection · C4 Stop gate on a red suite

---

## Module 4 — Plugins (80 min, Labs D1–D2)

| # | Topic |
|---|---|
| 4.1 | Standalone `.claude/` vs a plugin: the trigger is a second repository |
| 4.2 | Manifest: `.claude-plugin/plugin.json`, and version management |
| 4.3 | Directory contract: `skills/`, `agents/`, `hooks/`, `.mcp.json`, `.lsp.json`, `monitors/`, `bin/`, `settings.json` — all at the **plugin root**, never inside `.claude-plugin/` |
| 4.4 | Namespacing: `/plugin-name:skill` and `@agent-plugin-name:agent` |
| 4.5 | Path placeholders: `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}` |
| 4.6 | What plugins silently drop: `hooks`, `mcpServers`, `permissionMode` on plugin subagents |
| 4.7 | Precedence: project and user agents override same-named plugin agents; hooks merge |
| 4.8 | Dev loop: `--plugin-dir`, `--plugin-url`, `/reload-plugins`, `claude plugin validate` |
| 4.9 | `claude plugin init` and skills-directory plugins |
| 4.10 | Marketplaces: `.claude-plugin/marketplace.json`, `/plugin marketplace add`, `/plugin install` |
| 4.11 | Team distribution: `extraKnownMarketplaces`, private repositories, `CLAUDE_CODE_PLUGIN_SEED_DIR` for CI images |
| 4.12 | Migration: converting an existing `.claude/` setup into a plugin |
| 4.13 | Governance: `allowManagedHooksOnly`, `enabledPlugins`, the official and community marketplaces |

**Labs:** D1 package Modules 1–3 as `edge-ai-toolkit` · D2 marketplace, install, verify

---

## Module 5 — Capstone and wrap-up (45 min)

| # | Topic |
|---|---|
| 5.1 | Capstone: wire all four layers into one guarded workflow on the sandbox repo |
| 5.2 | Debugging the extension layer: `/context`, `/hooks`, `/mcp`, `/plugin` Errors tab, `claude --debug` |
| 5.3 | Failure modes seen today, and how each announced itself |
| 5.4 | Decision cheat sheet and a 30-day adoption path |

---

## Deliberately out of scope

Named here so participants know these exist and why the day does not cover
them: agent teams, dynamic workflows, cross-session messaging, background
agents, the Agent SDK, output styles, LSP/code-intelligence plugins,
Claude Code on the web. Each is a natural follow-on session.
