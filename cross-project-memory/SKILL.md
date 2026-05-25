---
name: cross-project-memory
description: >-
  Cross-project shared knowledge memory. Saves and retrieves reusable insights
  (bug fixes, patterns, configurations, decisions) across different projects
  using a global knowledge base. Use when user says "remember this", "save this
  for later", "log this knowledge", or "save to shared memory". Use when starting
  work in a new project and should check prior learnings. Use when encountering
  a problem that might have been solved before in another project. Use when user
  asks "have we done this before", "check cross-project memory", or "search shared
  knowledge". Use when finishing significant work and should persist key takeaways.
---

# Cross-Project Memory

Maintains a shared knowledge base at `~/.codex/shared-memory/entries/` that spans all projects. Knowledge saved in one project is automatically searchable when working in another.

## Core Workflow

### 1. When to Query (Proactive)

**At the start of every significant task**, before writing code or making decisions:

```bash
python "<SKILL_DIR>/scripts/memory.py" search "<keyword1> <keyword2>"
```

Search with keywords derived from the current context. For example, if the user asks about Docker setup:

```bash
python "<SKILL_DIR>/scripts/memory.py" search "docker compose postgres"
```

Also use `rg` for fast full-text search when you need broader coverage:

```bash
rg -il "<keyword>" ~/.codex/shared-memory/entries/
```

**Always query when:**
- Setting up infrastructure or configurations
- Choosing between libraries or frameworks
- Encountering an error that feels familiar
- User asks "have we done X before?"
- User explicitly asks to check shared memory

### 2. When to Save

**After resolving a non-trivial problem** or when the user says "remember this", "save this", "log this":

```bash
echo "<CONTENT>" | python "<SKILL_DIR>/scripts/memory.py" save \
  --title "<Short descriptive title>" \
  --tags "<tag1>" "<tag2>" "<tag3>" \
  --category "<category>" \
  --project "<current project path>"
```

**Save-worthy moments:**
- Solved a bug with a non-obvious root cause
- Made an architectural decision with trade-offs
- Discovered a useful pattern, library, or configuration trick
- Figured out environment-specific setup steps
- Learned a lesson that would prevent future mistakes
- User explicitly asks to save something

**Do NOT save:** trivial facts, standard library usage, or things easily found in docs.

### 3. At Session/Project End

Before wrapping up significant work, silently consider: "What did I learn here that would help in another project?" If anything qualifies, save it.

### 4. Categories

Use one of these standard categories:
- `devops` - Docker, CI/CD, deployment, infrastructure
- `frontend` - React, CSS, bundling, UI patterns
- `backend` - APIs, databases, auth, server logic
- `database` - Schema design, migrations, query optimization
- `testing` - Test setup, mocking patterns, test frameworks
- `api` - API design, REST/GraphQL patterns, rate limiting
- `general` - Cross-cutting knowledge, tools, workflows

### 5. Tags

Use lowercase, concise tags. Examples: `docker`, `compose`, `postgres`, `react`, `typescript`, `auth`, `jwt`, `cors`, `nginx`, `redis`, `pytest`, `migration`, `performance`, `security`.

## Script Reference

| Command | Usage |
|---------|-------|
| `search <query>` | Search by keyword (scored by title/tags/category/body) |
| `save` | Save new entry (content via stdin) |
| `list --limit N` | List recent entries |
| `list --tag <tag>` | Filter by tag |
| `recent` | Show last 5 entries |

Always expand `<SKILL_DIR>` to the actual skill installation path when running commands. Use `rg` as a fast fallback for full-text search when the Python search misses relevant entries.

## Example Flow

```
User: "I need to set up Docker Compose for this new project"

Agent (internal):
  -> Search shared memory: python .../memory.py search "docker compose setup"
  -> Found: "Docker Compose with Postgres + Redis health checks" from project ecommerce-api
  -> Reply: "I found a relevant setup from your ecommerce-api project. Here is the pattern..."
  -> Apply the reused knowledge to the new project
```