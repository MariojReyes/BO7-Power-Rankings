"""State machine helpers for the Discord match logging flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from discordbot_dev.roster import Player, ROSTER


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

    def to_supabase_payload(self, writer=None) -> Dict[str, Any]:
        """Flatten the current selections into the denormalized table payload.
        
        If writer is provided, looks up map_id and mode_id from the database.
        Otherwise, returns map and mode as codes (for backward compatibility).
        """
        from discordbot_dev.constants import MAPS, MODES
        
        # Get the labels for lookup
        mode_label = next((mode.label for mode in MODES if mode.code == self.mode_code), None)
        map_label = next((m.label for m in MAPS if m.code == self.map_code), None)
        
        payload: Dict[str, Any] = {
            "by_who": self.by_who,
            "guild_score": self.guild_score,
            "jsoc_score": self.jsoc_score,
        }
        
        # If writer is provided, look up IDs; otherwise use codes
        if writer:
            map_id = writer.lookup_map_id(map_label) if map_label else None
            mode_id = writer.lookup_mode_id(mode_label) if mode_label else None
            payload["map_id"] = map_id
            payload["mode_id"] = mode_id
        else:
            # Fallback to codes for backward compatibility
            payload["mode"] = self.mode_code
            payload["map"] = self.map_code


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

