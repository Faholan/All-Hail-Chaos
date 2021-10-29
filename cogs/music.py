"""MIT License.

Copyright (c) 2020-2021 Faholan

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

import math
import re
import typing as t
from asyncio import sleep

import discord
from discord.ext import commands, tasks

import lavalink

# ----- define constants ----- #
time_rx = re.compile("[0-9]+")
url_rx = re.compile("https?:\\/\\/(?:www\\.)?.+")
REPEAT_EMOJI = "<:repeat:520997116009513008>"
STOP_EMOJI = ":stop_button:"
LIVE_EMOJI = ":red_circle:"
SHUFFLE_EMOJI = ":twisted_rightwards_arrows:"
VOLUME_OFF_EMOJI = ":mute:"
VOLUME_ON_EMOJI = ":speaker:"
PAUSE_EMOJI = ":pause_button:"
PLAY_EMOJI = ":arrow_forward:"
VOLUME_UP_EMOJI = ":loud_sound:"
VOLUME_DOWN_EMOJI = ":sound:"
LYRIC_EMOJI = ":clipboard:"
TRASH_EMOJI = ":wastebasket:"
SKIP_EMOJI = ":next_track:"
BACK_EMOJI = ":previous_track:"
# ---------------------------- #


def rq_check(ctx: commands.Context) -> bool:
    """Restrict some commands to the current requester."""
    player = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
    if player and player.is_playing:
        return ctx.author.id == player.current.requester or (
            ctx.author.guild_permissions.mute_members
        )
    return False


def get_bar(current: int, total: int) -> str:
    """Get the progress bar."""
    barsize = 20
    num = int(current / total * barsize)
    return "▬" * num + "▭" + "―" * (barsize - num)


class Music(commands.Cog):
    """Listen to some [music](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Hello I'm a link")."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Music."""
        self.bot = bot
        self.paginator_queue = {}
        self.get_bar = get_bar

        if not hasattr(bot, "lavalink"):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(**bot.lavalink_credentials)
            bot.add_listener(
                bot.lavalink.voice_update_handler,
                "on_socket_response",
            )

        bot.lavalink.add_event_hook(self.track_hook)
        self.empty_channels: t.List[int] = []
        self.empty_vc_check.start()

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Music can only be played in guilds."""
        if not ctx.guild:
            raise commands.NoPrivateMessage()
        await self.ensure_voice(ctx)
        return True

    def formatter(self, embed: discord.Embed, ctx: commands.Context) -> None:
        """Format the embed."""
        embed.set_author(
            name=str(ctx.author),
            icon_url=str(ctx.author.avatar_url),
        )
        embed.set_footer(
            text=f"{self.bot.user.name} music player",
            icon_url=ctx.bot.user.avatar_url_as(static_format="png"),
        )

    @tasks.loop(minutes=1)
    async def empty_vc_check(self) -> None:
        """Stop playing if nobody is listening."""
        new_channels = []
        for player in list(self.bot.lavalink.player_manager.players.values()):
            if player and player.is_playing:
                guild = self.bot.get_guild(int(player.guild_id))
                vocal = guild.get_channel(int(player.channel_id))
                if len(vocal.voice_states) <= 1:
                    if guild.id in self.empty_channels:
                        player.queue.clear()
                        await player.stop()
                        await self.connect_to(guild.id, None)
                    else:
                        new_channels.append(guild.id)
        self.empty_channels = new_channels

    def cog_unload(self) -> None:
        """Do some cleanup."""
        self.bot.lavalink._event_hooks.clear()

    async def track_hook(self, event: t.Any) -> None:
        """Disconnect the player upon reaching the end of the queue."""
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
            # Disconnect from the channel -- there's nothing else to play.

    async def connect_to(
        self,
        guild_id: int,
        channel_id: t.Optional[str],
    ) -> None:
        """Connect to the given voicechannel ID. A channel_id of `None` means disconnect."""
        websocket = self.bot._connection._get_websocket(guild_id)
        await websocket.voice_state(str(guild_id), channel_id)
        # We could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    async def ensure_voice(self, ctx: commands.Context) -> None:
        """Ensure that the bot and command author are in the same voicechannel."""
        try:
            player = self.bot.lavalink.player_manager.create(
                ctx.guild.id,
                endpoint=str(ctx.guild.region),
            )
        except lavalink.exceptions.NodeException:
            self.bot.lavalink.add_node(**self.bot.lavalink_credentials)
            player = self.bot.lavalink.player_manager.create(
                ctx.guild.id,
                endpoint=str(ctx.guild.region),
            )

        # Create returns a player if one exists, otherwise creates.

        should_connect = ctx.command.name == "play"

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Join a voicechannel first.")
            return

        if not player.is_connected:
            if not should_connect:
                await ctx.send("Not connected.")
                return

            permissions = ctx.author.voice.channel.permissions_for(
                ctx.me or await ctx.guild.fetch_member(ctx.bot.user.id)
            )

            if not permissions.connect or not permissions.speak:
                await ctx.send("I need the `CONNECT` and `SPEAK` permissions.")
                return

            player.store("channel", ctx.channel.id)
            await self.connect_to(
                ctx.guild.id,
                str(ctx.author.voice.channel.id),
            )
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send("You need to be in my voicechannel.")

    @commands.command(aliases=["dc"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def disconnect(self, ctx: commands.Context) -> None:
        """Disconnect the player from the voice channel and clear its queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            embed = discord.Embed(title="Not connected.",
                                  colour=discord.Colour.red())
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return

        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            embed = discord.Embed(
                title="Please get in my voicechannel first.",
                colour=discord.Colour.red(),
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        embed = discord.Embed(
            title=f"{STOP_EMOJI} | Disconnected.",
            colour=0xFFFF00,
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def find(self, ctx: commands.Context, *, query: str) -> None:
        """List the first 10 search results from a given query."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not query.startswith("ytsearch:") and not query.startswith("scsearch:"):
            query = "ytsearch:" + query

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            await ctx.send("Nothing found.")
            return

        tracks = results["tracks"][:10]  # First 10 results

        output = ""
        for index, track in enumerate(tracks, start=1):
            track_title = track["info"]["title"]
            track_uri = track["info"]["uri"]
            output += f"`{index}.` [{track_title}]({track_uri})\n"

        embed = discord.Embed(
            colour=discord.Colour.blurple(),
            description=output,
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=["np", "n", "playing"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def now(self, ctx: commands.Context) -> None:
        """Show some stats about the currently playing song."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            await ctx.send(f"{PAUSE_EMOJI} | Nothing playing.")
            return
        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = f"{LIVE_EMOJI} LIVE"
        else:
            duration = lavalink.utils.format_time(player.current.duration)
        cur = None
        dur = None
        if not player.current.stream:
            cur = int(player.position / 1000)
            dur = int(player.current.duration / 1000)
        progressbar = "\n" + self.get_bar(cur, dur) if (cur and dur) else ""
        other = f"{(REPEAT_EMOJI if player.repeat else 'Repeat OFF')} | {(SHUFFLE_EMOJI if player.shuffle else 'Shuffle OFF')}"
        cleaned_title = await (commands.clean_content(escape_markdown=True)).convert(
            ctx, player.current.title
        )
        song = f"**[{cleaned_title}]({player.current.uri})**\n({position}/{duration}){progressbar}\n{other}"

        embed = discord.Embed(
            colour=discord.Colour.green(),
            title=f"{PLAY_EMOJI} | Now Playing",
            description=song,
        )
        embed.set_image(
            url=f"https://img.youtube.com/vi/{player.current.identifier}/hqdefault.jpg",
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=["resume"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def pause(self, ctx: commands.Context) -> None:
        """Pause/Resume the current track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            await ctx.send(f"{PAUSE_EMOJI} | Not playing.")
            return

        if player.paused:
            await player.set_pause(False)
            embed = discord.Embed(
                title=f"{PLAY_EMOJI} | Resumed",
                colour=discord.Colour.blue(),
            )
        else:
            await player.set_pause(True)
            embed = discord.Embed(
                title=f"{PAUSE_EMOJI} | Paused",
                colour=discord.Colour.blue(),
            )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=["p"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """Search and play a song from a given query."""
        await sleep(0.5)
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        query = query.strip("<>")

        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            await ctx.send("Nothing found!")
            return

        embed = discord.Embed(
            colour=discord.Colour.green(),
        )

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = f"{PLAY_EMOJI} | Playlist Enqueued!"
            other = f"{(REPEAT_EMOJI if player.repeat else 'Repeat OFF')} | {(SHUFFLE_EMOJI if player.shuffle else 'Shuffle OFF')}"
            embed.description = (
                f"{results['playlistInfo']['name']} - {len(tracks)} tracks\n{other}"
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
        else:
            track = results["tracks"][0]
            embed.title = f"{PLAY_EMOJI} | Track Enqueued"
            other = f"{(REPEAT_EMOJI if player.repeat else 'Repeat OFF')} | {(SHUFFLE_EMOJI if player.shuffle else 'Shuffle OFF')}"
            embed.description = (
                f"[{track['info']['title']}]({track['info']['uri']})\n{other}"
            )
            embed.set_image(
                url=f"https://img.youtube.com/vi/{track['info']['identifier']}/hqdefault.jpg",
            )
            embed.set_footer(
                text=f"Use {ctx.prefix}np for playing status | {self.bot.user.name} Music Player",
                icon_url=self.bot.user.avatar_url_as(static_format="png"),
            )
            embed.set_author(
                name=str(ctx.author),
                icon_url=str(ctx.author.avatar_url),
            )
            await ctx.send(embed=embed)

            track = lavalink.models.AudioTrack(
                track,
                ctx.author.id,
                recommended=True,
            )
            player.add(requester=ctx.author.id, track=track)

        if not player.is_playing:
            await player.play()
            await player.set_volume(100)

    @commands.command(aliases=["q"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def queue(self, ctx: commands.Context, page: int = 1) -> None:
        """Show the player's queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            await ctx.send(f"{PAUSE_EMOJI} | Nothing queued.")
            return

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ""
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f"{index + 1}. [**{track.title}**]({track.uri})\n"

        embed = discord.Embed(
            colour=discord.Colour.blue(),
            description=f"{len(player.queue)} {'tracks' if len(player.queue) > 1 else 'track'}\n\n{queue_list}",
        )
        embed.set_footer(text=f"Viewing page {page}/{pages}")
        embed.set_author(
            name=str(ctx.author),
            icon_url=str(ctx.author.avatar_url),
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def remove(self, ctx: commands.Context, index: int) -> None:
        """Remove an item from the player's queue with the given index."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            embed = discord.Embed(
                title=f"{PAUSE_EMOJI} | Nothing queued.",
                colour=discord.Colour.red(),
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return

        if index > len(player.queue) or index < 1:
            embed = discord.Embed(
                title=f"Index has to be **between** 1 and {len(player.queue)}.",
                colour=discord.Colour.red(),
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return

        removed = player.queue.pop(index - 1)  # Account for 0-index.

        embed = discord.Embed(
            title=f"Removed **{removed.title}** from the queue.", colour=0xFFFF00
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=["loop"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def repeat(self, ctx: commands.Context) -> None:
        """Repeat the current song until the command is invoked again."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(
                title=f"{PAUSE_EMOJI} | Nothing playing.",
                colour=discord.Colour.red(),
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return

        player.repeat = not player.repeat
        embed = discord.Embed(
            title=f"{REPEAT_EMOJI} | Repeat "
            + ("enabled" if player.repeat else "disabled"),
            colour=discord.Colour.blue(),
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(rq_check)
    async def seek(self, ctx: commands.Context, *, time: str) -> None:
        """Seek to a given position in a track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        raw_seconds = time_rx.search(time)
        if not raw_seconds:
            await ctx.send("You need to specify the amount of seconds to skip!")
            return

        seconds = int(raw_seconds.group()) * 1000
        if time.startswith("-"):
            seconds *= -1
        track_time = player.position + seconds
        await player.seek(track_time)

        await ctx.send(f"Moved track to **{lavalink.utils.format_time(track_time)}**")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.check(rq_check)
    async def shuffle(self, ctx: commands.Context) -> None:
        """Shuffle the player's queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            embed = discord.Embed(
                title=f"{PAUSE_EMOJI} | Nothing playing.", colour=discord.Colour.red()
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return
        player.shuffle = not player.shuffle
        embed = discord.Embed(
            title=f"{SHUFFLE_EMOJI} | Shuffle "
            + ("enabled" if player.shuffle else "disabled"),
            colour=discord.Colour.blue(),
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=["forceskip"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def skip(self, ctx: commands.Context) -> None:
        """Skip the current track."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            await ctx.send(f"{PAUSE_EMOJI} | Not playing.")
            return

        await player.skip()
        embed = discord.Embed(
            title=f"{SKIP_EMOJI} | Skipped.",
            colour=discord.Colour.blue(),
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the player and clear its queue."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            await ctx.send(f"{PAUSE_EMOJI} | Not playing.")
            return

        player.queue.clear()
        await player.stop()
        embed = discord.Embed(
            title=f"{STOP_EMOJI} | Stopped. (Queue cleared)",
            colour=0xFFFF00,
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=["vol"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.check(rq_check)
    async def volume(self, ctx: commands.Context, volume: int = None) -> None:
        """Change the player's volume. Must be between 0 and 1000."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not volume:
            embed = discord.Embed(
                title=f"{VOLUME_ON_EMOJI} | {player.volume}%",
                colour=discord.Colour.blue(),
            )
            self.formatter(embed, ctx)
            await ctx.send(embed=embed)
            return

        await player.set_volume(volume)
        embed = discord.Embed(
            title=f"{VOLUME_ON_EMOJI} | Set to {player.volume}%",
            colour=discord.Colour.blue(),
        )
        self.formatter(embed, ctx)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Music cog."""
    bot.add_cog(Music(bot))
