"""Thin Supabase wrapper so the bot can run in dry-run mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from supabase import Client, create_client

from bot_dev.config import Settings


@dataclass
class SupabaseWriter:
    settings: Settings
    client: Client

    @classmethod
    def from_settings(cls, settings: Settings) -> "SupabaseWriter":
        client = create_client(settings.supabase_url, settings.supabase_key)
        return cls(settings=settings, client=client)

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

