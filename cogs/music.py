"""MIT License.

Copyright (c) 2020 Faholan

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

from asyncio import sleep
import math
import re

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


def rq_check(ctx):
    p = ctx.bot.lavalink.player_manager.get(ctx.guild.id)
    if p:
        if p.is_playing:
            return ctx.author.id == p.current.requester
    return False

def get_bar(current, total):
    n = 20
    num = int(current / total * n)
    return "▬" * num + "▭" + "―" * (n - num)

class Music(commands.Cog):
    '''Listen to some [music](https://www.youtube.com/watch?v=dQw4w9WgXcQ "Hello I'm a link")'''
    def __init__(self, bot):
        self.bot = bot
        self.paginator_queue = dict()
        self.get_bar = get_bar

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'eu', 'default-node')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        bot.lavalink.add_event_hook(self.track_hook)
        self.empty_vc_check.start()

    async def cog_check(self,ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return ctx.guild

    def formatter(self, embed, ctx):
        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        embed.set_footer(text = f"{self.bot.user.name} music player", icon_url = ctx.me.avatar_url_as(static_format = "png"))

    @tasks.loop(seconds=5.0)
    async def empty_vc_check(self):
        for p in list(self.bot.lavalink.player_manager.players.values()):
            if p and p.is_playing:
                g = self.bot.get_guild(int(p.guild_id))
                vc = g.get_channel(int(p.channel_id))
                members = [m for m in vc.members if not m.bot]
                if len(members) == 0:
                    p.queue.clear()
                    await p.stop()
                    await self.connect_to(g.id, None)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
            # Disconnect from the channel -- there's nothing else to play.

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)
        # The above looks dirty, we could alternatively use `bot.shards[shard_id].ws` but that assumes
        # the bot instance is an AutoShardedBot.

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        try:
            player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        except:
            self.bot.lavalink.add_node('127.0.0.1', 2333, 'youshallnotpass', 'eu', 'default-node')
            player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))

        # Create returns a player if one exists, otherwise creates.

        should_connect = ctx.command.name in ('play')  # Add commands that require joining voice to work.

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Join a voicechannel first.')

        if not player.is_connected:
            if not should_connect:
                return await ctx.send('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                return await ctx.send('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                return await ctx.send('You need to be in my voicechannel.')

    @commands.command(aliases=['dc'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            embed = discord.Embed(title = "Not connected.", color = self.bot.colors['red'])
            self.formatter(embed, ctx)
            return await ctx.send(embed = embed)

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            embed = discord.Embed(title = "Please get in my voicechannel first.", color = self.bot.colors['red'])
            self.formatter(embed, ctx)
            return await ctx.send(embed = embed)

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        embed = discord.Embed(title = f"{STOP_EMOJI} | Disconnected.", color = self.bot.colors['yellow'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def find(self, ctx, *, query):
        """ Lists the first 10 search results from a given query. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found.')

        tracks = results['tracks'][:10]  # First 10 results

        o = ''
        for index, track in enumerate(tracks, start=1):
            track_title = track['info']['title']
            track_uri = track['info']['uri']
            o += f'`{index}.` [{track_title}]({track_uri})\n'

        embed = discord.Embed(color = discord.Color.blurple(), description = o)
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command(aliases=["np", "n", "playing"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def now(self, ctx):
        """ Shows some stats about the currently playing song. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            return await ctx.send(f"{PAUSE_EMOJI} | Nothing playing.")
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
        bar = "\n" + self.get_bar(cur, dur) if (cur and dur) else ""
        other = f"{(REPEAT_EMOJI if player.repeat else 'Repeat OFF')} | {(SHUFFLE_EMOJI if player.shuffle else 'Shuffle OFF')}"
        cleaned_title = await (commands.clean_content(escape_markdown=True)).convert(ctx, player.current.title)
        song = f"**[{cleaned_title}]({player.current.uri})**\n({position}/{duration}){bar}\n{other}"

        embed = discord.Embed(color = self.bot.colors['green'], title=f"{PLAY_EMOJI} | Now Playing", description = song)
        embed.set_image(url = f"https://img.youtube.com/vi/{player.current.identifier}/hqdefault.jpg")
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command(aliases=["resume"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def pause(self, ctx):
        """ Pauses/Resumes the current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{PAUSE_EMOJI} | Not playing.")

        if player.paused:
            await player.set_pause(False)
            embed = discord.Embed(title=f"{PLAY_EMOJI} | Resumed", color = self.bot.colors['blue'])
        else:
            await player.set_pause(True)
            embed = discord.Embed(title = f"{PAUSE_EMOJI} | Paused", color = self.bot.colors['blue'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command(aliases=["p"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        await sleep(1)
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        query = query.strip("<>")

        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("Nothing found!")

        embed = discord.Embed(color = self.bot.colors['green'])

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester = ctx.author.id, track = track)

            embed.title = f"{PLAY_EMOJI} | Playlist Enqueued!"
            other = f"{(REPEAT_EMOJI if player.repeat else 'Repeat OFF')} | {(SHUFFLE_EMOJI if player.shuffle else 'Shuffle OFF')}"
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks\n{other}'
            self.formatter(embed, ctx)
            await ctx.send(embed = embed)
        else:
            track = results["tracks"][0]
            embed.title = f"{PLAY_EMOJI} | Track Enqueued"
            other = f"{(REPEAT_EMOJI if player.repeat else 'Repeat OFF')} | {(SHUFFLE_EMOJI if player.shuffle else 'Shuffle OFF')}"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})\n{other}'
            embed.set_image(url = f"https://img.youtube.com/vi/{track['info']['identifier']}/hqdefault.jpg")
            embed.set_footer(text = f"Use {ctx.prefix}np for playing status | {self.bot.user.name} Music Player", icon_url = self.bot.user.avatar_url_as(static_format="png"))
            embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            await ctx.send(embed = embed)

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended = True)
            player.add(requester = ctx.author.id, track = track)

        if not player.is_playing:
            await player.play()
            await player.set_volume(100)

    @commands.command(aliases=["q"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def queue(self, ctx, page: int = 1):
        """ Shows the player's queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send(f"{PAUSE_EMOJI} | Nothing queued.")

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ""
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f"{index + 1}. [**{track.title}**]({track.uri})\n"

        embed = discord.Embed(colour = self.bot.colors['blue'], description = f'{len(player.queue)} {"tracks" if len(player.queue) > 1 else "track"}\n\n{queue_list}')
        embed.set_footer(text = f"Viewing page {page}/{pages}")
        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def remove(self, ctx, index: int):
        """ Removes an item from the player's queue with the given index. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            embed = discord.Embed(title=f"{PAUSE_EMOJI} | Nothing queued.", color = self.bot.colors['red'])
            self.formatter(embed, ctx)
            return await ctx.send(embed=embed)

        if index > len(player.queue) or index < 1:
            embed = discord.Embed(title = f"Index has to be **between** 1 and {len(player.queue)}.", color = self.bot.colors['red'])
            self.formatter(embed, ctx)
            return await ctx.send(embed = embed)

        removed = player.queue.pop(index - 1)  # Account for 0-index.

        embed = discord.Embed(title = f"Removed **{removed.title}** from the queue.", color = self.bot.colors['yellow'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command(aliases = ["loop"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def repeat(self, ctx):
        """ Repeats the current song until the command is invoked again. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            embed = discord.Embed(title = f"{PAUSE_EMOJI} | Nothing playing.", color = self.bot.colors['red'])
            self.formatter(embed, ctx)
            return await ctx.send(embed = embed)

        player.repeat = not player.repeat
        embed = discord.Embed(title = f"{REPEAT_EMOJI} | Repeat " + ("enabled" if player.repeat else "disabled"), color = self.bot.colors['blue'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.check(rq_check)
    async def seek(self, ctx, *, time: str):
        """ Seeks to a given position in a track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        seconds = time_rx.search(time)
        if not seconds:
            return await ctx.send("You need to specify the amount of seconds to skip!")

        seconds = int(seconds.group()) * 1000
        if time.startswith("-"):
            seconds *= -1
        track_time = player.position + seconds
        await player.seek(track_time)

        await ctx.send(f"Moved track to **{lavalink.utils.format_time(track_time)}**")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.check(rq_check)
    async def shuffle(self, ctx):
        """ Shuffles the player's queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            embed = discord.Embed(title = f"{PAUSE_EMOJI} | Nothing playing.", color = self.bot.colors['red'])
            self.formatter(embed, ctx)
            return await ctx.send(embed = embed)
        player.shuffle = not player.shuffle
        embed = discord.Embed(title = f"{SHUFFLE_EMOJI} | Shuffle " + ("enabled" if player.shuffle else "disabled"), color=self.bot.colors['blue'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command(aliases = ["forceskip"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def skip(self, ctx):
        """ Skips the current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{PAUSE_EMOJI} | Not playing.")

        await player.skip()
        embed = discord.Embed(title = f"{SKIP_EMOJI} | Skipped.", color = self.bot.colors['blue'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check(rq_check)
    async def stop(self, ctx):
        """ Stops the player and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send(f"{PAUSE_EMOJI} | Not playing.")

        player.queue.clear()
        await player.stop()
        embed = discord.Embed(title = f"{STOP_EMOJI} | Stopped. (Queue cleared)", color = self.bot.colors['yellow'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)


    @commands.command(aliases=["vol"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.check(rq_check)
    async def volume(self, ctx, volume: int = None):
        """ Changes the player's volume. Must be between 0 and 1000. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not volume:
            embed = discord.Embed(title = f"{VOLUME_ON_EMOJI} | {player.volume}%", color = self.bot.colors['blue'])
            self.formatter(embed, ctx)
            return await ctx.send(embed = embed)

        await player.set_volume(volume)
        embed = discord.Embed(title = f"{VOLUME_ON_EMOJI} | Set to {player.volume}%", color = self.bot.colors['blue'])
        self.formatter(embed, ctx)
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Music(bot))
