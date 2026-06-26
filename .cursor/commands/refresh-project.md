# Refresh Project

Force a full re-scan of this project's code knowledge graph.

Steps:
1. Call `generate_knowledge_graph` for the project root (let it auto-detect the
   source directory unless I specify one).
2. Report what changed: total files and symbols indexed, number of routes
   detected, and any parse errors returned.
3. Use this after large changes (new modules, restructured directories, big
   merges). For small edits, prefer `/kg-update` which is incremental.
