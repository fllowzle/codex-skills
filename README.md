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

---

#### How It Works

```
Project A                           Project B
+------------------+                +------------------+
| Solve tricky     |                | Start new task   |
| Docker setup     |                | "Set up Docker"  |
|                  |                |                  |
|  "remember       |    Shared      |  Agent auto-     |
|   this"   -------+--> Memory  <---+-- searches       |
|                  |   ~/.codex/    |   memory.py      |
|                  |   shared-      |   search         |
|                  |   memory/      |   "docker"       |
|                  |                |                  |
|                  |                |  Finds prior     |
|                  |                |  solution ------> Applies it!   |
+------------------+                +------------------+
```

#### Core Features

| Feature | How it works |
|---------|-------------|
| **Auto-Snapshot** | At end of every conversation, agent auto-saves reusable knowledge |
| **Thread Backfill** | Indexes past Codex conversations from SQLite (`state_5.sqlite`) |
| **Project Snapshot** | Captures tech stack, architecture, gotchas, and patterns per project |
| **README Pipeline** | After `readme-generator` runs, auto-distills key facts into memory |
| **Multi-Word Search** | `memory.py search "docker compose"` matches entries with both words |
| **Multi-Device Sync** | See instructions below |

#### Usage

| Action | How to trigger |
|--------|---------------|
| **Save knowledge** | Say "remember this", "save this to shared memory", "log this" |
| **Search memory** | Say "check shared memory for X", "have we done X before?" |
| **Backfill history** | Say "backfill old conversations", "index my past threads" |
| **Snapshot project** | Say "snapshot this project", "save project overview" |
| **Auto-retrieval** | Agent automatically searches when setting up infra, choosing libs, or hitting errors |

#### Commands Reference

```bash
# ── Save ──
echo "your markdown" | python ~/.codex/skills/cross-project-memory/scripts/memory.py save \
  --title "Title" --tags tag1 tag2 --category devops --thread-id "optional"

# ── Search (multi-word) ──
python ~/.codex/skills/cross-project-memory/scripts/memory.py search "docker compose postgres"

# ── List / Recent ──
python ~/.codex/skills/cross-project-memory/scripts/memory.py recent
python ~/.codex/skills/cross-project-memory/scripts/memory.py list --limit 20 --tag docker

# ── Thread Indexing ──
python ~/.codex/skills/cross-project-memory/scripts/memory.py threads --limit 20
python ~/.codex/skills/cross-project-memory/scripts/memory.py backfill --limit 50

# ── Project Snapshot ──
python ~/.codex/skills/cross-project-memory/scripts/memory.py snapshot --project /path/to/project
```

---

## Cross-Platform / Multi-Device Sync

Shared memory lives at `~/.codex/shared-memory/`. To sync knowledge across Windows, macOS, and Linux devices:

### Option A: Git + Private Repo (Recommended)

**On Device 1 (source):**
```bash
cd ~/.codex/shared-memory
git init
git add -A
git commit -m "Initial shared memory"
git branch -M main
git remote add origin https://github.com/YOU/private-shared-memory.git
git push -u origin main
```

**On Device 2 (new device):**
```bash
# Clone into the shared-memory location
rm -rf ~/.codex/shared-memory
git clone https://github.com/YOU/private-shared-memory.git ~/.codex/shared-memory
```

**Daily sync (both devices):**
```bash
cd ~/.codex/shared-memory
git pull origin main   # pull before working
# ... agent saves entries during conversation ...
git add -A && git commit -m "sync $(date +%Y-%m-%d)" && git push
```

### Option B: Cloud Sync (Dropbox / OneDrive / iCloud)

```bash
# On Device 1 - move memory to cloud folder
mv ~/.codex/shared-memory ~/Dropbox/codex-shared-memory

# Create symlink (macOS/Linux)
ln -s ~/Dropbox/codex-shared-memory ~/.codex/shared-memory

# Create symlink (Windows - admin PowerShell)
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.codex\shared-memory" -Target "$env:USERPROFILE\Dropbox\codex-shared-memory"

# Repeat on Device 2 - same symlink
```

### Option C: Periodic Export / Import

```bash
# Export (Device 1)
tar -czf shared-memory-backup.tar.gz ~/.codex/shared-memory

# Transfer via USB / email / cloud
# Import (Device 2)
tar -xzf shared-memory-backup.tar.gz -C ~/.codex/
```

### What Gets Synced

| Path | Content |
|------|---------|
| `entries/*.md` | Knowledge entries (Markdown + YAML frontmatter) |
| `index.json` | Search index (auto-rebuilt if missing) |

The `entries/` directory is plain text — no database, no binary format. Just Markdown files that work everywhere.

### Automated Sync

For Git-based sync, add this to your skill's `SKILL.md` or create a reminder:

> "After saving entries to shared memory, run: `cd ~/.codex/shared-memory && git add -A && git commit -m 'auto-sync' && git push`"

The `cross-project-memory` skill's auto-snapshot protocol will remind the agent to sync after saving.