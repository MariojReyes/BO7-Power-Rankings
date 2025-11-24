"""Entry point for the dev Discord bot."""

from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from bot_dev.config import Settings, load_settings
from bot_dev.match_flow import MatchState
from bot_dev.supabase_client import SupabaseWriter
from bot_dev.views import MatchLoggerView


logging.basicConfig(level=logging.INFO)


class MatchLoggerBot(commands.Bot):
    def __init__(self, settings: Settings):
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings
        self.writer = SupabaseWriter.from_settings(settings)

    async def setup_hook(self) -> None:
        await self.tree.sync()
        logging.info("Slash commands synced.")

    async def on_ready(self) -> None:
        logging.info("Logged in as %s", self.user)


def build_bot() -> MatchLoggerBot:
    settings = load_settings()
    return MatchLoggerBot(settings)


bot = build_bot()


@bot.tree.command(name="logmatch", description="Open the BO7 match logging menu.")
async def logmatch(interaction: discord.Interaction) -> None:
    state = MatchState(by_who=interaction.user.display_name)
    view = MatchLoggerView(owner_id=interaction.user.id, state=state, writer=bot.writer, settings=bot.settings)
    await interaction.response.send_message(
        embed=view.build_embed(),
        view=view,
        ephemeral=True,
    )


def main() -> None:
    asyncio.run(bot.start(bot.settings.discord_token))


if __name__ == "__main__":
    main()

