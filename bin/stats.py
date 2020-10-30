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
        global_row = await database.fetchrow(
            "SELECT * FROM stats.usage WHERE command=NULL "
            "AND EXTRACT(EPOCH FROM (NOW() - timestamp)) < 15*60",
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
        if global_row:
            await database.execute(
                "UPDATE stats.usage SET count=count+1 WHERE timestamp=$1"
                "AND command=NULL",
                global_row["timestamp"],
            )
        else:
            await database.execute(
                "INSERT INTO stats.usage VALUES (NULL, 1, "
                "to_timestamp((CAST(EXTRACT(EPOCH FROM NOW()) AS INTEGER)"
                " / 900) * 900))",
            )


def guilds(bot: commands.Bot):
    """Log the number of guilds."""
    async def predictate(_) -> None:
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


def setup(bot: commands.Bot) -> None:
    """Add stats listeners."""
    bot.add_listener(statistics, "on_command_completion")
    bot.guilds_logger = guilds(bot)
    bot.add_listener(bot.guilds_logger, "on_guild_join")
    bot.add_listener(bot.guilds_logger, "on_guild_remove")
    guild_loop.start(bot)


def teardown(bot: commands.Bot) -> None:
    """Remove stats listeners."""
    bot.remove_listener(statistics, "on_command_completion")
    bot.remove_listener(bot.guilds_logger, "on_guild_join")
    bot.remove_listener(bot.guilds_logger, "on_guild_remove")
    guild_loop.stop()
