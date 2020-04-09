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

from discord.ext import commands
import discord
from time import time
from data import data
from data.business_data import *
import pickle

p_vol=lambda n:75-(25*0.8**n)

class Business(commands.Cog):
    '''Some commands involving money'''
    def __init__(self,bot):
        self.bot=bot
        try:
            self.guys=pickle.load(open("data\\business.DAT",mode='rb'))
        except:
            self.guys=[]

    @commands.command(ignore_extra=True)
    @commands.cooldown(1,86400,commands.BucketType.user)
    async def daily(self,ctx):
        '''Get your daily GP (100*streak, max : 500)'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.daily())
        pickle.dump(self.guys,open("data\\business.DAT",mode='wb'))

    @commands.command(ignore_extra=False)
    async def deposit(self,ctx,money:int):
        '''Deposit your money in a safe at the bank'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.deposit(money))
        pickle.dump(self.guys,open("data\\business.DAT",mode='wb'))

    @commands.command(ignore_extra=True)
    @commands.cooldown(1,86400,commands.BucketType.guild)
    async def gift(self,ctx):
        '''Get the guild's daily gift (500 GP)'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.gift(ctx.guild.name))
        pickle.dump(self.guys,open("data\\business.DAT",mode='wb'))

    @commands.command(ignore_extra=True)
    async def money(self,ctx):
        '''How much money do I have ?'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(embed=business.money_out())

    @commands.command(ignore_extra=False)
    @commands.cooldown(1,600,commands.BucketType.user)
    async def steal(self,ctx,victim:discord.Member):
        '''Stealing is much more gainful than killing'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        pickpocket=self.guys[self.guys.index(ctx.author)]
        if not victim in self.guys:
            self.steal.reset_cooldown(ctx)
            return await ctx.send("`"+victim.display_name+"` doesn't have money on him. What a shame.")
        stolen=self.guys[self.guys.index(victim)]
        if stolen.money==0:
            self.steal.reset_cooldown(ctx)
            return await ctx.send("`"+victim.display_name+"` doesn't have money on him. What a shame.")
        m+=p_vol(pickpocket.steal_streak)
        if victim.state==discord.State.offline:
            m+=10
        if randint(1,100)<m:
            pickpocket.steal_streak=0
            await ctx.send(f"You failed in your attempt to steal {victim.display_name}. He hit you, so you must now wait 10 minutes to regain your usual sneakiness")
        else:
            self.steal.reset_cooldown(ctx)
            pickpocket.steal_streak+=1
            await ctx.send(f"You robbed `{pickpocket.steal(stolen)}` GP from {victim.display_name}")
            pickle.dump(self.guys,open("data\\business.DAT",mode='wb'))

    @steal.error
    async def steal_error(self,ctx,error):
        if not isinstance(error,commands.CommandOnCooldown):
            self.steal.reset_cooldown(ctx)

def setup(bot):
    bot.add_cog(Business(bot))
