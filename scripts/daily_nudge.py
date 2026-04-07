#!/usr/bin/env python3
"""
daily_nudge.py — Send a daily language coaching nudge via Telegram.

Picks the most frequent active error pattern that hasn't been seen in
the last 24 hours (based on last_seen date) and sends a short reminder.
Always sends, even if no messages were received that day.
"""

import json
import os
import sys
from datetime import date, timedelta

import requests

# ── Config ──────────────────────────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN"
ERRORS_FILE = "memory/english-errors.json"
CONFIG_FILE = "skills/language-coach/config.json"


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_telegram(text: str, chat_id: int) -> dict:
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=30,
    )
    return r.json()


def load_active_errors() -> list[dict]:
    if not os.path.exists(ERRORS_FILE):
        return []
    with open(ERRORS_FILE, "r", encoding="utf-8") as f:
        errors = json.load(f)
    return [e for e in errors if e.get("status") == "active"]


def pick_error(errors: list[dict]):
    """Pick active error not seen in last 24h, sorted by occurrences descending."""
    today = date.today()

    eligible = []
    for e in errors:
        try:
            last_seen = date.fromisoformat(e.get("last_seen", "2000-01-01"))
        except ValueError:
            last_seen = date(2000, 1, 1)
        # "not seen in last 24h" = last_seen is before today
        if last_seen < today:
            eligible.append(e)

    if not eligible:
        # All were seen today — fall back to highest occurrences overall
        eligible = errors

    if not eligible:
        return None

    return max(eligible, key=lambda e: e.get("occurrences", 0))


def main():
    config = load_config()
    target_lang = config.get("target_lang", "English")
    chat_id = config.get("chat_id", YOUR_CHAT_ID)

    print(f"🧠 Running daily {target_lang} nudge...")

    errors = load_active_errors()

    if not errors:
        message = f"🧠 Language coach: No active patterns tracked yet — keep talking!"
    else:
        error = pick_error(errors)
        if error:
            message = (
                f"🧠 <b>Today's {target_lang} focus:</b> {error['pattern']}\n\n"
                f"❌ <i>\"{error['example_wrong']}\"</i>\n"
                f"✅ \"{error['example_correct']}\""
            )
        else:
            message = f"🧠 Language coach: No active patterns tracked yet — keep talking!"

    result = send_telegram(message, chat_id)

    if result.get("ok"):
        print("✅ Daily nudge sent to Telegram!")
    else:
        print(f"❌ Telegram send failed: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
