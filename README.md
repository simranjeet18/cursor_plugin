# Cursor Project Manager

A code **knowledge graph** for [Cursor](https://cursor.com) — for people who use
Cursor and don't have access to Claude Code.

It's a port of the Claude Code [`project-manager`](https://github.com/HimanshuSingh2308/claude-code-plugins/tree/main/project-manager)
plugin. That plugin uses Claude *agents* to read and index your codebase. This
version replaces those agents with a small **MCP server** that parses your code
**deterministically** using Python's built-in `ast` — so it works with **any**
model Cursor is configured with (GPT, Gemini, etc.), and produces **exact** line
numbers instead of LLM guesses.

> **Scope:** Python projects (parsing is `ast`-based). The architecture is
> language-extensible — see [Extending](#extending-to-other-languages).

## What you get

- A `.cursor/knowledge_graph.json` index of every file, class, function, import,
  reverse-dependency (`importedBy`), and detected FastAPI/Flask route — with
  precise `[start, end]` line ranges.
- MCP tools the Cursor agent calls to **navigate code by exact location** instead
  of blindly scanning files.
- A Cursor **rule** that tells the agent to consult the graph first.
- Cursor **slash commands** (`/load-project`, `/kg-update`, etc.) as a UX layer.
- A recent-projects registry at `~/.cursor/project-registry.json`.

## How it compares to the Claude plugin

| | Claude `project-manager` | Cursor Project Manager (this) |
|---|---|---|
| Parsing engine | Claude agents (Sonnet/Haiku) | Deterministic `ast` via MCP server |
| Line-number accuracy | LLM estimate | Exact |
| Model required | Claude | Any (model-agnostic) |
| Graph location | `.claude/knowledge_graph.json` | `.cursor/knowledge_graph.json` |
| Interface | commands + skills + agents | MCP tools + rules + commands |

The graph schema is intentionally compatible with the original.

## Install

Requires Python 3.11+.

```bash
git clone <this-repo> cursor-project-manager
cd cursor-project-manager/mcp_server
pip install -e .          # installs the `mcp` dependency and the server
```

(Or skip install and run straight from source with `PYTHONPATH` — see the
example config.)

## Configure Cursor

Add the MCP server to Cursor. Either project-level (`.cursor/mcp.json` in your
repo) or global (`~/.cursor/mcp.json`). Copy `.cursor/mcp.json.example` and edit
the path:

```json
{
  "mcpServers": {
    "cursor-project-manager": {
      "command": "python",
      "args": ["-m", "cursor_project_manager"],
      "env": { "PYTHONPATH": "/ABSOLUTE/PATH/TO/cursor_plugin/mcp_server" }
    }
  }
}
```

If you `pip install`ed it, you can instead use the console script:

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

Then in Cursor: **Settings → MCP** and confirm the server is connected (the
seven tools should be listed).

To make the agent *use* the graph automatically, copy `.cursor/rules/` and
`.cursor/commands/` into your target project's `.cursor/` directory (or keep this
repo as your workspace to try it out).

## Usage

In Cursor's chat:

```
/load-project           → indexes the project, prints a summary
/project-info           → tech stack + git + graph status
/kg-update              → incremental re-index of changed files
/refresh-project        → full re-index
/recent-projects        → jump back to a recent project
```

Or just ask normally — the rule directs the agent to call `query_symbol` /
`query_file` before reading files.

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

## Extending to other languages

The parser interface in `mcp_server/cursor_project_manager/parser.py` returns a
`{file, file_entry, symbols}` dict per file. To add a language, write an
equivalent parser (e.g. tree-sitter for TS/Go) that returns the same shape and
dispatch on extension in `kg.discover_source_files` / `kg.build_graph`.

## License

MIT
