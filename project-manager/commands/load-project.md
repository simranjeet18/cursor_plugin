---
name: load-project
description: Switch working context to a project — loads configurations, detects tech stack, and prepares the session.
---

# Load Project

Load and switch context to the project path or name provided by the user.

## Trigger

Invoke when the user runs `/load-project` or asks to switch to, open, or load a project.

## Workflow

### Step 1: Resolve Project Path

If the argument is:

- An absolute path: use it directly
- A relative path: resolve from current working directory
- A project name: check `~/.cursor/project-registry.json` for registered projects
- Empty: prompt the user to provide a project path or select from recent projects

### Step 2: Check for Cached Project Knowledge

Check if a project knowledge file already exists at:

```
~/.cursor/projects/{sanitized-path}/memory/project_knowledge.md
```

Where `{sanitized-path}` is the project path with `/` replaced by `-` and leading `-` removed (e.g., `/Users/dev/code/my-app` → `-Users-dev-code-my-app`).

**If the knowledge file EXISTS and is less than 7 days old:**

1. Read the knowledge file instead of re-scanning the project
2. Do a quick validation only:
   - Verify the project path still exists
   - Check `git branch --show-current` for current branch
   - Check `git log --oneline -1` for latest commit
3. Update `lastAccessed` in the registry
4. Present the cached summary (with branch/commit freshened)
5. Skip to Step 7 (change directory)

**If the knowledge file DOES NOT exist or is older than 7 days:**

Continue with full scan (Steps 3–6), then save results.

### Step 3: Validate Project

1. Check the path exists and is a directory
2. Look for project markers:
   - `package.json` (Node.js/npm)
   - `Cargo.toml` (Rust)
   - `pyproject.toml` or `requirements.txt` (Python)
   - `go.mod` (Go)
   - `pom.xml` or `build.gradle` (Java)
   - `.git` directory (any git repo)
   - `AGENTS.md` or `.cursor/` (Cursor project)

If no project markers found, ask the user to confirm this is the correct directory.

### Step 4: Load Project Context

Read and summarize key configuration files (if they exist):

1. **Cursor Configuration**:
   - `AGENTS.md` — project instructions for the agent (summarize key rules/patterns)
   - `.cursor/rules/` — project rules (list available rule files)
   - `.cursor/commands/` — custom commands (list available ones)
   - `.cursor/skills/` — project skills (list available ones)

2. **Project Configuration**:
   - `package.json` — dependencies, scripts, project name/version
   - `tsconfig.json` / `jsconfig.json` — TypeScript/JS config
   - `.env.example` — environment variables needed
   - `README.md` — project description (first 2–3 paragraphs)

3. **CI/CD & Quality**:
   - `.github/workflows/` or `.gitlab-ci.yml` — CI workflows (list names)
   - `.eslintrc*` / `prettier.config*` — code style tools
   - `jest.config*` / `vitest.config*` — testing setup

4. **Project Structure**:
   - Top-level directory layout (1 level deep)
   - Key source directories and their purpose
   - Number of source files by type

5. **Git Context**:
   - Current branch
   - Last 5 commits (oneline)
   - Remote URLs
   - Any uncommitted changes

### Step 5: Detect Tech Stack

Based on files found, identify:

- **Runtime**: Node.js, Deno, Bun, Python, Rust, Go, Java, etc.
- **Framework**: React, Next.js, Vue, Svelte, Express, FastAPI, NestJS, etc.
- **Package Manager**: npm, yarn, pnpm, pip, cargo, etc.
- **Build Tool**: webpack, vite, esbuild, turbopack, nx, etc.
- **Testing**: Jest, Vitest, pytest, cargo test, etc.
- **Database**: PostgreSQL, MongoDB, Redis, Firebase, etc.
- **Deployment**: Firebase, Vercel, AWS, Docker, etc.

### Step 6: Save Project Knowledge

Save all gathered information to a knowledge file so future loads are instant.

**File**: `~/.cursor/projects/{sanitized-path}/memory/project_knowledge.md`

