"""MIT License

Copyright (c) 2022 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from random import choice
import re
import typing as t

from discord import app_commands, ui
from discord.ext import commands, tasks
import discord
import lavalink


# TODO : better error messages & handling


url_rx = re.compile(r"https?://(?:www\.)?.+")


class InteractionHolder:
    """Mutable placeholder for interactions."""

    def __init__(self, interaction: discord.Interaction, view: "MusicView") -> None:
        """Initialize the placeholder."""
        self._interaction = interaction
        self._view = view

    def __eq__(self, other: t.Any) -> bool:
        """Check for equality."""
        if isinstance(other, InteractionHolder):
            return self.interaction == other.interaction
        return False

    @property
    def interaction(self) -> discord.Interaction:
        """Get the underlying interaction."""
        return self._interaction

    @property
    def view(self) -> "MusicView":
        """Get the view."""
        return self._view

    @view.setter
    def view(self, view: "MusicView") -> None:
        """Set a new view and invalidate the old one."""
        self._view.stop()
        self._view = view

    def is_expired(self) -> bool:
        """Check if the underlying interaction has expired."""
        return self.interaction.is_expired()

    @property
    def guild_id(self) -> t.Optional[int]:
        """Get the guild id."""
        return self.interaction.guild_id

    @property
    def channel_id(self) -> t.Optional[int]:
        """Get the channel id."""
        return self.interaction.channel_id

    async def set_interaction(self, interaction: discord.Interaction) -> None:
        """Set a new interaction and delete the old one."""
        if interaction == self.interaction:  # no need to do anything
            return
        try:
            await self.interaction.delete_original_response()
        except (discord.NotFound, discord.HTTPException):
            pass
        self._interaction = interaction


class CustomPlayer(lavalink.DefaultPlayer):
    """Custom player with history."""

    def __init__(self, guild_id: int, node: lavalink.Node) -> None:
        """Initialise the player."""
        super().__init__(guild_id, node)

        self.repeat_once = False  # Repeat a single track forever

        self.history: t.List[lavalink.AudioTrack] = []  # Tracks previously played

        self._interactions: t.List[InteractionHolder] = []
        # All interactions with views controlling the player
        # Stored in order to update

    async def add_interaction(
        self, interaction: discord.Interaction, view: "MusicView"
    ) -> None:
        """Add an interaction to the player, removing old ones from the player."""
        i = 0
        while i < len(self._interactions):
            holder = self._interactions[i]
            if holder.is_expired():
                holder.view.stop()
                try:
                    await holder.interaction.delete_original_response()
                except (discord.NotFound, discord.HTTPException):
                    pass
                self._interactions.pop(i)
            elif (holder.guild_id, holder.channel_id,) == (
                interaction.guild_id,
                interaction.channel_id,
            ):
                view = MusicView(self, interaction)
                holder.view = view
                await holder.set_interaction(interaction)
                return

            i += 1

        self._interactions.append(InteractionHolder(interaction, view))

    async def remove_interaction(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Stop listening to an interaction."""
        for i, holder in enumerate(self._interactions):
            if holder.interaction == interaction:
                holder.view.stop()
                self._interactions.pop(i)
                break

        try:
            await interaction.edit_original_response(
                embed=await get_music_embed(self, interaction), view=None
            )
        except (discord.NotFound, discord.HTTPException):
            pass

    async def update_interactions(self) -> None:
        """Update the interfaces."""
        i = 0
        while i < len(self._interactions):
            # We may need to invalidate some interactions, hence a while loop rather than a for
            holder = self._interactions[i]
            if holder.is_expired():  # If the interaction is expired, delete it
                self._interactions.pop(i)
                holder.view.stop()
                try:
                    await holder.interaction.delete_original_response()
                except (discord.NotFound, discord.HTTPException):
                    pass
                continue

            view = MusicView(self, holder.interaction)

            try:
                await holder.interaction.edit_original_response(
                    embed=await get_music_embed(self, holder.interaction),
                    view=view,
                )
                holder.view = view
            except (
                discord.NotFound,
                discord.HTTPException,
            ):  # Interaction message got deleted, purge it
                holder.view.stop()
                self._interactions.pop(i)
            else:
                i += 1

    def set_repeat_once(self, repeat_once: bool) -> None:
        """Set the player's repeat once state."""
        # This is the same type of method as the rest of the Player API
        if not self.repeat and not self.shuffle:
            # This loop is incompatible with shuffling & repeating
            self.repeat_once = repeat_once

    def set_repeat(self, repeat: bool) -> None:
        """Set the player's repeat status."""
        if not self.repeat_once:
            # You can only have a single loop type
            super().set_repeat(repeat)

    async def play(
        self,
        track: t.Optional[t.Union[lavalink.AudioTrack, t.Dict[t.Any, t.Any]]] = None,
        start_time: int = 0,
        end_time: int = 0,
        no_replace: bool = False,
        no_history: bool = False,
    ) -> None:
        """Manage the history & repeat states when playing."""
        if not self.current or no_history:
            # If there is no current track, then there is nothing to add
            # no_history : Do not add the track to history
            await super().play(track, start_time, end_time, no_replace)  # type: ignore
            await self.update_interactions()
            return

        if self.repeat_once:
            self.queue.insert(0, self.current)
        elif not self.repeat:
            self.history.append(self.current)  # type: ignore

        # Lavalink messed up the types : play can accept a track of None
        # and current is an AudioTrack, not a dict (according to official docs & source)
        await super().play(track, start_time, end_time, no_replace)  # type: ignore
        await self.update_interactions()

    async def previous(self) -> None:
        """Got to the previous track in the history."""
        if not self.history:
            # If nothing is in the history, i. e. this is the first track,
            # go the the start of the song
            await self.seek(0)
            return

        previous_track = self.history.pop()  # Get the previous track

        self.queue.insert(0, self.current)  # Add the current track to the queue
        await self.play(
            previous_track, no_history=True
        )  # The track was already added to history, so do not add a second time
        await self.set_pause(False)  # Unpause if we were paused

    async def add_query(self, interaction: discord.Interaction, query: str) -> str:
        """Query Lavalink and add the results to the queue.

        Returns the message to send as followup.
        """

        if not url_rx.match(query):
            # If this is not an URL, search for it on YouTube
            query = f"ytsearch:{query}"

        results = await self.node.get_tracks(query)  # Query Lavalink

        if not results or not results["tracks"]:
            return "Nothing found !"

        if results["loadType"] == "PLAYLIST_LOADED":
            # Found a playlist, add all tracks to the queue
            tracks = results["tracks"]

            for track in tracks:
                self.add(requester=interaction.user.id, track=track)

            return f"Enqueued playlist {results['playlistInfo']['name']} - {len(tracks)} tracks"

        # Found a single track, add it to the queue
        track = results["tracks"][0]
        audiotrack = lavalink.models.AudioTrack(track, interaction.user.id)
        self.add(interaction.user.id, audiotrack)

        return f"Enqueued track {track['info']['title']}"

    async def stop(self) -> None:
        """Stop the player."""
        for holder in self._interactions:
            holder.view.stop()
            try:
                await holder.interaction.delete_original_response()
                # Remove all the player managers
            except (discord.NotFound, discord.HTTPException):
                continue  # Message was already deleted
        self._interactions.clear()
        self.queue.clear()
        self.history.clear()
        await super().stop()


