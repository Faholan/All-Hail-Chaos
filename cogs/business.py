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

from random import randint
from time import time

import discord
from discord.ext import commands


def p_vol(streak: int) -> int:
    """Return the probability of stealing based off the strek."""
    return 75 - (25 * 0.8 ** streak)


class Businessguy():
    """A guy that does business lol."""

    def __init__(self, sql: dict, user: discord.User, database) -> None:
        """Initialize the guy."""
        self.database = database
        if sql:
            self.money = sql['money']
            self.bank = sql['bank']
            self.bank_max = sql['bank_max']
            self.streak = sql['streak']
            self.last_daily = sql['last_daily']
            self.steal_streak = sql['steal_streak']
        else:
            self.money = 0
            self.bank = 0
            self.bank_max = 5000
            self.streak = 1
            self.last_daily = 0
            self.steal_streak = 0
        self.id = user.id
        self.name = str(user)
        self.avatar_url = str(user.avatar_url)

    def __eq__(self, other) -> bool:
        """Are we equal."""
        return self.id == other.id

    async def save(self) -> None:
        """Commit the changes."""
        await self.database.execute(
            "INSERT INTO public.business VALUES ($1, $2, $3, $4, $5, $6, $7)"
            " ON CONFLICT (id) DO UPDATE SET money=$2, bank=$3, bank_max=$4, "
            "streak=$5, last_daily=$6, steal_streak=$7",
            self.id,
            self.money,
            self.bank,
            self.bank_max,
            self.streak,
            self.last_daily,
            self.steal_streak,
        )

    async def daily(self) -> str:
        """Get your daily money."""
        if time() < self.last_daily + 172800 and self.streak < 5:
            self.streak += 1
        else:
            self.streak = 1
        self.last_daily = round(time())
        self.money += 100 * self.streak
        await self.save()
        return f"You gained {100 * self.streak} GP"

    async def gift(self, guild) -> str:
        """Get the guild's daily money."""
        self.money += 500
        await self.save()
        return f"You took {guild}'s 500 daily GP."

    def money_out(self) -> discord.Embed:
        """How much money do I have."""
        embed = discord.Embed(title=f"{self.name}'s bank :", colour=0x00008b)
        embed.set_author(name=self.name, icon_url=self.avatar_url)
        embed.add_field(name='Banked :', value=f"{self.bank}/{self.bank_max}")
        embed.add_field(name='Pocketed :', value=str(self.money))
        return embed

    async def deposit(self, money: int) -> str:
        """Deposit some money."""
        if self.money < money:
            return f"Sorry, but you only have {self.money} GP"
        deposit_max = self.bank_max - self.bank
        if money <= deposit_max:
            self.money -= money
            self.bank += money
            await self.save()
            return f"{money} GP deposited"
        self.money -= deposit_max
        self.bank += deposit_max
        await self.save()
        return (
            f"{deposit_max} GP deposited. {deposit_max - money} "
            "GP couldn't be deposited (capacity of {self.bank_max} GP"
            " reached)"
        )

    async def steal(self, other) -> int:
        """Gimme your money."""
        stolen = randint(round(0.05 * other.money), round(0.1 * other.money))
        self.money += stolen
        other.money -= stolen
        await self.save()
        await other.save()
        return stolen


class Business(commands.Cog):
    """Some commands involving money."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Business."""
        self.bot = bot

    async def _fetcher(self, identifier: int, database) -> dict:
        """Fetch the guy's data."""
        return await database.fetchrow(
            "SELECT * FROM public.business WHERE id=$1",
            identifier,
        )

    @commands.command(ignore_extra=True)
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: commands.Context) -> None:
        """Get your daily GP (100 * streak, max : 500)."""
        async with self.bot.pool.acquire(timeout=5) as database:
            business = Businessguy(
                await self._fetcher(ctx.author.id, database),
                ctx.author,
                database,
            )
            await ctx.send(await business.daily())

    @commands.command()
    async def deposit(self, ctx: commands.Context, money: int) -> None:
        """Deposit your money in a safe at the bank."""
        async with self.bot.pool.acquire(timeout=5) as database:
            business = Businessguy(
                await self._fetcher(ctx.author.id, database),
                ctx.author,
                database,
            )
            await ctx.send(await business.deposit(money))

    @commands.command(ignore_extra=True)
    @commands.guild_only()
    @commands.cooldown(1, 86400, commands.BucketType.guild)
    async def gift(self, ctx: commands.Context) -> None:
        """Get the guild's 500 GP of daily gift."""
        async with self.bot.pool.acquire(timeout=5) as database:
            business = Businessguy(
                await self._fetcher(ctx.author.id, database),
                ctx.author,
                database)
            await ctx.send(await business.gift(ctx.guild.name))

    @commands.command(ignore_extra=True)
    async def money(self, ctx: commands.Context) -> None:
        """Check how much money you have."""
        async with self.bot.pool.acquire(timeout=5) as database:
            business = Businessguy(
                await self._fetcher(ctx.author.id, database),
                ctx.author,
                database,
            )
            embed = business.money_out()
            embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.guild_only()
    async def steal(
        self,
        ctx: commands.Context,
        victim: discord.Member,
    ) -> None:
        """Stealing is much more gainful than killing."""
        async with self.bot.pool.acquire(timeout=5) as database:
            pickpocket = Businessguy(
                await self._fetcher(ctx.author.id, database),
                ctx.author,
                database,
            )
            stolen = Businessguy(
                await self._fetcher(victim.id, database),
                victim,
                database,
            )
            if pickpocket == stolen:
                self.steal.reset_cooldown(ctx)
                await ctx.send(
                    "Are you seriously tring to steal yourself ?"
                )
                return
            if stolen.money == 0:
                self.steal.reset_cooldown(ctx)
                await ctx.send(
                    f"`{victim.display_name}` doesn't have money on him. "
                    "What a shame."
                )
                return

            threshold = p_vol(pickpocket.steal_streak)
            if victim.status == discord.Status.offline:
                threshold += 10
            if randint(1, 100) < threshold:
                pickpocket.steal_streak = 0
                await pickpocket.save()
                await ctx.send(
                    "You failed in your attempt to steal "
                    f"{victim.display_name}."
                    " He hit you, so you must now wait 10 minutes to regain "
                    "your usual sneakiness"
                )
            else:
                self.steal.reset_cooldown(ctx)
                pickpocket.steal_streak += 1
                await ctx.send(
                    f"You robbed `{await pickpocket.steal(stolen)}` GP from "
                    f"{victim.display_name}"
                )

    @steal.error
    async def steal_error(self, ctx: commands.Context, error: Exception):
        """Mainly, reset the cooldown."""
        if not isinstance(error, commands.CommandOnCooldown):
            self.steal.reset_cooldown(ctx)


def setup(bot: commands.Bot):
    """Load the Business cog."""
    bot.add_cog(Business(bot))
