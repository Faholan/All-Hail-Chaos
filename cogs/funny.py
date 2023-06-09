# coding=utf-8
"""MIT License.

Copyright (c) 2020-2022 Faholan

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

import typing as t
from os import path
from random import choice, randint

import discord
from discord import app_commands
from discord.ext import commands

HitReturn = t.Tuple[str, str, str, str]

# All the data files necessary for the commands
with open(f"data{path.sep}deaths.txt", "r", encoding="utf-8") as file:
    death = file.readlines()  # -> kill command
with open(f"data{path.sep}excuses.txt", "r", encoding="utf-8") as file:
    excuses = file.readlines()  # -> excuse command


class Funny(commands.Cog):
    """Some funny commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Funny."""
        self.bot = bot

    @app_commands.command()
    async def chuck(self, interaction: discord.Interaction) -> None:
        """Get a random Chuck Norris joke."""
        async with self.bot.aio_session.get(
            "https://api.chucknorris.io/jokes/random"
        ) as response:
            joke = await response.json()
            await interaction.response.send_message(joke["value"])

    @app_commands.command()
    async def dad(self, interaction: discord.Interaction) -> None:
        """Get a random dad joke."""
        async with self.bot.aio_session.get(
            "https://icanhazdadjoke.com/slack"
        ) as response:
            joke = await response.json()
            await interaction.response.send_message(joke["attachments"][0]["text"])

    @app_commands.command()
    async def dong(
        self,
        interaction: discord.Interaction,
        dick: t.Optional[discord.Member] = None,
    ) -> None:
        """How long is this person's dong."""
        dickfinal = dick or interaction.user
        await interaction.response.send_message(
            f"{dickfinal.mention}'s magnum dong is this long : 8"
            f"{'=' * randint(0, 10)}>"
        )

    @app_commands.command()
    async def excuse(self, interaction: discord.Interaction) -> None:
        """We all do mishaps, and we all need a good excuse once in a while."""
        newline = "\n"  # One cannot use backslash in an f-string
        # The file is spread into 6 lines, to form a phrase like:
        #
        # I'm sorry master... it's because {person} {action} in {place} because of
        # {qualificative} {object} which {qualificative 2} so it's not my fault!
        #
        # Each parameter is on one line, with the options separated with |

        await interaction.response.send_message(
            "I'm sorry master... it's because "
            f"{choice(excuses[0].split('|')).strip(newline)} "
            f"{choice(excuses[1].split('|')).strip(newline)} in "
            f"{choice(excuses[2].split('|')).strip(newline)} and all of that "
            f"because of {choice(excuses[3].split('|')).strip(newline)} "
            f"{choice(excuses[4].split('|')).strip(newline)} which "
            f"{choice(excuses[5].split('|')).strip(newline)} "
            "so it's not my fault !"
        )

    @app_commands.command()
    async def joke(self, interaction: discord.Interaction) -> None:
        """Send a random joke."""
        async with self.bot.aio_session.get(
            "https://mrwinson.me/api/jokes/random"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    description=data["joke"], colour=discord.Colour.gold()
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Something went wrong.")
                await self.bot.log_channel.send(f"Code {resp.status} in joke")

    @app_commands.command()
    async def kill(
        self,
        interaction: discord.Interaction,
        target: str,
    ) -> None:
        """Just in case you want to kill your neighbour."""
        await interaction.response.send_message(
            choice(death).format(
                author=interaction.user.display_name,
                victim=target,
            )
        )


async def setup(bot: commands.Bot) -> None:
    """Load the Funny cog."""
    await bot.add_cog(Funny(bot))
