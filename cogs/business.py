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

class Business_guy():
    def __init__(self,user,bot,ini=True):
        self.bot=bot
        if ini:
            self.id=user.id
            self.name=str(user)
            self.avatar_url=str(user.avatar_url)
            self.money=0
            self.bank=0
            self.bank_max=5000
            self.streak=1
            self.last_daily=0
            self.steal_streak=0
            bot.db.execute("INSERT INTO businessmen values (?,?,?,?,?,?,?,?,?)",(self.id,self.name,self.avatar_url,self.money,self.bank,self.bank_max,self.streak,self.last_daily,self.steal_streak))

    def __eq__(self,other):
        return self.id==other.id

    def daily(self):
        if time()<self.last_daily+172800:
            if self.streak<5:
                self.streak+=1
        else:
            self.streak=1
        self.last_daily=time()
        self.money+=100*self.streak
        self._database_update()
        return 'You gained '+str(100*self.streak)+' GP'

    def gift(self,guild):
        self.money+=500
        self._database_update()
        return 'You took '+guild+"'s 500 daily GP.'"

    def money_out(self):
        embed=discord.Embed(title='Banque de '+self.name,colour=data.get_color())
        embed.set_author(name=self.name,icon_url=self.avatar_url)
        embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg') #A modifier
        embed.add_field(name='Banked :',value=str(self.bank)+'/'+str(self.bank_max))
        embed.add_field(name='Pocketed :',value=str(self.money))
        return embed

    def deposit(self,money):
        if self.money<money:
            return f"Sorry, but you only have {self.money} GP"
        else:
            M=self.bank_max-self.bank
            if money<=M:
                self.money-=money
                self.bank+=money
                self._database_update()
                return f"{money} GP deposited"
            else:
                self.money-=M
                self.bank+=M
                self._database_update()
                return f"{M} GP deposited. {M-money} GP couldn't be deposited (capacity of {self.bank_max} GP reached)"

    def steal(self,other):
        a=randint(round(0.05*other.money),round(0.1*other.money))
        self.money+=a
        other.stolen(a)
        self._database_update()
        return a

    def stolen(self,a):
        self.money-=a
        self._database_update()

    def _database_update(self):
        self.bot.db.execute("UPDATE businessmen SET money=?, bank=?, bank_max=?, streak=?, last_daily=?, steal_streak=? WHERE name=?",(self.money,self.bank,self.bank_max,self.streak,self.last_daily,self.steal_streak,self.name))

    @classmethod
    def data(cls,bot,guy):
        businessman=cls(None,bot,False)
        for attr in ("id","name","avatar_url","money","bank","bank_max","streak","last_daily","steal_streak"):
            setattr(businessman,attr,guy[attr])


p_vol=lambda n:75-(25*0.8**n)

class Business(commands.Cog):
    '''Some commands involving money'''
    def __init__(self,bot):
        self.bot=bot
        bot.db.execute("CREATE TABLE IF NOT EXISTS businessmen (id INTEGER, name TEXT, avater_url TEXT, money INTEGER, bank INTEGER, bank_max INTEGER, streak INTEGER, last_daily INTEGER, steal_streak INTEGER)")
        self.guys=[]
        for guy in bot.db.execute("SELECT * FROM businessmen"):
            self.guys.append(Business_guy.data(self.bot,guy))


    @commands.command(ignore_extra=True)
    @commands.cooldown(1,86400,commands.BucketType.user)
    async def daily(self,ctx):
        '''Get your daily GP (100*streak, max : 500)'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author,self.bot))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.daily())

    @commands.command(ignore_extra=False)
    async def deposit(self,ctx,money:int):
        '''Deposit your money in a safe at the bank'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author,self.bot))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.deposit(money))

    @commands.command(ignore_extra=True)
    @commands.cooldown(1,86400,commands.BucketType.guild)
    async def gift(self,ctx):
        '''Get the guild's daily gift (500 GP)'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author,self.bot))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.gift(ctx.guild.name))

    @commands.command(ignore_extra=True)
    async def money(self,ctx):
        '''How much money do I have ?'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author,self.bot))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(embed=business.money_out())

    @commands.command(ignore_extra=False)
    @commands.cooldown(1,600,commands.BucketType.user)
    async def steal(self,ctx,victim:discord.Member):
        '''Stealing is much more gainful than killing'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author,self.bot))
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

    @steal.error
    async def steal_error(self,ctx,error):
        if not isinstance(error,commands.CommandOnCooldown):
            self.steal.reset_cooldown(ctx)

def setup(bot):
    bot.add_cog(Business(bot))
