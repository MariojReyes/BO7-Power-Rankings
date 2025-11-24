# BO7 Analytics Dashboard (dev)

Prototype Shiny app that surfaces match insights from the dev Supabase table or the included sample CSV.

## Prerequisites

- R 4.3+
- Packages: `shiny`, `dplyr`, `tidyr`, `readr`, `DT`, `httr2`, `scales` (install via `install.packages`).

## Running locally

```r
renv::activate() # optional, if you prefer renv
shiny::runApp('analytics_dev')
```

By default the app reads `analytics_dev/data/sample_matches.csv`. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` to fetch live data from your dev Supabase instance via the auto-generated REST endpoint.

