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
import typing as t

from discord import Colour, Embed
from discord.ext import commands

Functions = t.Tuple[t.Callable[["Success", commands.Context, t.Any],
                               t.Awaitable[t.Tuple[bool, t.Any]], ],
                    t.Optional[t.Callable[["Success", commands.Context, t.Any],
                                          t.Awaitable[str], ]], ]


class Success:
    """Class implementation of a Discord success."""

    def __init__(
        self,
        name: str,
        description: str,
        functions: Functions,
        column: str,
        description_is_visible: bool = True,
    ) -> None:
        """Initialize a success."""
        self.name = name
        self.description = description
        self._checker, self._advancer = functions
        self.description_is_visible = description_is_visible
        self.column = column
        self.state_column = column + "_state"
        if description_is_visible:
            self.locked = description
        else:
            self.locked = "Hidden success"

    async def checker(
        self,
        ctx: commands.Context,
        data: t.Any,
        identifier: int,
        database: t.Any,
    ) -> bool:
        """Check the success."""
        test, data = await self._checker(self, ctx, data)
        await database.execute(
            f"UPDATE public.successes SET {self.column}=$1 WHERE id=$2",
            data,
            identifier,
        )
        return test

    async def advancer(self, ctx: commands.Context, data: t.Any) -> str:
        """Check how much I advanced."""
        if self._advancer:
            return await self._advancer(self, ctx, data)
        return " - Locked"


def command_count(number: int) -> Functions:
    """Generate the use n commands successes."""
    async def checker(_: Success, __: commands.Context,
                      data: int) -> t.Tuple[bool, int]:
        """Check for the success."""
        return data >= number, data + 1

    async def advancer(_: Success, __: commands.Context, data: int) -> str:
        """Advance the success."""
        return f" ({data}/{number})"

    return checker, advancer


def hidden_commands() -> Functions:
    """Generate the "hidden commands" success."""
    def total(bot: t.Any) -> int:
        """Compute the number of hidden commands."""
        return len([command for command in bot.commands if command.hidden])

    async def checker(_: Success, ctx: commands.Context,
                      data: t.List[str]) -> t.Tuple[bool, t.List[str]]:
        """Check for the success."""
        if not ctx.command or not ctx.command.hidden:
            return False, data
        if data and ctx.command.name in data:
            return False, data
        if data:
            data.append(ctx.command.name)
        else:
            data = [ctx.command.name]
        return len(data) == total(ctx.bot), data

    async def advancer(_: Success, ctx: commands.Context,
                       data: t.List[str]) -> str:
        """Advance the success."""
        if data:
            return f" ({len(data)}/{total(ctx.bot)})"
        return f" (0/{total(ctx.bot)})"

    return checker, advancer


def prefix() -> Functions:
    """Generate the "hidden prefix" success."""
    async def checker(_: Success, ctx: commands.Context,
                      __: t.Any) -> t.Tuple[bool, None]:
        """Check for the success."""
        return ctx.prefix == "¤", None

    return checker, None


success_list = [
    Success(
        "First command",
        "Begin using the bot",
        command_count(1),
        "n_use_1",
    ),
    Success(
        "Bot regular",
        "Launch 100 commands",
        command_count(100),
        "n_use_100",
    ),
    Success(
        "Bot master",
        "Launch 1000 commands",
        command_count(1000),
        "n_use_1000",
    ),
    Success(
        "The secrets of the bot",
        "Find every single hidden command",
        hidden_commands(),
        "hidden",
    ),
    Success(
        "The dark side of the chaos",
        "Find the hidden prefix",
        prefix(),
        "dark",
        description_is_visible=False,
    ),
]


