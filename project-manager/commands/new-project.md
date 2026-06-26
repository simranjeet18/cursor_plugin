---
name: new-project
description: Create a new project from built-in or custom templates.
---

# New Project

Create a new project from a template.

## Trigger

Invoke when the user runs `/new-project` or asks to scaffold, create, or bootstrap a new project.

**Arguments**: `<project-name> [--template <template-name>] [--path <parent-dir>]`

## Workflow

### Step 1: Parse Arguments

Parse the input for:

- `project-name` — required name for the new project
- `--template <name>` — optional template to use
- `--path <dir>` — optional parent directory (defaults to current directory)

If no project name provided, prompt for it.

### Step 2: Select Template

If no template specified, present options:

```
## Select a Project Template

### Web Frontend
1. react-vite    - React 18 + Vite + TypeScript + Tailwind
2. nextjs-app    - Next.js App Router + TypeScript
3. vue-vite      - Vue 3 + Vite + TypeScript + Pinia
4. svelte-kit    - SvelteKit + TypeScript

### Backend API
5. express-ts    - Express.js + TypeScript + Prisma
6. fastapi       - FastAPI + Python 3.11 + SQLAlchemy
7. nestjs        - NestJS + TypeScript + TypeORM
8. go-fiber      - Go + Fiber + GORM

### Full Stack
9. t3-stack      - Next.js + tRPC + Prisma + Tailwind

### CLI / Library
10. node-cli     - Node.js CLI with Commander + TypeScript
11. rust-cli     - Rust CLI with Clap
12. npm-package  - NPM package with TypeScript + Vitest

### Other
13. monorepo-nx  - NX Monorepo + TypeScript
14. custom       - Define your own stack
```

See `skills/project-context/references/project-templates.md` for scaffold commands per template.

### Step 3: Gather Project Details

Based on template, ask for additional config:

```
Project Name: my-awesome-app
Template: react-vite

Additional options:
- Include ESLint + Prettier? (Y/n)
- Include testing setup (Vitest)? (Y/n)
- Include CI/CD (GitHub Actions)? (Y/n)
- Initialize Git repository? (Y/n)
- Create AGENTS.md? (Y/n)
```

### Step 4: Scaffold Project

Execute the appropriate scaffolding command based on template. Examples:

#### React + Vite

```bash
npm create vite@latest my-awesome-app -- --template react-ts
cd my-awesome-app
npm install
```

#### Next.js

```bash
npx create-next-app@latest my-awesome-app --typescript --tailwind --eslint --app --src-dir
```

#### FastAPI

```bash
mkdir my-awesome-app && cd my-awesome-app
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic
```

### Step 5: Add Standard Files

After scaffolding, add these files when requested:

#### AGENTS.md

```markdown
# Project: {project-name}

## Overview
{description based on template}

## Tech Stack
- {detected tech stack}

## Getting Started
{startup commands}

## Project Structure
{auto-generated structure}

## Key Commands
- `npm run dev` - Start development
- `npm run build` - Build for production
- `npm run test` - Run tests
```

#### README.md

Generate basic README if not created by the scaffold tool.

### Step 6: Initialize Git

If requested:

```bash
git init
git add .
git commit -m "Initial commit: {template} scaffold"
```

### Step 7: Register Project

Add to `~/.cursor/project-registry.json` for quick access later.

### Step 8: Present Summary

```
## Project Created Successfully!

**Name**: my-awesome-app
**Path**: /Users/dev/code/my-awesome-app
**Template**: react-vite

### What was set up:
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS
- ESLint + Prettier
- Vitest for testing
- AGENTS.md for Cursor

### Next Steps:
1. `cd my-awesome-app`
2. `npm run dev` to start development

Or run `/load-project my-awesome-app` to switch context.
```

## Custom Templates

Users can define custom templates in `~/.cursor/project-templates/`:

```json
{
  "name": "my-company-stack",
  "description": "Standard company project setup",
  "commands": [
    "npm create vite@latest $PROJECT_NAME -- --template react-ts",
    "cd $PROJECT_NAME && npm install"
  ],
  "files": {
    "AGENTS.md": "templates/agents.md"
  },
  "postSetup": [
    "git init"
  ]
}
```

## Error Handling

- If directory exists: offer to use different name or overwrite
- If scaffold command fails: show error and suggest manual steps
- If git init fails: continue without git, warn user
- If template not found: show available templates
