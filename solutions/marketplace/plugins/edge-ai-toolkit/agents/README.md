Subagents shipped by this plugin. They load as `edge-ai-toolkit:<name>` and
appear in the @-mention typeahead under that scoped name.

`db-reader` is deliberately **not** here. Plugin subagents ignore the `hooks`,
`mcpServers` and `permissionMode` frontmatter fields for security reasons, and
`db-reader` depends on a `PreToolUse` hook for its read-only guarantee. An
agent whose safety property is silently dropped by the packaging layer is
worse than no agent, so it stays a project subagent in `.claude/agents/`.