class Successes(commands.Cog):  # type: ignore
    """Everything to know about successes."""

    def __init__(self, bot: t.Any, successes: t.List[Success]) -> None:
        """Initialize Successes."""
        self.bot = bot
        self.success_list = successes
        self._succ_conn: t.Any = None
        self._succ_con_lock: t.Any = None

    @commands.command(ignore_extra=True, aliases=["succes",
                                                  "successes"])  # type: ignore
    async def success(self, ctx: commands.Context) -> None:
        """Send back your successes."""
        async with self.bot.pool.acquire() as database:
            state = await database.fetchrow(
                "SELECT * FROM public.successes WHERE id=$1",
                ctx.author.id,
            )
            if not state:
                await database.execute(
                    "INSERT INTO public.successes (id) VALUES ($1)",
                    ctx.author.id,
                )
                state = await database.fetchrow(
                    "SELECT * FROM public.successes WHERE id=$1",
                    ctx.author.id,
                )
            completed = len(
                [s for s in self.success_list if state[s.state_column]])
            embed = Embed(
                title=(
                    f"Success t.List ({completed}/{len(self.success_list)})"),
                colour=Colour.green(),
            )
            embed.set_author(
                name=str(ctx.author),
                icon_url=str(ctx.author.avatar_url),
            )
            embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
            for succ in self.success_list:
                if state[succ.state_column]:
                    embed.add_field(
                        name=f"{succ.name} - Unlocked",
                        value=succ.description,
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=(
                            f"{succ.name}"
                            f"{await succ.advancer(ctx, state[succ.column])}"),
                        value=succ.locked,
                        inline=False,
                    )
            await ctx.send(embed=embed)

    @commands.command()  # type: ignore
    async def success_optout(self, ctx: commands.Context) -> None:
        """Opt in or out of success data collection."""
        async with self.bot.pool.acquire() as database:
            optout = await database.fetchrow(
                "SELECT * FROM public.success_optout WHERE user_id=$1",
                ctx.author.id,
            )
            if optout:
                await database.execute(
                    "DELETE FROM public.success_optout WHERE user_id=$1",
                    ctx.author.id,
                )
                await ctx.send("Successfully opted back in to successes")
            else:
                await database.execute(
                    "INSERT INTO public.success_optout VALUES ($1)",
                    ctx.author.id,
                )
                await ctx.send("Successfully opted out of successes")

    @commands.Cog.listener("on_command_completion")  # type: ignore
    async def succ_sender(self, ctx: commands.Context) -> None:
        """Check and send the successes."""
        if ctx.invoked_with in {"logout", "reboot"}:
            return
        if not self._succ_conn:
            self._succ_conn = await self.bot.pool.acquire()
            self._succ_con_lock = asyncio.Lock()
        async with self._succ_con_lock:
            opt_out = await self._succ_conn.fetchrow(
                "SELECT * FROM public.success_optout WHERE user_id=$1",
                ctx.author.id,
            )
            if opt_out:
                return
            result = await self._succ_conn.fetchrow(
                "SELECT * FROM public.successes WHERE id=$1",
                ctx.author.id,
            )
            if not result:
                await self._succ_conn.execute(
                    "INSERT INTO successes (id) VALUES ($1)",
                    ctx.author.id,
                )
                result = await self._succ_conn.fetchrow(
                    "SELECT * FROM public.successes WHERE id=$1",
                    ctx.author.id,
                )
            embeds: t.List[Embed] = []
            for success in success_list:
                if not result[success.state_column] and await success.checker(
                        ctx, result[success.column], ctx.author.id,
                        self._succ_conn):
                    embed = Embed(
                        title="Succes unlocked !",
                        description=success.name,
                        colour=Colour.random(),
                    )
                    embed.set_author(
                        name=str(ctx.author),
                        icon_url=str(ctx.author.avatar_url),
                    )
                    embed.set_thumbnail(url=ctx.bot.success_image)
                    embed.add_field(
                        name=success.description,
                        value="Requirements met",
                    )
                    embeds.append(embed)
                    await self._succ_conn.execute(
                        "UPDATE public.successes SET "
                        f"{success.state_column}=$1 WHERE id=$2",
                        True,
                        ctx.author.id,
                    )
        i = 0
        for embed in embeds:
            i += 1
            await ctx.send(embed=embed)
            if i == 4:
                await asyncio.sleep(5)
                i = 0

    def cog_unload(self) -> None:
        """Do some cleanup."""
        if self._succ_conn:
            asyncio.create_task(self.bot.pool.release(self._succ_conn))
        self.bot.remove_listener(self.succ_sender)


def setup(bot: t.Any) -> None:
    """Load the Successes cog."""
    bot.add_cog(Successes(bot, success_list))
