"""MIT License

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
SOFTWARE."""

from asyncio import create_task
from os import path
from random import randint
from time import time

import discord
from discord.ext import commands

p_vol=lambda n:75-(25*0.8**n)

class Business_guy():
    def __init__(self, sql, user, db):
        self.db = db
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

    def __eq__(self, other):
        return self.id == other.id

    async def save(self):
        cur = await self.db.execute("SELECT * FROM business WHERE id=?", (self.id,))
        result = await cur.fetchone()
        if result:
            await self.db.execute("UPDATE business SET money=?, bank=?, bank_max=?, streak=?, last_daily=?, steal_streak=? WHERE id=?", (self.money, self.bank, self.bank_max, self.streak, self.last_daily, self.steal_streak, self.id))
        else:
            await self.db.execute("INSERT INTO business VALUES (?, ?, ?, ?, ?, ?, ?)", (self.id, self.money, self.bank, self.bank_max, self.streak, self.last_daily, self.steal_streak))
        create_task(self.db.commit())

    async def daily(self):
        if time() < self.last_daily + 172800:
            if self.streak < 5:
                self.streak += 1
        else:
            self.streak = 1
        self.last_daily = time()
        self.money += 100*self.streak
        await self.save()
        return 'You gained ' + str(100*self.streak) + ' GP'

    async def gift(self, guild):
        self.money += 500
        await self.save()
        return 'You took ' + guild + "'s 500 daily GP."

    def money_out(self):
        embed = discord.Embed(title = f"{self.name}'s bank :", colour = 0x00008b)
        embed.set_author(name = self.name, icon_url = self.avatar_url)
        embed.add_field(name = 'Banked :',value = str(self.bank) + '/' + str(self.bank_max))
        embed.add_field(name = 'Pocketed :', value = str(self.money))
        return embed

    async def deposit(self, money):
        if self.money < money:
            return f"Sorry, but you only have {self.money} GP"
        else:
            M = self.bank_max - self.bank
            if money <= M:
                self.money -= money
                self.bank += money
                await self.save()
                return f"{money} GP deposited"
            else:
                self.money -= M
                self.bank += M
                await self.save()
                return f"{M} GP deposited. {M-money} GP couldn't be deposited (capacity of {self.bank_max} GP reached)"

    async def steal(self, other):
        a = randint(round(0.05*other.money), round(0.1*other.money))
        self.money += a
        other.money -= a
        await self.save()
        await other.save()
        return a

class Business(commands.Cog):
    '''Some commands involving money'''
    def __init__(self, bot):
        self.bot = bot

    async def _fetcher(self, identifier):
        await self.bot.db.execute('CREATE TABLE IF NOT EXISTS business (id INT PRIMARY KEY NOT NULL, money INT, bank INT, bank_max INT, streak INT, last_daily INT, steal_streak INT)')
        cur = await self.bot.db.execute('SELECT * FROM business WHERE id=?', (identifier,))
        return cur

    @commands.command(ignore_extra = True)
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        '''Get your daily GP (100*streak, max : 500)'''
        fetched = await self._fetcher(ctx.author.id)
        business = Business_guy(await fetched.fetchone(), ctx.author, ctx.bot.db)
        await ctx.send(await business.daily())

    @commands.command()
    async def deposit(self, ctx, money:int):
        '''Deposit your money in a safe at the bank'''
        fetched = await self._fetcher(ctx.author.id)
        business = Business_guy(await fetched.fetchone(), ctx.author, ctx.bot.db)
        await ctx.send(await business.deposit(money))

    @commands.command(ignore_extra=True)
    @commands.cooldown(1, 86400, commands.BucketType.guild)
    async def gift(self,ctx):
        '''Get the guild's daily gift (500 GP)'''
        fetched = await self._fetcher(ctx.author.id)
        business = Business_guy(await fetched.fetchone(), ctx.author, ctx.bot.db)
        await ctx.send(await business.gift(ctx.guild.name))

    @commands.command(ignore_extra=True)
    async def money(self,ctx):
        '''How much money do I have ?'''
        fetched = await self._fetcher(ctx.author.id)
        business = Business_guy(await fetched.fetchone(), ctx.author, ctx.bot.db)
        embed = business.money_out()
        embed.set_thumbnail(url = str(ctx.me.avatar_url)) #A modifier
        await ctx.send(embed = embed)

    @commands.command()
    @commands.cooldown(1,600, commands.BucketType.user)
    async def steal(self, ctx, victim:discord.Member):
        '''Stealing is much more gainful than killing'''
        fetched = await self._fetcher(ctx.author.id)
        pickpocket = Business_guy(await fetched.fetchone(), ctx.author, ctx.bot.db)
        fetched = await self._fetcher(victim.id)
        stolen = Business_guy(await fetched.fetchone(), victim, ctx.bot.db)
        if pickpocket == stolen:
            self.steal.reset_cooldown(ctx)
            return await ctx.send('Are you seriously tring to steal yourself ?')
        if stolen.money == 0:
            self.steal.reset_cooldown(ctx)
            return await ctx.send(f"`{victim.display_name}` doesn't have money on him. What a shame.")

        m = p_vol(pickpocket.steal_streak)
        if victim.status == discord.Status.offline:
            m += 10
        if randint(1,100) < m:
            pickpocket.steal_streak = 0
            await pickpocket.save()
            await ctx.send(f"You failed in your attempt to steal {victim.display_name}. He hit you, so you must now wait 10 minutes to regain your usual sneakiness")
        else:
            self.steal.reset_cooldown(ctx)
            pickpocket.steal_streak += 1
            await ctx.send(f"You robbed `{await pickpocket.steal(stolen)}` GP from {victim.display_name}")

    @steal.error
    async def steal_error(self, ctx, error):
        if not isinstance(error, commands.CommandOnCooldown):
            self.steal.reset_cooldown(ctx)

def setup(bot):
    bot.add_cog(Business(bot))
