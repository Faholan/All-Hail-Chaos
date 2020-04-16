"""MIT License

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
SOFTWARE."""

import datetime
import traceback

import discord
from discord.ext import commands, tasks


class Logging(commands.Cog):
    """Cog for the logging of data."""

    def __init__(self, bot):
        self.bot = bot
        self.log_channel = bot.log_channel

    #@commands.Cog.listener()
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
        embed.timestamp = datetime.datetime.utcnow()
        await self.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.UserInputError) or isinstance(error, commands.CheckFailure) or isinstance(error, commands.DisabledCommand) or isinstance(error, commands.CommandOnCooldown) or isinstance(error, commands.MaxConcurrencyReached):
            return
        if isinstance(error,commands.CommandInvokeError):
            error=error.original
        embed = discord.Embed(color=0xFF0000)
        embed.title = f"{ctx.author} ({ctx.author.id}) caused an error in {ctx.command} ({type(error).__name__})"
        if ctx.guild:
            embed.description = f"in {ctx.guild} ({ctx.guild.id})\n   in {ctx.channel.name} ({ctx.channel.id})"
        elif isinstance(ctx.channel,discord.DMChannel):
            embed.description = f"in a Private Channel ({ctx.channel.id})"
        else:
            embed.description = f"in the Group {ctx.channel.name} ({ctx.channel.id})"
        tb = "".join(traceback.format_tb(error.__traceback__))
        embed.description += f"```\n{tb}```"
        embed.set_footer(text=f"{self.bot.user.name} Logging", icon_url=ctx.me.avatar_url_as(static_format="png"))
        embed.timestamp = datetime.datetime.utcnow()
        await self.log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logging(bot))
