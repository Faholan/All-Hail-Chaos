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

import datetime
import sys
import traceback
import typing as t
from io import StringIO
from typing import Callable

import discord
from discord.ext import commands


def secondes(num_seconds: int) -> str:
    """Convert a number of seconds in human-readabla format."""
    human_readable: t.List[str] = []
    if num_seconds >= 86400:
        human_readable.append(f"{num_seconds//86400} days")
        num_seconds %= 86400
    if num_seconds >= 3600:
        human_readable.append(f"{num_seconds//3600} hours")
        num_seconds %= 3600
    if num_seconds >= 60:
        human_readable.append(f"{num_seconds//60} minutes")
        num_seconds %= 60
    if num_seconds > 0:
        human_readable.append(f"{num_seconds} seconds")
    return ", ".join(human_readable)


async def error_manager(
    ctx: commands.Context,
    error: Exception,
) -> None:
    """Error manager."""
    if isinstance(error, commands.CheckAnyFailure):
        await ctx.bot.httpcat(
            ctx,
            401,
            ("You don't have the rights to send use the command "
             f"{ctx.invoked_with}"),
        )
        return
    if isinstance(error, (commands.BadArgument, commands.BadUnionArgument)):
        await ctx.bot.httpcat(ctx, 400, str(error))
        return
    if isinstance(error, commands.MaxConcurrencyReached):
        pers = {
            commands.BucketType.default: "bot",
            commands.BucketType.user: "user",
            commands.BucketType.guild: "guild",
            commands.BucketType.channel: "channel",
            commands.BucketType.member: "member",
            commands.BucketType.category: "category",
            commands.BucketType.role: "role",
        }
        await ctx.bot.httpcat(
            ctx,
            429,
            (f"This command can only be used {error.number} "
             f"time{'s' if error.number > 1 else ''} per {pers[error.per]} "
             "concurrently."),
        )
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.bot.httpcat(
            ctx, 400,
            f"Hmmmm, looks like an argument is missing : {error.param.name}")
        return
    if isinstance(error, commands.PrivateMessageOnly):
        await ctx.bot.httpcat(
            ctx, 403, "You must be in a private channel to use this command.")
        return
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.bot.httpcat(ctx, 403, "I can't dot this in private.")
        return
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found
    if isinstance(error, commands.DisabledCommand):
        await ctx.bot.httpcat(
            ctx,
            423,
            "Sorry but this command is under maintenance",
        )
        return
    if isinstance(error, commands.TooManyArguments):
        await ctx.bot.httpcat(
            ctx,
            400,
            "You gave me too many arguments for me to process.",
        )
        return
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.bot.httpcat(
            ctx,
            429,
            ("Calm down, breath and try again in "
             f"{secondes(round(error.retry_after))}"),
        )
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.bot.httpcat(
            ctx,
            401,
            "\n-".join(["Try again with the following permission(s) :"] +
                       error.missing_perms),
        )
        return
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.bot.httpcat(
            ctx,
            401,
            "\n-".join(["I need these permissions :"] + error.missing_perms),
        )
        return
    if isinstance(error, commands.MissingRole):
        await ctx.bot.httpcat(
            ctx,
            401,
            f"Sorry, but you need to be a {error.missing_role}",
        )
        return
    if isinstance(error, commands.BotMissingRole):
        await ctx.bot.httpcat(
            ctx,
            401,
            f"Gimme the role {error.missing_role}, ok ?",
        )
        return
    if isinstance(error, commands.NSFWChannelRequired):
        await ctx.bot.httpcat(
            ctx,
            403,
            "Woooh ! You must be in an NSFW channel to use this.",
        )
        return
    if isinstance(error, commands.UnexpectedQuoteError):
        await ctx.bot.httpcat(
            ctx,
            400,
            "I didn't expected that quote...",
        )
        return
    if isinstance(error, commands.InvalidEndOfQuotedStringError):
        await ctx.bot.httpcat(
            ctx,
            400,
            "You must separate the quoted argument from the others with spaces",
        )
        return
    if isinstance(error, commands.ExpectedClosingQuoteError):
        await ctx.bot.httpcat(ctx, 400, "I expected a closing quote")
        return
    if isinstance(error, commands.CheckFailure):
        await ctx.bot.httpcat(
            ctx,
            401,
            "You don't have the rights to use this command",
        )
        return

    # Here are the real errors
    if isinstance(error, commands.CommandInvokeError):
        await ctx.bot.httpcat(
            ctx,
            500,
            "Internal error",
            description=(
                "Thank you. My owner is now aware of this bug, which'll"
                " be fixed shortly. (typically, a few minutes "
                "from when he sees it)"),
        )
    else:
        await ctx.bot.httpcat(
            ctx,
            500,
            "The command raised an error",
            description=(
                "Thank you. My owner is now aware of this bug, "
                "which'll be fixed shortly. (typically, a few minutes from "
                "when he sees it)"),
        )

    if not ctx.bot.log_channel:  # With nowhere to log, raise
        raise error

    if isinstance(error, commands.CommandInvokeError):
        error = error.original

    embed = discord.Embed(colour=0xFF0000)
    embed.set_author(name=str(ctx.author), icon_url=str(ctx.author.avatar_url))
    embed.title = f"{ctx.author.id} caused an error in {ctx.command}"
    embed.description = f"{type(error).__name__} : {error}"

    if ctx.guild:
        embed.description += (
            f"\nin {ctx.guild} ({ctx.guild.id})\n   in {ctx.channel.name} "
            f"({ctx.channel.id})")
    elif isinstance(ctx.channel, discord.DMChannel):
        embed.description += f"\nin a Private Channel ({ctx.channel.id})"
    else:
        embed.description += f"\nin the Group {ctx.channel.name} ({ctx.channel.id})"

    formatted_traceback = "".join(traceback.format_tb(error.__traceback__))
    embed.description += f"```\n{formatted_traceback}```"
    embed.set_footer(
        text=f"{ctx.bot.user.name} Logging",
        icon_url=ctx.bot.user.avatar_url_as(static_format="png"),
    )
    embed.timestamp = datetime.datetime.utcnow()
    try:
        await ctx.bot.log_channel.send(embed=embed)
    except discord.DiscordException:
        await ctx.bot.log_channel.send(file=discord.File(StringIO(
            f"{embed.title}\n\n{embed.description}"),
            filename="error.md"))
        # Send errors in files if they are too big


