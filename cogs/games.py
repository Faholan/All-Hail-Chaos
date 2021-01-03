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

import asyncio
from datetime import datetime
from itertools import cycle
from random import shuffle
import traceback
from typing import Iterator

import discord
from discord.ext import commands, menus, tasks


class Connect4(menus.Menu):
    """How to play connect4."""

    def __init__(self, *players, **kwargs) -> None:
        """Initialize the game."""
        super().__init__(**kwargs)
        self.winner = None
        self.id_dict = {players[i].id: i + 1 for i in range(len(players))}
        self.ids = cycle(list(self.id_dict))
        self.players = players
        self.next = next(self.ids)
        self.status = [
            ":black_large_square:",
            ":green_circle:",
            ":red_circle:"
        ]
        self.state = [[0 for _ in range(6)] for __ in range(7)]

    async def update(self, payload: discord.RawReactionActionEvent) -> None:
        """On payload, do that."""
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception as error:
            embed = discord.Embed(color=0xFF0000)
            embed.set_author(
                name=str(self.ctx.author),
                icon_url=str(self.ctx.author.avatar_url)
            )
            embed.title = f"{self.ctx.author.id} caused an error in connect 4"
            embed.description = f"{type(error).__name__} : {error}"
            if self.ctx.guild:
                embed.description += (
                    f"\nin {self.ctx.guild} "
                    f"({self.ctx.guild.id})\n   in {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})"
                )
            elif isinstance(self.ctx.channel, discord.DMChannel):
                embed.description += (
                    f"\nin a Private Channel ({self.ctx.channel.id})"
                )
            else:
                embed.description += (
                    f"\nin the Group {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})"
                )
            formatted_tb = "".join(traceback.format_tb(error.__traceback__))
            embed.description += f"```\n{formatted_tb}```"
            embed.set_footer(
                text=f"{self.bot.user.name} Logging",
                icon_url=self.ctx.bot.user.avatar_url_as(static_format="png"),
            )
            embed.timestamp = datetime.utcnow()
            try:
                await self.bot.log_channel.send(embed=embed)
            except Exception:
                await self.bot.log_channel.send(
                    "Please check the logs for connect 4"
                )
                raise error

    def reaction_check(self, payload: discord.RawReactionActionEvent) -> bool:
        """Whether or not to process the payload."""
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    def get_embed(self) -> discord.Embed:
        """Generate the next embed."""
        return discord.Embed(
            description="\n".join(
                ["".join(
                    [self.status[column[5 - i]] for column in self.state]
                ) for i in range(6)])
            )

    async def send_initial_message(
            self,
            ctx: commands.Context,
            channel: discord.TextChannel) -> discord.Message:
        """Send the first message."""
        return await ctx.send(embed=self.get_embed())

    async def action(
            self,
            number: int,
            payload: discord.RawReactionActionEvent) -> None:
        """Do something."""
        if 0 not in self.state[number]:
            return
        self.next = next(self.ids)
        next_id = self.id_dict[payload.user_id]
        self.state[number][self.state[number].index(0)] = next_id
        await self.embed_updating()
        check = self.check(next_id)
        if check:
            self.winner = self.players[next_id - 1]
            return self.stop()

    def check(self, user_id: int) -> bool:
        """Did you win."""
        schema = str(user_id) + 3 * f", {user_id}"
        if any(schema in str(x) for x in self.state):
            return True
        for i in range(6):
            if schema in str([column[i] for column in self.state]):
                return True
        for diagonal in range(3):
            lines = [
                [
                    self.state[3 + diagonal - i][i]
                    for i in range(4 + diagonal)
                ],
                [
                    self.state[i - diagonal - 4][-i - 1]
                    for i in range(4 + diagonal)
                ],
                [
                    self.state[i - diagonal - 4][i]
                    for i in range(4 + diagonal)
                ],
                [
                    self.state[3 + diagonal - i][-i - 1]
                    for i in range(4 + diagonal)
                ],
            ]
            if any(schema in line for line in lines):
                return True
        return False

    async def embed_updating(self) -> None:
        """Update the embed."""
        await self.message.edit(embed=self.get_embed())

    @menus.button("1\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_1(self, payload: discord.RawReactionActionEvent) -> None:
        """First column."""
        await self.action(0, payload)

    @menus.button("2\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_2(self, payload: discord.RawReactionActionEvent) -> None:
        """Second column."""
        await self.action(1, payload)

    @menus.button("3\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_3(self, payload: discord.RawReactionActionEvent) -> None:
        """Third column."""
        await self.action(2, payload)

    @menus.button("4\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_4(self, payload: discord.RawReactionActionEvent) -> None:
        """Fourth column."""
        await self.action(3, payload)

    @menus.button("5\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_5(self, payload: discord.RawReactionActionEvent) -> None:
        """Fifth column."""
        await self.action(4, payload)

    @menus.button("6\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_6(self, payload: discord.RawReactionActionEvent) -> None:
        """Sixth column."""
        await self.action(5, payload)

    @menus.button("7\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_7(self, payload: discord.RawReactionActionEvent) -> None:
        """Seventh column."""
        await self.action(6, payload)

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload: discord.RawReactionActionEvent) -> None:
        """Stop."""
        self.stop()

    async def prompt(self, ctx: commands.Context) -> discord.User:
        """Start it the real way."""
        await self.start(ctx, wait=True)
        return self.winner


class BCard:
    """A blackjack card."""

    def __init__(self, value: int, colour: int) -> None:
        """Initialize the card."""
        self._value = value
        self.is_ace = value == 1
        self.colour = colour

    @property
    def name(self) -> str:
        """Get the card's full name."""
        if self.is_ace:
            fullname = "Ace of "
        elif self._value > 10:
            fullname = ["Jack", "Queen", "King"][self._value - 11] + " of "
        else:
            fullname = f"{self._value} of "
        fullname += [
            "\U00002660\N{variation selector-16}",
            "\U00002663\N{variation selector-16}",
            "\U00002665\N{variation selector-16}",
            "\U00002666\N{variation selector-16}",
        ][self.colour]
        return fullname
        # spades, clubs, hearts, diamonds

    @property
    def value(self) -> int:
        """Get the card's worth."""
        if self._value > 10:
            return 10
        return self._value

    def tuple(self) -> tuple:
        """Get the card as a tuple."""
        return (self._value, self.colour)

    def __eq__(self, other) -> bool:
        """Check if two cards are equal in value."""
        return self._value == other._value

    def min(self) -> int:
        """Get the card's minimal value."""
        if self.is_ace:
            return 1
        return self.value


class BRow(list):
    """A row of blackjack cards."""

    def isvalid(self) -> bool:
        """Check the row's validity."""
        return self.value_min() <= 21

    def value_min(self) -> int:
        """Get the minimal value of the row."""
        return sum([card.min() for card in self])

    def value(self) -> int:
        """Get the real value of the row."""
        total_value = self.value_min()
        ace_counter = 0
        for card in self:
            if card.is_ace:
                ace_counter += 1
        while ace_counter:
            if total_value <= 11:
                total_value += 10
                ace_counter -= 1
            else:
                break
        return total_value


class Deck:
    """A deck full of rows."""

    def __init__(self, money: int, cost: int, player_id: int) -> None:
        """Initialize the deck."""
        self.cards = [BRow()]
        self._money = money
        self.balance = - cost
        self.cost = cost
        self.player_id = player_id

    @property
    def money(self) -> int:
        """Get your money."""
        return self._money + self.balance

    def __contains__(self, card: BCard) -> bool:
        """If a card is in the deck."""
        return any(
            card in column for column in self.cards
        ) and len(self.cards) < 3

    def __iter__(self) -> Iterator:
        """Iterate over me."""
        return self.cards.__iter__()

    def isvalid(self) -> bool:
        """Check the validity of the deck."""
        return any(
            column.isvalid() for column in self.cards
        ) and self.money > 0

    async def add(
            self,
            card: BCard,
            ctx: commands.Context,
            ini: bool = False) -> None:
        """Add a card to the deck."""
        if card in self and self.cost < self.money and not ini:
            def check(message: discord.Message) -> bool:
                if message.author == ctx.author:
                    if message.channel == ctx.channel:
                        return message.content.lower() in [
                            "y", "yes", "n", "no"
                        ]
                return False
            message1 = await ctx.send(
                f"You have a {card.name}. Do you want to split ? (y/n)"
            )
            try:
                message = await ctx.bot.wait_for(
                    "message",
                    check=check,
                    timeout=30,
                )
                answer = message.content.lower().startswith("y")
            except asyncio.TimeoutError:
                answer = False
                message = None
            try:
                await message1.delete()
                if message:
                    await message.delete()
            except discord.DiscordException:
                pass
            if answer:
                return self.split(card)
        row_numbers = [
            i for i in range(len(self.cards)) if self.cards[i].isvalid()
        ]
        if len(row_numbers) == 1:
            card_id = row_numbers[0]
        else:
            message1 = await ctx.send(
                f"You have {len(row_numbers)} rows available. "
                "In which one do you want to play ?"
            )

            def check2(message: discord.Message) -> bool:
                if message.author == ctx.author and (
                        message.channel == ctx.channel
                        and message.content.isdigit()):
                    try:
                        return self.cards[int(message.content) - 1].isvalid()
                    except Exception:
                        pass
                return False

            try:
                message = await ctx.bot.wait_for(
                    "message",
                    check=check2,
                    timeout=30,
                )
                card_id = int(message.content) - 1
            except asyncio.TimeoutError:
                card_id = row_numbers[0]
                await ctx.send(
                    f"Defaulting to row {card_id + 1}", delete_after=3
                )
            try:
                await message1.delete()
                await message.delete()
            except discord.DiscordException:
                pass
        self.cards[card_id].append(card)

    def split(self, card: BCard) -> None:
        """Split a card."""
        self.balance -= self.cost
        self.cards.append(BRow([card]))


class Blackjack(menus.Menu):
    """Let's play Blackjack."""

    def __init__(
            self,
            players: list,
            money_dict: dict,
            cost: int,
            **kwargs) -> None:
        """Initialize all the fuzzy stuff."""
        super().__init__(**kwargs)
        self.ids = cycle([player.id for player in players])
        self.index = cycle(range(len(players)))
        self.next = next(self.ids)
        self.next_index = next(self.index)

        self.player_dict = {player.id: player for player in players}
        self.money_dict = money_dict
        self.cost = cost

        self.cards = []
        self.players = []
        self.dealer: BRow = None
        self.next_card: BCard = None

    async def update(self, payload: discord.RawReactionActionEvent) -> None:
        """Update if necessary."""
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception as error:
            embed = discord.Embed(color=0xFF0000)
            embed.set_author(
                name=str(self.ctx.author),
                icon_url=str(self.ctx.author.avatar_url),
            )
            embed.title = f"{self.ctx.author.id} caused an error in Blackjack"
            embed.description = f"{type(error).__name__} : {error}"
            if self.ctx.guild:
                embed.description += (
                    f"\nin {self.ctx.guild} ({self.ctx.guild.id})\n   in "
                    f"{self.ctx.channel.name} ({self.ctx.channel.id})"
                )
            elif isinstance(self.ctx.channel, discord.DMChannel):
                embed.description += (
                    f"\nin a Private Channel ({self.ctx.channel.id})"
                )
            else:
                embed.description += (
                    f"\nin the Group {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})"
                )
            formatted_tb = "".join(traceback.format_tb(error.__traceback__))
            embed.description += f"```\n{formatted_tb}```"
            embed.set_footer(
                text=f"{self.bot.user.name} Logging",
                icon_url=self.ctx.bot.user.avatar_url_as(static_format="png"),
            )
            embed.timestamp = datetime.utcnow()
            try:
                await self.bot.log_channel.send(embed=embed)
            except Exception:
                await self.bot.log_channel.send(
                    "Please check the logs for Blackjack"
                )
                raise error

    def reaction_check(self, payload: discord.RawReactionActionEvent) -> bool:
        """Whether or not it shall be processed."""
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    @property
    def card(self) -> BCard:
        """Get a random card."""
        shuffle(self.cards)
        return self.cards.pop()

    async def new_game(self) -> None:
        """Start a new game."""
        self.cards = [
            BCard(i + 1, j) for i in range(13)
            for j in range(4)
            for _ in range(6)
        ]
        self.players = [
            Deck(self.money_dict[i], self.cost, i) for i in self.money_dict
        ]
        self.dealer = BRow()
        self.dealer.append(self.card)
        for i in range(len(self.players)):
            for _ in range(2):
                await self.players[i].add(self.card, None, True)
        self.next_card = self.card

    def generate_embed(self) -> discord.Embed:
        """Generate the next embed."""
        embed = discord.Embed(title=f"The bet is fixed at {self.cost} GP")
        embed.add_field(
            name="Dealer :",
            value=", ".join([card.name for card in self.dealer]),
            inline=False,
        )
        for player in self.players:
            embed.add_field(
                name=(
                    f"{self.player_dict[player.player_id].display_name} "
                    f"({player.money} GP)"
                ),
                value="\n".join(
                    [", ".join(
                        [card.name for card in row]
                    ) for row in player.cards]
                ),
                inline=False,
            )
        return embed

    async def send_initial_message(
            self,
            ctx: commands.Context,
            channel: discord.TextChannel) -> discord.Message:
        """Send the first embed."""
        return await ctx.send(
            self.player_dict[self.next].mention, embed=self.generate_embed()
        )

    async def update_embed(self, new_turn: bool = False) -> None:
        """Update the embed."""
        if new_turn:
            self.next = next(self.ids)
            self.next_index = next(self.index)
            if self.next_index == 0:
                return await self.result()
        else:
            self.next_card = self.card
        await self.message.edit(
            content=self.player_dict[self.next].mention,
            embed=self.generate_embed(),
        )

    async def result(self) -> None:
        """Run this at the end."""
        while self.dealer.value() < 17:
            self.dealer.append(self.card)

        embed = discord.Embed()

        if not self.dealer.isvalid():
            number = "Busted"
            dealer_score = 0
        elif len(self.dealer) == 2 and self.dealer.value() == 21:
            number = "Blackjack"
            dealer_score = 22
        else:
            dealer_score = self.dealer.value()
            number = f"{dealer_score} points"
        number += f" : {', '.join([card.name for card in self.dealer])}"
        embed.add_field(name="Dealer", value=number, inline=False)
        for player in self.players:
            numbers = []
            if player.cards[0].value() == 21 and len(player.cards) == 1 and (
                    len(player.cards[0]) == 2):
                numbers.append(
                    "Blackjack : "
                    f"{', '.join([card.name for card in player.cards[0]])}"
                )
                if dealer_score == 22:
                    player.balance += self.cost
                else:
                    player.balance += round(2.5 * self.cost)
            else:
                for row in player.cards:
                    if row.isvalid():
                        numbers.append(
                            f"{row.value()} points : "
                            f"{', '.join([card.name for card in row])}"
                        )
                        if row.value() == dealer_score:
                            player.balance += self.cost
                        elif row.value() > dealer_score:
                            player.balance += 2 * self.cost
                    else:
                        numbers.append(
                            "Busted : "
                            f"{', '.join([card.name for card in row])}"
                        )
            embed.add_field(
                name=(
                    f"{self.player_dict[player.player_id]} : {player.money}"
                    " GP"
                ),
                value="\n".join(numbers),
                inline=False,
            )
        await self.message.edit(content=None, embed=embed)
        self.stop()

    @menus.button("\U00002795")
    async def action(self, payload: discord.RawReactionActionEvent) -> None:
        """Get a card."""
        await self.players[self.next_index].add(self.next_card, self.ctx)
        await self.update_embed(not self.players[self.next_index].isvalid())

    @menus.button("\U0000274c")
    async def next_turn(self, payload: discord.RawReactionActionEvent) -> None:
        """Time for the next player to shine."""
        await self.update_embed(True)

    async def prompt(self, ctx: commands.Context) -> dict:
        """Start it the real way."""
        await self.new_game()
        await self.start(ctx, wait=True)
        return {P.player_id: P.balance for P in self.players}


class Blackjackplayers(menus.Menu):
    """Menu to check who wants to play."""

    def __init__(
            self,
            author: discord.User,
            author_money: int,
            cost: int,
            database,
            **kwargs) -> None:
        """Get who wanna play."""
        super().__init__(**kwargs)
        self.players = [author]
        self.money_dict = {author.id: author_money}
        self.lock = asyncio.Lock()
        self.database = database
        self.cost = cost
        self.current_state = 0
        self.time = 0

    def reaction_check(self, payload: discord.RawReactionActionEvent) -> bool:
        """Check whether or not to process the reaction."""
        return payload.message_id == self.message.id and (
            payload.user_id != self.bot.user.id
        )

    async def update(self, payload: discord.RawReactionActionEvent) -> None:
        """Update if necessary."""
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception as error:
            embed = discord.Embed(color=0xFF0000)
            embed.set_author(
                name=str(self.ctx.author),
                icon_url=str(self.ctx.author.avatar_url),
            )
            embed.title = (
                f"{self.ctx.author.id} caused an error in Blackjack Players"
            )
            embed.description = f"{type(error).__name__} : {error}"
            if self.ctx.guild:
                embed.description += (
                    f"\nin {self.ctx.guild} ({self.ctx.guild.id})\n   in "
                    f"{self.ctx.channel.name} ({self.ctx.channel.id})"
                )
            elif isinstance(self.ctx.channel, discord.DMChannel):
                embed.description += (
                    f"\nin a Private Channel ({self.ctx.channel.id})"
                )
            else:
                embed.description += (
                    f"\nin the Group {self.ctx.channel.name} "
                    f"({self.ctx.channel.id})"
                )
            formatted_tb = "".join(traceback.format_tb(error.__traceback__))
            embed.description += f"```\n{formatted_tb}```"
            embed.set_footer(
                text=f"{self.bot.user.name} Logging",
                icon_url=self.ctx.bot.user.avatar_url_as(static_format="png"),
            )
            embed.timestamp = datetime.utcnow()
            try:
                await self.bot.log_channel.send(embed=embed)
            except Exception:
                await self.bot.log_channel.send(
                    "Please check the logs for Blackjack Players"
                )
                raise error

    async def send_initial_message(
            self,
            ctx: commands.Context,
            channel: discord.TextChannel) -> discord.Message:
        """Send the first embed."""
        self.time = 120
        self.current_state = 1
        return await ctx.send(embed=self.get_embed())

    async def updater(self) -> None:
        """Update the embed."""
        self.time -= 5
        await self.message.edit(embed=self.get_embed())
        if self.time <= 0:
            self.stop()

    def get_embed(self) -> discord.Embed:
        """Get the embed."""
        newline = "\n -"
        return discord.Embed(
            title=(
                f"Come play blackjack ! Initial bet is {self.cost} GP "
                f"({self.time} seconds left)"
            ),
            description=(
                "Check the command's help for the rules. React with "
                ":white_check_mark: to join, :track_next: to begin the game"
                "\n\nCurrent players :\n -"
                f"{newline.join([player.mention for player in self.players])}"
            ),
        )

    @menus.button("\U00002705")
    async def adder(self, payload: discord.RawReactionActionEvent) -> None:
        """Add a player."""
        member = self.ctx.guild.get_member(
            payload.user_id
        ) or await self.ctx.guild.fetch_member(payload.user_id)
        async with self.lock:
            row = await self.database.fetchrow(
                "SELECT * FROM public.business WHERE id=$1", payload.user_id
            )
            if not row:
                return await self.ctx.send(
                    f"Sorry {member.mention}, but you don't have any money "
                    "to join this table"
                )
            if payload.user_id in self.money_dict:
                del self.money_dict[payload.user_id]
            else:
                money = row["money"] + row["bank"]
                if money < self.cost:
                    return await self.ctx.send(
                        f"Sorry {member.mention}, but you don't have enough "
                        "money to come to this table"
                    )
                self.money_dict[payload.user_id] = money
        if member in self.players:
            self.players.remove(member)
        else:
            self.players.append(member)

    @menus.button("\U000023ed\N{variation selector-16}")
    async def skipper(self, payload: discord.RawReactionActionEvent) -> None:
        """Start the game ahead of time."""
        self.time = 5
        self.current_state = -1
        await self.updater()

    async def prompt(self, ctx: commands.Context) -> tuple:
        """Start it the real way."""
        await self.start(ctx, wait=True)
        return self.players, self.money_dict

    def stop(self) -> None:
        """Stop the thingy."""
        self.current_state = -1
        super().stop()


class Games(commands.Cog):
    """Good games."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the games."""
        self.bot = bot
        self.blackjack_list = []
        self.blackjack_updater.start()

    def cog_unload(self) -> None:
        """Cleanup on cog unload."""
        self.blackjack_updater.cancel()

    @commands.command(ignore_extra=True)
    async def blackjack(self, ctx: commands.Context, cost: int = 5) -> None:
        """Please see the detailed help.

        Rules : if it's your turn, press the \U00002795 button to get a card.
        If you want to stop, press \U0000274c, and the next player will play.
        To win, you must score more than the dealer, but no more than 21.
        Each card's value is its pip value, except faces.
        Those are worth 10 points, and the Ace is worth either 1 or 11.
        An Ace plus a face is called a blackjack, and beats a 21
        """
        if cost < 0:
            await ctx.send("You can't bet negative money")
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.business WHERE id=$1", ctx.author.id
            )
            if not row:
                return await ctx.send(
                    "You don't have money. You can't run this command without "
                    "yourself having money"
                )
            money = row["money"] + row["bank"]
            if money < cost:
                return await ctx.send(
                    "Sorry, but you don't have enough money"
                    " to come to this table"
                )
            new_players = Blackjackplayers(
                ctx.author,
                money,
                cost,
                database,
                delete_message_after=True,
            )
            self.blackjack_list.append(new_players)
            players, money_dict = await new_players.prompt(ctx)
        if not players:
            return await ctx.send("Nobody wants to play")
        balance_dict = await Blackjack(
            players,
            money_dict,
            cost,
            clear_reactions_after=True,
        ).prompt(ctx)
        async with self.bot.pool.acquire() as database:
            for player_id in balance_dict:
                if balance_dict[player_id] >= 0:
                    await database.execute(
                        "UPDATE public.business SET money=money+$2 WHERE "
                        "id=$1",
                        player_id,
                        balance_dict[player_id],
                    )
                else:
                    row = await database.fetchrow(
                        "SELECT * FROM public.business WHERE id=$1", player_id
                    )
                    if row["money"] >= -balance_dict[player_id]:
                        await database.execute(
                            "UPDATE public.business SET money=money+$2 WHERE "
                            "id=$1",
                            player_id,
                            balance_dict[player_id],
                        )
                    else:
                        await database.execute(
                            "UPDATE public.business SET money=0, bank=bank+$2"
                            " WHERE id=$1",
                            player_id,
                            row["money"] + balance_dict[player_id],
                        )

    @tasks.loop(seconds=5)
    async def blackjack_updater(self) -> None:
        """Update all Blackjackplayers menus."""
        new = []
        for black in self.blackjack_list:
            if black.current_state == 1:
                await black.updater()
            elif black.current_state == -1:
                continue
            new.append(black)
        self.blackjack_list = new

    @commands.command(aliases=["c4"])
    async def connect4(
            self, ctx: commands.Context, member: discord.Member) -> None:
        """Play connect 4 with a friend."""
        winner = await Connect4(
            ctx.author,
            member,
            clear_reactions_after=True
        ).prompt(ctx)
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")


def setup(bot: commands.Bot) -> None:
    """Add games to the bot."""
    bot.add_cog(Games(bot))
