"""Static roster definitions for dev flows."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Player:
    id: int
    name: str
    gamertag: str


ROSTER: List[Player] = [
    Player(1, "Mario", "Nooport"),
    Player(2, "Kai", "MuffinMan"),
    Player(3, "Danny", "Dflo"),
    Player(4, "Gio", "Kobe"),
    Player(5, "Jozy", "BaconEggCheese"),
    Player(6, "Alan", "retro"),
]