def generator(bot: commands.Bot) -> Callable[..., None]:
    """Generate an on_error for the bot."""
    # This needs to be wrapped in order to access bot and its attributes
    async def predictate(event: str, *args: t.Any, **kwargs: t.Any) -> None:
        """Process the on_error event."""
        error_type, value, raw_traceback = sys.exc_info()
        if not error_type:
            return  # This shouldn't happen : no error
        if not bot.log_channel:
            raise  # There is nowhere to log
        embed = discord.Embed(colour=0xFF0000)
        embed.title = f"Error in {event} with args {args} {kwargs}"
        embed.description = f"{error_type.__name__} : {value}"
        formatted_traceback = "".join(traceback.format_tb(raw_traceback))
        embed.description += f"```\n{formatted_traceback}```"
        embed.set_footer(
            text=f"{bot.user.name} Logging",
            icon_url=bot.user.avatar_url_as(static_format="png"),
        )
        embed.timestamp = datetime.datetime.utcnow()
        try:
            await bot.log_channel.send(embed=embed)
            return
        except discord.DiscordException:
            await bot.log_channel.send(file=discord.File(
                StringIO(f"{embed.title}\n\n{embed.description}"),
                filename="error.md",
            ))

    return predictate


def setup(bot: commands.Bot) -> None:
    """Add error managing."""
    bot.add_listener(error_manager, "on_command_error")
    bot.on_error = generator(bot)
