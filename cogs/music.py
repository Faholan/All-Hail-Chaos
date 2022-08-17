from random import choice
import re
import typing as t

from discord import app_commands, ui
from discord.ext import commands
import discord
import lavalink


# TODO : better error messages & handling


url_rx = re.compile(r"https?://(?:www\.)?.+")


class CustomPlayer(lavalink.DefaultPlayer):
    """Custom player with history."""

    def __init__(self, guild_id: int, node: lavalink.Node) -> None:
        """Initialise the player."""
        super().__init__(guild_id, node)

        self.repeat_once = False

        self.history: t.List[lavalink.AudioTrack] = []

    def set_repeat_once(self, repeat_once: bool) -> None:
        """Set the player's repeat once state."""
        self.repeat_once = repeat_once

    async def _handle_event(self, event: lavalink.Event) -> None:
        """Handle events and add to history."""
        if isinstance(event, lavalink.TrackEndEvent):
            if self.repeat_once:
                self.add(event.track.requester, event.track, 0)
            elif not self.repeat:
                self.history.append(event.track)

        await super()._handle_event(event)

    async def previous(self) -> None:
        """Got to the previous track in the history."""
        if not self.history:
            await self.set_pause(True)
            await self.seek(0)
            return

        previous_track = self.history.pop()

        self.add(self.current.requester, self.current, 0)
        await self.play(previous_track)
        await self.set_pause(False)

    async def skip(self) -> None:
        """Skip the current track."""
        if self.current is not None:
            self.history.append(self.current)
        await super().skip()

    async def add_query(self, interaction: discord.Interaction, query: str) -> bool:
        """Query Lavalink and add the results to the queue.

        Returns True if the query returned results, False otherwise.
        """

        query = query.strip("<>")

        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await self.node.get_tracks(query)

        if not results or not results["tracks"]:
            await interaction.response.send_message("Nothing found !", ephemeral=True)
            return False

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                self.add(requester=interaction.user.id, track=track)

            await interaction.response.send_message(
                f"Enqueued playlist {results['playlistInfo']['name']} - {len(tracks)} tracks",
                ephemeral=True,
            )
        else:
            track = results["tracks"][0]

            await interaction.response.send_message(
                f"Enqueued track {track['info']['title']}",
                ephemeral=True,
            )
            track = lavalink.models.AudioTrack(track, interaction.user.id)
            self.add(interaction.user.id, track)

        return True


def add_lavalink(client: discord.Client) -> None:
    """Add a Lavalink client if there isn't one."""
    if not hasattr(client, "lavalink"):
        client.lavalink = lavalink.Client(client.user.id, CustomPlayer)

        for node in client.lavalink_nodes:
            client.lavalink.add_node(**node)


