"""State machine helpers for the Discord match logging flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from bot_dev.roster import Player, ROSTER


ROSTER_LOOKUP: Dict[int, Player] = {player.id: player for player in ROSTER}


@dataclass
class MatchState:
    by_who: Optional[str] = None
    mode_code: Optional[str] = None
    map_code: Optional[str] = None
    guild_size: Optional[int] = None
    jsoc_size: Optional[int] = None
    ffa_size: Optional[int] = None
    guild_players: List[int] = field(default_factory=list)
    jsoc_players: List[int] = field(default_factory=list)
    ffa_players: List[int] = field(default_factory=list)
    guild_score: Optional[int] = None
    jsoc_score: Optional[int] = None

    def is_free_for_all(self) -> bool:
        return self.mode_code == "FFA"

    def roster_summary(self) -> str:
        if self.is_free_for_all():
            names = [ROSTER_LOOKUP[p].name for p in self.ffa_players]
            return f"FFA ({len(names)} players): {', '.join(names) or 'TBD'}"

        guild_names = ", ".join(ROSTER_LOOKUP[p].name for p in self.guild_players) or "TBD"
        jsoc_names = ", ".join(ROSTER_LOOKUP[p].name for p in self.jsoc_players) or "TBD"
        return f"Guild [{guild_names}] vs JSOC [{jsoc_names}]"

    def to_supabase_payload(self) -> Dict[str, Optional[str]]:
        """Flatten the current selections into the denormalized table payload."""
        payload: Dict[str, Optional[str]] = {
            "by_who": self.by_who,
            "mode": self.mode_code,
            "map": self.map_code,
            "guild_score": self.guild_score,
            "jsoc_score": self.jsoc_score,
        }


        def assign(prefix: str, players: List[int]) -> None:
            for idx in range(4):
                player = ROSTER_LOOKUP.get(players[idx]) if idx < len(players) else None
                payload[f"{prefix}_player{idx + 1}_level"] = None
                payload[f"{prefix}_player{idx + 1}_name"] = player.name if player else None
                payload[f"{prefix}_player{idx + 1}_obj_score"] = None
                payload[f"{prefix}_player{idx + 1}_time"] = None
                payload[f"{prefix}_player{idx + 1}_obj_kills"] = None
                payload[f"{prefix}_player{idx + 1}_captures"] = None

        if self.is_free_for_all():
            # Treat the first 4 players as guild, rest as JSOC placeholders for analytics.
            assign("guild", self.ffa_players[:4])
            assign("jsoc", self.ffa_players[4:])
        else:
            assign("guild", self.guild_players)
            assign("jsoc", self.jsoc_players)

        return payload

