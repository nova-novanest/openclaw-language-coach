#!/usr/bin/env python3
"""
weekly_lesson.py — Generate and send a weekly language lesson.

Reads the last 7 days of transcripts + active error patterns, sends them
to Claude for analysis, then delivers the lesson via Telegram Bot API.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

import requests

# ── Config ──────────────────────────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN"

CONFIG_FILE = "skills/language-coach/config.json"

def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_anthropic_key() -> str:
    # Try env first, then .env file fallback
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        env_path = "/path/to/.env"
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ANTHROPIC_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
    return key

ANTHROPIC_API_KEY = _load_anthropic_key()
TRANSCRIPTS_FILE = "memory/english-transcripts.jsonl"
ERRORS_FILE = "memory/english-errors.json"
MODEL = "claude-sonnet-4-6"


def send_telegram(text: str, chat_id: int) -> dict:
    # Telegram max message length is 4096; split if needed
    max_len = 4000
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    results = []
    for chunk in chunks:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"},
            timeout=30,
        )
        results.append(r.json())
    return results[-1] if results else {}


def load_recent_transcripts(days: int = 7) -> list[dict]:
    if not os.path.exists(TRANSCRIPTS_FILE):
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    with open(TRANSCRIPTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc
                )
                if ts >= cutoff:
                    entries.append(entry)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    return entries


def load_active_errors() -> list[dict]:
    if not os.path.exists(ERRORS_FILE):
        return []
    with open(ERRORS_FILE, "r", encoding="utf-8") as f:
        errors = json.load(f)
    return [e for e in errors if e.get("status") == "active"]


def call_claude(transcripts: list[dict], errors: list[dict], config: dict) -> str:
    if not ANTHROPIC_API_KEY:
        return "⚠️ ANTHROPIC_API_KEY not set — weekly lesson could not be generated."

    target_lang = config.get("target_lang", "English")
    target_context = config.get("target_context", "clear, professional communication")

    transcript_text = "\n".join(
        f"[{e['timestamp']} | {e['source']}] {e['text']}" for e in transcripts
    ) or "(No transcripts recorded this week)"

    error_text = "\n".join(
        f"- {e['pattern']}: \"{e['example_wrong']}\" → \"{e['example_correct']}\" (seen {e['occurrences']}x)"
        for e in errors
    ) or "(No tracked error patterns yet)"

    prompt = f"""You are a language coach analyzing transcripts of a non-native {target_lang} speaker named the user.
His goal is {target_context}.

Here are his recent messages (voice + typed):
{transcript_text}

Here are his currently tracked error patterns:
{error_text}

Produce a weekly {target_lang} lesson in this exact format:

🗓 WEEKLY {target_lang.upper()} LESSON

📌 NEW MISTAKES THIS WEEK
[List each new pattern with: what he said → better version → why in plain language]

🔁 RECURRING PATTERNS (still showing up)
[List errors that appeared again from the tracked list]

✅ PROGRESS
[Any improvements noticed compared to tracked patterns]

💡 THIS WEEK'S FOCUS
[One specific thing to practice]

Keep it practical. Use his actual sentences. No grammar jargon — plain language explanations."""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["content"][0]["text"]


def main():
    config = load_config()
    target_lang = config.get("target_lang", "English")
    chat_id = config.get("chat_id", YOUR_CHAT_ID)

    print(f"📚 Running weekly {target_lang} lesson...")

    transcripts = load_recent_transcripts(days=7)
    errors = load_active_errors()
    print(f"  Transcripts this week: {len(transcripts)}")
    print(f"  Active error patterns: {len(errors)}")

    lesson = call_claude(transcripts, errors, config)
    result = send_telegram(lesson, chat_id)

    if result.get("ok"):
        print("✅ Weekly lesson sent to Telegram!")
    else:
        print(f"❌ Telegram send failed: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