class LavalinkVoiceClient(discord.VoiceClient):
    """Manage the voice connection."""

    # pylint: disable=super-init-not-called
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        """Initialise the voice client."""
        self.client = client
        self.channel = channel

        add_lavalink(client)

        self.lavalink: lavalink.Client = self.client.lavalink

    async def connect(
        self,
        *,
        reconnect: bool,
        timeout: float,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        """Connect the voice client and create a player."""
        self.lavalink.player_manager.create(self.channel.guild.id)
        await self.channel.guild.change_voice_state(
            channel=self.channel,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

    async def disconnect(self, *, force: bool = False) -> None:
        """Handle disconnects."""
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if not force and not player.is_connected:
            return

        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()

    async def on_voice_server_update(self, data: t.Dict[t.Any, t.Any]) -> None:
        """Manage voice server update events."""
        await self.lavalink.voice_update_handler(
            {
                "t": "VOICE_SERVER_UPDATE",
                "d": data,
            }
        )

    async def on_voice_state_update(self, data: t.Dict[t.Any, t.Any]) -> None:
        """Manage voice state update events."""
        await self.lavalink.voice_update_handler(
            {
                "t": "VOICE_STATE_UPDATE",
                "d": data,
            }
        )


class MusicInput(ui.Modal, title="Music search"):
    """Music modal input."""

    def __init__(self, player: CustomPlayer):
        """Initialize the input."""
        super().__init__()
        self.add_item(
            ui.TextInput(
                label="Music to search for",
                placeholder=choice(
                    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Hotel California")
                ),
                required=True,
            )
        )
        self.player = player

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Submit the search."""
        if await self.player.add_query(interaction, self.children[0].value):
            self.stop()
            await interaction.edit_original_response(
                embed=await get_music_embed(self.player), view=MusicView(self.player)
            )


class MusicView(ui.View):
    """View for the music cog."""

    def __init__(self, player: CustomPlayer):
        """View for the music cog."""
        super().__init__()

        self.player = player

        if not player.history:
            self.children[0].disabled = True
        if player.paused:
            self.children[1].style = discord.ButtonStyle.secondary
        if not player.queue:
            self.children[2].disabled = True
        if player.repeat:
            self.children[4].style = discord.ButtonStyle.secondary
        if player.repeat_once:
            self.children[5].style = discord.ButtonStyle.secondary
        if player.shuffle:
            self.children[6].style = discord.ButtonStyle.secondary

    @ui.button(emoji="\U000023ee\U0000fe0f", style=discord.ButtonStyle.primary, row=1)
    async def previous(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Go to the previous track."""
        await interaction.response.defer()
        await self.player.previous()
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=MusicView(self.player)
        )

    @ui.button(emoji="\U000023ef\U0000fe0f", style=discord.ButtonStyle.primary, row=1)
    async def pause_play(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Play or pause the player."""
        await interaction.response.defer()
        await self.player.set_pause(not self.player.paused)
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=MusicView(self.player)
        )

    @ui.button(emoji="\U000023ed\U0000fe0f", style=discord.ButtonStyle.primary, row=1)
    async def next(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Go to the next track."""
        await interaction.response.defer()
        await self.player.skip()
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=MusicView(self.player)
        )

    @ui.button(emoji="\U000023f9\U0000fe0f", style=discord.ButtonStyle.danger, row=2)
    async def stop(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Stop playing altogether."""
        await interaction.response.defer()
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=None
        )
        await self.player.stop()

    @ui.button(emoji="\U0001f501", style=discord.ButtonStyle.primary, row=2)
    async def repeat(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Toggle repeat."""
        await interaction.response.defer()
        self.player.set_repeat(not self.player.repeat)
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=MusicView(self.player)
        )

    @ui.button(emoji="\U0001f502", style=discord.ButtonStyle.primary, row=2)
    async def repeat_once(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Toggle repeat once."""
        await interaction.response.defer()
        self.player.set_repeat_once(not self.player.repeat_once)
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=MusicView(self.player)
        )

    @ui.button(emoji="\U0001f500", style=discord.ButtonStyle.primary, row=2)
    async def shuffle(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Toggle shuffle."""
        await interaction.response.defer()
        self.player.set_shuffle(not self.player.shuffle)
        await interaction.edit_original_response(
            embed=await get_music_embed(self.player), view=MusicView(self.player)
        )

    @ui.button(emoji="\U0001f50e", style=discord.ButtonStyle.primary, row=2)
    async def search(self, interaction: discord.Interaction, _: ui.Button) -> None:
        """Search for a track."""
        await interaction.response.send_modal(MusicInput(self.player))


async def get_music_embed(player: CustomPlayer) -> discord.Embed:
    """Get the interface for the music player."""
    embed = discord.Embed()  # TODO : FILL ME !!!

    return None


@app_commands.guild_only()
class Music(commands.GroupCog):
    """Play music."""

    def __init__(self, bot: commands.Bot) -> None:
        """Load the cog."""
        self.bot = bot

        if not bot.lavalink_nodes:
            raise ValueError("No Lavalink nodes configured !")

        add_lavalink(bot)
        lavalink.add_event_hook(self.track_hook)

    async def cog_unload(self) -> None:
        """Cleanup the event hooks."""
        self.bot.lavalink._event_hooks.clear()

    async def track_hook(self, event: lavalink.Event) -> None:
        """Disconnect the client upon reaching the end of queue."""
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            if guild:
                await guild.voice_client.disconnect(force=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the interaction should be processed."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "You must be in a voice channel to use this command.",
                ephemeral=True,
            )
            return False

        should_connect = (
            interaction.command is not None and interaction.command.name == "play"
        )

        player = self.bot.lavalink.player_manager.create(interaction.guild_id)

        if not player.is_connected:
            if not should_connect:
                await interaction.response.send_message(
                    "I'm not connected to a voice channel.",
                    ephemeral=True,
                )
                return False

            permissions = interaction.user.voice.channel.permissions_for(
                interaction.guild.me
            )

            if not permissions.connect or not permissions.speak:
                await interaction.response.send_message(
                    "I don't have the permissions to join and speak in your voice channel.",
                    ephemeral=True,
                )
                return False

            if interaction.user.voice.channel.user_limit == len(
                interaction.user.voice.channel.members
            ):
                await interaction.response.send_message(
                    "I can't join this voice channel because it is full.",
                    ephemeral=True,
                )
                return False

            await interaction.user.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if player.channel_id != interaction.user.voice.channel.id:
                await interaction.response.send_message(
                    "I'm already in a different voice channel.", ephemeral=True
                )
                return False

        return True

    @app_commands.command()
    async def play(
        self, interaction: discord.Interaction, query: t.Optional[str]
    ) -> None:
        """Play music."""
        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        if query is not None:
            await player.add_query(interaction, query)

        if player.queue and not player.is_playing:
            await player.play()

        if player.paused:
            await player.set_pause(False)

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=await get_music_embed(player), view=MusicView(player)
            )
        else:
            await interaction.response.send_message(
                embed=await get_music_embed(player), view=MusicView(player)
            )

    @app_commands.command()
    async def np(self, interaction: discord.Interaction) -> None:
        """Check the current status of player."""
        player = self.bot.lavalink.player_manager.get(interaction.guild_id)

        await interaction.response.send_message(
            embed=await get_music_embed(player), view=MusicView(player)
        )


async def setup(bot: commands.Bot) -> None:
    """Setup the music extension."""
    await bot.add_cog(Music(bot))
