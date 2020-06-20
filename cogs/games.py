import asyncio
from itertools import cycle
from math import inf
from random import shuffle

import discord
from discord.ext import commands, menus, tasks

class connect4(menus.Menu):
    def __init__(self, *players, **kwargs):
        super().__init__(**kwargs)
        self.winner = None
        self.id_dict = {players[i].id : i+1 for i in range(len(players))}
        self.ids = cycle(list(self.id_dict))
        self.players = players
        self.next = next(self.ids)
        self.status = [":black_large_square:", ":green_circle:", ":red_circle:"]
        self.state = [[0 for _ in range(6)] for __ in range(7)]

    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    def get_embed(self):
        return discord.Embed(description = "\n".join(["".join([self.status[column[5 - i]] for column in self.state]) for i in range(6)]))

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(embed = self.get_embed())

    async def action(self, n, payload):
        if not 0 in self.state[n]:
            return
        self.next = next(self.ids)
        ID = self.id_dict[payload.user_id]
        self.state[n][self.state[n].index(0)] = ID
        await self.embed_updating()
        check = self.check(ID)
        if check:
            self.winner = self.players[ID - 1]
            return self.stop()

    def check(self, id):
        S = str(id) + 3*f", {id}"
        if any(S in str(x) for x in self.state):
            return True
        for i in range(6):
            if S in str([column[i] for column in self.state]):
                return True
        for i in range(3):
            L, L2, L3, L4 = [], [], [], []
            for c in range(4 + i):
                L.append(self.state[3 + i - c][c])
                L2.append(self.state[3 + i - c][5 - c])
                L3.append(self.state[3 - i + c][c])
                L4.append(self.state[3 - i + c][5 - c])
            if any(S in str(column) for column in (L, L2, L3, L4)):
                return True
        return False

    async def embed_updating(self):
        await self.message.edit(embed = self.get_embed())

    @menus.button("1\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_1(self, payload):
        await self.action(0, payload)

    @menus.button("2\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_2(self, payload):
        await self.action(1, payload)

    @menus.button("3\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_3(self, payload):
        await self.action(2, payload)

    @menus.button("4\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_4(self, payload):
        await self.action(3, payload)

    @menus.button("5\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_5(self, payload):
        await self.action(4, payload)

    @menus.button("6\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_6(self, payload):
        await self.action(5, payload)

    @menus.button("7\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_7(self, payload):
        await self.action(6, payload)

    @menus.button('\N{BLACK SQUARE FOR STOP}\ufe0f')
    async def on_stop(self, payload):
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.winner

class BCard():
    def __init__(self, value, colour):
        self._value = value
        self.is_ace = value == 1
        self.colour = colour

    @property
    def name(self):
        if self.is_ace:
            N = "Ace of "
        elif self._value > 10:
            N = ["Jack", "Queen", "King"][self._value - 11] + " of "
        else:
            N = f"{self._value} of "
        N += ["\U00002660\N{variation selector-16}", "\U00002663\N{variation selector-16}", "\U00002665\N{variation selector-16}", "\U00002666\N{variation selector-16}"][self.colour]
        return N
        #spades, clubs, hearts, diamonds

    @property
    def value(self):
        if self._value > 10:
            return 10
        return self._value

    def tuple(self):
        return (self._value, self.colour)

    def __eq__(self, other):
        return self.value == other.value

    def min(self):
        if self.is_ace:
            return 1
        return self.value

class BRow(list):
    def isvalid(self):
        return self.value_min() <= 21

    def value_min(self):
        return sum([card.min() for card in self])

    def value(self):
        V = self.value_min()
        c = self.count(BCard(11, 0))
        while c:
            if V <= 11:
                V+=10
                c -= 1
            else:
                break
        return V

class Deck():
    def __init__(self, money, cost, player_id):
        self.cards = [BRow()]
        self.money = money - cost
        self.cost = cost
        self.player_id = player_id

    def __contains__(self, card):
        return any(card in column for column in self.cards) and len(self.cards) < 3

    def __iter__(self):
        return self.cards

    def isvalid(self):
        return any(column.isvalid() for column in self.cards) and self.money > 0

    def add(self, card, id):
        if len(self.cards) == 0:
            id = 0
        if not self.cards[id].isvalid():
            raise IndexError("You cannot play here")
        self.cards[id].append(card)

    def split(self, card):
        if not card in self:
            raise ValueError("You don't have this card yet")
        if self.cost > self.money:
            raise ValueError("You don't have enough money to split")
        self.money -= self.cost
        self.cards.append(BRow([card]))

class Blackjack(menus.Menu):
    def __init__(self, players, **kwargs):
        super().__init__(**kwargs)
        self.ids = cycle([player.id for player in players])
        self.index = cycle([i for i in range(len(players))])
        self.next = next(self.ids)
        self.next_index = next(self.index)

        self.player_dict = {player.id : player for player in players}
        self.money_dict = {player.id : 100 for player in players}
        self.new_game()

    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False

        return payload.user_id == self.next and payload.emoji in self.buttons

    @property
    def card(self):
        shuffle(self.cards)
        return self.cards.pop()

    def new_game(self):
        self.cards = [BCard(i+1, j) for i in range(13) for j in range(4) for _ in range(6)]
        self.players = [Deck(self.money_dict[i], 5, i) for i in self.money_dict]
        self.dealer = BRow()
        self.dealer.append(self.card)
        for i in range(len(self.players)):
            for _ in range(2):
                self.players[i].add(self.card, 0)
        self.next_card = self.card

    def generate_embed(self):
        self.embed = discord.Embed(title = "Each game costs 5 $")
        self.embed.add_field(name = "Dealer :", value = ", ".join([card.name for card in self.dealer]), inline = False)
        for player in self.players:
            self.embed.add_field(name = f"{self.player_dict[player.player_id].display_name} ({player.money} $)", value = "\n".join([", ".join([card.name for card in row]) for row in player.cards]), inline = False)
        return self.embed

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(self.player_dict[self.next].mention, embed = self.generate_embed())

    async def update_embed(self, new_turn = False):
        if new_turn:
            self.next = next(self.ids)
            self.next_index = next(self.index)
            if self.next_index == 0:
                return await self.result()
        else:
            self.next_card = self.card
        await self.message.edit(content = self.player_dict[self.next].mention, embed = self.generate_embed())

    async def result(self):
        while self.dealer.value() < 17:
            self.dealer.append(self.card)

        embed = discord.Embed()

        if not self.dealer.isvalid():
            n = "Busted"
            V = 0
        elif len(self.dealer) == 2 and self.dealer.value() == 21:
            n = "Blackjack"
            V = 22
        else:
            V = self.dealer.value()
            n = f"{V} points"
        embed.add_field(name = "Dealer", value = n)
        for player in self.players:
            n = []
            if player.cards[0].value == 21 and len(player.cards) == 1 and len(player.cards[0]) == 2:
                n.append("Blackjack")
                if V == 22:
                    player.money += 5
                else:
                    player.money += round(2.5 *5)
            else:
                for row in player.cards:
                    if row.isvalid():
                        n.append(f"{row.value()} points")
                        if row.value() == V:
                            player.money += 5
                        elif row.value() > V:
                            player.money += 2 * 5
                    else:
                        n.append("Busted")
            embed.add_field(name = f"{self.player_dict[player.player_id]} : {player.money} $", value = ", ".join(n))
        await self.message.edit(embed = embed)
        self.stop()

    @menus.button("\U0001f1f8")
    async def split(self, payload):
        try:
            self.players[self.next_index].split(self.next_card)
        except Exception as e:
            return await self.message.edit(content = str(e), embed = self.embed)
        await self.update_embed()

    async def action(self, index, payload):
        try:
            self.players[self.next_index].add(self.next_card, index)
        except:
            return await self.message.edit(content = "You can't add a card there", embed = self.embed)
        await self.update_embed()

    @menus.button("1\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_1(self, payload):
        await self.action(0, payload)

    @menus.button("2\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_2(self, payload):
        await self.action(1, payload)

    @menus.button("3\N{variation selector-16}\N{combining enclosing keycap}")
    async def column_3(self, payload):
        await self.action(2, payload)

    @menus.button("\U0000274c")
    async def next_turn(self, payload):
        await self.update_embed(True)

class Blackjack_players(menus.Menu):
    def __init__(self, author, **kwargs):
        super().__init__(**kwargs)
        self.players = [author]

    def reaction_check(self, payload):
        return payload.message_id == self.message.id and payload.user_id != self.bot.user.id

    async def send_initial_message(self, ctx, channel):
        self.time = 120
        self.updater.start()
        return await ctx.send(embed = self.get_embed())

    @tasks.loop(seconds = 5)
    async def updater(self):
        self.time -= 5
        await self.message.edit(embed = self.get_embed())
        if self.time == 0:
            self.stop()

    @updater.before_loop
    async def waiter(self):
        await asyncio.sleep(5)

    def get_embed(self):
        r = "\n -"
        return discord.Embed(title = f"Come play blackjack ! ({self.time} seconds left)",
            description = f"Check the command's help for the rules. React with :white_check_mark: to join\n\nCurrent players :\n -{r.join([player.mention for player in self.players])}")

    @menus.button("\U00002705")
    async def adder(self, payload):
        member = self.ctx.guild.get_member(payload.user_id)
        if member in self.players:
            self.players.remove(member)
        else:
            self.players.append(member)

    @menus.button("\U000023ed\N{variation selector-16}")
    async def skipper(self, payload):
        self.time = 5

    async def prompt(self, ctx):
        await self.start(ctx, wait = True)
        return self.players

    def stop(self):
        self.updater.stop()
        super().stop()

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ["c4"])
    async def connect4(self, ctx, member : discord.Member):
        """Play connect 4 with a friend"""
        winner = await connect4(ctx.author, member, clear_reactions_after = True).prompt(ctx)
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")

    @commands.command(ignore_extra = True)
    async def blackjack(self, ctx):
        """Please see the detailed help
        Rules : if it's your turn, press the button corresponding to the column in which you wana place the card.
        If you want to split (play on one more column, up to a max of 3, press :regional_indicator_3:). If you want to stop, press :x:.
        To win, you must score more than the dealer, but no more than 21 (each card's value is its pip value, except faces, which are worth 10 points, and the Ace, which is worth either 1 or 11).
        An Ace plus a face is called a blackjack, and beats a 21"""
        players = await Blackjack_players(ctx.author, clear_reactions_after = True).prompt(ctx)
        await Blackjack(players, clear_reactions_after = True).start(ctx)

def setup(bot):
    bot.add_cog(Games(bot))
