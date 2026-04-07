#!/usr/bin/env python3
"""
manage_errors.py — Manage tracked English error patterns.

Usage:
    python3 manage_errors.py add --pattern "..." --wrong "..." --correct "..."
    python3 manage_errors.py list
    python3 manage_errors.py bump --id error_id
    python3 manage_errors.py resolve --id error_id
    python3 manage_errors.py active-count
"""

import argparse
import json
import os
import re
import sys
from datetime import date

ERRORS_FILE = "memory/english-errors.json"


def load_errors():
    if not os.path.exists(ERRORS_FILE):
        return []
    with open(ERRORS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_errors(errors):
    os.makedirs(os.path.dirname(ERRORS_FILE), exist_ok=True)
    with open(ERRORS_FILE, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)


def make_id(pattern: str) -> str:
    """Generate a slug-style ID from a pattern string."""
    slug = re.sub(r"[^a-z0-9]+", "_", pattern.lower()).strip("_")
    return slug[:50]


def ensure_unique_id(base_id: str, errors: list) -> str:
    existing = {e["id"] for e in errors}
    if base_id not in existing:
        return base_id
    i = 2
    while f"{base_id}_{i}" in existing:
        i += 1
    return f"{base_id}_{i}"


def cmd_add(args):
    errors = load_errors()
    base_id = make_id(args.pattern)
    error_id = ensure_unique_id(base_id, errors)
    today = date.today().isoformat()

    new_error = {
        "id": error_id,
        "pattern": args.pattern,
        "example_wrong": args.wrong,
        "example_correct": args.correct,
        "first_seen": today,
        "last_seen": today,
        "occurrences": 1,
        "status": "active",
        "resolved_date": None,
    }
    errors.append(new_error)
    save_errors(errors)
    print(f"✅ Added error pattern: [{error_id}] {args.pattern}")


def cmd_list(args):
    errors = load_errors()
    active = [e for e in errors if e["status"] == "active"]
    if not active:
        print("No active error patterns tracked.")
        return
    print(f"📋 Active error patterns ({len(active)}):\n")
    for e in active:
        print(f"  [{e['id']}] {e['pattern']}")
        print(f"     ❌ \"{e['example_wrong']}\"")
        print(f"     ✅ \"{e['example_correct']}\"")
        print(f"     Occurrences: {e['occurrences']} | Last seen: {e['last_seen']}")
        print()


def cmd_bump(args):
    errors = load_errors()
    today = date.today().isoformat()
    for e in errors:
        if e["id"] == args.id:
            e["occurrences"] += 1
            e["last_seen"] = today
            save_errors(errors)
            print(f"✅ Bumped [{args.id}] — occurrences: {e['occurrences']}, last_seen: {today}")
            return
    print(f"❌ Error ID not found: {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_resolve(args):
    errors = load_errors()
    today = date.today().isoformat()
    for e in errors:
        if e["id"] == args.id:
            e["status"] = "resolved"
            e["resolved_date"] = today
            save_errors(errors)
            print(f"✅ Resolved [{args.id}]")
            return
    print(f"❌ Error ID not found: {args.id}", file=sys.stderr)
    sys.exit(1)


def cmd_active_count(args):
    errors = load_errors()
    count = sum(1 for e in errors if e["status"] == "active")
    print(count)


def main():
    parser = argparse.ArgumentParser(description="Manage English error patterns.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add a new error pattern")
    p_add.add_argument("--pattern", required=True, help="Description of the pattern")
    p_add.add_argument("--wrong", required=True, help="Example of the wrong usage")
    p_add.add_argument("--correct", required=True, help="Corrected version")

    # list
    subparsers.add_parser("list", help="List active error patterns")

    # bump
    p_bump = subparsers.add_parser("bump", help="Increment occurrences for an error")
    p_bump.add_argument("--id", required=True, help="Error ID to bump")

    # resolve
    p_resolve = subparsers.add_parser("resolve", help="Mark an error as resolved")
    p_resolve.add_argument("--id", required=True, help="Error ID to resolve")

    # active-count
    subparsers.add_parser("active-count", help="Print count of active errors")

    args = parser.parse_args()

    dispatch = {
        "add": cmd_add,
        "list": cmd_list,
        "bump": cmd_bump,
        "resolve": cmd_resolve,
        "active-count": cmd_active_count,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
