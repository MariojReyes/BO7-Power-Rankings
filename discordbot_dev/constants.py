"""Shared constants for match logging menus."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ModeOption:
    code: str
    label: str


@dataclass(frozen=True)
class MapOption:
    code: str
    label: str


MODES: List[ModeOption] = [
    ModeOption("HP", "Hardpoint"),
    ModeOption("SND", "Search and Destroy"),
    ModeOption("GF", "Gunfight"),
    ModeOption("FFA", "Free For All"),
    ModeOption("TDM", "Team Deathmatch"),
    ModeOption("OVR", "Overload"),
]

MAPS: List[MapOption] = [
    MapOption("BLACKHEART", "Blackheart"),
    MapOption("COLOSSUS", "Colossus"),
    MapOption("CORTEX", "Cortex"),
    MapOption("HIJACKED", "Hijacked"),
    MapOption("RAID", "Raid"),
    MapOption("FORGE", "The Forge"),
]

