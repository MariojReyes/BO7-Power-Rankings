"""discord.py UI components for the match logging workflow."""

from __future__ import annotations

import discord

from bot_dev.config import Settings
from bot_dev.constants import MAPS, MODES
from bot_dev.match_flow import MatchState, ROSTER, ROSTER_LOOKUP
from bot_dev.supabase_client import SupabaseWriter


class MatchLoggerView(discord.ui.View):
    def __init__(self, *, owner_id: int, state: MatchState, writer: SupabaseWriter, settings: Settings):
        super().__init__(timeout=900)
        self.owner_id = owner_id
        self.state = state
        self.writer = writer
        self.settings = settings

        self.mode_select = ModeSelect(self)
        self.map_select = MapSelect(self)
        self.guild_size_select = TeamSizeSelect(self, team="guild")
        self.guild_player_select = PlayerSelect(self, team="guild")
        self.jsoc_size_select = TeamSizeSelect(self, team="jsoc")
        self.jsoc_player_select = PlayerSelect(self, team="jsoc")
        self.ffa_size_select = FFASizeSelect(self)
        self.ffa_player_select = FFAPlayerSelect(self)
        self.add_item(self.mode_select)
        self.add_item(self.map_select)
        self.add_item(self.guild_size_select)
        self.add_item(self.guild_player_select)
        self.add_item(self.jsoc_size_select)
        self.add_item(self.jsoc_player_select)
        self.add_item(self.ffa_size_select)
        self.add_item(self.ffa_player_select)
        self.add_item(OpenScoreModalButton(self))
        self.add_item(SubmitButton(self))
        self.add_item(CancelButton(self))

        self._apply_mode_rules(initial=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Only the session owner can modify this form.", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(title="BO7 Match Logger (dev)", color=0x00AEEF)
        embed.add_field(
            name="Selected Mode",
            value=self._mode_label() or "Pending",
            inline=False,
        )
        embed.add_field(
            name="Map",
            value=self._map_label() or "Pending",
            inline=False,
        )
        embed.add_field(
            name="Roster",
            value=self.state.roster_summary(),
            inline=False,
        )
        score_summary = (
            f"{self.settings.guild_label}: {self.state.guild_score or '-'} | "
            f"{self.settings.jsoc_label}: {self.state.jsoc_score or '-'}"
        )
        embed.add_field(name="Scores", value=score_summary, inline=False)
        embed.add_field(
            name="Entered By",
            value=self.state.by_who or "Pending",
            inline=False,
        )
        embed.set_footer(text="Selections auto-save as you update the menus.")
        return embed

    async def refresh(self, interaction: discord.Interaction) -> None:
        self._apply_mode_rules()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    def _apply_mode_rules(self, initial: bool = False) -> None:
        is_ffa = self.state.is_free_for_all()
        # Toggle team-based controls
        for control in (self.guild_size_select, self.guild_player_select, self.jsoc_size_select, self.jsoc_player_select):
            control.disabled = is_ffa
        self.ffa_size_select.disabled = not is_ffa
        self.ffa_player_select.disabled = not is_ffa

        if initial:
            # ensure defaults
            self.guild_size_select.disabled = True
            self.jsoc_size_select.disabled = True
            self.guild_player_select.disabled = True
            self.jsoc_player_select.disabled = True
            self.ffa_size_select.disabled = True
            self.ffa_player_select.disabled = True

    def _mode_label(self) -> str | None:
        return next((mode.label for mode in MODES if mode.code == self.state.mode_code), None)

    def _map_label(self) -> str | None:
        return next((m.label for m in MAPS if m.code == self.state.map_code), None)

    def selections_complete(self) -> bool:
        base_ready = self.state.mode_code and self.state.map_code and self.state.by_who and self.state.guild_score is not None
        base_ready = base_ready and self.state.jsoc_score is not None
        if not base_ready:
            return False
        if self.state.is_free_for_all():
            return bool(self.state.ffa_size and len(self.state.ffa_players) == self.state.ffa_size)
        return bool(
            self.state.guild_size
            and len(self.state.guild_players) == self.state.guild_size
            and self.state.jsoc_size
            and len(self.state.jsoc_players) == self.state.jsoc_size
        )

    async def submit(self, interaction: discord.Interaction) -> None:
        if not self.selections_complete():
            await interaction.response.send_message("Selections incomplete. Fill out every section before submitting.", ephemeral=True)
            return
        payload = self.state.to_supabase_payload()
        result = self.writer.insert_match(payload)
        await interaction.response.send_message(f"Match recorded! Dry run: {result.get('dry_run', False)}", ephemeral=True)


class ModeSelect(discord.ui.Select):
    def __init__(self, view: MatchLoggerView):
        options = [
            discord.SelectOption(label=mode.label, value=mode.code) for mode in MODES
        ]
        super().__init__(placeholder="Choose Game Mode", min_values=1, max_values=1, options=options)
        self.view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        self.view.state.mode_code = self.values[0]
        # Reset roster selections when switching modes
        self.view.state.guild_players.clear()
        self.view.state.jsoc_players.clear()
        self.view.state.ffa_players.clear()
        await self.view.refresh(interaction)


class MapSelect(discord.ui.Select):
    def __init__(self, view: MatchLoggerView):
        options = [discord.SelectOption(label=m.label, value=m.code) for m in MAPS]
        super().__init__(placeholder="Choose Map", min_values=1, max_values=1, options=options)
        self.view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        self.view.state.map_code = self.values[0]
        await self.view.refresh(interaction)


class TeamSizeSelect(discord.ui.Select):
    def __init__(self, view: MatchLoggerView, *, team: str):
        options = [discord.SelectOption(label=f"{i} Players", value=str(i)) for i in range(1, 5)]
        placeholder = f"How many players on {team.capitalize()}?"
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, disabled=True)
        self.view = view
        self.team = team

    async def callback(self, interaction: discord.Interaction) -> None:
        size = int(self.values[0])
        if self.team == "guild":
            self.view.state.guild_size = size
            self.view.guild_player_select.set_limit(size)
            self.view.guild_player_select.disabled = False
        else:
            self.view.state.jsoc_size = size
            self.view.jsoc_player_select.set_limit(size)
            self.view.jsoc_player_select.disabled = False
        await self.view.refresh(interaction)


