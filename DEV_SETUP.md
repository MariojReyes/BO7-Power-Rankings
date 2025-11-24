# BO7 Dev Playground

Isolated artifacts for experimenting with Supabase, Discord ingestion, and Shiny analytics without touching production assets.

## 1. Supabase schema + seed

- File: `db/master_denorm_dev.sql`
- Run inside the Supabase SQL editor or via `psql -f db/master_denorm_dev.sql`.
- Creates lookup tables (`players`, `game_modes`, `maps`) and the denormalized `match_master` table, then loads three seed matches you can query from other tools.

## 2. Discord bot (`bot_dev/`)

### Prereqs

- Python 3.11+
- `pip install -r bot_dev/requirements.txt`
- Copy `bot_dev/env.example` to `bot_dev/.env` and fill in:
  - `DISCORD_TOKEN`: dev bot token.
  - `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`: point at the dev Supabase project seeded above.
  - Leave `DRY_RUN=true` until you are ready to persist entries.

### Run

```
cd bot_dev
python -m bot_dev.main
```

- Registers `/logmatch`, which opens dropdown-based menus mirroring the decision tree (mode → roster sizes → players → scores → submit).
- Duplicate player picks are blocked, team sizes are enforced, and submissions funnel through `SupabaseWriter` (dry-run friendly).

## 3. Analytics dashboard (`analytics_dev/`)

- Install required R packages: `install.packages(c('shiny','dplyr','tidyr','readr','DT','httr2','scales'))`.
- Launch with `shiny::runApp('analytics_dev')`.
- Reads from `analytics_dev/data/sample_matches.csv` by default. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in your R environment to stream live rows from the Supabase REST endpoint.
- Tabs:
  - Leaderboard: player-level win/loss table.
  - Mode Breakdown: average scores and win counts per mode.
  - Match Log: raw table for quick validation.

## 4. Review pipeline

- Keep all experimentation within the `*_dev` directories/files when vibecoding.
- Once satisfied, cherry-pick SQL/bot/dashboard pieces into production paths through normal PR review.

