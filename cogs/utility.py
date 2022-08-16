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

import asyncio
import codecs
import inspect
import os
import pathlib
from datetime import datetime
from os import path
from sys import version
from textwrap import dedent
from typing import Callable

import discord
import humanize
import psutil
from discord.ext import commands, menus, tasks
from discord.utils import escape_markdown

ZWS = "\u200b"
POLL_EMOJIS = [chr(0x1F1E6 + i) for i in range(0x1A)]
# :regional_indicator_a: up to :regional_indicator_z


class SnipeSource(menus.ListPageSource):
    """Source for the snipe."""

    def __init__(self, embeds_dict: list) -> None:
        """Initialize SnipeSource."""
        super().__init__(embeds_dict, per_page=1)

    async def format_page(
        self,
        menu: menus.Menu,
        page: dict,
    ) -> discord.Embed:
        """Create an embed from a dict."""
        embed = discord.Embed(
            title=page["title"].format(
                message_number=menu.current_page + 1,
                max_number=self.get_max_pages(),
            ),
            colour=0xFFFF00,
        )
        embed.set_author(
            name=page["author"]["name"],
            icon_url=page["author"]["icon_url"],
        )
        for field in page["fields"]:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=False,
            )
        embed.timestamp = page["timestamp"]
        return embed


class SauceSource(menus.ListPageSource):
    """Source for the sauce command."""

    async def format_page(self, menu: menus.Menu, page: str):
        """Format the page of code."""
        max_pages = self.get_max_pages()
        embed = discord.Embed(description=page, colour=discord.Colour.purple())
        if max_pages > 1:
            embed.set_footer(text=f"Page {menu.current_page + 1}/{max_pages}")
        return embed


def check_administrator() -> Callable:
    """Check for admin rights."""

    def predictate(ctx: commands.Context) -> bool:
        """Process the check."""
        if isinstance(ctx.channel, discord.TextChannel):
            return ctx.channel.permissions_for(ctx.author).administrator
        return True

    return commands.check(predictate)


def secondes(number: int) -> str:
    """Convert a number of seconds in human-readable format."""
    formatted = []
    if number >= 86400:
        formatted.append(f"{number // 86400} days")
        number %= 86400
    if number >= 3600:
        formatted.append(f"{number // 3600} hours")
        number %= 3600
    if number >= 60:
        formatted.append(f"{number // 60} minutes")
        number %= 60
    if number > 0:
        formatted.append(f"{number} seconds")
    return ", ".join(formatted)


