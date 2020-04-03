from discord.ext import commands
import discord
import pickle
from time import time
from data import data

class Business_guy():
    def __init__(self,user):
        self.id=user.id
        self.name=str(user)
        self.avatar_url=str(user.avatar_url)
        self.money=0
        self.bank=0
        self.bank_max=5000
        self.streak=1
        self.last_daily=0
        self.steal_streak=0

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
        return 'You gained '+str(100*self.streak)+' GP'

    def gift(self,guild):
        self.money+=500
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
                return f"{money} GP deposited"
            else:
                self.money-=M
                self.bank+=M
                return f"{M} GP deposited. {M-money} GP couldn't be deposited (capacity of {self.bank_max} GP reached)"

    def voler(self,other):
        a=randint(round(0.05*other.money),round(0.1*other.money))
        self.money+=a
        other.money-=a
        return a

p_vol=lambda n:75-(25*0.8**n)

class business(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        try:
            self.guys=pickle.load(open('data\\business.DAT',mode='rb'))
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
        pickle.dump(self.guys,open('data\\business.DAT',mode='wb'))

    @commands.command(ignore_extra=False)
    async def deposit(self,ctx,money:int):
        '''Deposit your money in a safe at the bank'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.deposit(money))
        pickle.dump(self.guys,open('data\\business.DAT',mode='wb'))

    @commands.command(ignore_extra=True)
    @commands.cooldown(1,86400,commands.BucketType.guild)
    async def gift(self,ctx):
        '''Get the guild's daily gift (500 GP)'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(business.gift(ctx.guild.name))
        pickle.dump(self.guys,open('data\\business.DAT',mode='wb'))

    @commands.command(ignore_extra=True)
    async def money(self,ctx):
        '''How much money do I have ?'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        business=self.guys[self.guys.index(ctx.author)]
        await ctx.send(embed=business.money_out())

    @commands.command(aliases=['voler'],ignore_extra=False)
    @commands.cooldown(1,600,commands.BucketType.user)
    async def steal(self,ctx,victime:discord.Member):
        '''Stealing is much more gainflu than killing'''
        if not ctx.author in self.guys:
            self.guys.append(Business_guy(ctx.author))
        voleur=self.guys[self.guys.index(ctx.author)]
        if not victime in self.guys:
            self.steal.reset_cooldown(ctx)
            return await ctx.send("`"+victime.display_name+"` doesn't have money on him. What a shame.")
        vole=self.guys[self.guys.index(victime)]
        if vole.money==0:
            self.steal.reset_cooldown(ctx)
            return await ctx.send("`"+victime.display_name+"` doesn't have money on him. What a shame.")
        m+=p_vol(voleur.steal_streak)
        if victime.state==discord.State.offline:
            m+=10
        if randint(1,100)<m:
            voleur.steal_streak=0
            await ctx.send(f"You failed in your attempt to steal {victime.display_name}. He hit you, so you must now wait 10 minutes to regain your usual sneakiness")
            pickle.dump(self.guys,open('data\\business.DAT',mode='wb'))
        else:
            self.steal.reset_cooldown(ctx)
            voleur.steal_streak+=1
            await ctx.send(f"You robbed `{voleur.voler(vole)}` GP from {victime.display_name}")
            pickle.dump(self.guys,open('data\\business.DAT',mode='wb'))

    @steal.error
    async def steal_error(self,ctx,error):
        if not isinstance(error,commands.CommandOnCooldown):
            self.steal.reset_cooldown(ctx)

def setup(bot):
    bot.add_cog(business(bot))
