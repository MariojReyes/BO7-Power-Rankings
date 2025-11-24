"""Dev configuration loader for the BO7 match logger bot."""

from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    discord_token: str
    supabase_url: str
    supabase_key: str
    table_name: str = "match_master"
    dry_run: bool = True
    guild_label: str = "Guild"
    jsoc_label: str = "JSOC"


def load_settings(env_path: Optional[str] = None) -> Settings:
    """Load environment variables into a strongly typed Settings object."""
    load_dotenv(dotenv_path=env_path)
    discord_token = os.environ.get("DISCORD_TOKEN", "")
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    table_name = os.environ.get("SUPABASE_TABLE", "match_master")
    dry_run = os.environ.get("DRY_RUN", "true").lower() in {"1", "true", "yes"}
    guild_label = os.environ.get("GUILD_LABEL", "Guild")
    jsoc_label = os.environ.get("JSOC_LABEL", "JSOC")

    if not discord_token:
        raise ValueError("DISCORD_TOKEN is required for the dev bot.")
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set.")

    return Settings(
        discord_token=discord_token,
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        table_name=table_name,
        dry_run=dry_run,
        guild_label=guild_label,
        jsoc_label=jsoc_label,
    )

