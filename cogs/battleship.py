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
SOFTWARE."""

import asyncio
from random import choice,randint
from discord.ext import commands

green = ":green_square:"
blue = ":blue_square:"
red = ":red_square:"
white = ":white_large_square:"
black = ":black_large_square:"

class Battleship(commands.Cog):
    """Play battleship !!"""
    def __init__(self, bot):
        self.bot = bot
        self.boat_size = [(5, "Carrier"), (4, "Battleship"), (3, "Cruiser"), (3, "Submarine"), (2, "Destroyer")]
        self.column = list("abcdefghij")

    def j2_boats(self):
        j2, boats = [[0]*10 for _ in range(10)], []
        for i, k in self.boat_size:
            test = True
            while test:
                test = False
                a, b = [randint(0, 9), randint(0, 9)], randint(0, 1)
                if b:
                    if a[1] <= 10 - i:
                        if a[1] != 0:
                            if j2[a[0]][a[1] - 1] != 0:
                                test = True
                            if a[0] != 0:
                                if j2[a[0] - 1][a[1] - 1] != 0:
                                    test = True
                            if a[0] != 9:
                                if j2[a[0] + 1][a[1] - 1] != 0:
                                    test = True
                        if a[1] + i < 10:
                            if j2[a[0]][a[1] + i] != 0:
                                test = True
                            if a[0] != 9:
                                if j2[a[0] + 1][a[1] + i] != 0:
                                    test = True
                            if a[0] != 0:
                                if j2[a[0] - 1][a[1] + i] != 0:
                                    test = True
                        if not test:
                            if a[0] == 0:
                                for j in range(i):
                                    if j2[0][a[1] + j] != 0 or j2[1][a[1] + j] != 0:
                                        test = True
                            elif a[0] == 9:
                                for j in range(i):
                                    if j2[9][a[1] + j] != 0 or j2[8][a[1] + j] != 0:
                                        test = True
                            else:
                                for j in range(i):
                                    if j2[a[0]][a[1] + j] != 0 or j2[a[0] + 1][a[1] + j] != 0 or j2[a[0] - 1][a[1] + j] != 0:
                                        test = True
                    else:
                        test = True
                    if not test:
                        boat = []
                        for j in range(i):
                            j2[a[0]][a[1] + j] = 1
                            boat.append((a[0], a[1] + j))
                        boats.append(boat)
                else:
                    if a[0] <= 10 - i:
                        if a[0] != 0:
                            if j2[a[0] - 1][a[1]] != 0:
                                test = True
                            if a[1] != 0:
                                if j2[a[0] - 1][a[1] - 1] != 0:
                                    test = True
                            if a[1] != 9:
                                if j2[a[0] - 1][a[1] + 1] != 0:
                                    test = True
                        if a[0] + i < 10:
                            if j2[a[0] + i][a[1]] != 0:
                                test = True
                            if a[1] != 9:
                                if j2[a[0] + i][a[1] + 1] != 0:
                                    test = True
                            if a[1] != 0:
                                if j2[a[0] + i][a[1] - 1] != 0:
                                    test = True
                        if not test:
                            if a[1] == 0:
                                for j in range(i):
                                    if j2[a[0] + j][0] != 0 or j2[a[0] + j][1] != 0:
                                        test = True
                            elif a[1] == 9:
                                for j in range(i):
                                    if j2[a[0] + j][9] != 0 or j2[a[0] + j][8] != 0:
                                        test = True
                            else:
                                for j in range(i):
                                    if j2[a[0] + j][a[1]] != 0 or j2[a[0] + j][a[1] + 1] != 0 or j2[a[0] + j][a[1] - 1] != 0:
                                        test = True
                    else:
                        test = True
                    if not test:
                        boat = []
                        for j in range(i):
                            j2[a[0] + j][a[1]] = 1
                            boat.append((a[0] + j, a[1]))
                        boats.append(boat)
        return (boats, j2)

    @staticmethod
    def grille_de_tir(d,f):
        e=[]
        for i in range(10):
            for j in range(round(10/d)):
                e.append((i, d*j + i%d))
        for i in f:
            if i in e:
                e.remove(i)
        return e

    def grider(self, grid, player = True):
        return '\n'.join([". 1    2    3    4   5    6    7   8    9  10"] + [''.join([green if (grid[i][j] == 1 and player) else white if grid[i][j] == -1 else red if grid[i][j] == -2 else black if grid[i][j] == -3 else blue for j in range(len(grid[i]))] + [" " + self.column[i].upper()]) for i in range(len(grid))])

    @staticmethod
    def check(coups, b, not_possible):
        for i in b:
            if i[0] != 0:
                not_possible.append((i[0] - 1, i[1]))
                if (i[0]-1, i[1]) in coups:
                    coups.remove((i[0] - 1, i[1]))
                if i[1] != 0:
                    not_possible.append((i[0] - 1, i[1] - 1))
                    if (i[0] - 1, i[1] - 1) in coups:
                        coups.remove((i[0] - 1, i[1] - 1))
                if i[1] != 9:
                    not_possible.append((i[0] - 1, i[1] + 1))
                    if (i[0] - 1, i[1] + 1) in coups:
                        coups.remove((i[0] - 1, i[1] + 1))
            if i[0] != 9:
                not_possible.append((i[0] + 1, i[1]))
                if (i[0]+1,i[1]) in coups:
                    coups.remove((i[0] + 1, i[1]))
                if i[1] != 0:
                    not_possible.append((i[0] + 1, i[1] - 1))
                    if (i[0] + 1, i[1] - 1) in coups:
                        coups.remove((i[0] + 1, i[1] - 1))
                if i[1] != 9:
                    not_possible.append((i[0] + 1, i[1] + 1))
                    if (i[0] + 1, i[1] + 1) in coups:
                        coups.remove((i[0] + 1, i[1] + 1))
        return coups, not_possible

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def game(self, ctx):
        """Play Battleship against myself"""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and (2 < len(m.content) < 5 or m.content.lower() == "quit")
        player_grid = [[0]*10 for _ in range(10)]
        player_boats = []
        player_state = [1]*len(self.boat_size)
        await ctx.send("Welcome to battleship !\nPlease place your boats sending messages formatted like this : [Column][Row][Way]\nColumn : A-J\nRow : 1-10\nWay : h (horizontal) / v (vertical)\n\nYou can send `quit` any time to quit the game")
        for size,name in self.boat_size:
            await ctx.send(self.grider(player_grid))
            await ctx.send(f"Place your {name} (size : {size})")
            invalid = True
            while invalid:
                msg = await self.bot.wait_for('message', check = check)
                if msg.content.lower() == "quit":
                    return await ctx.send("Maybe we can play together another time")
                if msg.content.lower()[0] not in self.column or not msg.content[1:-1].isdigit():
                    await self.bot.httpcat(ctx, 400, "Please input a message correctly formatted")
                elif not 0 < int(msg.content[1:-1]) < 11:
                    await self.bot.httpcat(ctx, 400, "Please input a message correctly formatted")
                elif msg.content.lower()[-1] == 'v':
                    origin = (self.column.index(msg.content.lower()[0]), int(msg.content[1:-1]) - 1)
                    if origin[0] + size > 9:
                        await self.bot.httpcat(ctx, 400, "The boat is too long to be placed in such a position")
                    else:
                        invalid = False
                        for i in range(size):
                            if i + origin[0] > 0:
                                if origin[1] > 0:
                                    if player_grid[i + origin[0] - 1][origin[1] - 1] != 0:
                                        invalid = True
                                        break
                                if player_grid[i + origin[0] - 1][origin[1]] != 0:
                                    invalid = True
                                    break
                                if origin[1] < 9:
                                    if player_grid[i + origin[0] - 1][origin[1] + 1] != 0:
                                        invalid = True
                                        break
                            if origin[1] > 0:
                                if player_grid[i + origin[0]][origin[1] - 1] != 0:
                                    invalid = True
                                    break
                            if player_grid[i + origin[0]][origin[1]] != 0:
                                invalid = True
                                break
                            if origin[1] < 9:
                                if player_grid[i + origin[0]][origin[1] + 1] != 0:
                                    invalid = True
                                    break
                            if i + origin[0] < 9:
                                if origin[1] > 0:
                                    if player_grid[i + origin[0] + 1][origin[1] - 1] != 0:
                                        invalid = True
                                        break
                                if player_grid[i + origin[0] + 1][origin[1]] != 0:
                                    invalid = True
                                    break
                                if origin[1] < 9:
                                    if player_grid[i + origin[0] + 1][origin[1] + 1] != 0:
                                        invalid = True
                                        break
                        if not invalid:
                            player_boats.append([(origin[0] + i, origin[1]) for i in range(size)])
                            for i in range(size):
                                player_grid[origin[0] + i][origin[1]] = 1
                        else:
                            await ctx.send("There's already something there")
                elif msg.content.lower()[-1] == "h":
                    origin = (self.column.index(msg.content.lower()[0]), int(msg.content[1:-1]) - 1)
                    if origin[1]+size>10:
                        await ctx.send("The boat is too long to be placed in such a position")
                    else:
                        invalid = False
                        for i in range(size):
                            if i + origin[1] > 0:
                                if origin[0] > 0:
                                    if player_grid[origin[0] - 1][origin[1] + i - 1] != 0:
                                        invalid = True
                                        break
                                if player_grid[origin[0]][origin[1] + i - 1] != 0:
                                    invalid = True
                                    break
                                if origin[0] < 9:
                                    if player_grid[origin[0] + 1][origin[1] + i - 1] != 0:
                                        invalid = True
                                        break
                            if origin[0] > 0:
                                if player_grid[origin[0] - 1][origin[1] + i] != 0:
                                    invalid = True
                                    break
                            if player_grid[origin[0]][origin[1] + i] != 0:
                                invalid = True
                                break
                            if origin[0] < 9:
                                if player_grid[origin[0] + 1][origin[1] + i] != 0:
                                    invalid = True
                                    break
                            if i + origin[1] < 9:
                                if origin[0] > 0:
                                    if player_grid[origin[0] - 1][origin[1] + i + 1] != 0:
                                        invalid = True
                                        break
                                if player_grid[origin[0]][origin[1] + i + 1] != 0:
                                    invalid = True
                                    break
                                if origin[0] < 9:
                                    if player_grid[origin[0] + 1][origin[1] + i + 1] != 0:
                                        invalid = True
                                        break
                        if not invalid:
                            player_boats.append([(origin[0],origin[1]+i) for i in range(size)])
                            for i in range(size):
                                player_grid[origin[0]][origin[1] + i] = 1
                        else:
                            await ctx.send("There's already something there")
                else:
                    await ctx.send("Please input a correctly formatted message")
        enemy_boats, enemy_grid = self.j2_boats()
        dist = 2
        must_fire = []
        not_possible = []
        enemy_state = [1]*len(self.boat_size)
        enemy_fire = self.grille_de_tir(dist,not_possible)
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and (1 < len(m.content) < 4 or m.content.lower() == "quit")
        while True:
            await ctx.send(self.grider(player_grid))
            await ctx.send(self.grider(enemy_grid, False))
            await ctx.send("You can now fire upon me !")
            player_turn = True
            while player_turn:
                msg = await self.bot.wait_for("message", check = check)
                if msg.content.lower() == "quit":
                    return await ctx.send("Maybe we can play together another day")
                if msg.content.lower()[0] not in self.column or not msg.content[1:].isdigit():
                    await ctx.send("Please input a message correctly formatted")
                elif not 0 < int(msg.content[1:]) < 11:
                    await ctx.send("Please input a message correctly formatted")
                else:
                    hit = (self.column.index(msg.content.lower()[0]), int(msg.content[1:]) - 1)
                    if enemy_grid[hit[0]][hit[1]] >= 0:
                        player_turn = False
                        enemy_grid[hit[0]][hit[1]] -= 1 + 2*enemy_grid[hit[0]][hit[1]]
                        for b in enemy_boats:
                            if (hit[0],hit[1]) in b:
                                t = True
                                for c in b:
                                    if enemy_grid[c[0]][c[1]] == 1:
                                        t = False
                                if t:
                                    await ctx.send(f"You sunk my {self.boat_size[enemy_boats.index(b)][1]} !")
                                    for j in b:
                                        enemy_grid[j[0]][j[1]] =- 3
                                    enemy_state[enemy_boats.index(b)] = 0
                                    if sum(enemy_state) == 0:
                                        return await ctx.send("You won !!")
                                break
                    else:
                        await ctx.send("You cannot fire twice in the same place !")
            if must_fire == []:
                fire = choice(enemy_fire)
                enemy_fire.remove(fire)
                not_possible.append(fire)
                await ctx.send(f"{self.column[fire[0]].upper()}{fire[1] + 1}")
                if player_grid[fire[0]][fire[1]]:
                    player_grid[fire[0]][fire[1]] = -2
                    must_fire.append(1)
                    must_fire.append(fire)
                    if fire[0] != 0:
                        must_fire.append((fire[0]-1, fire[1]))
                    if fire[0] != 9:
                        must_fire.append((fire[0] + 1, fire[1]))
                    if fire[1] != 0:
                        must_fire.append((fire[0], fire[1]-1))
                    if fire[1] != 9:
                        must_fire.append((fire[0], fire[1]+1))
                else:
                    player_grid[fire[0]][fire[1]] = -1
            elif must_fire[0] == 1:
                fire = choice(must_fire[2:])
                while fire in not_possible:
                    fire = choice(must_fire[2:])
                await ctx.send(f"{self.column[fire[0]].upper()}{fire[1]+1}")
                not_possible.append(fire)
                must_fire.remove(fire)
                if player_grid[fire[0]][fire[1]]:
                    player_grid[fire[0]][fire[1]] =- 2
                    original = must_fire[1]
                    must_fire.clear()
                    sunk = True
                    for i in range(5):
                        if (fire[0], fire[1]) in player_boats[i]:
                            test = True
                            for c in player_boats[i]:
                                if player_grid[c[0]][c[1]] == 1:
                                    test = False
                            if test:
                                player_state[i] = 0
                                if i == 4:
                                    dist = 3
                                    enemy_fire = self.grille_de_tir(dist, not_possible)
                                if dist == 3 and player_state[3] == player_state[2] == 0:
                                    dist = 4
                                    enemy_fire = self.grille_de_tir(dist, not_possible)
                                if dist == 4 and not player_state[1]:
                                    dist = 5
                                    enemy_fire = self.grille_de_tir(dist, not_possible)
                                sunk = False
                                enemy_fire,not_possible=self.check(enemy_fire, player_boats[i], not_possible)
                                await ctx.send(f"I sunk your {self.boat_size[i][1]}")
                                for j in player_boats[i]:
                                    player_grid[j[0]][j[1]] = -3
                                if sum(player_state) == 0:
                                    return await ctx.send("I won !")
                    if sunk:
                        must_fire.append(2)
                        must_fire.append(original)
                        if fire[1] == original[1]:
                            if fire[0] == 0:
                                must_fire[0] = 3
                                must_fire.append((original[0] + 1, original[1]))
                            elif fire[0] == 9:
                                must_fire[0] = 3
                                must_fire.append((original[0] - 1, original[1]))
                            elif original[0] == 0:
                                must_fire[0] = 3
                                must_fire.append((fire[0] + 1, original[1]))
                            elif original[0] == 9:
                                must_fire[0] = 3
                                must_fire.append((fire[0] - 1, original[1]))
                            elif fire[0] == original[0] + 1:
                                must_fire.append((fire[0] + 1, original[1]))
                                must_fire.append((original[0] - 1, original[1]))
                            else:
                                must_fire.append((fire[0]-1, original[1]))
                                must_fire.append((original[0] + 1, original[1]))
                        else:
                            if fire[1] == 0:
                                must_fire[0] = 3
                                must_fire.append((original[0], original[1] + 1))
                            elif fire[1] == 9:
                                must_fire[0] = 3
                                must_fire.append((original[0], original[1] - 1))
                            elif original[1] == 0:
                                must_fire[0] = 3
                                must_fire.append((original[0], fire[1] + 1))
                            elif original[1] == 9:
                                must_fire[0] = 3
                                must_fire.append((original[1], fire[1] - 1))
                            elif fire[1] == original[1] + 1:
                                must_fire.append((original[0], fire[1] + 1))
                                must_fire.append((original[0], original[1] - 1))
                            else:
                                must_fire.append((original[0], fire[1] - 1))
                                must_fire.append((original[0], original[1] + 1))
                else:
                    player_grid[fire[0]][fire[1]] =- 1
            elif must_fire[0] == 2:
                fire = choice(must_fire[2:])
                while fire in not_possible:
                    fire = choice(must_fire[2:])
                await ctx.send(f"{self.column[fire[0]].upper()}{fire[1]+1}")
                must_fire.remove(fire)
                not_possible.append(fire)
                if fire in enemy_fire:
                    enemy_fire.remove(fire)
                if player_grid[fire[0]][fire[1]]:
                    player_grid[fire[0]][fire[1]] = -2
                    for i in range(5):
                        if (fire[0], fire[1]) in player_boats[i]:
                            test = True
                            for c in player_boats[i]:
                                if player_grid[c[0]][c[1]] == 1:
                                    test = False
                            if test:
                                player_state[i] = 0
                                if i == 4:
                                    dist = 3
                                    enemy_fire = self.grille_de_tir(dist, not_possible)
                                if dist == 3 and player_state[3] == player_state[2] == 0:
                                    dist = 4
                                    enemy_fire = self.grille_de_tir(dist, not_possible)
                                if dist == 4 and not player_state[1]:
                                    dist = 5
                                    enemy_fire = self.grille_de_tir(dist, not_possible)
                                enemy_fire, not_possible = self.check(enemy_fire, player_boats[i], not_possible)
                                await ctx.send(f"I sunk your {self.boat_size[i][1]}")
                                must_fire.clear()
                                for j in player_boats[i]:
                                    player_grid[j[0]][j[1]] = -3
                                if sum(player_state) == 0:
                                    return await ctx.send("I won !")
                            else:
                                if fire[0]<must_fire[1][0]:
                                    if fire[0] == 0:
                                        must_fire[0] = 3
                                    else:
                                        must_fire.append((fire[0] - 1, fire[1]))
                                elif fire[0] > must_fire[1][0]:
                                    if fire[0] == 0:
                                        must_fire[0] = 3
                                    else:
                                        must_fire.append((fire[0] + 1, fire[1]))
                                elif fire[1] < must_fire[1][1]:
                                    if fire[1] == 0:
                                        must_fire[0] = 3
                                    else:
                                        must_fire.append((fire[0], fire[1] - 1))
                                elif fire[1] > must_fire[1][1]:
                                    if fire[0] == 0:
                                        must_fire[0] = 3
                                    else:
                                        must_fire.append((fire[0], fire[1] + 1))
                else:
                    player_grid[fire[0]][fire[1]] = -1
                    must_fire[0] = 3
            elif must_fire[0] == 3:
                fire = must_fire[2]
                await ctx.send(f"{self.column[fire[0]].upper()}{fire[1] + 1}")
                not_possible.append(fire)
                if fire in enemy_fire:
                    enemy_fire.remove(fire)
                player_grid[fire[0]][fire[1]] = -2
                for i in range(5):
                    if (fire[0], fire[1]) in player_boats[i]:
                        test = True
                        for c in player_boats[i]:
                            if player_grid[c[0]][c[1]] == 1:
                                test = False
                        if test:
                            player_state[i] = 0
                            if i == 4:
                                dist = 3
                                enemy_fire = self.grille_de_tir(dist, not_possible)
                            if dist == 3 and player_state[3] == player_state[2] == 0:
                                dist = 4
                                enemy_fire = self.grille_de_tir(dist, not_possible)
                            if dist == 4 and not player_state[1]:
                                dist = 5
                                enemy_fire = self.grille_de_tir(dist, not_possible)
                            enemy_fire, not_possible = self.check(enemy_fire, player_boats[i], not_possible)
                            must_fire.clear()
                            await ctx.send(f"I sunk your {self.boat_size[i][1]}")
                            for j in player_boats[i]:
                                player_grid[j[0]][j[1]] = -3
                            if sum(player_state) == 0:
                                return await ctx.send("I won !")
                if must_fire != []:
                    must_fire.remove(fire)
                    if fire[0] < must_fire[1][0]:
                        must_fire.append((fire[0] - 1, fire[1]))
                    elif fire[0] > must_fire[1][0]:
                        must_fire.append((fire[0]+1, fire[1]))
                    elif fire[1] < must_fire[1][1]:
                        must_fire.append((fire[0], fire[1] - 1))
                    elif fire[1] > must_fire[1][1]:
                        must_fire.append((fire[0], fire[1] + 1))


def setup(bot):
    bot.add_cog(Battleship(bot))