```markdown
---
name: {project-name} project knowledge
description: Cached project context for {project-name} — tech stack, structure, scripts, and key patterns
type: project
scannedAt: {ISO timestamp}
---

## Project: {project-name}

**Path**: {absolute-path}
**Tech Stack**: {comma-separated list}
**Package Manager**: {name}
**Framework**: {name}

## Structure

{top-level directory layout with purpose of each dir}

## Key Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| ... | ... | ... |

## AGENTS.md Summary

{Key rules, patterns, and API conventions from AGENTS.md — condensed}

## Dependencies (Key)

**Production**: {list of important deps}
**Dev**: {list of important dev deps}

## CI/CD

{CI workflows, deploy process}

## Custom Commands

{List of available /commands from .cursor/commands/}

## Conventions

{Coding patterns, naming conventions, file organization rules}
```

Create the parent directory if it does not exist.

### Step 6.5: Knowledge Graph (Cursor-only)

If the project has **10 or more** source files (Python `.py` for the MCP parser;
count other languages for display only):

1. **Generate the graph** at `.cursor/knowledge_graph.json`:
   - Call the `generate_knowledge_graph` MCP tool with the project root, or
   - Use the `kg-generator` subagent with an explicit output path of
     `.cursor/knowledge_graph.json`.
   - Skip if a fresh graph already exists (check `meta.generatedAt`).

2. **Scaffold agent rule** — if `.cursor/rules/knowledge-graph.mdc` is missing,
   copy the template from this plugin's `project-manager/rules/knowledge-graph.mdc`
   into the project's `.cursor/rules/` directory.

3. **Scaffold slash command** — if `.cursor/commands/kg-update.md` is missing,
   copy the template from this plugin's `project-manager/commands/kg-update.md`
   into the project's `.cursor/commands/` directory.

**Cursor-only** — scaffold `.cursor/` paths and `AGENTS.md` only. Do not create
artifacts from other agent tools.

If fewer than 10 source files, note that the knowledge graph was skipped and
suggest `/refresh-project` or `generate_knowledge_graph` after the codebase grows.

### Step 7: Update Project Registry

Add or update entry in `~/.cursor/project-registry.json`:

```json
{
  "projects": {
    "/path/to/project": {
      "name": "project-name",
      "lastAccessed": "2026-03-25T12:00:00Z",
      "techStack": ["node", "typescript", "react", "vite"],
      "hasCursorConfig": true,
      "hasKnowledgeCache": true
    }
  }
}
```

Keep at most 20 projects (remove oldest by `lastAccessed` when exceeded).

### Step 8: Present Summary

Display a concise summary:

```
## Project Loaded: {project-name} {cached ? "(from cache)" : ""}

**Path**: /path/to/project
**Tech Stack**: Node.js, TypeScript, React, Vite
**Package Manager**: pnpm
**Branch**: main (latest: abc1234 - commit message)

### Key Files Found
- AGENTS.md (project instructions)
- `.cursor/knowledge_graph.json` (code index, if 10+ source files)
- 15 npm scripts available
- Vitest test setup configured
- GitHub Actions CI/CD

### Quick Actions
- `npm run dev` - Start development server
- `npm run test` - Run tests
- `npm run build` - Build for production

Ready to work! Ask me anything about this project.
```

### Step 9: Change Working Directory

Use the Shell tool to change to the project directory:

```bash
cd /path/to/project
```

## Output Format

Always end with the project path, tech stack, branch, and 2–3 suggested next commands.

## Error Handling

- If path doesn't exist: suggest similar paths or recent projects via `/recent-projects`
- If path is a file: use its parent directory
- If permission denied: inform user and suggest alternatives
- If no project markers: warn but still load if user confirms
- If knowledge cache is corrupted: delete it and do a fresh scan

## Notes

- This command updates the session context for all subsequent interactions
- Recent projects can be accessed via `/recent-projects`
- Project metadata can be viewed anytime via `/project-info`
- Use `/refresh-project` to force a full re-scan and update the knowledge cache
- Knowledge cache expires after 7 days and is automatically refreshed
