#!/usr/bin/env python3
"""Cross-project shared memory manager.

Stores knowledge entries in ~/.codex/shared-memory/entries/ as Markdown files
with YAML frontmatter. Supports save, search, list, and recent operations.
"""

import argparse
import json
import os
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = Path.home() / ".codex" / "shared-memory"
ENTRIES_DIR = MEMORY_ROOT / "entries"
INDEX_FILE = MEMORY_ROOT / "index.json"


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


def cmd_save(args):
    """Save a new knowledge entry."""
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

    frontmatter = textwrap.dedent(f"""\
    ---
    date: {date_str}
    project: {project}
    tags: {json.dumps(tags)}
    category: {args.category or "general"}
    title: "{args.title}"
    ---

    """)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content)
        f.write("\n")

    # Update index
    index = load_index()
    index.insert(0, {
        "file": filename,
        "date": date_str,
        "project": project,
        "tags": tags,
        "category": args.category or "general",
        "title": args.title,
    })
    save_index(index)

    print(f"SAVED: {filepath}")
    print(f"Tags: {', '.join(tags) if tags else '(none)'}")


def cmd_search(args):
    """Search entries by keyword, tag, or full text."""
    query = args.query.lower()
    results = []

    if not ENTRIES_DIR.exists():
        print("No memory entries yet.", file=sys.stderr)
        return

    for fpath in sorted(ENTRIES_DIR.glob("*.md"), reverse=True):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        # Extract frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue

        body = text[fm_match.end():].strip()
        fm_text = fm_match.group(1)

        # Parse simple YAML-like fields
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

        # Determine relevance
        score = 0
        if query in title.lower():
            score += 10
        if any(query in t.lower() for t in tags):
            score += 5
        if query in category.lower():
            score += 3
        if query in body.lower():
            score += 1

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


def cmd_list(args):
    """List recent entries."""
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

        if tag_filter and tag_filter not in tags:
            continue

        category = re.search(r"category:\s*(\S+)", fm_text)
        category = category.group(1) if category else "general"

        count += 1
        print(f"  [{date}] {title}")
        print(f"         tags: {', '.join(tags)} | category: {category}")
        print()


def cmd_recent(args):
    """Show most recent entries (shorthand)."""
    cmd_list(argparse.Namespace(limit=args.limit, tag=None))


def main():
    parser = argparse.ArgumentParser(
        description="Cross-project shared memory manager"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # save
    p_save = sub.add_parser("save", help="Save a knowledge entry (content from stdin)")
    p_save.add_argument("--title", "-t", required=True, help="Entry title")
    p_save.add_argument("--tags", "-g", nargs="*", default=[], help="Tags (space-separated)")
    p_save.add_argument("--category", "-c", default="general", help="Category")
    p_save.add_argument("--project", "-p", help="Source project path (default: CWD)")

    # search
    p_search = sub.add_parser("search", help="Search entries")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    p_search.add_argument("--preview", type=int, default=500, help="Preview length")

    # list
    p_list = sub.add_parser("list", help="List entries")
    p_list.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    p_list.add_argument("--tag", help="Filter by tag")

    # recent
    p_recent = sub.add_parser("recent", help="Show most recent entries")
    p_recent.add_argument("--limit", "-n", type=int, default=5, help="Max results")

    args = parser.parse_args()

    if args.command == "save":
        cmd_save(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "recent":
        cmd_recent(args)


if __name__ == "__main__":
    main()
