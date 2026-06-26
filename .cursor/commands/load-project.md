# Load Project

Switch working context to this project and prepare the code knowledge graph.

Steps:
1. Call the `load_project` MCP tool with the project root path.
2. It records the project, detects the tech stack and source directory, and
   auto-generates `.cursor/knowledge_graph.json` if the project has 10+ source
   files and no fresh graph exists.
3. Summarize for me: project name, language, frameworks, package manager, git
   branch/last commit, and the knowledge-graph status (files + symbols indexed).
4. From now on, use `query_symbol` / `query_file` before reading source files.
