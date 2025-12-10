"""Environment validation script for BO7 Discord bot.

Run this before starting the bot to verify your configuration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    from supabase import create_client
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_status(label: str, status: str, value: str = "") -> None:
    """Print a status line with emoji indicator."""
    status_icons = {
        "✅": "OK",
        "⚠️": "WARNING",
        "❌": "ERROR",
        "ℹ️": "INFO",
    }
    icon = "✅" if status == "OK" else "⚠️" if status == "WARNING" else "❌" if status == "ERROR" else "ℹ️"
    
    print(f"{icon} {label:.<40} {status}")
    if value and status != "OK":
        # Mask sensitive values
        if "token" in label.lower() or "key" in label.lower():
            if len(value) > 20:
                masked = value[:8] + "..." + value[-4:]
            else:
                masked = "***" if value else "MISSING"
            print(f"   Value: {masked}")
        else:
            print(f"   Value: {value}")


def check_env_file() -> tuple[bool, Path | None]:
    """Check if .env file exists."""
    env_path = Path(__file__).parent / ".env"
    exists = env_path.exists()
    return exists, env_path if exists else None


def validate_discord_token(token: str) -> tuple[str, str]:
    """Basic Discord token validation."""
    if not token:
        return "ERROR", "Token is empty"
    
    if token == "your-dev-discord-token":
        return "ERROR", "Still using placeholder value"
    
    # Discord bot tokens are typically 59-70 characters
    if len(token) < 50:
        return "WARNING", f"Token seems too short ({len(token)} chars)"
    
    # Basic format check (should have dots separating parts)
    if token.count(".") < 2:
        return "WARNING", "Token format looks unusual"
    
    return "OK", ""


def validate_supabase_url(url: str) -> tuple[str, str]:
    """Validate Supabase URL format."""
    if not url:
        return "ERROR", "URL is empty"
    
    if url == "https://your-project.supabase.co":
        return "ERROR", "Still using placeholder value"
    
    if not url.startswith("https://"):
        return "ERROR", "URL must start with https://"
    
    if ".supabase.co" not in url:
        return "WARNING", "URL doesn't contain .supabase.co"
    
    return "OK", ""


def validate_supabase_key(key: str) -> tuple[str, str]:
    """Validate Supabase key format."""
    if not key:
        return "ERROR", "Key is empty"
    
    if key == "service-role-key":
        return "ERROR", "Still using placeholder value"
    
    if len(key) < 50:
        return "WARNING", f"Key seems too short ({len(key)} chars)"
    
    return "OK", ""


def test_supabase_connection(url: str, key: str, table: str) -> tuple[str, str]:
    """Test Supabase connection by attempting to query the table."""
    try:
        client = create_client(url, key)
        # Try to select 0 rows (just test connection)
        result = client.table(table).select("*", count="exact").limit(0).execute()
        return "OK", f"Connected successfully (table exists)"
    except Exception as e:
        error_msg = str(e)
        if "JWT" in error_msg or "invalid" in error_msg.lower():
            return "ERROR", f"Authentication failed: Check your SUPABASE_SERVICE_KEY"
        elif "relation" in error_msg.lower() or "does not exist" in error_msg.lower():
            return "WARNING", f"Table '{table}' not found. Run the SQL schema first."
        else:
            return "ERROR", f"Connection failed: {error_msg[:100]}"


def main() -> int:
    """Main validation function."""
    print_header("BO7 Discord Bot - Environment Validation")
    
    # Check .env file exists
    env_exists, env_path = check_env_file()
    if env_exists:
        print_status(".env file", "OK", str(env_path))
        load_dotenv(dotenv_path=env_path)
    else:
        print_status(".env file", "ERROR", "Not found")
        print("\n   💡 Create .env file:")
        print("      cp env.example .env")
        print("      Then edit .env with your actual values")
        return 1
    
    print_header("Required Environment Variables")
    
    # Load and validate variables
    discord_token = os.environ.get("DISCORD_TOKEN", "")
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    table_name = os.environ.get("SUPABASE_TABLE", "match_master")
    dry_run = os.environ.get("DRY_RUN", "true").lower() in {"1", "true", "yes"}
    
    # Validate each variable
    status, msg = validate_discord_token(discord_token)
    print_status("DISCORD_TOKEN", status, msg or discord_token[:20] + "...")
    
    status, msg = validate_supabase_url(supabase_url)
    print_status("SUPABASE_URL", status, msg or supabase_url)
    
    status, msg = validate_supabase_key(supabase_key)
    print_status("SUPABASE_SERVICE_KEY", status, msg or supabase_key[:20] + "...")
    
    print_header("Optional Environment Variables")
    
    print_status("SUPABASE_TABLE", "OK" if table_name else "WARNING", 
                 table_name or "Using default: match_master")
    
    print_status("DRY_RUN", "INFO", 
                 f"{'Enabled (safe mode)' if dry_run else 'Disabled (will write to DB)'}")
    
    guild_label = os.environ.get("GUILD_LABEL", "Guild")
    jsoc_label = os.environ.get("JSOC_LABEL", "JSOC")
    print_status("GUILD_LABEL", "OK", guild_label)
    print_status("JSOC_LABEL", "OK", jsoc_label)
    
    # Test Supabase connection if we have valid credentials
    if supabase_url and supabase_key and supabase_url != "https://your-project.supabase.co":
        print_header("Supabase Connection Test")
        status, msg = test_supabase_connection(supabase_url, supabase_key, table_name)
        print_status("Connection", status, msg)
    
    print_header("Summary")
    
    # Check if we can proceed
    errors = [
        not env_exists,
        not discord_token or discord_token == "your-dev-discord-token",
        not supabase_url or supabase_url == "https://your-project.supabase.co",
        not supabase_key or supabase_key == "service-role-key",
    ]
    
    if any(errors):
        print("❌ Configuration incomplete. Fix the errors above before running the bot.")
        print("\n   Next steps:")
        print("   1. Copy env.example to .env")
        print("   2. Fill in DISCORD_TOKEN, SUPABASE_URL, and SUPABASE_SERVICE_KEY")
        print("   3. Run this script again to validate")
        return 1
    else:
        print("✅ All required variables are set!")
        print(f"\n   Ready to run: python -m discordbot_dev.main")
        if dry_run:
            print("   ⚠️  DRY_RUN is enabled - matches won't be saved to database")
        return 0


if __name__ == "__main__":
    sys.exit(main())