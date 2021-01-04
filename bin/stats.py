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

from discord.ext import commands, tasks


async def statistics(ctx: commands.Context) -> None:
    """Log usage statistics."""
    if await ctx.bot.is_owner(ctx.author):
        return

    async with ctx.bot.pool.acquire() as database:
        row = await database.fetchrow(
            "SELECT * FROM stats.usage WHERE command=$1 "
            "AND EXTRACT(EPOCH FROM (NOW() - timestamp)) < 15*60",
            ctx.command.name,
        )
        if row:
            await database.execute(
                "UPDATE stats.usage SET count=count+1 WHERE timestamp=$1"
                "AND command=$2",
                row["timestamp"],
                ctx.command.name,
            )
        else:
            await database.execute(
                "INSERT INTO stats.usage VALUES ($1, 1, "
                "to_timestamp((CAST(EXTRACT(EPOCH FROM NOW()) AS INTEGER)"
                " / 900) * 900))",
                ctx.command.name,
            )


def guilds(bot: commands.Bot):
    """Log the number of guilds."""
    async def predictate(_) -> None:
        """Compute the logging."""
        async with bot.pool.acquire() as database:
            await database.execute(
                "INSERT INTO stats.guilds VALUES ($1)",
                len(bot.guilds),
            )
    return predictate


@tasks.loop(hours=1)
async def guild_loop(bot: commands.Bot):
    """Log the number of guilds."""
    async with bot.pool.acquire() as database:
        await database.execute(
            "INSERT INTO stats.guilds VALUES ($1)",
            len(bot.guilds),
        )


@tasks.loop(minutes=14)
async def usage_loop(bot: commands.Bot):
    """Log a default value."""
    async with bot.pool.acquire() as database:
        for command in bot.commands:
            row = await database.fetchrow(
                "SELECT * FROM stats.usage WHERE command=$1 "
                "AND EXTRACT(EPOCH FROM (NOW() - timestamp)) < 15*60",
                command.name,
            )
            if not row:
                await database.execute(
                    "INSERT INTO stats.usage VALUES ($1, 0, "
                    "to_timestamp((CAST(EXTRACT(EPOCH FROM NOW()) AS INTEGER)"
                    " / 900) * 900))",
                    command.name,
                )


def setup(bot: commands.Bot) -> None:
    """Add stats listeners."""
    bot.add_listener(statistics, "on_command_completion")
    bot.guilds_logger = guilds(bot)
    bot.add_listener(bot.guilds_logger, "on_guild_join")
    bot.add_listener(bot.guilds_logger, "on_guild_remove")
    guild_loop.start(bot)
    usage_loop.start(bot)


def teardown(bot: commands.Bot) -> None:
    """Remove stats listeners."""
    bot.remove_listener(statistics, "on_command_completion")
    bot.remove_listener(bot.guilds_logger, "on_guild_join")
    bot.remove_listener(bot.guilds_logger, "on_guild_remove")
    guild_loop.stop()
    usage_loop.stop()
