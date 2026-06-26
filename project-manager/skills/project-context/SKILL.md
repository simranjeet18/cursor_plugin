---
name: project-context
description: >
  Background knowledge for project context management in Cursor. Applied when
  working with projects, detecting tech stacks, managing session state, and
  navigating between codebases. Provides patterns for project detection,
  registry management, and context persistence.
---

# Project Context Management

Background knowledge for managing project contexts in Cursor sessions.

## Project Registry Schema

The project registry is stored at `~/.cursor/project-registry.json`:

```json
{
  "version": "1.0",
  "maxProjects": 20,
  "projects": {
    "/absolute/path/to/project": {
      "name": "project-name",
      "alias": "short-alias",
      "lastAccessed": "2026-03-18T14:30:00Z",
      "accessCount": 15,
      "techStack": {
        "language": "typescript",
        "runtime": "node",
        "framework": "react",
        "buildTool": "vite",
        "packageManager": "pnpm",
        "testing": "vitest"
      },
      "hasCursorConfig": true,
      "hasKnowledgeCache": true,
      "scripts": ["dev", "build", "test", "lint"],
      "gitBranch": "main",
      "gitRemote": "origin"
    }
  }
}
```

## Tech Stack Detection

See [tech-stack-patterns.md](references/tech-stack-patterns.md) for the full detection matrix.

Quick reference — language from manifest files:

| File/Pattern | Language |
|--------------|----------|
| `package.json` | JavaScript/TypeScript |
| `tsconfig.json` | TypeScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml`, `setup.py` | Python |
| `pom.xml`, `build.gradle` | Java |

Package manager from lockfiles:

| File | Package Manager |
|------|-----------------|
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | yarn |
| `package-lock.json` | npm |
| `bun.lockb` | bun |
| `poetry.lock` | poetry |
| `Cargo.lock` | cargo |

## Project Markers Priority

When detecting if a directory is a project, check in this order:

1. **Cursor Config** (highest priority)
   - `AGENTS.md`
   - `.cursor/rules/`
   - `.cursor/commands/`

2. **Version Control**
   - `.git/`

3. **Package Manifests**
   - `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`

4. **Build Config**
   - `Makefile`, `Dockerfile`, `docker-compose.yml`

## Context Switching Best Practices

When switching between projects:

1. **Save current state** — note uncommitted changes and current branch
2. **Load new context** — read AGENTS.md, detect tech stack, list custom commands
3. **Update registry** — bump `lastAccessed`, increment `accessCount`, update `gitBranch`

## Knowledge Cache System

**Location**: `~/.cursor/projects/{sanitized-path}/memory/project_knowledge.md`

**Sanitized path**: replace `/` with `-`, remove leading `-`
- `/Users/dev/code/my-app` → `-Users-dev-code-my-app`

**Contents**: Tech stack, directory structure, key scripts, AGENTS.md summary, dependencies, CI/CD, custom commands, conventions.

**Cache rules**:

- Created on first `/load-project` (full scan)
- Reused on subsequent loads (instant)
- Expires after 7 days (auto-refreshed on next load)
- Manually refreshed via `/refresh-project`
- Deep refresh via `/refresh-project --deep`

## Project Templates

Built-in templates and scaffold commands: [project-templates.md](references/project-templates.md)

Custom templates: `~/.cursor/project-templates/`

## Session State Management

Project context is maintained through:

1. **Current Working Directory** — primary context indicator
2. **Project Registry** — metadata and history (`~/.cursor/project-registry.json`)
3. **Knowledge Cache** — persistent project knowledge (`~/.cursor/projects/{path}/memory/project_knowledge.md`)
4. **Conversation context** — maintained by the agent session

## Error Recovery

| Issue | Solution |
|-------|----------|
| Project path doesn't exist | Check for moved/renamed, offer to remove from registry |
| Git repo corrupted | Suggest `git fsck` or re-clone |
| Package manifest invalid | Offer to validate/fix JSON |
| Missing dependencies | Suggest `npm install` or equivalent |
| Permission denied | Check file permissions |

## Integration Points

- `/load-project` — switch context (uses knowledge cache)
- `/refresh-project` — force re-scan and update cache
- `/recent-projects` — list and navigate history
- `/project-info` — display current project details
- `/new-project` — create from templates
