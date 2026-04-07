#!/usr/bin/env python3
"""
log_transcript.py — Append a voice or typed transcript to english-transcripts.jsonl.

Usage:
    python3 log_transcript.py --source voice --text "transcript here"
    python3 log_transcript.py --source typed --text "message here"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

TRANSCRIPTS_FILE = "memory/english-transcripts.jsonl"


def main():
    parser = argparse.ArgumentParser(description="Log a transcript for English coaching.")
    parser.add_argument("--source", required=True, choices=["voice", "typed"],
                        help="Source of the transcript: 'voice' or 'typed'")
    parser.add_argument("--text", required=True, help="The transcript or message text")
    args = parser.parse_args()

    if not args.text.strip():
        print("Error: --text cannot be empty.", file=sys.stderr)
        sys.exit(1)

    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": args.source,
        "text": args.text.strip(),
    }

    os.makedirs(os.path.dirname(TRANSCRIPTS_FILE), exist_ok=True)
    with open(TRANSCRIPTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Logged ({args.source}): {args.text[:80]}{'...' if len(args.text) > 80 else ''}")


if __name__ == "__main__":
    main()