class Utility(commands.Cog):
    """Manage the bot and get informations about it."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the utility."""
        self.bot = bot
        self.snipe_list = {}
        if self.bot.discord_bots:
            self.discord_bots.start()
        if self.bot.xyz:
            self.xyz.start()
        if self.bot.discord_bot_list:
            self.discord_bot_list.start()

    @commands.command(ignore_extra=True)
    async def add(self, ctx: commands.Context) -> None:
        """Return a link to add the bot to a new server."""
        link = discord.utils.oauth_url(
            str(self.bot.user.id),
            permissions=discord.Permissions(self.bot.invite_permissions),
        )
        await ctx.send(f"You can add me using this link : {link}")

    @commands.command(ignore_extra=True)
    async def block(self, ctx: commands.Context) -> None:
        """Imped me from DMing you (except if you DM me commands)."""
        async with self.bot.pool.acquire(timeout=5) as database:
            result = await database.fetchrow(
                "SELECT * FROM public.block WHERE id=$1",
                ctx.author.id,
            )
            if result:
                await database.execute(
                    "DELETE FROM public.block WHERE id=$1",
                    ctx.author.id,
                )
                await ctx.send("You unblocked me")
            else:
                await database.execute(
                    "INSERT INTO public.block VALUES ($1)",
                    ctx.author.id,
                )
                await ctx.send("You blocked me")

    @commands.command(ignore_extra=True)
    async def code(self, ctx: commands.Context) -> None:
        """Return stats about the bot's code.

        Credits to Dutchy#6127 for this command
        """
        total = 0
        file_amount = 0
        list_of_files = []
        for filepath, _, files in os.walk("."):
            for name in files:
                if name.endswith(".py"):
                    file_lines = 0
                    file_amount += 1
                    with codecs.open(
                            "./" + str(pathlib.PurePath(filepath, name)), "r",
                            "utf-8") as file:
                        for _, line in enumerate(file):
                            if line.strip().startswith("#") or len(
                                    line.strip()) == 0:
                                pass
                            else:
                                total += 1
                                file_lines += 1
                    final_path = filepath + path.sep + name
                    list_of_files.append(
                        final_path.split("." + path.sep)[-1] +
                        f" : {file_lines} lines")
        embed = discord.Embed(colour=0xFFFF00)
        embed.add_field(
            name=f"{self.bot.user.name}'s structure",
            value="\n".join(sorted(list_of_files)),
        )
        embed.set_footer(
            text=(f"I am made of {total} lines of Python, spread across "
                  f"{file_amount} files !"), )
        await ctx.send(embed=embed)

    @commands.command()
    async def contact(self, ctx: commands.Context, *, message: str) -> None:
        """Contact my staff for anything you think requires their attention."""
        embed = discord.Embed(
            title=f"Message from an user ({ctx.author.id})",
            description=message,
        )
        embed.set_author(
            name=f"{ctx.author.name}#{ctx.author.discriminator}",
            icon_url=str(ctx.author.avatar_url),
        )
        channel = self.bot.get_channel(self.bot.contact_channel_id)
        if channel:
            await channel.send(embed=embed)
            await ctx.send("Your message has been successfully sent")
        else:
            await ctx.send(
                "Sorry but my owner hasn't correctly configured this")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def github(self, ctx: commands.Context) -> None:
        """Create or delete a webhook to get updates about the bot."""
        if not hasattr(self.bot, "github") or not self.bot.github_repo:
            await ctx.send(
                "This command hasn't been configured by the developer yet")
            return
        for hook in await ctx.channel.webhooks():
            if hook.user == self.bot.user:
                await ctx.send(
                    "I already have created a webhook in this channel. Do you"
                    " want me to delete it (y/n)")

                def check(message: discord.Message) -> bool:
                    return (message.author == ctx.author
                            and (message.content.lower().startswith("y") or
                                 (message.content.lower().startswith("n")))
                            and message.channel == ctx.channel)

                try:
                    msg = await self.bot.wait_for(
                        "message",
                        check=check,
                        timeout=30.0,
                    )
                except asyncio.TimeoutError:
                    await ctx.send("The webhook wasn't deleted")
                    return
                if msg.content.lower().startswith("y"):
                    repo = self.bot.github.get_repo(self.bot.github_repo)
                    for webhook in repo.get_hooks():
                        if webhook.config["url"].startswith(hook.url):
                            webhook.delete()
                            break
                    await hook.delete()
                    await ctx.send("Webhook deleted")
                    return
                await ctx.send("The webhook wasn't deleted")
                return

        repo = self.bot.github.get_repo(self.bot.github_repo)
        hook = await ctx.channel.create_webhook(
            name=f"{self.bot.user.name} GitHub updates")
        repo.create_hook(
            "web",
            {
                "url": hook.url + "/github",
                "content_type": "json"
            },
            [
                "fork",
                "create",
                "delete",
                "pull_request",
                "push",
                "issue_comment",
                "project",
                "project_card",
                "project_column",
            ],
        )
        await ctx.send("Webhook successfully created !")
        await self.bot.log_channel.send(
            f"Webhook created : {ctx.guild} - {ctx.channel} ({ctx.author})")

    @commands.command(ignore_extra=True)
    async def info(self, ctx: commands.Context) -> None:
        """Get info about me."""
        delta = datetime.utcnow() - self.bot.last_update
        link = discord.utils.oauth_url(
            str(self.bot.user.id),
            permissions=discord.Permissions(self.bot.invite_permissions),
        )
        app = await self.bot.application_info()
        embed = discord.Embed(
            title=f"Informations about {self.bot.user}",
            description=(
                f'[Invite Link]({link} "Please stay at home and use bots")'
                f"\n[Support Server Invite]({self.bot.support})"),
            colour=discord.Colour.random(),
        )
        embed.set_author(
            name=str(ctx.author),
            icon_url=str(ctx.author.avatar_url),
        )
        embed.set_footer(
            text=(f"Discord.py version {discord.__version__}, Python version "
                  f"{version.split(' ', maxsplit=1)[0]}"), )
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        embed.add_field(
            name=f"My owner{'s' if app.team else ''} :",
            value=", ".join([str(member) for member in app.team.members])
            if app.team else str(app.owner),
            inline=False,
        )
        artist = self.bot.get_user(372336190919147522)
        if artist:
            embed.add_field(
                name="Credits for the superb profile pic :",
                value=str(artist),
                inline=False,
            )
        embed.add_field(
            name="I'm very social. Number of servers i'm in :",
            value=str(len(self.bot.guilds)),
            inline=False,
        )
        members = sum(guild.member_count for guild in self.bot.guilds)
        embed.add_field(
            name="I know pretty much everybody.",
            value=f"In fact I only know {members} users",
            inline=False,
        )
        embed.add_field(
            name="I've got many commands",
            value=f"More exactly {len(self.bot.commands)} commands",
            inline=False,
        )
        embed.add_field(
            name="GitHub repository",
            value=(f"[It's open source !]({self.bot.github_link})"),
        )
        embed.add_field(
            name="Description page :",
            value=(
                f"[top.gg page]({self.bot.top_gg})\n"
                f"[bots on discord page]({self.bot.bots_on_discord})\n"
                f"[Discord bots page]({self.bot.discord_bots_page})\n"
                f"[Discord bot list page]({self.bot.discord_bot_list_page})"),
            inline=False,
        )
        embed.add_field(
            name="Libraries used :",
            value=(
                "[DiscordRep](https://discordrep.com/) : Reputation\n"
                '[Lavalink](https://github.com/Frederikam/Lavalink/ "I thank'
                'chr1sBot for learning about this") : Whole Music Cog'
                '\n[discord.py](https://discordapp.com/ "More exactly '
                'discord.ext.commands") : Basically this whole bot\n'
                '[NASA](https://api.nasa.gov/ "Yes I hacked the NASA") : '
                "Whole NASA Cog"),
            inline=False,
        )
        embed.add_field(
            name="Time since last update :",
            value=secondes(delta.seconds + 86400 * delta.days),
            inline=False,
        )
        embed.add_field(
            name="Privacy policy",
            value=f"[{self.bot.user.name} Privacy policy]({self.bot.privacy})",
        )
        process = psutil.Process()
        with process.oneshot():
            mem = process.memory_full_info()
            name = process.name()
            pid = process.pid
            threads = process.num_threads()
            embed.add_field(
                name="Memory usage :",
                value=(
                    f"Using {humanize.naturalsize(mem.rss)} physical memory "
                    f"and {humanize.naturalsize(mem.vms)} virtual memory, "
                    f"{humanize.naturalsize(mem.uss)} of which unique to "
                    "this process.\nRunning on PID "
                    f"{pid} (`{name}`) with {threads} thread(s)."),
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    @commands.guild_only()
    @commands.check_any(commands.is_owner(),
                        commands.has_permissions(administrator=True))
    async def quit(self, ctx: commands.Context) -> None:
        """Make the bot quit the server.

        Only a server admin can use this
        """
        try:
            if await self.bot.fetch_confirmation(
                    ctx, f"Do you really want me to leave {ctx.guild.name} ?"):
                await ctx.guild.leave()
        except asyncio.TimeoutError:
            await ctx.send("Aborting")

    @commands.command(aliases=["sauce"])
    async def source(
        self,
        ctx: commands.Context,
        *,
        command_name: str,
    ) -> None:
        """Get the source code of a command."""
        command = self.bot.get_command(command_name)
        if not command:
            await ctx.send(f"No command named `{command_name}` found.")
            return
        try:
            source_lines, _ = inspect.getsourcelines(command.callback)
        except (TypeError, OSError):
            await ctx.send("I was unable to retrieve the source for "
                           f"`{command_name}` for some reason.")
            return

        # Get rid of extra \n
        source_lines = dedent("".join(source_lines).replace(
            "```", f"`{ZWS}`{ZWS}`")).split("\n")
        paginator = commands.Paginator(
            prefix="```py",
            suffix="```",
            max_size=2048,
        )
        for line in source_lines:
            paginator.add_line(line)
        pages = menus.MenuPages(
            source=SauceSource(
                paginator.pages,
                per_page=1,
            ),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

    @commands.command(ignore_extra=True)
    @commands.guild_only()
    async def snipe(self, ctx: commands.Context) -> None:
        """Return up to the 20 most recently edited / deleted messages."""
        embed_dicts = self.snipe_list.get(ctx.channel.id)
        if embed_dicts:
            pages = menus.MenuPages(
                source=SnipeSource(embed_dicts),
                clear_reactions_after=True,
            )
            await pages.start(ctx)
        else:
            await ctx.send("I don't have any record for this channel yet")

    @commands.Cog.listener("on_message_edit")
    async def snipe_edit(self, before: discord.Message,
                         after: discord.Message) -> None:
        """Log edited messages."""
        if before.content != after.content:
            embed_dicts = self.snipe_list.get(before.channel.id, [])
            embed_dict = {
                "title": "Message edited ({message_number}/{max_number})",
                "author": {
                    "name": str(before.author),
                    "icon_url": str(before.author.avatar_url),
                },
                "fields": [],
            }
            original = before.content.replace("```", f"`{ZWS}`{ZWS}`")[:1016]
            embed_dict["fields"] += [{
                "name": "Original message",
                "value": f"```\n{original}\n```",
            }]

            new = after.content.replace("```", f"`{ZWS}`{ZWS}`")[:1016]
            embed_dict["fields"] += [{
                "name": "Edited message",
                "value": f"```\n{new}\n```",
            }]

            embed_dict["timestamp"] = datetime.utcnow()
            embed_dicts = [embed_dict] + embed_dicts
            self.snipe_list[before.channel.id] = embed_dicts[:20]

    @commands.Cog.listener("on_message_delete")
    async def snipe_delete(self, message: discord.Message) -> None:
        """Log deleted messages."""
        if message.content:
            embed_dicts = self.snipe_list.get(message.channel.id, [])
            embed_dict = {
                "title": "Message deleted ({message_number}/{max_number})",
                "author": {
                    "name": str(message.author),
                    "icon_url": str(message.author.avatar_url),
                },
                "fields": [],
            }
            content = message.content.replace("```", f"`{ZWS}`{ZWS}`")[:1016]
            embed_dict["fields"] += [{
                "name": "Original message",
                "value": f"```\n{content}\n```",
            }]
            embed_dict["timestamp"] = datetime.utcnow()
            embed_dicts = [embed_dict] + embed_dicts
            self.snipe_list[message.channel.id] = embed_dicts[:20]

    @commands.command()
    @commands.cooldown(2, 600, commands.BucketType.user)
    async def suggestion(
        self,
        ctx: commands.Context,
        subject: str,
        *,
        idea: str,
    ) -> None:
        """Make suggestions for the bot.

        Your Discord name will be recorded and publicly associated to the idea.
        """
        embed = discord.Embed(
            title=f"Suggestion for **{subject}**",
            description=(
                f"{ctx.author.mention} ({ctx.author.id})'s idea: {idea}"),
            colour=0xFFFF00,
        )
        embed.set_author(
            name=str(ctx.author),
            icon_url=str(ctx.author.avatar_url),
        )
        if self.bot.suggestion_channel:
            await self.bot.suggestion_channel.send(embed=embed)
            await ctx.send("Thanks for your participation in this project !")
        else:
            await ctx.send(
                "Sorry but my owner hasn't correctly configured this command")

    @tasks.loop(minutes=30)
    async def discord_bots(self):
        """Update the profile ont discord.bots.gg."""
        await self.bot.aio_session.post(
            f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",
            json={"guildCount": len(self.bot.guilds)},
            headers={"authorization": self.bot.discord_bots},
        )

    @tasks.loop(minutes=30)
    async def xyz(self):
        """Update the profile on bots.ondiscord.xyz."""
        await self.bot.aio_session.post(
            "https://bots.ondiscord.xyz/bot-api/bots/"
            f"{self.bot.user.id}/guilds",
            json={"guildCount": len(self.bot.guilds)},
            headers={"Authorization": self.bot.xyz},
        )

    @tasks.loop(minutes=30)
    async def discord_bot_list(self):
        """Update the profile on discordbotlist.com."""
        await self.bot.aio_session.post(
            f"https://discordbotlist.com/api/bots/{self.bot.user.id}/stats",
            json={
                "guilds": len(self.bot.guilds),
                "users": sum(guild.member_count for guild in self.bot.guilds),
            },
            headers={"Authorization": f"Bot {self.bot.discord_bot_list}"},
        )


def setup(bot):
    """Load the Utility cog."""
    bot.add_cog(Utility(bot))