def add_lavalink(client: discord.Client) -> None:
    """Add a Lavalink client if there isn't one."""
    if not hasattr(client, "lavalink"):
        client.lavalink = lavalink.Client(client.user.id, CustomPlayer)  # type: ignore

        for node in client.lavalink_nodes:  # type: ignore
            client.lavalink.add_node(**node)  # type: ignore


class LavalinkVoiceClient(discord.VoiceClient):
    """Manage the voice connection."""

    # This is based on the official Lavalink example

    # pylint: disable=super-init-not-called
    def __init__(self, client: discord.Client, channel: discord.VoiceChannel):
        """Initialise the voice client."""
        self.client = client
        self.channel = channel

        add_lavalink(client)

        self.lavalink: lavalink.Client = client.lavalink  # type: ignore

    async def connect(
        self,
        *,
        self_deaf: bool = False,
        self_mute: bool = False,
        **_: t.Any,
    ) -> None:
        """Connect the voice client and create a player."""
        self.lavalink.player_manager.create(self.channel.guild.id)
        await self.channel.guild.change_voice_state(
            channel=self.channel,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

    async def disconnect(self, **_: t.Any) -> None:
        """Handle disconnects."""
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if player is None:
            await self.channel.guild.change_voice_state(channel=None)
            self.cleanup()
            return

        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()

    async def on_voice_server_update(self, data: t.Any) -> None:
        """Manage voice server update events."""
        await self.lavalink.voice_update_handler(
            {
                "t": "VOICE_SERVER_UPDATE",
                "d": data,
            }
        )

    async def on_voice_state_update(self, data: t.Any) -> None:
        """Manage voice state update events."""
        await self.lavalink.voice_update_handler(
            {
                "t": "VOICE_STATE_UPDATE",
                "d": data,
            }
        )


class MusicInput(ui.Modal, title="Music search"):
    """Music modal input."""

    music_input = ui.TextInput(
        label="Music to search for",
        required=True,
    )

    def __init__(self, player: CustomPlayer):
        """Initialize the input."""
        super().__init__()
        self.music_input.placeholder = choice(
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Hotel California")
        )  # Provide variaions in the placeholder
        self.player = player

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Submit the search."""
        response = await self.player.add_query(interaction, self.music_input.value)
        await interaction.response.send_message(response, ephemeral=True)
        await self.player.update_interactions()


class MusicView(ui.View):
    """View for the music cog."""

    def __init__(self, player: CustomPlayer, interaction: discord.Interaction):
        """View for the music cog."""
        super().__init__(timeout=870)

        self.player = player
        self.interaction = interaction

        if player.paused:
            self.pause_play.style = discord.ButtonStyle.secondary
        if not player.queue:
            self.next.disabled = (
                True  # Disable the next button if there is nothing in the queue
            )
        if player.repeat:
            self.repeat.style = discord.ButtonStyle.secondary
        if player.repeat_once:
            self.repeat_once.style = discord.ButtonStyle.secondary
        if player.shuffle:
            self.shuffle.style = discord.ButtonStyle.secondary

    async def interaction_check(
        self,
        interaction: discord.Interaction,
    ) -> bool:
        """Check whether to process the interaction."""
        if self.player.is_playing and isinstance(interaction.user, discord.Member):
            return interaction.user.id == self.player.current.requester or (  # type: ignore
                interaction.user.guild_permissions.mute_members
            )
        return True

    async def on_timeout(self) -> None:
        """Handle timeouts."""
        await self.player.remove_interaction(self.interaction)
        self.stop()

    @ui.button(emoji="\U000023ee\U0000fe0f", style=discord.ButtonStyle.primary, row=0)
    async def previous(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Go to the previous track."""
        await interaction.response.defer()
        await self.player.previous()

    @ui.button(emoji="\U000023ef\U0000fe0f", style=discord.ButtonStyle.primary, row=0)
    async def pause_play(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Play or pause the player."""
        await interaction.response.defer()
        await self.player.set_pause(not self.player.paused)
        await self.player.update_interactions()

    @ui.button(emoji="\U000023ed\U0000fe0f", style=discord.ButtonStyle.primary, row=0)
    async def next(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Go to the next track."""
        await interaction.response.defer()
        await self.player.skip()

    @ui.button(emoji="\U000023f9\U0000fe0f", style=discord.ButtonStyle.danger, row=1)
    async def stop_button(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Stop playing altogether."""
        await interaction.response.defer()
        await self.player.stop()
        if interaction.guild and interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect(force=True)

    @ui.button(emoji="\U0001f501", style=discord.ButtonStyle.primary, row=1)
    async def repeat(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Toggle repeat."""
        await interaction.response.defer()
        self.player.set_repeat(not self.player.repeat)
        await self.player.update_interactions()

    @ui.button(emoji="\U0001f502", style=discord.ButtonStyle.primary, row=1)
    async def repeat_once(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Toggle repeat once."""
        await interaction.response.defer()
        self.player.set_repeat_once(not self.player.repeat_once)
        await self.player.update_interactions()

    @ui.button(emoji="\U0001f500", style=discord.ButtonStyle.primary, row=1)
    async def shuffle(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Toggle shuffle."""
        await interaction.response.defer()
        self.player.set_shuffle(not self.player.shuffle)
        await self.player.update_interactions()

    @ui.button(emoji="\U0001f50e", style=discord.ButtonStyle.primary, row=0)
    async def search(
        self, interaction: discord.Interaction, _: ui.Button["MusicView"]
    ) -> None:
        """Search for a track."""
        await interaction.response.send_modal(MusicInput(self.player))


def duration_str(mili_sec: int) -> str:
    sec = mili_sec // 1000
    minute = sec // 60
    hour = minute // 60
    minute = minute % 60
    sec = sec % 60
    if hour:
        return f"{hour}:{minute:02d}:{sec:02d}"
    return f"{minute:02d}:{sec:02d}"


async def get_music_embed(
    player: CustomPlayer, interaction: discord.Interaction
) -> discord.Embed:
    """Get the interface for the music player."""
    if player.current:
        mus: lavalink.AudioTrack = player.current  # type: ignore
        embed = discord.Embed(
            title=f"Currently playing: {mus.title} ({duration_str(mus.duration)})",
            url=f"https://www.youtube.com/watch?v={mus.identifier}",
            color=0x99D9EA,
        )
        embed.set_thumbnail(
            url=f"https://img.youtube.com/vi/{mus.identifier}/hqdefault.jpg"
        )
    else:
        embed = discord.Embed(title="Music list", description=desc, color=0x99D9EA)
        if player.queue:
            embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{player.queue[0].identifier}/hqdefault.jpg"
            )

    if player.history:
        desc = ""

        for i in range(min(len(player.history), 5)):
            mus = player.history[-i]
            desc += "- [" + mus.title
            desc += f'](https://www.youtube.com/watch?v={mus.identifier} "{mus.title}") ({duration_str(mus.duration)})\n'
        embed.add_field(name="History", value=desc, inline=False)

    if player.queue:
        desc = ""

        for i in range(min(len(player.queue), 5)):
            mus = player.queue[i]
            desc += "- [" + mus.title
            desc += f'](https://www.youtube.com/watch?v={mus.identifier} "{mus.title}") ({duration_str(mus.duration)})\n'
        embed.add_field(name="Next", value=desc, inline=False)

    if interaction.client.user:
        embed.set_author(
            name=interaction.client.user.name,
            icon_url=interaction.client.user.display_avatar.url,
        )  # Idk why this would'nt be set, but anyways

    return embed


class MusicError(app_commands.CheckFailure):
    """Music error."""

    def __init__(self, code: int, message: str) -> None:
        """Initialize."""
        self.code = code
        self.message = message
        super().__init__()


class Music(commands.Cog):
    """Play music."""

    def __init__(self, bot: commands.Bot) -> None:
        """Load the cog."""
        self.bot = bot

        if not bot.lavalink_nodes:  # type: ignore
            raise ValueError("No Lavalink nodes configured !")

        add_lavalink(bot)
        lavalink.add_event_hook(self.track_hook)

        self.empty_channels: t.List[int] = []
        self.empty_vc_check.start()

    @tasks.loop(minutes=1)
    async def empty_vc_check(self) -> None:
        """Stop playing if nobody's listening."""
        new_channels = []
        for player in tuple(self.bot.lavalink.player_manager.players.values()):  # type: ignore
            if player and player.is_playing:
                guild = self.bot.get_guild(int(player.guild_id))
                if not guild:
                    await player.stop()
                    await self.force_disconnect(int(player.guild_id))
                    continue

                vocal = guild.get_channel(int(player.channel_id))
                if not vocal:
                    await player.stop()
                    await self.force_disconnect(int(player.guild_id))
                    continue

                if len(vocal.voice_states) <= 1:  # type: ignore
                    if guild.id in self.empty_channels:
                        await player.stop()
                        await self.force_disconnect(int(player.guild_id))
                    else:
                        new_channels.append(guild.id)
        self.empty_channels = new_channels

    async def cog_unload(self) -> None:
        """Cleanup the event hooks."""
        self.bot.lavalink._event_hooks.clear()

    async def force_disconnect(self, guild_id: int) -> None:
        """Force a websocket disconnection."""
        websocket = self.bot._connection._get_websocket(guild_id)
        await websocket.voice_state(guild_id, None)

    async def track_hook(self, event: lavalink.Event) -> None:
        """Disconnect the client upon reaching the end of queue."""
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            if guild and guild.voice_client:
                await guild.voice_client.disconnect(force=True)
            else:
                await self.force_disconnect(guild_id)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        """Catch the errors."""
        if isinstance(error, MusicError):
            await self.bot.httpcat(
                interaction, error.code, error.message, ephemeral=True
            )
            return
        raise error

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the interaction should be processed."""
        if (
            not interaction.guild
            or not interaction.guild_id
            or isinstance(interaction.user, discord.User)
        ):
            raise MusicError(412, "You need to be in a guild to use this command.")

        if not interaction.user.voice or not interaction.user.voice.channel:
            raise MusicError(412, "You must be in a voice channel to use this command.")

        should_connect = (
            interaction.command is not None and interaction.command.name == "play"
        )

        player = self.bot.lavalink.player_manager.create(interaction.guild_id)

        if not player.is_connected:
            if not should_connect:
                raise MusicError(417, "I'm not connected to a voice channel.")

            permissions = interaction.user.voice.channel.permissions_for(
                interaction.guild.me
            )

            if not permissions.connect or not permissions.speak:
                raise MusicError(
                    424,
                    (
                        "I don't have the permissions to join and "
                        "speak in your voice channel."
                    ),
                )

            if interaction.user.voice.channel.user_limit == len(
                interaction.user.voice.channel.members
            ):
                raise MusicError(
                    413, "I can't join this voice channel because it is full."
                )

            if interaction.guild.voice_client:  # Cleanup strange state
                await interaction.guild.voice_client.disconnect(force=True)

            await interaction.user.voice.channel.connect(cls=LavalinkVoiceClient)  # type: ignore
        else:
            if int(player.channel_id) != interaction.user.voice.channel.id:
                raise MusicError(421, "I'm already in a different voice channel.")

        return True

    @app_commands.guild_only()
    @app_commands.command()
    async def play(
        self, interaction: discord.Interaction, query: t.Optional[str]
    ) -> None:
        """Play music."""
        player: CustomPlayer = self.bot.lavalink.player_manager.get(
            interaction.guild_id
        )

        response = None

        if query is not None:
            response = await player.add_query(interaction, query)

        if player.queue and not player.is_playing:
            await player.play()

        if player.paused:
            await player.set_pause(False)

        view = MusicView(player, interaction)

        await player.add_interaction(interaction, view)

        await interaction.response.send_message(
            embed=await get_music_embed(player, interaction),
            view=view,
        )

        if response:
            await interaction.followup.send(response, ephemeral=True)

    @app_commands.guild_only()
    @app_commands.command()
    async def now(self, interaction: discord.Interaction) -> None:
        """Check the current status of player."""
        player: CustomPlayer = self.bot.lavalink.player_manager.get(
            interaction.guild_id
        )

        view = MusicView(player, interaction)

        await player.add_interaction(interaction, view)

        await interaction.response.send_message(
            embed=await get_music_embed(player, interaction),
            view=view,
        )


async def setup(bot: commands.Bot) -> None:
    """Setup the music extension."""
    await bot.add_cog(Music(bot))
