---
name: cross-project-memory
description: >-
  Cross-project shared knowledge memory. Saves and retrieves reusable insights
  (bug fixes, patterns, configurations, decisions) across different projects
  using a global knowledge base. Use when user says "remember this", "save this
  for later", "snapshot this project", "log this knowledge", or "save to shared
  memory". Use when starting work in a new project and should check prior
  learnings. Use when encountering a problem that might have been solved before
  in another project. Use when user asks "have we done this before", "check
  cross-project memory", or "search shared knowledge". Use after generating a
  README or project overview to persist key architectural facts.
---

# Cross-Project Memory

Maintains a shared knowledge base at `~/.codex/shared-memory/entries/` that spans all projects. Knowledge saved in one project is automatically searchable when working in another.

## Core Workflow

### 1. Project Snapshot (New!)

Capture the essence of a project so other projects can benefit from it. Triggered by:
- User says "snapshot this project", "save project overview", "capture project context"
- After `readme-generator` finishes generating a README
- When wrapping up significant work on a project

**Two-step process:**

Step A - Generate the template:
```bash
python "<SKILL_DIR>/scripts/memory.py" snapshot --project "<project-path>"
```

Step B - Fill in the template by analyzing the project:
1. Read existing README.md, package.json, requirements.txt, docker-compose.yml, etc.
2. Identify tech stack, architecture pattern, entry points, key dependencies
3. Fill each section with concrete facts (not generic descriptions)
4. Pipe the completed content to save:

```bash
python "<SKILL_DIR>/scripts/memory.py" snapshot --project "<path>" | \
  (echo "<FILLED_CONTENT>" | python "<SKILL_DIR>/scripts/memory.py" save \
    --title "Project Snapshot: <project-name>" \
    --tags "<lang>" "<framework>" "<db>" project-snapshot \
    --category "general")
```

**Snapshot template sections:**
- Tech Stack - languages, frameworks, databases, infrastructure
- Architecture - high-level pattern, key architectural decisions
- Entry Points - main files, API endpoints, CLI commands
- Key Dependencies - critical libraries and why chosen
- Environment / Setup Notes - env vars, config, ports, services
- Gotchas & Lessons Learned - pitfalls, workarounds
- Project-Specific Patterns - conventions, naming rules

### 2. README + Memory Pipeline

When the `readme-generator` skill is used on a project:

1. `readme-generator` produces a comprehensive README.md
2. **Immediately after**, distill the README into shared memory entries:
   - Architecture facts -> memory entry tagged `architecture`
   - Tech stack choices -> memory entry tagged `tech-stack`
   - Setup gotchas -> memory entry tagged `gotchas`
   - Key dependencies -> memory entry tagged `dependencies`

This ensures that when you move to another project, the agent can search shared memory and find relevant prior art.

### 3. When to Query (Proactive)

**At the start of every significant task**, before writing code or making decisions:

```bash
python "<SKILL_DIR>/scripts/memory.py" search "<keyword1> <keyword2>"
```

Also use `rg` for fast full-text:
```bash
rg -il "<keyword>" ~/.codex/shared-memory/entries/
```

**Always query when:**
- Setting up infrastructure or configurations
- Choosing between libraries or frameworks
- Encountering an error that feels familiar
- Starting work in a new project (search for project snapshots + tech keywords)
- User asks "have we done X before?"

### 4. When to Save

**After resolving a non-trivial problem** or when the user says "remember this":

```bash
echo "<CONTENT>" | python "<SKILL_DIR>/scripts/memory.py" save \
  --title "<Short descriptive title>" \
  --tags "<tag1>" "<tag2>" \
  --category "<category>" \
  --project "<current project path>"
```

**Save-worthy moments:**
- Solved a bug with a non-obvious root cause
- Made an architectural decision with trade-offs
- Discovered a useful pattern, library, or config trick
- Figured out environment-specific setup steps
- Generated a README or project overview (auto-trigger snapshot)
- User explicitly asks to save something

**Do NOT save:** trivial facts, standard library usage, or things easily found in docs.

### 5. Categories

- `devops` - Docker, CI/CD, deployment, infrastructure
- `frontend` - React, CSS, bundling, UI patterns
- `backend` - APIs, databases, auth, server logic
- `database` - Schema design, migrations, query optimization
- `testing` - Test setup, mocking patterns, test frameworks
- `api` - API design, REST/GraphQL patterns
- `general` - Cross-cutting knowledge, project snapshots

### 6. Tags

Use lowercase, concise tags. Always include `project-snapshot` for project overview entries. Examples: `docker`, `compose`, `postgres`, `react`, `typescript`, `auth`, `jwt`, `cors`, `nginx`, `redis`, `pytest`, `migration`, `performance`, `security`, `project-snapshot`.

## Script Reference

| Command | Usage |
|---------|-------|
| `snapshot --project <path>` | Output project snapshot template to stdout |
| `save` | Save new entry (content via stdin) |
| `search <query>` | Search by keyword (scored) |
| `list --limit N` | List recent entries |
| `list --tag <tag>` | Filter by tag |
| `recent` | Show last 5 entries |

## Example: Full README-to-Memory Pipeline

```
User: "Generate a README for this project"

Agent:
  1. readme-generator analyzes repo -> produces README.md
  2. Agent thinks: "Let me snapshot this into shared memory"
  3. Runs: python memory.py snapshot -> gets template
  4. Fills template from README + codebase analysis
  5. Saves to shared memory with tags: python, fastapi, postgres, project-snapshot
  6. Confirms: "Saved project snapshot to shared memory (6 tags)"

Later, in a different project:
  User: "Set up FastAPI with Postgres"
  Agent: searches shared memory -> finds the prior project's snapshot
  Agent: "Your previous project used FastAPI + asyncpg + Alembic. Reuse that pattern?"
```