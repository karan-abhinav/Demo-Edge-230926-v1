# Hands-on labs

Nine labs across four modules. Each has a goal, the steps, and a checkpoint
you can verify without an instructor. Reference answers are in `solutions/`.

Throughout, `$PROJECT` means the repository root — the directory you started
`claude` in.

---

# Module 1 — Subagents

## Lab A1 — A read-only reviewer (20 min)

**Goal.** Build a custom subagent that reviews code and cannot change it, and
watch the difference between a description that gets picked and one that doesn't.

1. Ask Claude to write the file for you, and be specific about the constraints:

   ```
   Create a project subagent at .claude/agents/telemetry-reviewer.md that reviews
   Python changes in src/ for correctness, error handling and leaked secrets.
   Make it read-only — Read, Grep, Glob and Bash only, no Edit or Write.
   It should run git diff first, then report CRITICAL / WARNING / SUGGESTION
   with a concrete fix for every CRITICAL.
   ```

2. Open the generated file. Confirm the frontmatter has `name`, `description`
   and a `tools` line with no `Edit` or `Write`. Fix it by hand if not.

3. Introduce something to find:

   ```bash
   git checkout -b lab-a1
   ```

   Ask Claude to add a `median_temp` helper to `src/edge_telemetry/features.py`
   — with no test and no docstring.

4. Invoke the reviewer explicitly:

   ```
   @telemetry-reviewer review my recent changes
   ```

5. Now make the description worse. Change it to `Reviews code.` and start a new
   session. Ask *"can you check my recent changes?"* without naming the agent.

**Checkpoint.** With the specific description Claude delegates on its own; with
`Reviews code.` it usually doesn't. The reviewer reports the bare `except` in
`ingest.py` and the hard-coded `FLEET_API_TOKEN` in `config.py`, and it never
edits a file. Restore the good description before moving on.

> **Why it matters.** `description` is the routing key. It is also the only part
> of a subagent that costs context on every request — detail belongs in the body.

---

## Lab A2 — Chain two specialists (25 min)

**Goal.** Show context isolation paying for itself, and chain subagents so each
one's output feeds the next.

1. Create `.claude/agents/test-runner.md` with `model: haiku` and
   `tools: Bash, Read, Grep`. Its prompt must forbid pasting full pytest output —
   failures only. (Reference: `solutions/agents/test-runner.md`.)

2. Create `.claude/agents/docs-writer.md` with `tools: Read, Grep, Glob, Write, Edit`
   and `disallowedTools: Bash`, so it can write Markdown but cannot run anything.

3. Break something on purpose:

   ```bash
   sed -i 's/window + 2/window + 3/' src/edge_telemetry/features.py
   ```

   (On macOS: `sed -i ''`.)

4. Run the chain in one prompt:

   ```
   Use the test-runner subagent to find what is failing, then use the
   docs-writer subagent to write docs/known-issues.md describing the defect.
   ```

5. Run `/context` and note how much of your window the test output did *not* take.

6. Now the real one. `rolling_mean` in `features.py` has an off-by-one that no
   test covers. Ask Claude:

   ```
   Use a subagent to check whether rolling_mean actually averages `window`
   samples. Give it a failing test case if it does not.
   ```

**Checkpoint.** `docs/known-issues.md` exists and describes a real failure. The
subagent finds the off-by-one in the slice start. Your main transcript never
contains a full pytest dump.

> **Why it matters.** The subagent read dozens of lines of pytest output; you
> received four. That is the entire value proposition.

---

## Lab A3 — Constraints the `tools` field cannot express (25 min)

**Goal.** Use a `PreToolUse` hook in subagent frontmatter to allow *some* uses
of a tool and block others — a read-only database agent that still has Bash.

1. Build the database if you have not: `python scripts/seed_db.py`.

2. Copy `solutions/hooks/validate_readonly_sql.py` to `.claude/hooks/`, and
   read it. It exits 2 on any write keyword; exit 2 blocks the tool call and
   shows stderr to the agent.

3. Create `.claude/agents/db-reader.md` with `tools: Bash` and a `hooks:` block:

   ```yaml
   hooks:
     PreToolUse:
       - matcher: "Bash"
         hooks:
           - type: command
             command: "python3"
             args: ["${CLAUDE_PROJECT_DIR}/.claude/hooks/validate_readonly_sql.py"]
   ```

