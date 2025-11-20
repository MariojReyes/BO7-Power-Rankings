CREATE TABLE players (
    player_id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gamer_tag   VARCHAR(50) NOT NULL,
    display_name VARCHAR(50) NULL,
    CONSTRAINT uq_players_gamer_tag UNIQUE (gamer_tag)
);


CREATE TABLE modes (
    mode_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mode_name VARCHAR(50) NOT NULL
);

CREATE TABLE maps (
    map_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_name VARCHAR(50) NOT NULL
);


CREATE TABLE matches (
    match_id        INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entry_id        INT NULL,           -- if you want to link back to master
    by_who          VARCHAR(50),
    match_timestamp TIMESTAMP NULL,
    map_id          INT REFERENCES maps(map_id),
    mode_id         INT REFERENCES modes(mode_id),
    guild_score     INT,
    jsoc_score      INT
);


CREATE TABLE teams (
    team_id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL      -- 'Guild', 'JSOC', or whatever clan
);

CREATE TABLE match_teams (
    match_team_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    match_id      INT NOT NULL REFERENCES matches(match_id),
    team_id       INT NULL REFERENCES teams(team_id),  -- NULL for FFA if you want
    team_label    VARCHAR(20) NOT NULL,                -- 'Guild', 'JSOC', or 'FFA'
    team_score    INT NULL
);
