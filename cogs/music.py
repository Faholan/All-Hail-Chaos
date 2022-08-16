from discord import app_commands

import discord

from discord.ext import commands


class Music(commands.GroupCog):
    """Play music."""

    def __init__(self, bot: commands.Bot) -> None:
        """Load the cog."""
        self.bot = bot

        if not hasattr(bot, "lavalink"):
            bot.lavalink = lavalink.Client(bot.user.id)

            for node in bot.lavalink
                bot.lavalink.add_node(

                )
