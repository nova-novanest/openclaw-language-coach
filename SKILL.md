---
name: language-coach
description: >-
  Personal language coaching skill for non-native speakers. Analyzes voice
  transcripts and typed messages to identify recurring grammar and language
  mistakes. Sends personalized weekly lessons and daily nudges based on real
  mistakes the user made. Supports any target language via config.json. Use
  when logging a voice transcript for language analysis, running a weekly
  lesson, sending a daily language nudge, tracking or resolving error patterns,
  or when the user asks for language training exercises.
---

# Language Coach

A personal language improvement system for the user — tracks real mistakes from voice and typed messages, generates weekly AI-powered lessons, and sends daily reminders about active patterns.

Target language and context are configured in `config.json` (default: English at investor/pitch level).

---

## Configuration

Edit `skills/language-coach/config.json` to change the target language:

```json
{
  "target_lang": "English",
  "target_context": "investor/pitch level — clear, professional, persuasive",
  "chat_id": YOUR_CHAT_ID
}
```

---

## Logging Transcripts

Every voice message and typed message should be logged for analysis:

```bash
# After a voice transcription:
python3 skills/language-coach/scripts/log_transcript.py --source voice --text "transcript here"

# After a typed message:
python3 skills/language-coach/scripts/log_transcript.py --source typed --text "message here"
```

Logs are stored in: `memory/english-transcripts.jsonl`

Each entry:
```json
{"timestamp": "2026-04-01T12:30:00Z", "source": "voice", "text": "..."}
```

---

## Managing Error Patterns

Nova (or Hovo) tracks recurring mistakes in `memory/english-errors.json`.

```bash
# Add a new tracked error:
python3 skills/language-coach/scripts/manage_errors.py add \
  --pattern "Present tense overuse" \
  --wrong "from that time you are not normal" \
  --correct "since then you haven't been acting normally"

# List all active errors:
python3 skills/language-coach/scripts/manage_errors.py list

# Increment occurrences when a pattern reappears:
python3 skills/language-coach/scripts/manage_errors.py bump --id present_tense_overuse

# Mark a pattern as resolved when the user stops making the mistake:
python3 skills/language-coach/scripts/manage_errors.py resolve --id present_tense_overuse

# Count active errors (for cron/automation):
python3 skills/language-coach/scripts/manage_errors.py active-count
```

---

## Weekly Lesson (Automated — Sundays 20:00 Barcelona)

The weekly lesson script reads the last 7 days of transcripts + active errors, sends them to Claude, and delivers a formatted lesson to the user's Telegram.

```bash
python3 skills/language-coach/scripts/weekly_lesson.py
```

Requires: `ANTHROPIC_API_KEY` environment variable.

The lesson format:
- 📌 New mistakes spotted this week
- 🔁 Recurring patterns still showing up
- ✅ Progress vs. tracked patterns
- 💡 One focused thing to practice

---

## Daily Nudge (Automated — Every Day 20:00 Barcelona)

Picks the most-occurring active error pattern and sends a short reminder. Always sends even if no messages were received that day:

```bash
python3 skills/language-coach/scripts/daily_nudge.py
```

Example output:
> 🧠 **Today's English focus:** Present tense overuse
> ❌ "from that time you are not normal"
> ✅ "since then you haven't been acting normally"

---

## On-Demand Training Mode

When Hovo says **"make me training"** or **"give me exercises"**, Nova should:

1. Load config: `cat skills/language-coach/config.json`
2. Run: `python3 skills/language-coach/scripts/manage_errors.py list`
3. Pick 3–5 active error patterns from the output
4. Call Claude with this prompt:

```
The user is practicing {target_lang}. His goal is {target_context}.

Here are his active error patterns:
{errors}

Generate 3-5 short practice exercises targeting these patterns. Each exercise:
- One sentence to rewrite (wrong version)
- A hint (one word about what's wrong)
- The correct version (hidden below — "Answer: ...")

Keep it practical and brief. Use realistic business/startup contexts.
```

No scripts needed — just generate and send right in the chat.

---

## Data Files

| File | Purpose |
|------|---------|
| `memory/english-transcripts.jsonl` | Running log of all voice/typed messages |
| `memory/english-errors.json` | Tracked error patterns with status |

---

## Notes

- `ANTHROPIC_API_KEY` must be set in environment for weekly lessons to work
- Telegram Bot Token is hardcoded in the scripts (bot: `8120149172:AAE0Mj...`)
- Cron jobs: `english-coach-weekly` (Sun 19:00 UTC) + `english-coach-daily` (daily 19:00 UTC)
