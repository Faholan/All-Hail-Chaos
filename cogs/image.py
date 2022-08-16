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
import discord
from discord.ext import commands
from discord import app_commands


def check_channel(channel: discord.abc.Messageable) -> bool:
    """Check for NSFW rights."""
    if isinstance(channel, discord.TextChannel):
        return channel.is_nsfw()
    return True


class Images(commands.GroupCog):  # Thanks KSoft.si
    """Commands to get random images.

    You can try using the nsfw command, if you dare
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Images."""
        self.bot = bot

    @app_commands.command()
    async def koala(self, interaction: discord.Interaction) -> None:
        """Get a random picture of a koala."""
        async with self.bot.aio_session.get(
            "https://some-random-api.ml/img/koala"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    title="Random Koala", colour=discord.Colour.gold()
                )
                embed.set_image(url=data["link"])
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Something went wrong.")
                await self.bot.log_channel.send(f"Code {resp.status} in koala")

    @app_commands.command()
    async def panda(self, interaction: discord.Interaction) -> None:
        """Get a random picture of a panda."""
        async with self.bot.aio_session.get(
            "https://some-random-api.ml/img/panda"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    title="Random Panda!",
                    colour=discord.Colour.gold(),
                )
                embed.set_image(url=data["link"])
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"Something went boom! :( [CODE: {resp.status}]"
                )
                await self.bot.log_channel.send(f"Code {resp.status} in panda")


async def setup(bot: commands.Bot) -> None:
    """Load the Images cog."""
    await bot.add_cog(Images(bot))
