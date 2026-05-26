---
name: cross-project-memory
description: >-
  Cross-project shared knowledge memory. Saves and retrieves reusable insights
  (bug fixes, patterns, configurations, decisions) across different projects
  using a global knowledge base. Auto-snapshots conversation learnings at session
  end. Indexes past Codex threads for backfill. Use when user says "remember this",
  "snapshot this project", "backfill old conversations", "save to shared memory".
  Use when starting work in a new project and should check prior learnings. Use
  when encountering a problem that might have been solved before. Use after
  generating a README to persist key architectural facts.
---

# Cross-Project Memory

Maintains a shared knowledge base at `~/.codex/shared-memory/entries/` that spans all projects. Two core capabilities:

- **Live capture**: auto-snapshot learnings at end of every conversation
- **Historical backfill**: index past Codex threads and import their knowledge

## Auto-Snapshot Protocol

**At the end of EVERY conversation**, before saying goodbye:

1. Scan the conversation for reusable knowledge
2. For each finding, run:
```bash
echo "<SUMMARY>" | python "<SKILL_DIR>/scripts/memory.py" save \
  --title "<topic>" --tags <tag1> <tag2> --category <cat> \
  --project "<cwd>" --thread-id "<thread_id>"
```

**What to snapshot:**
- Non-trivial bugs solved with their root cause
- Configuration patterns that actually worked
- Library/framework choices with the reasoning
- Environment setup steps that were tricky
- Code patterns you'd want to reuse

**What to skip:** trivial facts, standard docs, one-off typos.

**Report format:** After saving, list what was saved:
```
Shared memory updated:
  - "Docker Compose health checks" (devops)
  - "FastAPI CORS middleware pattern" (backend)
```

---

## Historical Backfill

To index knowledge from past conversations:

### Step 1: List past threads
```bash
python "<SKILL_DIR>/scripts/memory.py" threads --limit 20
```

### Step 2: Find unindexed ones
```bash
python "<SKILL_DIR>/scripts/memory.py" backfill --limit 20
```

### Step 3: For each candidate, recall what was discussed and save

The agent should:
1. Read the thread title and cwd to recall the conversation topic
2. Based on context (rollout_path, artifacts left on disk), summarize key learnings
3. Save each to shared memory with `--thread-id` to link back

```bash
echo "<RECALLED_SUMMARY>" | python "<SKILL_DIR>/scripts/memory.py" save \
  --title "..." --tags ... --thread-id "<thread_id>"
```

---

## Live Workflows

### Project Snapshot
```bash
python "<SKILL_DIR>/scripts/memory.py" snapshot --project "<path>"
```
Fill the template by analyzing the codebase, then pipe to `save`.

### README-to-Memory Pipeline
After `readme-generator` finishes: extract architecture, tech stack, gotchas into memory entries.

### On-Demand Save
```bash
echo "<CONTENT>" | python "<SKILL_DIR>/scripts/memory.py" save \
  --title "<Title>" --tags <t1> <t2> --category <cat>
```

---

## Querying

```bash
python "<SKILL_DIR>/scripts/memory.py" search "<multi word query>"
```
Supports multi-word: "docker compose" matches entries with both words.
Fallback: `rg -il "<keyword>" ~/.codex/shared-memory/entries/`

**Query when:**
- Setting up infra or configs
- Choosing libraries/frameworks
- Encountering errors that feel familiar
- Starting a new project

---

## Categories

- `devops` - Docker, CI/CD, deployment
- `frontend` - React, CSS, bundling, UI
- `backend` - APIs, databases, auth
- `database` - Schema, migrations, queries
- `testing` - Test setup, mocking
- `api` - API design, REST/GraphQL
- `general` - Cross-cutting, project snapshots

---

## Script Reference

| Command | Usage |
|---------|-------|
| `threads --limit N` | List recent Codex conversations |
| `backfill --limit N` | Find unindexed past conversations |
| `snapshot --project <p>` | Output project snapshot template |
| `save --title ... --tags ... --thread-id ...` | Save entry (content via stdin) |
| `search <multi-word query>` | Search by keywords (scored) |
| `list --limit N --tag <t>` | List / filter entries |
| `recent` | Show last 5 entries |

---

## Multi-Device Strategy

Shared memory lives at `~/.codex/shared-memory/`. To sync across devices:
1. Git-track the directory: `cd ~/.codex/shared-memory && git init && git add -A && git commit -m "memory"`
2. Push to a private repo
3. On a new device: `git clone <repo> ~/.codex/shared-memory`

This way knowledge captured on device A is queryable on device B.