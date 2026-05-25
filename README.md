# Codex Skills

Personal collection of Codex agent skills.

---

## Skills

### cross-project-memory

Cross-project shared knowledge memory. Saves and retrieves reusable insights (bug fixes, patterns, configurations, decisions) across different projects using a global knowledge base.

#### Install

```bash
npx skills add fllowzle/codex-skills@cross-project-memory -g -y
```

Then restart Codex (or open a new conversation) to load the skill.

#### How It Works

```
Project A                          Project B
┌─────────────────┐                ┌─────────────────┐
│ Solve tricky    │                │ Start new task  │
│ Docker setup    │                │ "Set up Docker" │
│                 │                │                 │
│  "remember      │    Shared      │  Agent auto-    │
│   this"   ──────┼──► Memory  ◄──┼── searches      │
│                 │   ~/.codex/    │   memory.py      │
│                 │   shared-      │   search         │
│                 │   memory/      │   "docker"       │
│                 │                │                 │
│                 │                │  Finds prior    │
│                 │                │  solution ──────► Applies it!   │
└─────────────────┘                └─────────────────┘
```

#### Usage

| Action | How to trigger |
|--------|---------------|
| **Save knowledge** | Say "remember this", "save this to shared memory", "log this" |
| **Search memory** | Say "check shared memory for X", "have we done X before?" |
| **Auto-retrieval** | Agent automatically searches when setting up infra, choosing libs, or hitting errors |

#### Commands (manual)

```bash
# Save an entry
echo "your markdown content" | python ~/.codex/skills/cross-project-memory/scripts/memory.py save \
  --title "Title" --tags tag1 tag2 --category devops

# Search
python ~/.codex/skills/cross-project-memory/scripts/memory.py search "keyword"

# List recent
python ~/.codex/skills/cross-project-memory/scripts/memory.py recent
```