# Project Manager

A Cursor plugin for managing project sessions, switching contexts, tracking recent projects, and scaffolding new projects from templates.

## Commands

| Command | Description |
|---------|-------------|
| `/load-project <path>` | Switch working context to a project (uses cache if available) |
| `/refresh-project` | Force re-scan current project and update knowledge cache |
| `/recent-projects` | List and navigate to recent projects |
| `/project-info` | Display metadata about current project |
| `/new-project <name>` | Create a new project from a template |

## Features

### Smart Project Loading with Knowledge Cache

When you load a project, the plugin saves a knowledge snapshot so subsequent loads are **instant** — no re-reading dozens of files.

**First load**: Full scan → reads AGENTS.md, package.json, configs, structure → saves to knowledge cache  
**Subsequent loads**: Reads cache → quick git status check → ready in seconds

Knowledge cache is stored at:

```
~/.cursor/projects/{sanitized-path}/memory/project_knowledge.md
```

Cache expires after 7 days and is automatically refreshed.

### Refresh Project

Use `/refresh-project` when the project has changed significantly:

```bash
# Quick refresh — git status, changed files, updated scripts
/refresh-project

# Deep refresh — full re-scan of everything
/refresh-project --deep
```

The refresh shows a diff of what changed since last scan.

### Context Switching

When you load a project, the plugin:

- Checks for cached knowledge first (instant load)
- Detects the tech stack (language, framework, build tools)
- Reads project configuration (AGENTS.md, package.json, etc.)
- Saves project knowledge for future sessions
- Updates the project registry for quick access later
- Changes to the project directory

### Recent Projects

- Automatically tracks projects when using `/load-project`
- Shows last accessed time and tech stack
- Quick jump to any recent project by number
- Maintains up to 20 recent projects

### Project Metadata

Get a comprehensive view of your project:

- Tech stack detection (language, framework, build tool, testing)
- Available scripts and commands
- Git status and recent commits
- Dependencies summary
- Environment variables required
- Cursor configuration status (AGENTS.md, rules, commands, skills)

### Project Templates

Scaffold new projects quickly:

- Built-in templates for React, Next.js, Vue, FastAPI, and more
- Custom templates support via `~/.cursor/project-templates/`
- Automatic AGENTS.md generation
- Git initialization and initial commit

## Knowledge Cache Contents

| Section | Contents |
|---------|----------|
| **Structure** | Top-level directory layout with purpose of each dir |
| **Tech Stack** | Runtime, framework, package manager, build tool, testing, DB, deploy |
| **Key Scripts** | Available npm/make scripts with descriptions |
| **AGENTS.md Summary** | Condensed rules, patterns, and API conventions |
| **Dependencies** | Key production and dev dependencies |
| **CI/CD** | GitHub Actions / GitLab CI workflows, deploy process |
| **Custom Commands** | Available `/commands` from `.cursor/commands/` |
| **Conventions** | Coding patterns, naming conventions, file organization |

## Built-in Templates

| Template | Description |
|----------|-------------|
| `react-vite` | React 18 + Vite + TypeScript + Tailwind |
| `nextjs-app` | Next.js App Router + TypeScript |
| `vue-vite` | Vue 3 + Vite + TypeScript + Pinia |
| `svelte-kit` | SvelteKit + TypeScript |
| `express-ts` | Express.js + TypeScript + Prisma |
| `fastapi` | FastAPI + Python 3.11 + SQLAlchemy |
| `nestjs` | NestJS + TypeScript + TypeORM |
| `go-fiber` | Go + Fiber + GORM |
| `t3-stack` | Next.js + tRPC + Prisma + Tailwind |
| `node-cli` | Node.js CLI with Commander |
| `rust-cli` | Rust CLI with Clap |
| `npm-package` | NPM package with TypeScript |
| `monorepo-nx` | NX Monorepo |

## Project Registry

Projects are tracked in `~/.cursor/project-registry.json`:

```json
{
  "projects": {
    "/path/to/project": {
      "name": "project-name",
      "lastAccessed": "2026-03-25T12:00:00Z",
      "techStack": ["node", "typescript", "react"],
      "hasCursorConfig": true,
      "hasKnowledgeCache": true
    }
  }
}
```

## Usage Examples

```bash
# Load a project (uses cache if available)
/load-project ~/code/my-app

# Load by name (from registry)
/load-project my-app

# Refresh after major changes
/refresh-project

# Deep refresh (full re-scan)
/refresh-project --deep

# See recent projects
/recent-projects

# Jump to project #2
/recent-projects 2

# Get project info
/project-info

# Get only dependency info
/project-info deps

# Create a new React project
/new-project my-new-app --template react-vite
```

## Installation

### Local development

Install from this directory in Cursor:

1. Open **Cursor Settings → Plugins**
2. Add a local plugin path pointing to this `project-manager` folder
3. Enable the plugin

Or symlink into your plugins directory:

```bash
ln -s "$(pwd)/project-manager" ~/.cursor/plugins/local/project-manager
```

## Plugin Structure

```
project-manager/
├── .cursor-plugin/
│   └── plugin.json
├── commands/
│   ├── load-project.md
│   ├── refresh-project.md
│   ├── recent-projects.md
│   ├── project-info.md
│   └── new-project.md
├── skills/
│   └── project-context/
│       ├── SKILL.md
│       └── references/
│           ├── project-templates.md
│           └── tech-stack-patterns.md
└── README.md
```

## License

MIT
