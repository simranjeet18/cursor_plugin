---
name: project-info
description: Display comprehensive metadata and info about the current project.
---

# Project Info

Display detailed information about the current working project.

## Trigger

Invoke when the user runs `/project-info` or asks for project metadata, tech stack, scripts, or git status.

**Section filter**: `deps`, `scripts`, `structure`, `git`, `cursor`, or `all` (default)

## Workflow

### Step 1: Verify Project Context

Check current working directory. If not in a valid project:

- Suggest using `/load-project` first
- Or offer to analyze the current directory anyway

Prefer reading from the knowledge cache at `~/.cursor/projects/{sanitized-path}/memory/project_knowledge.md` if available and fresh.

### Step 2: Gather Project Metadata

Collect information from multiple sources:

#### 2.1 Basic Info

From `package.json`, `Cargo.toml`, `pyproject.toml`, etc.:

```
Project: my-app
Version: 1.2.0
Description: ...
License: MIT
```

#### 2.2 Tech Stack Detection

- **Language**: JavaScript/TypeScript, Python, Rust, Go, Java
- **Runtime**: Node.js, Python 3.11, etc.
- **Framework**: React, Next.js, FastAPI, etc.
- **Build Tool**: Vite, Webpack, esbuild
- **Package Manager**: npm, pnpm, yarn, pip, cargo
- **Database**: PostgreSQL, MongoDB, Redis, Firebase
- **Testing**: Jest, Vitest, pytest

#### 2.3 Project Structure

Top-level directory tree with purpose annotations.

#### 2.4 Available Scripts

From `package.json` scripts, Makefile, or similar — table format with script name, command, and description.

#### 2.5 Dependencies Summary

Production and dev dependency counts with key packages listed. Note outdated packages if `npm outdated` or equivalent is available.

#### 2.6 Git Status

Branch, remote sync status, staged/modified/untracked counts, recent commits.

#### 2.7 Cursor Configuration

```
## Cursor Setup

**AGENTS.md**: Found / Not found
**Rules**: .cursor/rules/ (list files)
**Knowledge Graph**: `.cursor/knowledge_graph.json` (exists / not found)
**Custom Commands**: N commands from .cursor/commands/
**Project Skills**: N skills from .cursor/skills/
```

#### 2.8 Environment Variables

From `.env.example` or `.env.template` — variable name, description, and whether set locally (without reading secret values).

### Step 3: Section Filtering

Based on argument, show only specific sections:

- `deps` — dependencies only
- `scripts` — available scripts only
- `structure` — project structure only
- `git` — git status only
- `cursor` — Cursor configuration only
- `all` or empty — everything (default)

### Step 4: Output Format

Present information in a clean, scannable format:

- Use tables for structured data
- Use code blocks for file structures
- Highlight important info (outdated deps, missing env vars)

End with relevant quick actions based on the project (e.g., `npm run dev`, `git pull`).

## Caching

- Prefer knowledge cache when fresh (< 7 days)
- Use `/refresh-project` or `/project-info refresh` to force refresh
