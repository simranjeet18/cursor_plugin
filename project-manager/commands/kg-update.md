---
name: kg-update
description: Incrementally update the code knowledge graph for changed source files.
---

# Update Knowledge Graph

Incrementally update the code knowledge graph at `.cursor/knowledge_graph.json`
for files changed in the current project.

## Trigger

Invoke when the user runs `/kg-update`, or after finishing a feature or bug fix
when the knowledge graph should reflect recent edits.

## Workflow

1. Call the `update_knowledge_graph` MCP tool for the project root.
2. If the user named specific files, pass them as `files`; otherwise let the tool
   auto-detect changed Python files via git.
3. Report which files were added, modified, or removed, and the new
   `totalFiles` / `totalSymbols` totals.

If no graph exists yet, run `generate_knowledge_graph` first (or use
`/load-project` on a project with 10+ source files).

## Notes

- Run at natural breakpoints, not after every single edit.
- Graph path is always `.cursor/knowledge_graph.json`.
- The `knowledge-graph.mdc` rule directs agents to consult the graph before
  reading source files.
