# Update Knowledge Graph

Incrementally update the code knowledge graph for files I changed.

Steps:
1. Call the `update_knowledge_graph` MCP tool for the project root.
2. If I named specific files, pass them as `files`; otherwise let it auto-detect
   changed Python files via git.
3. Report which files were added, modified, or removed, and the new totals.

Run this at natural breakpoints (after finishing a feature or fixing a bug),
not after every single edit.

**Graph location:** `.cursor/knowledge_graph.json` (never `.claude/`).
