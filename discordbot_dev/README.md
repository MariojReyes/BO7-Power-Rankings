# BO7 Discord Bot (dev)

Interactive slash-command bot for logging private match results straight into the Supabase dev schema.

## Setup

1. `cd bot_dev`
2. `python -m venv .venv && source .venv/Scripts/activate` (PowerShell: `.venv\\Scripts\\Activate.ps1`)
3. `pip install -r requirements.txt`
4. Copy `env.example` to `.env` and fill in your dev tokens (keep `DRY_RUN=true` until ready).

## Running

```bash
python -m bot_dev.main
```

The bot registers a `/logmatch` command. The command launches dropdown-driven menus that mirror the match setup prompts, prevents duplicate player selections, and submits a denormalized payload to Supabase via the helper client. Leave `DRY_RUN=true` to capture payloads without writing to the database.

