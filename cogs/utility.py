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

import codecs
import inspect
import os
import pathlib
from os import path
from sys import version
from textwrap import dedent
import typing as t

import discord
import humanize
import psutil

from discord import app_commands

# from discord.ext import commands, menus, tasks
from discord.ext import commands, tasks

ZWS = "\u200b"
POLL_EMOJIS = [chr(0x1F1E6 + i) for i in range(0x1A)]
# :regional_indicator_a: up to :regional_indicator_z


# class SauceSource(menus.ListPageSource):
class SauceSource:
    """Source for the sauce command."""

    # async def format_page(self, menu: menus.Menu, page: str):
    async def format_page():
        """Format the page of code."""
        max_pages = self.get_max_pages()
        embed = discord.Embed(description=page, colour=discord.Colour.purple())
        if max_pages > 1:
            embed.set_footer(text=f"Page {menu.current_page + 1}/{max_pages}")
        return embed


def secondes(number: int) -> str:
    """Convert a number of seconds in human-readable format."""
    formatted: t.List[str] = []
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
        self.top_gg_token = (
            self.discord_bots_token
        ) = self.xyz_token = self.discordbotlist_token = None

        for bot_list in self.bot.config.get("bot_lists", []):
            if not isinstance(bot_list, dict):  # type: ignore
                continue

            bot_list: t.Dict[str, str]

            if bot_list.get("name") == "top.gg":
                pass  # Custom top.gg runner I believe

            if bot_list.get("name") == "discord.bots.gg":
                if self.discord_bots.is_running():
                    continue
                self.discord_bots_token = bot_list.get("token")
                self.discord_bots.start()

            if bot_list.get("name") == "bots.ondiscord.xyz":
                if self.xyz.is_running():
                    continue

                self.xyz_token = bot_list.get("token")
                self.xyz.start()

            if bot_list.get("name") == "discordbotlist.com":
                if self.discordbotlist.is_running():
                    continue

                self.discordbotlist_token = bot_list.get("token")
                self.discordbotlist.start()

    @app_commands.command()
    async def add(self, interaction: discord.Interaction) -> None:
        """Return a link to add the bot to a new server."""
        link = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(self.bot.invite_permissions),
        )
        await interaction.response.send_message(
            f"You can add me using this link : {link}", ephemeral=True
        )

    @app_commands.command()
    async def code(self, interaction: discord.Interaction) -> None:
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
                        "./" + str(pathlib.PurePath(filepath, name)), "r", "utf-8"
                    ) as file:
                        for _, line in enumerate(file):
                            if line.strip().startswith("#") or len(line.strip()) == 0:
                                pass
                            else:
                                total += 1
                                file_lines += 1
                    final_path = filepath + path.sep + name
                    list_of_files.append(
                        final_path.split("." + path.sep)[-1] + f" : {file_lines} lines"
                    )
        embed = discord.Embed(colour=0xFFFF00)
        embed.add_field(
            name=f"{self.bot.user.name}'s structure",
            value="\n".join(sorted(list_of_files)),
        )
        embed.set_footer(
            text=(
                f"I am made of {total} lines of Python, spread across "
                f"{file_amount} files !"
            ),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def info(self, interaction: discord.Interaction) -> None:
        """Get info about me."""
        link = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(self.bot.invite_permissions),
        )

        app = await self.bot.application_info()
        embed = discord.Embed(
            title=f"Informations about {self.bot.user}",
            description=(
                f'[Invite Link]({link} "Please stay at home and use bots")'
                f"\n[Support Server Invite]({self.bot.support})"
            ),
            colour=discord.Colour.random(),
        )
        embed.set_author(
            name=str(interaction.user),
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(
            text=(
                f"Discord.py version {discord.__version__}, Python version "
                f"{version.split(' ', maxsplit=1)[0]}"
            ),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name=f"My owner{'s' if app.team else ''} :",
            value=", ".join([str(member) for member in app.team.members])
            if app.team
            else str(app.owner),
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
            value=f"More exactly {len(self.bot.tree.get_commands())} commands",
            inline=False,
        )
        embed.add_field(
            name="GitHub repository",
            value=(f"[It's open source !]({self.bot.github_link})"),
        )
        # embed.add_field(
        #    name="Description page :",
        #    value=(
        #        f"[top.gg page]({self.bot.top_gg})\n"
        #        f"[bots on discord page]({self.bot.bots_on_discord})\n"
        #        f"[Discord bots page]({self.bot.discord_bots_page})\n"
        #        f"[Discord bot list page]({self.bot.discord_bot_list_page})"
        #    ),
        #    inline=False,
        # )
        embed.add_field(
            name="Libraries used :",
            value=(
                '[Lavalink](https://github.com/Frederikam/Lavalink/ "I thank'
                'chr1sBot for learning about this") : Whole Music Cog'
                '\n[discord.py](https://discordpy.readthedocs.io "More exactly '
                'discord.ext.commands") : Basically this whole bot\n'
                '[NASA](https://api.nasa.gov/ "Yes I hacked the NASA") : '
                "Whole NASA Cog"
            ),
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
                    f"{pid} (`{name}`) with {threads} thread(s)."
                ),
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    # TODO : create a v2 paginator
    # @app_commands.command(aliases=["sauce"])
    async def source(
        self,
        interaction: discord.Interaction,
        *,
        command_name: str,
    ) -> None:
        """Get the source code of a command."""
        command = self.bot.tree.get_command(command_name)
        if not command:
            await ctx.send(f"No command named `{command_name}` found.")
            return
        try:
            source_lines, _ = inspect.getsourcelines(command.callback)
        except (TypeError, OSError):
            await ctx.send(
                "I was unable to retrieve the source for "
                f"`{command_name}` for some reason."
            )
            return

        # Get rid of extra \n
        source_lines = dedent(
            "".join(source_lines).replace("```", f"`{ZWS}`{ZWS}`")
        ).split("\n")
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

    @app_commands.command()
    @app_commands.cooldown(2, 600)
    async def suggestion(
        self,
        interaction: discord.Interaction,
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
                f"{interaction.user.mention} ({interaction.user.id})'s idea: {idea}"
            ),
            colour=0xFFFF00,
        )
        embed.set_author(
            name=str(ctx.author),
            icon_url=ctx.author.display_avatar.url,
        )
        if self.bot.suggestion_channel:
            await self.bot.suggestion_channel.send(embed=embed)
            await interaction.response.send_message(
                "Thanks for your participation in this project !"
            )
        else:
            await interaction.response.send_message(
                "Sorry but my owner hasn't correctly configured this command"
            )

    @tasks.loop(minutes=30)
    async def discord_bots(self):
        """Update the profile ont discord.bots.gg."""
        if not self.discord_bots_token:
            self.discord_bots.stop()
            return

        await self.bot.aio_session.post(
            f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",
            json={"guildCount": len(self.bot.guilds)},
            headers={"authorization": self.discord_bots_token},
        )

    @tasks.loop(minutes=30)
    async def xyz(self):
        """Update the profile on bots.ondiscord.xyz."""
        if not self.xyz_token:
            self.xyz.stop()
            return

        await self.bot.aio_session.post(
            "https://bots.ondiscord.xyz/bot-api/bots/" f"{self.bot.user.id}/guilds",
            json={"guildCount": len(self.bot.guilds)},
            headers={"Authorization": self.xyz_token},
        )

    @tasks.loop(minutes=30)
    async def discordbotlist(self):
        """Update the profile on discordbotlist.com."""
        if not self.discordbotlist_token:
            self.discordbotlist.stop()
            return

        await self.bot.aio_session.post(
            f"https://discordbotlist.com/api/bots/{self.bot.user.id}/stats",
            json={
                "guilds": len(self.bot.guilds),
                "users": sum(guild.member_count for guild in self.bot.guilds),
            },
            headers={"Authorization": f"Bot {self.discordbotlist_token}"},
        )


async def setup(bot: commands.Bot) -> None:
    """Load the Utility cog."""
    await bot.add_cog(Utility(bot))
