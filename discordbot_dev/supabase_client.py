"""Thin Supabase wrapper so the bot can run in dry-run mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from supabase import Client, create_client

from discordbot_dev.config import Settings


@dataclass
class SupabaseWriter:
    settings: Settings
    client: Client

    @classmethod
    def from_settings(cls, settings: Settings) -> "SupabaseWriter":
        client = create_client(settings.supabase_url, settings.supabase_key)
        return cls(settings=settings, client=client)

    def lookup_map_id(self, map_label: str) -> Optional[int]:
        """Look up map_id from maps table using map_name."""
        try:
            result = (
                self.client.table("maps")
                .select("map_id")
                .eq("map_name", map_label)
                .limit(1)
                .execute()
            )
            if result.data and len(result.data) > 0:
                return result.data[0]["map_id"]
        except Exception:
            pass
        return None

    def lookup_mode_id(self, mode_label: str) -> Optional[int]:
        """Look up mode_id from modes table using mode_name."""
        try:
            result = (
                self.client.table("modes")
                .select("mode_id")
                .eq("mode_name", mode_label)
                .limit(1)
                .execute()
            )
            if result.data and len(result.data) > 0:
                return result.data[0]["mode_id"]
        except Exception:
            pass
        return None

    def insert_match(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a match row or echo the payload when dry-run is enabled."""
        if self.settings.dry_run:
            return {"data": [payload], "dry_run": True}
        return (
            self.client.table(self.settings.table_name)
            .insert(payload)
            .execute()
            .model_dump()
        )

