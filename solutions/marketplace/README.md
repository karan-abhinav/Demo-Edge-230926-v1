# edge-ai-training marketplace

A one-plugin marketplace, used in Lab D2 to show the full distribution path
without needing a git host.

```bash
/plugin marketplace add ./solutions/marketplace
/plugin                                  # browse, install, check the Errors tab
/plugin install edge-ai-toolkit@edge-ai-training
```

In real use the `source` field points at a git repository instead of a
relative path, and teams pre-register the marketplace for everyone with
`extraKnownMarketplaces` in `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "edge-ai-training": {
      "source": { "source": "github", "repo": "your-org/edge-ai-training" }
    }
  }
}
```

Marketplace state is stored once per user in
`~/.claude/plugins/known_marketplaces.json`, not per project.