4. Restart Claude Code (frontmatter hooks in a project agent need the workspace
   trust dialog accepted), then:

   ```
   @db-reader which device has the most fault runs?
   @db-reader delete every run for uno-q-03
   ```

**Checkpoint.** The first question is answered with SQL and a table. The second
is blocked, and the agent sees `Blocked: db-reader may only run SELECT
statements against telemetry.db.`

> **Why it matters.** `tools: Bash` is all-or-nothing. The hook is what turns it
> into "Bash, but only SELECT." The system prompt asks; the hook enforces.

**Stretch.** Give `db-reader` `memory: project` and ask it the same question in
two sessions. Inspect `.claude/agent-memory/db-reader/`.

---

# Module 2 — MCP

## Lab B1 — Connect and commit a server (20 min)

**Goal.** Add a server at project scope, see the tools arrive, and understand
what commit means for your team.

1. Add the Claude Code documentation server at project scope:

   ```bash
   claude mcp add --scope project --transport http \
     claude-code-docs https://code.claude.com/docs/mcp
   ```

2. Inspect what it wrote:

   ```bash
   cat .mcp.json
   claude mcp list
   ```

3. Start a session and run `/mcp`. Note the connection status. Then run
   `/context all` and find the token cost of the loaded tools.

4. Ask a question that needs the server, and watch the tool name in the
   transcript: `mcp__claude-code-docs__*`.

5. Change the scope. Remove it and re-add at user scope:

   ```bash
   claude mcp remove claude-code-docs
   claude mcp add --scope user --transport http \
     claude-code-docs https://code.claude.com/docs/mcp
   ```

   `.mcp.json` no longer mentions it. Scope is fixed at add time — changing it
   means remove and re-add.

**Checkpoint.** You can state, without looking it up, which file each of the
three scopes writes to and which of them you would commit.

---

## Lab B2 — Build your own server (35 min)

**Goal.** Write a real MCP server over the project's own data, and learn that
the tool docstring is the interface.

1. `pip install "mcp[cli]>=1.2"` and `python scripts/seed_db.py`.

2. Open `mcp_servers/telemetry_mcp.py`. It is complete and commented — read it
   rather than typing it. Note four things:
   - `sqlite3.connect("file:...?mode=ro", uri=True)` — read-only by construction
   - `order_by` checked against an allowlist, `limit` clamped to 1–200
   - every tool has a docstring saying what it returns and when to reach for it
   - it reads `TELEMETRY_DB` from the environment, so the path is not hard-coded

3. Register it at project scope:

   ```bash
   claude mcp add --scope project telemetry \
     -- python3 "$PWD/mcp_servers/telemetry_mcp.py"
   ```

   The `--` matters: everything after it is the server command, untouched.

4. Restart, run `/mcp`, then ask:

   ```
   Which device in the fleet runs hottest, and how many runs breach 58 C?
   ```

5. **The experiment.** Replace the `anomaly_summary` docstring with the single
   word `Summary.` Restart and ask the same question. Then restore it.

**Checkpoint.** With good docstrings Claude picks `anomaly_summary` in one call.
With `Summary.` it usually pulls raw rows with `query_runs` and does the
arithmetic itself — slower, more tokens, and easier to get wrong.

> **Why it matters.** You are not writing an API for a programmer who can read
> your source. You are writing for a model that sees only the name, the
> signature and the docstring.

---

## Lab B3 — Scope a server to one subagent (15 min)

**Goal.** Keep an MCP server's tool descriptions out of the main context.

1. Remove `telemetry` from `.mcp.json`.

2. Add it to a subagent instead — create `.claude/agents/fleet-analyst.md`:

   ```yaml
   ---
   name: fleet-analyst
   description: Answers fleet-level questions about device telemetry using the telemetry database.
   mcpServers:
     - telemetry:
         type: stdio
         command: python3
         args: ["./mcp_servers/telemetry_mcp.py"]
   ---
   Answer fleet questions with the telemetry tools. Always state which tool
   you called and why.
   ```

3. Restart. Run `/mcp` in the main session — `telemetry` is absent. Now:

   ```
   @fleet-analyst which device is hottest?
   ```

**Checkpoint.** The subagent answers using tools the main conversation never
loaded. Compare `/context` before and after.

---

# Module 3 — Hooks

## Lab C1 — Format on every edit (20 min)

