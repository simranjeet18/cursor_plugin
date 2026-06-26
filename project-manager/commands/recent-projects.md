---
name: recent-projects
description: List recently accessed projects and quickly jump to any of them.
---

# Recent Projects

Manage and navigate to recently accessed projects.

## Trigger

Invoke when the user runs `/recent-projects` or asks to see, list, or switch between recent projects.

**Argument**: optional number to load, or `clear` to reset history

## Workflow

### Step 1: Load Project Registry

Read `~/.cursor/project-registry.json`. If it doesn't exist, inform the user no projects have been registered yet and suggest using `/load-project`.

### Step 2: Process Arguments

- **No argument**: Display list of recent projects
- **Number (1–9)**: Immediately load that project (shortcut)
- **`clear`**: Clear the project history after confirmation

### Step 3: Display Recent Projects

Sort projects by `lastAccessed` (most recent first) and display:

```
## Recent Projects

| # | Project       | Last Accessed      | Tech Stack                |
|---|---------------|--------------------|---------------------------|
| 1 | my-app        | Today, 2:30 PM     | Node, TypeScript, React   |
| 2 | my-api        | Yesterday, 9:15 AM | Python, FastAPI           |
| 3 | blog-platform | Mar 15, 10:00 AM   | Next.js, Tailwind, Prisma |

Enter a number to load that project, or use `/load-project <path>` for a new one.
```

### Step 4: Handle Selection

If the user provides a number or selects one:

1. Validate the number is within range
2. Check if the project path still exists
3. If exists: execute `/load-project /path/to/project`
4. If not exists: offer to remove from registry and suggest alternatives

### Step 5: Clear History (if requested)

If argument is `clear`:

1. Ask for confirmation: "This will remove all projects from your history. Continue? (y/n)"
2. If confirmed: clear the registry and confirm
3. If declined: cancel operation

## Additional Features

### Filtering by Tech Stack

If the user has many projects, support filtering:

- `/recent-projects node` — show only Node.js projects
- `/recent-projects python` — show only Python projects

### Project Health Indicators

Add indicators for each project:

- **Active** — has recent git commits (within 7 days)
- **Stale** — no activity for 30+ days
- **Missing** — path no longer exists

## Output Format

When displaying the table, include:

- Relative time formatting ("Today", "Yesterday", "Mar 15")
- Truncated tech stack if too long
- Status indicators for project health

## Registry Management

The registry is stored at `~/.cursor/project-registry.json`:

- Maximum 20 projects stored (oldest auto-removed)
- Projects automatically added when using `/load-project`
