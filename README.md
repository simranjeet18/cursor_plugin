# Cursor Project Manager

A Cursor **plugin** for managing project sessions, switching contexts, tracking
recent projects, and scaffolding a **code knowledge graph** — for people who use
Cursor and don't have access to Claude Code.

It's a port of the Claude Code [`project-manager`](https://github.com/HimanshuSingh2308/claude-code-plugins/tree/main/project-manager)
plugin. That plugin uses Claude *agents* to read and index your codebase. This
version uses Cursor-native paths (`.cursor/`, `AGENTS.md`) and pairs with the
**cursor-project-manager** MCP server for deterministic Python indexing via `ast`.

> **Scope:** The knowledge graph parser is Python-only (`ast`-based). The plugin
> itself works with any project type.

## What you get

- Slash commands: `/load-project`, `/kg-update`, `/refresh-project`, etc.
- A `.cursor/knowledge_graph.json` index (when MCP is configured) with exact
  `[start, end]` line ranges for every file, class, function, import, and route.
- Agent rules and commands scaffolded into loaded projects automatically.
- A recent-projects registry at `~/.cursor/project-registry.json`.

## Repo layout

```
cursor_plugin/
├── project-manager/          ← Cursor plugin (install this)
│   ├── .cursor-plugin/
│   ├── commands/
│   ├── rules/
│   └── skills/
└── .cursor/                  ← Example config for this repo
    ├── commands/
    ├── rules/
    └── mcp.json.example
```

## How it compares to the Claude plugin

> **Canonical paths in this repo are Cursor-only** (`.cursor/`, `AGENTS.md`,
> `~/.cursor/project-registry.json`). The Claude column is historical context
> from the upstream plugin this project ports.

| | Claude `project-manager` | Cursor Project Manager (this) |
|---|---|---|
| Parsing engine | Claude agents (Sonnet/Haiku) | Deterministic `ast` via MCP server |
| Line-number accuracy | LLM estimate | Exact |
| Model required | Claude | Any (model-agnostic) |
| Graph location | `.claude/knowledge_graph.json` | `.cursor/knowledge_graph.json` |
| Interface | commands + skills + agents | plugin + MCP tools + rules |

The graph schema is intentionally compatible with the upstream plugin.

## Install the plugin

1. Clone this repo (or add it as a local plugin path).
2. In Cursor: **Settings → Plugins → Add local plugin** pointing at the
   `project-manager/` directory.

Or symlink:

```bash
ln -s "$(pwd)/project-manager" ~/.cursor/plugins/local/project-manager
```

See [`project-manager/README.md`](project-manager/README.md) for full plugin docs.

## Configure the MCP server (knowledge graph)

The knowledge graph features (`query_symbol`, `query_file`, `/kg-update`) require
the **cursor-project-manager** MCP server installed separately:

```bash
pip install cursor-project-manager   # when published
# or install from source if you maintain a separate MCP package
```

Add to `~/.cursor/mcp.json` (copy from `.cursor/mcp.json.example`):

```json
{
  "mcpServers": {
    "cursor-project-manager": {
      "command": "cursor-project-manager",
      "args": []
    }
  }
}
```

Then in Cursor: **Settings → MCP** and confirm the server is connected.

## Usage

In Cursor's chat:

```
/load-project           → switch context, generate graph if 10+ source files
/project-info           → tech stack + git + graph status
/kg-update              → incremental re-index of changed files
/refresh-project        → full re-scan of project knowledge cache
/recent-projects        → jump back to a recent project
```

Or just ask normally — the `knowledge-graph.mdc` rule directs the agent to call
`query_symbol` / `query_file` before reading files.

## MCP tools

| Tool | Description |
|------|-------------|
| `load_project(project_path)` | Record project, detect stack, auto-build graph |
| `get_project_info(project_path)` | Tech stack, source dir, git, graph status |
| `generate_knowledge_graph(project_path, source_dir, include_tests)` | Full scan |
| `update_knowledge_graph(project_path, files)` | Incremental update (git-aware) |
| `query_symbol(name, project_path)` | Symbol → file + line range |
| `query_file(path, project_path)` | File symbols, imports, `importedBy` |
| `list_recent_projects()` | Recently loaded projects |

## Graph schema

```json
{
  "meta": {
    "version": "1.0.0",
    "generatedAt": "ISO-8601",
    "language": "python",
    "sourceDir": "src/",
    "totalFiles": 84,
    "totalSymbols": 191
  },
  "directories": { "src/services/": { "description": "...", "fileCount": 4 } },
  "files": {
    "src/services/auth.py": {
      "description": "Auth service",
      "lines": 210,
      "symbols": ["AuthService"],
      "imports": ["src/services/api.py"],
      "importedBy": ["src/routes/login.py"]
    }
  },
  "symbols": {
    "AuthService": {
      "kind": "class",
      "file": "src/services/auth.py",
      "lines": [15, 210],
      "extends": ["BaseService"],
      "description": "...",
      "members": { "login": { "kind": "method", "lines": [40, 72] } }
    }
  },
  "routes": { "POST /login": "src/routes/login.py:login" }
}
```

## License

MIT