**Goal.** A `PostToolUse` hook that runs ruff and feeds what it cannot fix back
into the conversation.

1. Copy `solutions/hooks/_hookio.py` and `solutions/hooks/format_python.py`
   into `.claude/hooks/` and read them.

2. Register in `.claude/settings.json`:

   ```json
   "hooks": {
     "PostToolUse": [
       {
         "matcher": "Edit|Write",
         "hooks": [
           {
             "type": "command",
             "command": "python3",
             "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/format_python.py"],
             "timeout": 30,
             "statusMessage": "Formatting with ruff"
           }
         ]
       }
     ]
   }
   ```

3. Run `/hooks` and confirm it appears under Project Settings.

4. Ask Claude to add a badly formatted function to `features.py` — long lines,
   no spacing. Watch the spinner message, then read the file.

5. Ask Claude to edit `src/edge_telemetry/ingest.py`. The hook auto-removes the
   unused `import os`, cannot fix the bare `except`, and hands that finding back
   as `additionalContext`. Claude should react to it on the next turn.

**Checkpoint.** The file is formatted without you asking. Claude mentions the
bare `except` without you mentioning it.

> **Bash equivalent.** The official examples use `jq`:
> `file=$(jq -r '.tool_input.file_path' <<<"$input")`. Python avoids the
> dependency; both read the same JSON off stdin.

---

## Lab C2 — A guardrail that actually holds (20 min)

**Goal.** The difference between an instruction and an enforcement.

1. First, prove the instruction is only a request. `CLAUDE.md` already says
   *"Never edit anything under `data/`."* Ask:

   ```
   Add a row to data/sensor_runs.csv for device uno-q-04.
   ```

   Note what happens. Usually Claude complies with the rule — but nothing
   *stopped* it, and a long session or a stray subagent can drift.

2. Copy `solutions/hooks/protect_paths.py` into `.claude/hooks/` and read the
   `deny()` function. It returns a structured `permissionDecision` rather than
   exiting 2, so Claude receives a readable reason.

3. Register it on `PreToolUse` with matcher `Edit|Write|NotebookEdit`.

4. Ask the same question again.

**Checkpoint.** The tool call is denied with your reason text, and Claude
explains the guardrail instead of editing. Try `solutions/` and `.env` too.

5. **Break it on purpose.** Mistype the script path in `settings.json` and try
   again. The edit goes through, and the transcript shows a non-blocking hook
   error. A policy hook that cannot start fails *open*.

> **Why it matters.** `PreToolUse` + exit 2 or `permissionDecision: deny` is the
> only way to make a rule hold every time. Everything else is a prompt.

---

## Lab C3 — Inject live state at session start (15 min)

**Goal.** Give Claude facts it would otherwise have to discover, at zero
ongoing context cost.

1. Copy `solutions/hooks/session_context.py` into `.claude/hooks/` and register
   it on `SessionStart` (no matcher).

2. Restart. Ask: *"what branch am I on and is the database built?"* Claude
   answers without running a single command.

3. Read the `additionalContext` string. Every sentence is a **statement of
   fact**. Now rewrite one as an order — `"You must always run pytest first."` —
   restart, and see whether Claude surfaces the text to you instead of using it.

**Checkpoint.** The factual version becomes silent context. The imperative
version can trip prompt-injection defences and get shown to you as text.

> **Why it matters.** `SessionStart` context is for environment state that
> changes. Rules that never change belong in `CLAUDE.md`, which needs no process.

---

## Lab C4 — Refuse to finish on a red suite (20 min)

**Goal.** A `Stop` hook, and the loop guard that makes it safe.

1. Copy `solutions/hooks/pytest_gate.py` into `.claude/hooks/` and register it
   on `Stop` with `"timeout": 120`.

2. Read the first four lines of `main()`. `stop_hook_active` is checked before
   anything else. Without it, blocking a stop re-fires the hook forever.

3. Break a test:

   ```bash
   sed -i 's/assert len(runs) == 240/assert len(runs) == 999/' tests/test_ingest.py
   ```

4. Ask Claude to do something small and unrelated — *"add a docstring to
   `zscores`"* — and watch it try to finish.

**Checkpoint.** Claude cannot end the turn; it reads the blocking reason and
fixes the test. Then comment out the `stop_hook_active` check, break a test the
model cannot fix, and observe the loop. Restore it.

