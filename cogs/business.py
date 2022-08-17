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
from random import randint
from time import time

import discord
from discord import app_commands
from discord.ext import commands


def p_vol(streak: int) -> float:
    """Return the probability of stealing based off the strek."""
    return 75 - (25 * 0.8**streak)


class Businessguy:
    """A guy that does business lol."""

    def __init__(
        self,
        sql: t.Dict[str, int],
        user: t.Union[discord.User, discord.Member],
        database: t.Any,
    ) -> None:
        """Initialize the guy."""
        self.database = database
        if sql:
            self.money = sql["money"]
            self.bank = sql["bank"]
            self.bank_max = sql["bank_max"]
            self.streak = sql["streak"]
            self.last_daily = sql["last_daily"]
            self.steal_streak = sql["steal_streak"]
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

    def __eq__(self, other: object) -> bool:
        """Are we equal."""
        return isinstance(other, Businessguy) and self.id == other.id

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
            self.streak += 1  # Less than a day
        else:
            self.streak = 1
        self.last_daily = round(time())
        self.money += 100 * self.streak
        await self.save()
        return f"You gained {100 * self.streak} GP"

    async def gift(self, guild: str) -> str:
        """Get the guild's daily money."""
        self.money += 500
        await self.save()
        return f"You took {guild}'s 500 daily GP."

    def money_out(self) -> discord.Embed:
        """How much money do I have."""
        embed = discord.Embed(title=f"{self.name}'s bank :", colour=0x00008B)
        embed.set_author(name=self.name, icon_url=self.avatar_url)
        embed.add_field(name="Banked :", value=f"{self.bank}/{self.bank_max}")
        embed.add_field(name="Pocketed :", value=str(self.money))
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

    async def steal(self, other: "Businessguy") -> int:
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

    async def _fetcher(self, identifier: int, connection: t.Any) -> t.Dict[str, t.Any]:
        """Fetch the guy's data."""
        return await (
            await connection.execute(
                "SELECT * FROM public.business WHERE id=$1",
                identifier,
            )
        ).fetchone()

    @app_commands.command()
    @app_commands.checks.cooldown(1, 86400)
    async def daily(self, interaction: discord.Interaction) -> None:
        """Get your daily GP (100 * streak, max : 500)."""
        async with self.bot.pool.connection() as connection:
            business = Businessguy(
                await self._fetcher(interaction.user.id, connection),
                interaction.user,
                connection,
            )
            await interaction.response.send_message(await business.daily())

    @app_commands.command()
    async def deposit(self, interaction: discord.Interaction, money: int) -> None:
        """Deposit your money in a safe at the bank."""
        async with self.bot.pool.connection() as connection:
            business = Businessguy(
                await self._fetcher(interaction.user.id, connection),
                interaction.user,
                connection,
            )
            await interaction.response.send_message(await business.deposit(money))

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.cooldown(
        1, 86400, key=lambda interaction: interaction.guild_id
    )
    async def gift(self, interaction: discord.Interaction) -> None:
        """Get the guild's 500 GP of daily gift."""
        async with self.bot.pool.connection() as connection:
            business = Businessguy(
                await self._fetcher(interaction.user.id, connection),
                interaction.user,
                connection,
            )
            await interaction.response.send_message(
                await business.gift(interaction.guild.name)  # type: ignore
                # guild only check guaratees that guild is not None
            )

    @app_commands.command()
    async def money(self, interaction: discord.Interaction) -> None:
        """Check how much money you have."""
        async with self.bot.pool.connection(timeout=5) as connection:
            business = Businessguy(
                await self._fetcher(interaction.user.id, connection),
                interaction.user,
                connection,
            )
            embed = business.money_out()
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)  # type: ignore
            # Bot is logged in
            await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.cooldown(
        1, 600, key=lambda interaction: (interaction.guild_id, interaction.user.id)
    )
    async def steal(
        self,
        interaction: discord.Interaction,
        victim: discord.Member,
    ) -> None:
        """Stealing is much more gainful than killing."""
        async with self.bot.pool.connection() as connection:
            pickpocket = Businessguy(
                await self._fetcher(interaction.user.id, connection),
                interaction.user,
                connection,
            )
            stolen = Businessguy(
                await self._fetcher(victim.id, connection),
                victim,
                connection,
            )
            if pickpocket == stolen:
                await interaction.response.send_message(
                    "Are you seriously tring to steal yourself ?"
                )
                return
            if stolen.money == 0:
                await interaction.response.send_message(
                    f"`{victim.display_name}` doesn't have money on him. "
                    "What a shame."
                )
                return

            threshold = p_vol(pickpocket.steal_streak)
            if victim.status == discord.Status.offline:
                threshold -= 10
            if randint(1, 100) < threshold:
                pickpocket.steal_streak = 0
                await pickpocket.save()
                await interaction.response.send_message(
                    "You failed in your attempt to steal "
                    f"{victim.display_name}."
                    " He hit you, so you must now wait 10 minutes to regain "
                    "your usual sneakiness"
                )
            else:
                pickpocket.steal_streak += 1
                await interaction.response.send_message(
                    f"You robbed `{await pickpocket.steal(stolen)}` GP from "
                    f"{victim.display_name}"
                )


async def setup(bot: commands.Bot):
    """Load the Business cog."""
    await bot.add_cog(Business(bot))
