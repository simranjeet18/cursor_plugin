# Project Templates Reference

## Built-in Templates

### 1. react-vite

**Description**: Modern React setup with Vite, TypeScript, and Tailwind CSS

**Scaffold Commands**:
```bash
npm create vite@latest $PROJECT_NAME -- --template react-ts
cd $PROJECT_NAME
npm install
npm install -D tailwindcss postcss autoprefixer @types/node
npx tailwindcss init -p
npm install -D eslint eslint-plugin-react-hooks @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

**Post-setup Files**:
- `tailwind.config.js` - Configure content paths
- `src/index.css` - Add Tailwind directives
- `.eslintrc.cjs` - ESLint configuration
- `.prettierrc` - Prettier configuration
- `vitest.config.ts` - Test configuration

---

### 2. nextjs-app

**Description**: Next.js with App Router, TypeScript, and Tailwind CSS

**Scaffold Command**:
```bash
npx create-next-app@latest $PROJECT_NAME \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"
```

---

### 3. vue-vite

**Description**: Vue 3 with Vite, TypeScript, Pinia, and Vue Router

**Scaffold Commands**:
```bash
npm create vue@latest $PROJECT_NAME
# Select: TypeScript, Vue Router, Pinia, Vitest, ESLint, Prettier
cd $PROJECT_NAME
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

### 4. svelte-kit

**Description**: SvelteKit with TypeScript and Tailwind CSS

**Scaffold Commands**:
```bash
npm create svelte@latest $PROJECT_NAME
# Select: Skeleton project, TypeScript, ESLint, Prettier, Vitest
cd $PROJECT_NAME
npm install
npx svelte-add@latest tailwindcss
npm install
```

---

### 5. express-ts

**Description**: Express.js API with TypeScript, Prisma, and testing

**Scaffold Commands**:
```bash
mkdir $PROJECT_NAME && cd $PROJECT_NAME
npm init -y
npm install express cors helmet morgan dotenv
npm install -D typescript @types/node @types/express @types/cors @types/morgan
npm install -D ts-node-dev nodemon
npm install prisma @prisma/client
npm install -D vitest supertest @types/supertest
npx tsc --init
npx prisma init
```

---

### 6. fastapi

**Description**: FastAPI with Python, SQLAlchemy, and Alembic

**Scaffold Commands**:
```bash
mkdir $PROJECT_NAME && cd $PROJECT_NAME
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy alembic python-dotenv
pip install pytest pytest-asyncio httpx
pip freeze > requirements.txt
```

---

### 7. nestjs

**Description**: NestJS with TypeScript, TypeORM, and testing

**Scaffold Commands**:
```bash
npx @nestjs/cli new $PROJECT_NAME
cd $PROJECT_NAME
npm install @nestjs/typeorm typeorm pg
npm install @nestjs/config class-validator class-transformer
```

---

### 8. go-fiber

**Description**: Go API with Fiber and GORM

**Scaffold Commands**:
```bash
mkdir $PROJECT_NAME && cd $PROJECT_NAME
go mod init github.com/username/$PROJECT_NAME
go get github.com/gofiber/fiber/v2
go get gorm.io/gorm gorm.io/driver/postgres
go get github.com/joho/godotenv
```

---

### 9. t3-stack

**Description**: Full-stack T3 Stack (Next.js + tRPC + Prisma + Tailwind)

**Scaffold Command**:
```bash
npm create t3-app@latest $PROJECT_NAME
```

---

### 10. node-cli

**Description**: Node.js CLI tool with Commander and TypeScript

**Scaffold Commands**:
```bash
mkdir $PROJECT_NAME && cd $PROJECT_NAME
npm init -y
npm install commander chalk ora inquirer
npm install -D typescript @types/node @types/inquirer
npm install -D tsup vitest
npx tsc --init
```

---

### 11. rust-cli

**Description**: Rust CLI tool with Clap

**Scaffold Commands**:
```bash
cargo new $PROJECT_NAME
cd $PROJECT_NAME
cargo add clap --features derive
cargo add anyhow thiserror
```

---

### 12. npm-package

**Description**: Publishable NPM package with TypeScript

**Scaffold Commands**:
```bash
mkdir $PROJECT_NAME && cd $PROJECT_NAME
npm init -y
npm install -D typescript tsup vitest @types/node
npx tsc --init
```

---

### 13. monorepo-nx

**Description**: NX Monorepo with TypeScript

**Scaffold Command**:
```bash
npx create-nx-workspace@latest $PROJECT_NAME --preset=ts --packageManager=pnpm
```

---

## AGENTS.md Template

All templates should include an `AGENTS.md`:

```markdown
# Project: $PROJECT_NAME

## Overview
$DESCRIPTION

## Tech Stack
$TECH_STACK_LIST

## Getting Started

\`\`\`bash
$INSTALL_COMMAND
$DEV_COMMAND
\`\`\`

## Project Structure

\`\`\`
$DIRECTORY_STRUCTURE
\`\`\`

## Key Commands

| Command | Description |
|---------|-------------|
| `$DEV_COMMAND` | Start development server |
| `$BUILD_COMMAND` | Build for production |
| `$TEST_COMMAND` | Run tests |
| `$LINT_COMMAND` | Lint code |

## Environment Variables

Copy `.env.example` to `.env` and fill in values.

## Development Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
```

## Custom Template Creation

Add a directory to `~/.cursor/project-templates/`:

```
~/.cursor/project-templates/my-template/
├── template.json
├── files/
│   ├── AGENTS.md
│   └── src/
│       └── index.ts
└── README.md
```

### template.json Schema

```json
{
  "name": "my-template",
  "description": "My custom project template",
  "category": "fullstack",
  "techStack": ["typescript", "react", "express"],
  "scaffoldCommands": [
    "npm init -y",
    "npm install react express"
  ],
  "files": {
    "AGENTS.md": "files/AGENTS.md",
    "src/index.ts": "files/src/index.ts"
  },
  "variables": {
    "AUTHOR": { "prompt": "Author name", "default": "" },
    "DESCRIPTION": { "prompt": "Project description", "default": "A new project" }
  },
  "postSetup": ["git init", "npm install"]
}
```
