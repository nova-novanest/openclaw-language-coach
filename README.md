# openclaw-language-coach

An [OpenClaw](https://openclaw.com) skill that coaches non-native speakers by analyzing their actual messages — voice transcripts and typed text. It tracks recurring mistakes, sends weekly AI-generated lessons, and delivers daily reminders about patterns you keep getting wrong.

Built this because I wanted to actually improve my English at a professional level, not just "learn English." The difference: this watches what you *actually say* and catches the patterns you don't notice yourself.

## What it does

1. **Logs your messages** — every voice transcript and typed message gets appended to a JSONL file
2. **Tracks error patterns** — when an AI or human spots a recurring mistake, it gets added to a tracked list with wrong/correct examples
3. **Weekly lessons** — every Sunday, Claude reads your week's transcripts + tracked errors and generates a personalized lesson
4. **Daily nudges** — picks your most frequent mistake and sends a quick reminder via Telegram

## Install

Copy this repo into your OpenClaw skills directory:

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/nova-novanest/openclaw-language-coach.git language-coach
```

OpenClaw will auto-detect it from the SKILL.md frontmatter.

## Setup

1. Edit `config.json`:
   - `target_lang` — the language you're practicing (default: English)
   - `target_context` — what level you're targeting (e.g., "investor/pitch level", "casual conversation")
   - `chat_id` — your Telegram chat ID for receiving lessons/nudges

2. Set your bot token in the scripts (search for `YOUR_BOT_TOKEN` in `weekly_lesson.py` and `daily_nudge.py`)

3. Set `ANTHROPIC_API_KEY` in your environment (needed for weekly lessons)

4. Set up cron jobs:
   ```bash
   # Weekly lesson — Sundays at 7pm UTC
   openclaw cron add --name english-coach-weekly --schedule "0 19 * * 0" --task "Run the weekly language lesson: python3 skills/language-coach/scripts/weekly_lesson.py"

   # Daily nudge — every day at 7pm UTC  
   openclaw cron add --name english-coach-daily --schedule "0 19 * * *" --task "Run the daily language nudge: python3 skills/language-coach/scripts/daily_nudge.py"
   ```

## Usage

The skill integrates with your OpenClaw agent. When voice messages come in, the agent logs them automatically. You can also:

```bash
# Log a transcript manually
python3 scripts/log_transcript.py --source voice --text "transcript here"

# Add a tracked error pattern
python3 scripts/manage_errors.py add --pattern "Present tense overuse" --wrong "from that time you are not normal" --correct "since then you haven't been acting normally"

# List active errors
python3 scripts/manage_errors.py list

# Mark one as resolved
python3 scripts/manage_errors.py resolve --id present_tense_overuse
```

## How it actually works

The weekly lesson sends your real transcripts to Claude with your tracked error list. Claude spots new mistakes, checks if old patterns are still showing up, and notes any progress. It's not a generic grammar lesson — it's built from what you actually said that week.

The daily nudge just picks your most frequent active error and sends a quick wrong/right example. Takes 2 seconds to read. That's the point.

## Requirements

- Python 3.10+
- `requests` library
- Anthropic API key (for weekly lessons)
- Telegram bot token (for sending messages)
- OpenClaw (for skill integration)

## License

MIT
