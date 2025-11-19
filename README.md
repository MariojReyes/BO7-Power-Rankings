**#Black Ops 7 Private Match Tracker**
A stat tracking system for our private matches. No fluff, just data.
What This Does
Records match results and shows who's actually good at what. Supports everything from 1v1s to chaotic FFA games.
The core loop:

Match ends
Someone logs the stats (Discord command or screenshot)
Dashboard updates
Arguments get settled with numbers

**Who Plays**
Mario, Kai, Danny, Gio, Jozy, Alan + whoever shows up
What We Track
Per Match:

Map, gamemode, final score
Who was on which team
When it happened

Per Player:

Kills, deaths, score
Works for any team size (1v1, 2v2, 3v2, FFA, whatever)

**Modes We Play:**
Hardpoint, Search & Destroy, Gunfight, TDM, Free-For-All
**Current Map Pool:**
Blackheart, Cortex, Raid, Hijacked

How to Log a Match
Discord slash command:
```
/match add 
map:Hijacked 
mode:Hardpoint 
team1:"Mario,Gio" 
team2:"Kai,Danny" 
score:250-243 
kills:"34,22 vs 28,31"
deaths:"19,26 vs 22,25"
```

**What You Can See**
Global leaderboard - who wins, who has the best KD, who scores most
Map breakdowns - your best/worst maps, who dominates where
Gamemode rankings - separate stats for HP, SND, Gunfight, etc.
Head-to-head - your record against specific players, trends over time
Personal page - all your stats, recent matches, where you're improving or falling off
Everything's filterable by date range, map, or mode.
Database Structure
Three tables:
players - gamertag and an ID
matches - map, mode, scores, timestamp, whether it's FFA
match_players - links players to matches with their kills/deaths/score and team number
That's it. Simple and expandable.
