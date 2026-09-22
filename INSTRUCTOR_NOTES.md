# Instructor notes

## Shape of the day

| Block | Minutes | Content |
|---|---|---|
| Setup and Module 0 | 40 | Environment check, extension-layer map |
| Module 1 — Subagents | 100 | Talk 35, Labs A1–A3 65 |
| Break | 15 | |
| Module 2 — MCP | 80 | Talk 30, Labs B1–B3 50 |
| Lunch | 45 | |
| Module 3 — Hooks | 85 | Talk 30, Labs C1–C4 55 |
| Break | 15 | |
| Module 4 — Plugins | 80 | Talk 30, Labs D1–D2 50 |
| Capstone and wrap-up | 45 | |

Total contact time 6h25 plus 75 minutes of breaks.

**If you are running short**, cut in this order: Lab B3, then Lab A3's stretch,
then Lab C3. Do not cut C2 or D1 — they carry the two ideas most likely to
change what people do on Monday.

## Planted defects

| Where | What | Which lab finds it |
|---|---|---|
| `src/edge_telemetry/ingest.py:18` | bare `except` swallowing coercion errors, turning bad input into `0.0` | A1 reviewer, C1 formatter |
| `src/edge_telemetry/ingest.py:4` | unused `import os` — auto-fixable, so C1's hook removes it live | C1 |
| `src/edge_telemetry/config.py` | hard-coded `FLEET_API_TOKEN` | A1, security-scanner |
| `src/edge_telemetry/features.py` | `rolling_mean` slice start is `i - window + 2`; each window holds `window - 1` samples | A2 |
| `src/edge_telemetry/anomaly.py` | no test file at all | A2, capstone |

None of these break the test suite. That is the point: the baseline is green,
so every lab starts from a clean checkpoint and any red suite is the room's own
doing.

Reset between cohorts: `git checkout . && git clean -fd && python scripts/seed_db.py`

## Demos worth doing live

1. **`/context` before and after a subagent.** Run a deliberately noisy task in
   the main conversation first — "read every file in src and summarise it" —
   then the same task through Explore. Show the two context bars side by side.
   This lands the whole Module 1 argument in ninety seconds.

2. **The description experiment (A1).** Two identical agents, one described as
   `Reviews code.` and one properly. Ask the same ambiguous question. People
   argue about prompt engineering all day; watching routing fail is faster.

3. **The docstring experiment (B2).** Same idea one layer down. Replace
   `anomaly_summary`'s docstring with `Summary.` and watch Claude do the
   arithmetic by hand instead.

4. **The failing-open hook (C2 step 5).** Mistype a hook path and show the edit
   going through anyway. Everyone assumes a broken guard fails closed. It does
   not, and the notice is easy to miss.

5. **The plugin gotcha (D1 step 7).** Move `db-reader` into a plugin, then ask
   it to DELETE. Its guarantee is gone and nothing announced it. Best single
   moment of Module 4.

## Failure modes, in the order you will meet them

| Symptom | Cause | Fix |
|---|---|---|
| New subagent not found | `.claude/agents/` did not exist when the session started | Restart Claude Code |
| Agent file silently ignored | No `name`, no `description`, frontmatter not on line 1, or a `:` in `name` | `claude --debug`, or `claude plugin validate .claude/agents` |
| Frontmatter hooks never fire | Workspace trust not accepted for the folder | Accept the trust dialog; a `-p` session does not count |
| Hook "runs" but nothing happens | Script not executable, or path wrong — both fail *open* | `chmod +x`; watch for `Failed with non-blocking status code` |
| Hook JSON ignored | Something else printed to stdout, often a shell profile banner | stdout must contain only the JSON object |
| `Stop` hook loops forever | `stop_hook_active` not checked | Check it first thing |
| Matcher fires too widely | Hyphenated or dotted matcher read as an unanchored regex | Anchor it: `^db-agent$` |
| MCP tools absent | Wrong scope, or the session started before `.mcp.json` existed | `claude mcp list`, `/mcp`, restart |
| MCP server exits immediately | Missing `mcp` package, or `data/telemetry.db` not built | `pip install "mcp[cli]"`, `python scripts/seed_db.py` |
| Plugin skills missing | Directories placed inside `.claude-plugin/` | Only `plugin.json` goes in there |
| Plugin agent lost its guard | Plugin agents ignore `hooks`/`mcpServers`/`permissionMode` | Keep it in `.claude/agents/` |

## Questions that always come up

**"Subagent or skill?"** Isolation or reuse. Need the output *out* of your
context — subagent. Need the same instructions *in* several contexts — skill.
They compose: a subagent can preload skills.

**"Why not put everything in CLAUDE.md?"** It loads on every request, and past
roughly 200 lines it stops being read carefully. Reference material goes in
skills; enforcement goes in hooks.

**"Isn't a hook just a git pre-commit hook?"** Same idea, different point in the
loop. A pre-commit hook catches it at the end; a `PreToolUse` hook stops the
write before it happens and tells the model why, so the model corrects itself.

**"Do MCP servers slow things down?"** Tool names load at startup, schemas load
on use, and tool search is on by default — so idle servers are cheap. Ten
servers you never call still cost something; `/context all` shows exactly what.

**"Can we ship this to the whole org?"** Yes — managed settings, an internal
marketplace via `extraKnownMarketplaces`, and `allowManagedHooksOnly` if you
need only administrator-approved hooks to run. That is a follow-on session.

## Currency check

Claude Code moves fast. Before each delivery, re-check the behaviour of
`/agents`, fork mode defaults, and the subagent model-resolution order against
the live docs, and re-run the full lab set once end to end:

- Subagents: https://code.claude.com/docs/en/sub-agents
- MCP: https://code.claude.com/docs/en/mcp
- Hooks: https://code.claude.com/docs/en/hooks
- Plugins: https://code.claude.com/docs/en/plugins
- Feature comparison: https://code.claude.com/docs/en/features-overview
