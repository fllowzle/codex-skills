#!/usr/bin/env python3
"""Cross-project shared memory manager.

Stores knowledge entries in ~/.codex/shared-memory/entries/ as Markdown files
with YAML frontmatter. Supports save, search, list, recent, snapshot, threads,
and backfill operations.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import textwrap
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = Path.home() / ".codex" / "shared-memory"
ENTRIES_DIR = MEMORY_ROOT / "entries"
INDEX_FILE = MEMORY_ROOT / "index.json"
CODEX_STATE_DB = Path.home() / ".codex" / "state_5.sqlite"


def ensure_dirs():
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)


def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_index(entries):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


# 鈹€鈹€ Save 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def cmd_save(args):
    ensure_dirs()
    content = sys.stdin.read().strip()
    if not content:
        print("ERROR: No content provided via stdin", file=sys.stderr)
        sys.exit(1)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d-%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:60]
    filename = f"{timestamp}-{slug}.md"
    filepath = ENTRIES_DIR / filename

    tags = args.tags if args.tags else []
    project = args.project or os.getcwd()
    thread_id = args.thread_id or ""

    frontmatter = textwrap.dedent(f"""\
    ---
    date: {date_str}
    project: {project}
    tags: {json.dumps(tags)}
    category: {args.category or "general"}
    title: "{args.title}"
    {f'thread_id: "{thread_id}"' if thread_id else ""}
    ---

    """)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content)
        f.write("\n")

    index = load_index()
    index.insert(0, {
        "file": filename,
        "date": date_str,
        "project": project,
        "tags": tags,
        "category": args.category or "general",
        "title": args.title,
        "thread_id": thread_id,
    })
    save_index(index)

    print(f"SAVED: {filepath}")
    print(f"Tags: {', '.join(tags) if tags else '(none)'}")


# 鈹€鈹€ Search 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def cmd_search(args):
    query = args.query.lower()
    words = query.split()
    results = []

    if not ENTRIES_DIR.exists():
        print("No memory entries yet.", file=sys.stderr)
        return

    for fpath in sorted(ENTRIES_DIR.glob("*.md"), reverse=True):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue

        body = text[fm_match.end():].strip()
        fm_text = fm_match.group(1)

        title = re.search(r'title:\s*"(.*?)"', fm_text)
        title = title.group(1) if title else fpath.stem
        date = re.search(r"date:\s*(\S+)", fm_text)
        date = date.group(1) if date else "unknown"
        project = re.search(r"project:\s*(\S+)", fm_text)
        project = project.group(1) if project else "unknown"
        tags_str = re.search(r"tags:\s*(\[.*?\])", fm_text)
        tags = json.loads(tags_str.group(1)) if tags_str else []
        category = re.search(r"category:\s*(\S+)", fm_text)
        category = category.group(1) if category else "general"

        # Multi-word scoring: any word matches = score
        score = 0
        title_l = title.lower()
        body_l = body.lower()
        for w in words:
            if w in title_l:
                score += 10
            if any(w in t.lower() for t in tags):
                score += 5
            if w in category.lower():
                score += 3
            if w in body_l:
                score += 1
        # Bonus for full phrase match
        if query in title_l:
            score += 15
        if query in body_l:
            score += 3

        if score > 0:
            results.append({
                "file": str(fpath),
                "title": title,
                "date": date,
                "project": project,
                "tags": tags,
                "category": category,
                "body": body[:args.preview or 500],
                "score": score,
            })

    results.sort(key=lambda r: r["score"], reverse=True)

    if not results:
        print(f"No results for: {args.query}")
        return

    print(f"\n{'='*60}")
    print(f"  Found {len(results)} result(s) for: {args.query}")
    print(f"{'='*60}\n")

    for i, r in enumerate(results[:args.limit or 20], 1):
        print(f"--- Result {i} (score: {r['score']}) ---")
        print(f"  Title:    {r['title']}")
        print(f"  Date:     {r['date']}")
        print(f"  Project:  {r['project']}")
        print(f"  Tags:     {', '.join(r['tags'])}")
        print(f"  Category: {r['category']}")
        print(f"  Preview:  {r['body'][:200]}...")
        print()


# 鈹€鈹€ List / Recent 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def cmd_list(args):
    if not ENTRIES_DIR.exists():
        print("No memory entries yet.")
        return

    files = sorted(ENTRIES_DIR.glob("*.md"), reverse=True)
    limit = args.limit or 10
    tag_filter = args.tag

    count = 0
    print(f"\n{'='*60}")
    print(f"  Recent Shared Memory Entries")
    print(f"{'='*60}\n")

    for fpath in files:
        if count >= limit:
            break

        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue

        fm_text = fm_match.group(1)
        title = re.search(r'title:\s*"(.*?)"', fm_text)
        title = title.group(1) if title else fpath.stem
        date = re.search(r"date:\s*(\S+)", fm_text)
        date = date.group(1) if date else "unknown"
        tags_str = re.search(r"tags:\s*(\[.*?\])", fm_text)
        tags = json.loads(tags_str.group(1)) if tags_str else []
        thread_id = re.search(r'thread_id:\s*"(\S+)"', fm_text)
        thread_id = thread_id.group(1) if thread_id else ""

        if tag_filter and tag_filter not in tags:
            continue

        category = re.search(r"category:\s*(\S+)", fm_text)
        category = category.group(1) if category else "general"

        count += 1
        tid = f" [thread:{thread_id[:8]}...]" if thread_id else ""
        print(f"  [{date}] {title}{tid}")
        print(f"         tags: {', '.join(tags)} | category: {category}")
        print()


def cmd_recent(args):
    cmd_list(argparse.Namespace(limit=args.limit, tag=None))


# 鈹€鈹€ Snapshot 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def cmd_snapshot(args):
    project_path = args.project or os.getcwd()
    project_name = os.path.basename(project_path.rstrip("/\\"))

    template = textwrap.dedent(f"""\
    ## Project Snapshot: {project_name}

    ### Tech Stack
    - (list languages, frameworks, databases, infrastructure)

    ### Architecture
    - (high-level architecture pattern: monolith, microservices, serverless, etc.)
    - (key architectural decisions)

    ### Entry Points
    - (main entry files, API endpoints, CLI commands)

    ### Key Dependencies
    - (critical libraries and why they were chosen)

    ### Environment / Setup Notes
    - (env vars, config files, ports, services needed)

    ### Gotchas & Lessons Learned
    - (non-obvious pitfalls, workarounds, things that broke)

    ### Project-Specific Patterns
    - (conventions, design patterns, naming rules used in this project)
    """)

    print(template)


# 鈹€鈹€ Threads (list past conversations) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def cmd_threads(args):
    """List recent Codex conversation threads from the SQLite database."""
    if not CODEX_STATE_DB.exists():
        print("Codex state database not found.", file=sys.stderr)
        return

    try:
        conn = sqlite3.connect(str(CODEX_STATE_DB))
        limit = args.limit or 20
        rows = conn.execute(
            "SELECT id, title, cwd, created_at, rollout_path FROM threads "
            "ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
    except Exception as e:
        print(f"Error reading Codex database: {e}", file=sys.stderr)
        return

    if not rows:
        print("No conversation threads found.")
        return

    print(f"\n{'='*60}")
    print(f"  Recent Codex Conversations ({len(rows)} threads)")
    print(f"{'='*60}\n")

    for row in rows:
        thread_id, title, cwd, created_at, rollout_path = row
        ts = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M") if created_at else "?"
        tid_short = thread_id[:12] if thread_id else "?"
        title = title or "(no title)"
        # truncate title for display
        display_title = title[:60] + ("..." if len(title) > 60 else "")
        print(f"  [{ts}] {display_title}")
        print(f"         id:{tid_short}  cwd:{cwd or '?'}")
        if args.verbose:
            print(f"         rollout:{rollout_path or '?'}")
        print()


# 鈹€鈹€ Backfill (import old conversations into memory) 鈹€鈹€鈹€鈹€

def cmd_backfill(args):
    """Output a list of past conversations for the agent to review and save."""
    
    # First, list threads
    if not CODEX_STATE_DB.exists():
        print("Codex state database not found.", file=sys.stderr)
        return

    try:
        conn = sqlite3.connect(str(CODEX_STATE_DB))
        limit = args.limit or 20
        rows = conn.execute(
            "SELECT id, title, cwd, created_at, rollout_path FROM threads "
            "ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return

    if not rows:
        print("No conversations to backfill.")
        return

    # Check which threads are already in shared memory
    index = load_index()
    indexed_ids = {e.get("thread_id", "") for e in index}

    new_count = 0
    for row in rows:
        thread_id, title, cwd, created_at, rollout_path = row
        if thread_id in indexed_ids:
            continue
        new_count += 1
        ts = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d") if created_at else "?"
        title = title or "(no title)"
        print(f"BACKFILL_CANDIDATE: id={thread_id} date={ts} title={title} cwd={cwd or '?'}")

    if new_count == 0:
        print("All recent conversations already indexed in shared memory.")
    else:
        print(f"\n{new_count} conversations not yet in shared memory.")
        print("The agent should review each candidate and save notable ones via:")
        print("  echo '<summary>' | python memory.py save --title '...' --tags ... --thread-id <id>")


# 鈹€鈹€ Main 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def main():
    parser = argparse.ArgumentParser(
        description="Cross-project shared memory manager"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Save a knowledge entry (content from stdin)")
    p_save.add_argument("--title", "-t", required=True, help="Entry title")
    p_save.add_argument("--tags", "-g", nargs="*", default=[], help="Tags")
    p_save.add_argument("--category", "-c", default="general", help="Category")
    p_save.add_argument("--project", "-p", help="Source project path")
    p_save.add_argument("--thread-id", help="Codex thread ID this came from")

    p_search = sub.add_parser("search", help="Search entries (supports multi-word)")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    p_search.add_argument("--preview", type=int, default=500, help="Preview length")

    p_list = sub.add_parser("list", help="List entries")
    p_list.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    p_list.add_argument("--tag", help="Filter by tag")

    p_recent = sub.add_parser("recent", help="Show most recent entries")
    p_recent.add_argument("--limit", "-n", type=int, default=5, help="Max results")

    p_snapshot = sub.add_parser("snapshot", help="Output project snapshot template")
    p_snapshot.add_argument("--project", "-p", help="Project path")

    p_threads = sub.add_parser("threads", help="List recent Codex conversation threads")
    p_threads.add_argument("--limit", "-n", type=int, default=20, help="Max threads")
    p_threads.add_argument("--verbose", "-v", action="store_true", help="Show rollout paths")

    p_backfill = sub.add_parser("backfill", help="Find past conversations not yet in shared memory")
    p_backfill.add_argument("--limit", "-n", type=int, default=20, help="Max threads to check")

    args = parser.parse_args()

    if args.command == "save":
        cmd_save(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "recent":
        cmd_recent(args)
    elif args.command == "snapshot":
        cmd_snapshot(args)
    elif args.command == "threads":
        cmd_threads(args)
    elif args.command == "backfill":
        cmd_backfill(args)


if __name__ == "__main__":
    main()