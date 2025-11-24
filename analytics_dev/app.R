library(shiny)
library(dplyr)
library(tidyr)
library(readr)
library(DT)
library(httr2)

load_matches <- function() {
  supabase_url <- Sys.getenv("SUPABASE_URL")
  supabase_key <- Sys.getenv("SUPABASE_ANON_KEY")
  if (nzchar(supabase_url) && nzchar(supabase_key)) {
    req <- request(file.path(supabase_url, "rest/v1/match_master")) |>
      req_url_query(select = "*") |>
      req_headers(Authorization = paste("Bearer", supabase_key), apikey = supabase_key)
    resp <- req_perform(req)
    return(resp |>
      resp_body_json(simplifyVector = TRUE) |>
      as_tibble())
  }
  read_csv("analytics_dev/data/sample_matches.csv", show_col_types = FALSE)
}

matches_raw <- load_matches()

extract_team <- function(df, prefix, team_label) {
  name_cols <- paste0(prefix, "_player", 1:4, "_name")
  df |>
    select(entry_id, by_who, mode, map, guild_score, jsoc_score, all_of(name_cols)) |>
    pivot_longer(cols = all_of(name_cols), values_to = "player_name") |>
    filter(!is.na(player_name)) |>
    mutate(
      team = team_label,
      win = case_when(
        team_label == "Guild" ~ guild_score > jsoc_score,
        team_label == "JSOC" ~ jsoc_score > guild_score,
        TRUE ~ NA
      )
    ) |>
    select(entry_id, player_name, team, win, mode, map)
}

player_rows <- bind_rows(
  extract_team(matches_raw, "guild", "Guild"),
  extract_team(matches_raw, "jsoc", "JSOC")
)

leaderboard <- player_rows |>
  group_by(player_name) |>
  summarise(
    matches = n(),
    wins = sum(win, na.rm = TRUE),
    losses = matches - wins,
    win_rate = scales::percent(wins / matches)
  ) |>
  arrange(desc(wins))

mode_summary <- matches_raw |>
  group_by(mode) |>
  summarise(
    matches = n(),
    avg_guild = mean(guild_score, na.rm = TRUE),
    avg_jsoc = mean(jsoc_score, na.rm = TRUE),
    guild_wins = sum(guild_score > jsoc_score, na.rm = TRUE),
    jsoc_wins = sum(jsoc_score > guild_score, na.rm = TRUE)
  )

ui <- navbarPage(
  "BO7 Power Rankings (dev)",
  tabPanel(
    "Leaderboard",
    fluidRow(
      column(
        width = 12,
        DTOutput("leaderboard_table")
      )
    )
  ),
  tabPanel(
    "Mode Breakdown",
    DTOutput("mode_table")
  ),
  tabPanel(
    "Match Log",
    DTOutput("match_log")
  )
)

server <- function(input, output, session) {
  output$leaderboard_table <- renderDT({
    datatable(leaderboard, options = list(pageLength = 10))
  })

  output$mode_table <- renderDT({
    datatable(mode_summary, options = list(pageLength = 10))
  })

  output$match_log <- renderDT({
    datatable(matches_raw, options = list(pageLength = 10))
  })
}

shinyApp(ui, server)

