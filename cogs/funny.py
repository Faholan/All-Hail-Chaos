"""MIT License..

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

import asyncio
import typing as t
from os import path
from random import choice, randint

import discord
from discord.ext import commands
from discord import app_commands

HitReturn = t.Tuple[str, str, str, str]

# All the data files necessary for the commands
with open(f"data{path.sep}deaths.txt", "r", encoding="utf-8") as file:
    death = file.readlines()
with open(f"data{path.sep}Excuses.txt", "r", encoding="utf-8") as file:
    excuses = file.readlines()
with open(f"data{path.sep}weapons.txt", "r", encoding="utf-8") as file:
    weapons = file.readlines()


class Fighter:  # Class for the fight command
    """Imma hit you."""

    def __init__(self, user: t.Union[discord.Member, discord.User]) -> None:
        """Initialize that hitter."""
        self.display_name = user.display_name
        self.id = user.id
        self.mention = user.mention
        self.avatar_url = str(user.avatar_url)
        self.pv = 1000

    def hit(
        self,
        weapon: t.List[str],
        pbonus: int = 0,
    ) -> HitReturn:
        """Ouch you hit me."""
        if len(weapon) == 8:
            name, touche, min_damage, max_damage, prob, rate, url, url2 = weapon
        elif len(weapon) == 7:
            name, touche, min_damage, max_damage, prob, rate, url = weapon
            url2 = url
        else:
            name, touche, min_damage, max_damage, prob, rate = weapon
            url = url2 = self.avatar_url

        if randint(1, 100) + pbonus > int(prob):
            return rate, "", name, url2
        damage = randint(int(min_damage), int(max_damage))
        self.pv -= damage
        return touche, str(damage), name, url


# Special effects for the fight command
def pink(
    attacking: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Boom you're pink."""
    return (
        (
            "Chaotic energies swirl around you, making you pink for 3 turns",
            "",
            "Life in pink",
            attacking.avatar_url,
        ),
        victim.hit(choice(weapon_list).split("|")),
    )


def teleportation(
    attacking: Fighter, _: Fighter, __: t.List[str]
) -> t.Tuple[HitReturn]:
    """Get outta here."""
    return (
        (
            (
                "Chaotic energies swirl around you. You were teleported 20 km "
                "away in a random direction, thus missing your attack"
            ),
            "",
            "Teleportation",
            attacking.avatar_url,
        ),
    )


def combustion(
    attacking: Fighter,
    victim: Fighter,
    weapon_list: t.List[str],
) -> t.Tuple[HitReturn, HitReturn]:
    """I love fire."""
    attacking.pv -= 100
    return (
        (
            "{attacking} suddenly bursts into a fireball, losing 100 HP",
            "",
            "Spontaneous combustion",
            "https://i.ytimg.com/vi/ymsiLGVsi_k/maxresdefault.jpg",
        ),
        victim.hit(choice(weapon_list).split("|")),
    )


def election(
    _: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn, HitReturn]:
    """You like my wall."""
    return (
        victim.hit(choice(weapon_list).split("|")),
        (
            "Right after his election, Donald Trump built a wall between"
            " {attacking} and {defending}. He must kip his turn",
            "",
            "Donald Trump's election",
            "https://d.newsweek.com/en/full/607858/adsgads.jpg",
        ),
        victim.hit(choice(weapon_list).split("|")),
    )