> **Why it matters.** `Stop` is one of the few events that can block. It is the
> closest thing Claude Code has to a definition-of-done.

---

# Module 4 — Plugins

## Lab D1 — Package everything (30 min)

**Goal.** Turn a working `.claude/` setup into something a second repository
can install.

1. Scaffold at `my-toolkit/` in the project root:

   ```
   my-toolkit/
   ├── .claude-plugin/plugin.json     <- ONLY plugin.json goes in here
   ├── agents/
   ├── skills/
   ├── hooks/hooks.json
   └── scripts/
   ```

2. Write `plugin.json` with `name`, `description`, `version`, `author`.

3. Move your agents into `agents/` and your hook scripts into `scripts/`.

4. Convert your `settings.json` hooks block into `hooks/hooks.json`. Two
   changes: wrap it in a top-level `"hooks"` key, and swap
   `${CLAUDE_PROJECT_DIR}` for `${CLAUDE_PLUGIN_ROOT}` on every script path.

5. Validate, then load it:

   ```bash
   claude plugin validate ./my-toolkit
   claude --plugin-dir ./my-toolkit
   ```

6. Inside the session: `/help` (skills appear as `/my-toolkit:<name>`), `/context`
   (agents under Custom Agents), `/hooks` (source shows Plugin Hooks). Edit a
   skill, run `/reload-plugins`, confirm the change without restarting.

7. **The gotcha.** Move `db-reader.md` into `my-toolkit/agents/` and reload. Ask
   it to run a DELETE.

**Checkpoint.** `claude plugin validate` passes. Skills are namespaced. And
`db-reader`'s guard hook is *silently gone* — plugin subagents ignore `hooks`,
`mcpServers` and `permissionMode`. Move it back to `.claude/agents/`.

> **Why it matters.** Packaging is not neutral. An agent whose safety property
> the packaging layer drops must not be packaged.

---

## Lab D2 — Distribute it (20 min)

**Goal.** The full marketplace path, locally.

1. Create `my-marketplace/.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "my-training-marketplace",
     "owner": { "name": "Your Name" },
     "plugins": [
       {
         "name": "my-toolkit",
         "description": "Review, test and guardrail workflow.",
         "source": "./plugins/my-toolkit",
         "category": "development"
       }
     ]
   }
   ```

   Move `my-toolkit/` to `my-marketplace/plugins/my-toolkit/`.

2. Register and install:

   ```
   /plugin marketplace add ./my-marketplace
   /plugin install my-toolkit@my-training-marketplace
   /reload-plugins
   ```

3. Open `/plugin` and check the **Errors** tab. Then break something on
   purpose — a typo in `hooks.json` — reinstall, and read the error.

4. Compare with the reference: `solutions/marketplace/`.

5. For a team, add to `.claude/settings.json`:

   ```json
   {
     "extraKnownMarketplaces": {
       "my-training-marketplace": {
         "source": { "source": "github", "repo": "your-org/your-marketplace" }
       }
     }
   }
   ```

**Checkpoint.** The plugin installs from the marketplace, its skills namespace
correctly, and you can name the one file that has to exist for a directory to
be a marketplace.

---

# Capstone (40 min)

Wire all four layers into one workflow on a fresh branch.

```bash
git checkout -b capstone
```

**Requirements.**

1. `edge-ai-toolkit` (or your `my-toolkit`) installed from a marketplace.
2. The `telemetry` MCP server connected at project scope.
3. `data/` and `solutions/` write-protected by a `PreToolUse` hook.
4. A `Stop` hook that will not let the turn end on a red suite.
5. At least two subagents in the chain, one of them read-only.

**The task.** Give Claude one prompt and let the machinery work:

```
The anomaly detector only looks at temperature and vibration. Add current_a
to the z-score scoring in detect(), with tests. Use the fleet data to pick a
sensible threshold, have the reviewer check the change, and write the result
up as a lab report.
```

**What good looks like.**

- The MCP server was queried for real thresholds, not guessed ones.
- `anomaly.py` and `tests/test_anomaly.py` changed; nothing under `data/` did.
- The formatter ran on every edit without being asked.
- The reviewer ran read-only and raised something real.
- Claude could not stop until the suite was green.
- A report exists in `reports/`.

**Debrief.** For each of the six lines above, name which primitive produced it
and why the other three would have been the wrong choice.
