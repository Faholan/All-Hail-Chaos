import datetime
import traceback

import discord
from discord.ext import commands, tasks


class Logging(commands.Cog):
    """Cog for the logging of data."""

    def __init__(self, bot):
        self.bot = bot
        self.log_channel = bot.log_channel

    @commands.Cog.listener()
    async def on_command(self, ctx):
        embed = discord.Embed(color=0x7289DA)
        embed.title = f"{ctx.author} ({ctx.author.id}) used {ctx.command}"
        if ctx.guild:
            embed.description = f"in {ctx.guild} ({ctx.guild.id})\n   in {ctx.channel.name} ({ctx.channel.id})"
        elif isinstance(ctx.channel,discord.DMChannel):
            embed.description = f"in a Private Channel ({ctx.channel.id})"
        else:
            embed.description = f"in the Group {ctx.channel.name} ({ctx.channel.id})"
        embed.description += f"```fix\n{ctx.message.content}```"
        embed.set_footer(text=f"{self.bot.user.name} Logging", icon_url=ctx.me.avatar_url_as(static_format="png"))
        embed.timestamp = datetime.datetime.now()
        await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        embed = discord.Embed(color=0xFF0000)
        embed.title = f"{ctx.author} ({ctx.author.id}) caused an error in {ctx.command}"
        if ctx.guild:
            embed.description = f"in {ctx.guild} ({ctx.guild.id})\n   in {ctx.channel.name} ({ctx.channel.id})"
        elif isinstance(ctx.channel,discord.DMChannel):
            embed.description = f"in a Private Channel ({ctx.channel.id})"
        else:
            embed.description = f"in the Group {ctx.channel.name} ({ctx.channel.id})"
        tb = "".join(traceback.format_tb(error.__traceback__))
        embed.description += f"```\n{tb}```"
        embed.set_footer(text=f"{self.bot.user.name} Logging", icon_url=ctx.me.avatar_url_as(static_format="png"))
        embed.timestamp = datetime.datetime.now()
        await self.log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logging(bot))