def mishap(
    attacking: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Wupsy."""
    attacking_pv = list(str(attacking.pv))
    attacking_pv.reverse()
    attacking.pv = int("".join(attacking_pv))
    victim_pv = list(str(victim.pv))
    victim_pv.reverse()
    victim.pv = int("".join(victim_pv))
    return (
        (
            "Because of a lunatic divine scribe, the two players' HP "
            "were reversed. Have a good day",
            "",
            "Transcription mishap",
            "https://i.ytimg.com/vi/-dKG0gQKA3I/maxresdefault.jpg",
        ),
        victim.hit(choice(weapon_list).split("|")),
    )


def double(
    attacking: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Haha so funny."""
    attacking.pv, victim.pv = victim.pv, attacking.pv
    return (
        (
            "Bob, god of Chaos and Spaghettis, decided that {attacking}'s "
            "and {defending}'s HP shall be exhanged",
            "",
            "Double trigonometric reversed possession",
            attacking.avatar_url,
        ),
        victim.hit(choice(weapon_list).split("|")),
    )


def intervention(
    attacking: Fighter,
    victim: Fighter,
    weapon_list: t.List[str],
) -> t.Tuple[HitReturn, HitReturn]:
    """Itsa me, Bob."""
    attacking.pv, victim.pv = 1000, 1000
    return (
        (
            "Michel, god of dad jokes, decided to restart the fight : "
            "each player now has 1000 HP",
            "",
            "Michel's intervention",
            attacking.avatar_url,
        ),
        victim.hit(choice(weapon_list).split("|")),
    )


def fumble(
    attacking: Fighter, _: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Oh shit."""
    message, damage, attack, url = attacking.hit(choice(weapon_list).split("|"))
    return (
        (
            "{attacking} just hurt himself !",
            "",
            "Fumble",
            attacking.avatar_url,
        ),
        (
            message.format(
                defending=attacking.display_name,
                attacking=attacking.display_name,
                damage=damage,
            ),
            damage,
            attack,
            url,
        ),
    )


def armor(
    attacking: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Suck on my thorns."""
    message, damage, attack, url = victim.hit(choice(weapon_list).split("|"))
    if damage == "":
        damage = "0"
    attacking.pv -= round(int(damage) / 2)
    return (
        (
            "{defending} wore a thorny armor, and {attacking} thus hurt"
            " himself for half the damage !",
            "",
            "Thorny armor",
            "https://66.media.tumblr.com/e68eb510217f17f96e1a7249294a01ee/"
            "tumblr_p7yj5oWrO91rvzucio1_1280.jpg",
        ),
        (
            message,
            damage,
            attack,
            url,
        ),
    )


def steal(
    attacking: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Your life is now mine."""
    message, damage, attack, url = victim.hit(choice(weapon_list).split("|"))
    if damage == "":
        damage = "0"
    attacking.pv += round(int(damage) / 2)
    return (
        (
            "{attacking}, thanks to a demonic ritual to the glory of our "
            "lord Satan, steals half the HP lost by {defending}.",
            "",
            "Life steal",
            attacking.avatar_url,
        ),
        (
            message,
            damage,
            attack,
            url,
        ),
    )


def depression(
    _: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """I wanna die."""
    return (
        (
            "{defending} thinks he is basically a piece of shit (which isn't "
            "totally false, by the way), making him pretty much easier to hit",
            "",
            "Depression",
            victim.avatar_url,
        ),
        victim.hit(choice(weapon_list).split("|"), 10),
    )


def bottle(
    attacking: Fighter, victim: Fighter, weapon_list: t.List[str]
) -> t.Tuple[HitReturn, HitReturn]:
    """Not a good idea."""
    return (
        (
            "{attacking} tried drinking from the hornet-filled bottle. He "
            "logically cannot very well aim for {defending}",
            "",
            "Hornet bottle",
            attacking.avatar_url,
        ),
        victim.hit(choice(weapon_list).split("|"), -10),
    )


chaos: t.List[t.Callable[[Fighter, Fighter, t.List[str]], t.Tuple[HitReturn, ...]]] = [
    pink,
    teleportation,
    combustion,
    election,
    mishap,
    double,
    intervention,
    fumble,
    armor,
    steal,
    depression,
    bottle,
]


class Funny(commands.Cog):
    """Some funny commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Funny."""
        self.bot = bot

    @app_commands.command()
    async def chuck(self, interaction: discord.Interaction) -> None:
        """Get a random Chuck Norris joke."""
        if randint(0, 1):
            async with self.bot.aio_session.get(
                "https://api.chucknorris.io/jokes/random"
            ) as response:
                joke = await response.json()
                await interaction.response.send_message(joke["value"])
            return

        # TODO : Fix for threads & shit
        if interaction.guild_id and not interaction.channel.is_nsfw():
            url = "http://api.icndb.com/jokes/random?exclude=[explicit]"
            async with self.bot.aio_session.get(url) as response:
                joke = await response.json()
                await interaction.response.send_message(joke["value"]["joke"])
            return
        async with self.bot.aio_session.get(
            "http://api.icndb.com/jokes/random"
        ) as response:
            joke = await response.json()
            await interaction.response.send_message(
                joke["value"]["joke"].replace("&quote", '"')
            )

    @app_commands.command()
    async def dad(self, interaction: discord.Interaction) -> None:
        """Get a random dad joke."""
        async with self.bot.aio_session.get(
            "https://icanhazdadjoke.com/slack"
        ) as response:
            joke = await response.json()
            await interaction.response.send_message(joke["attachments"][0]["text"])

    @app_commands.command()
    async def dong(
        self,
        interaction: discord.Interaction,
        dick: t.Optional[discord.Member] = None,
    ) -> None:
        """How long is this person's dong."""
        dickfinal = dick or interaction.user
        await interaction.response.send_message(
            f"{dickfinal.mention}'s magnum dong is this long : 8"
            f"{'=' * randint(0, 10)}>"
        )

    @app_commands.command()
    async def excuse(self, interaction: discord.Interaction) -> None:
        """We all do mishaps, and we all need a good excuse once in a while."""
        newline = "\n"  # One cannot use backslash in a f-string
        await interaction.response.send_message(
            "I'm sorry master... it's because "
            f"{choice(excuses[0].split('|')).strip(newline)} "
            f"{choice(excuses[1].split('|')).strip(newline)} in "
            f"{choice(excuses[2].split('|')).strip(newline)} and all of that "
            f"because of {choice(excuses[3].split('|')).strip(newline)} "
            f"{choice(excuses[4].split('|')).strip(newline)} which "
            f"{choice(excuses[5].split('|')).strip(newline)} "
            "so it's not my fault !"
        )

    # TODO : work on that
    # @app_commands.command(aliases=["baston"])
    # @app_commands.guild_only()
    async def fight(
        self,
        ctx: commands.Context,
        cible: discord.Member,
    ) -> None:
        """To punch someone to death.

        We won't be held accountable for any broken cranes, ripped guts
        or any other painful death.
        If you got any idea, use €suggestion fight [idea]
        """
        attacker = Fighter(ctx.author)
        defender = Fighter(cible)
        if defender.id == attacker.id:
            await self.bot.httpcat(
                ctx,
                403,
                "You cannot fight alone. Try asking a friend you don't like much.",
            )
        elif defender.id == self.bot.user.id:
            await self.bot.httpcat(
                ctx,
                403,
                "You cannot fight me : I'm juste the supreme judge.",
            )
        else:
            combat = True
            fight = [defender, attacker]
            while combat:
                next_player = fight[0]
                fight.reverse()
                if randint(1, 100) >= 85:
                    data = choice(chaos)(fight[0], next_player, weapons)
                else:
                    data = (next_player.hit(choice(weapons).split("|")),)
                for message, damage, attack, url in data:
                    embed = discord.Embed(
                        title=attack,
                        description=message.format(
                            attacking=fight[0].display_name,
                            defending=next_player.display_name,
                            damage=damage,
                        ),
                        colour=discord.Colour.random(),
                    )
                    embed.set_author(
                        name=fight[0].display_name,
                        icon_url=fight[0].avatar_url,
                    )
                    embed.set_thumbnail(url=url)
                    await ctx.send(embed=embed)
                embed = discord.Embed(
                    title=fight[0].display_name,
                    colour=discord.Colour.blue(),
                )
                embed.set_thumbnail(url=fight[0].avatar_url)
                embed.add_field(name="Remaining HP :", value=str(fight[0].pv))
                await ctx.send(embed=embed)
                embed = discord.Embed(
                    title=next_player.display_name,
                    colour=discord.Colour.blurple(),
                )
                embed.set_thumbnail(url=next_player.avatar_url)
                embed.add_field(name="Remaining HP :", value=str(next_player.pv))
                await ctx.send(embed=embed)
                if next_player.pv > 0 and fight[0].pv > 0:

                    def check(message: discord.Message) -> bool:
                        if message.author.id == next_player.id and (
                            message.content.lower().startswith(
                                f"defend {fight[0].display_name.lower()}"
                            )
                        ):
                            return message.channel == ctx.channel
                        return False

                    await ctx.send(
                        f"{next_player.mention}, send `defend "
                        f"{fight[0].display_name}` in the next 30 seconds, "
                        "or run away like a coward."
                    )
                    try:
                        await self.bot.wait_for(
                            "message",
                            check=check,
                            timeout=30.0,
                        )
                    except asyncio.TimeoutError:
                        await ctx.send(f"{next_player.display_name} is just a coward.")
                        combat = False
                elif next_player.pv < fight[0].pv:
                    combat = False
                    await ctx.send(
                        f"{fight[0].display_name} annihilated "
                        f"{next_player.display_name}. What a show !"
                    )
                else:
                    combat = False
                    await ctx.send(
                        f"{next_player.display_name} annihilated "
                        f"{fight[0].display_name}. What a show !"
                    )

    @app_commands.command()
    async def joke(self, interaction: discord.Interaction) -> None:
        """Send a random joke."""
        async with self.bot.aio_session.get(
            "https://mrwinson.me/api/jokes/random"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    description=data["joke"], colour=discord.Colour.gold()
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Something went wrong.")
                await self.bot.log_channel.send(f"Code {resp.status} in joke")

    @app_commands.command()
    async def kill(
        self,
        interaction: discord.Interaction,
        target: str,
    ) -> None:
        """Just in case you wanna kill your neighbour."""
        await interaction.response.send_message(
            choice(death).format(
                author=interaction.user.display_name,
                victim=target,
            )
        )


async def setup(bot: commands.Bot) -> None:
    """Load the Funny cog."""
    await bot.add_cog(Funny(bot))