class PlayerSelect(discord.ui.Select):
    def __init__(self, view: MatchLoggerView, *, team: str):
        options = [
            discord.SelectOption(label=f"{player.name} ({player.gamertag})", value=str(player.id))
            for player in ROSTER
        ]
        super().__init__(
            placeholder=f"Who is on {team.capitalize()}?",
            min_values=0,
            max_values=4,
            options=options,
            disabled=True,
        )
        self.view = view
        self.team = team

    def set_limit(self, limit: int) -> None:
        self.min_values = limit
        self.max_values = limit

    async def callback(self, interaction: discord.Interaction) -> None:
        picks = [int(value) for value in self.values]
        other_team = self.view.state.jsoc_players if self.team == "guild" else self.view.state.guild_players
        if set(picks) & set(other_team):
            await interaction.response.send_message("Players cannot be on both teams.", ephemeral=True)
            return
        if self.team == "guild":
            self.view.state.guild_players = picks
        else:
            self.view.state.jsoc_players = picks
        await self.view.refresh(interaction)


class FFASizeSelect(discord.ui.Select):
    def __init__(self, view: MatchLoggerView):
        options = [discord.SelectOption(label=f"{i} Players", value=str(i)) for i in range(2, 9)]
        super().__init__(placeholder="How many FFA players?", min_values=1, max_values=1, options=options, disabled=True)
        self.view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        size = int(self.values[0])
        self.view.state.ffa_size = size
        self.view.ffa_player_select.set_limit(size)
        self.view.ffa_player_select.disabled = False
        await self.view.refresh(interaction)


class FFAPlayerSelect(discord.ui.Select):
    def __init__(self, view: MatchLoggerView):
        options = [
            discord.SelectOption(label=f"{player.name} ({player.gamertag})", value=str(player.id))
            for player in ROSTER
        ]
        super().__init__(
            placeholder="FFA Roster",
            min_values=0,
            max_values=8,
            options=options,
            disabled=True,
        )
        self.view = view

    def set_limit(self, limit: int) -> None:
        self.min_values = limit
        self.max_values = limit

    async def callback(self, interaction: discord.Interaction) -> None:
        picks = [int(value) for value in self.values]
        if len(picks) != (self.view.state.ffa_size or 0):
            await interaction.response.send_message("Select the exact number of FFA players.", ephemeral=True)
            return
        self.view.state.ffa_players = picks
        await self.view.refresh(interaction)


class ScoreModal(discord.ui.Modal):
    def __init__(self, view: MatchLoggerView):
        super().__init__(title="Enter Scores")
        self.view = view
        self.by_who = discord.ui.TextInput(label="Logged by", default=view.state.by_who or "")
        self.guild_score = discord.ui.TextInput(
            label=f"{view.settings.guild_label} score",
            placeholder="Numeric value",
            default=str(view.state.guild_score or ""),
        )
        self.jsoc_score = discord.ui.TextInput(
            label=f"{view.settings.jsoc_label} score",
            placeholder="Numeric value",
            default=str(view.state.jsoc_score or ""),
        )
        self.add_item(self.by_who)
        self.add_item(self.guild_score)
        self.add_item(self.jsoc_score)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            guild_score = int(self.guild_score.value)
            jsoc_score = int(self.jsoc_score.value)
        except ValueError:
            await interaction.response.send_message("Scores must be integers.", ephemeral=True)
            return
        self.view.state.by_who = self.by_who.value
        self.view.state.guild_score = guild_score
        self.view.state.jsoc_score = jsoc_score
        await interaction.response.send_message("Scores updated.", ephemeral=True)


class OpenScoreModalButton(discord.ui.Button):
    def __init__(self, view: MatchLoggerView):
        super().__init__(label="Enter Scores", style=discord.ButtonStyle.primary)
        self.view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(ScoreModal(self.view))


class SubmitButton(discord.ui.Button):
    def __init__(self, view: MatchLoggerView):
        super().__init__(label="Submit Match", style=discord.ButtonStyle.success)
        self.view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.submit(interaction)


class CancelButton(discord.ui.Button):
    def __init__(self, view: MatchLoggerView):
        super().__init__(label="Cancel Session", style=discord.ButtonStyle.danger)
        self.view = view

    async def callback(self, interaction: discord.Interaction) -> None:
        for child in self.view.children:
            child.disabled = True
        await interaction.response.edit_message(content="Session cancelled.", view=self.view)

