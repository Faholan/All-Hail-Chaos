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

from discord import Embed
import pickle
from discord.ext import commands
from data import data

class Success():
    '''Class implementation of a Discord success'''
    def __init__(self,name,description,condition,description_is_visible=True,extra_data=None,avancement=None):
        self.name=name
        self.description=description
        self.condition=condition
        self.description_is_visible=description_is_visible
        self.extra_data=extra_data
        self.avancement=avancement
        if description_is_visible:
            self.locked=description
        else:
            self.locked='Hidden success'

    def __eq__(self,other):
        if type(other)!=type(self):
            return False
        return self.name==other.name

    def __call__(self,ctx):
        test,self.extra_data=self.condition(ctx,self.extra_data)
        if test:
            return self
        else:
            return None
    def advance(self):
        if self.avancement==None:
            return ''
        else:
            return self.avancement(self.extra_data)

class Account():
    '''Class implementation of an account'''
    def __init__(self,identifier,succ):
        self.identifier=identifier
        self.succ=succ
        self.succ_state=[]
        for s in self.succ:
            self.succ_state.append(False)

    def __str__(self):
        return self.identifier

    def __eq__(self,other):
        return self.identifier==other

    def __call__(self,ctx):
        embeds=[]
        for i in range(len(self.succ)):
            if not self.succ_state[i]:
                s=self.succ[i](ctx)
                if s!=None:
                    self.unlock_success(s)
                    embed=Embed(title='Succes unlocked !',description=s.name,colour=data.get_color())
                    embed.set_author(name=str(ctx.author),icon_url=str(ctx.author.avatar_url))
                    embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    embed.add_field(name=s.description,value='Requirements met')
                    embeds.append(embed)
        return embeds

    def add_success(self,successes):
        '''In case the successes changed'''
        for s in successes:
            if s not in self.succ:
                self.succ.append(s)
                self.succ_state.append(False)
        for i in range(len(self.succ)):
            if self.succ[i] not in successes:
                self.succ.pop(i)
                self.succ_state.pop(i)

    def get_successes(self):
        gotten=[]
        locked=[]
        for s in range(len(self.succ_state)):
            if self.succ_state[s]:
                gotten.append(self.succ[s])
            else:
                locked.append(self.succ[s])
        return gotten,locked,len(self.succ)

    def reset(self):
        for i in range(len(self.succ_state)):
            self.succ_state[i]=False

    def unlock_success(self,success):
        self.succ_state[self.succ.index(success)]=True

#Les conditions des succès
def nombre_de_commandes(ctx,n):
    return n[0]+1==n[1],[n[0]+1,n[1]]
def avancement_n_commandes(n):
    return f' ({n[0]}/{n[1]})'
def commandes_cachees(ctx,commands):
    if ctx.command.name in commands or not ctx.command.hidden:
        return False,commands
    commands.append(ctx.command.name)
    return len(commands)==hidden,commands
def n_commandes_cachees(commands):
    return f' ({len(commands)}/{hidden})'
def prefix(ctx,nothing):
    return ctx.prefix=='¤',None

success_list=[
Success(name='First command',description="Begin using the bot",condition=nombre_de_commandes,extra_data=[0,1],avancement=avancement_n_commandes),
Success(name="Bot regular",description="Launch 100 commands",condition=nombre_de_commandes,extra_data=[0,100],avancement=avancement_n_commandes),
Success(name='Bot master',description="Launch 1000 commands",condition=nombre_de_commandes,extra_data=[0,1000],avancement=avancement_n_commandes),
Success(name='The secrets of the bot',description="Find every single hidden command",condition=commandes_cachees,extra_data=[],avancement=n_commandes_cachees),
Success(name='The dark side of the chaos',description='Find the hidden prefix',condition=prefix,description_is_visible=False)
]

try:
    account_list=pickle.load(open('data\\accounts.DAT',mode='rb'))
except:
    account_list=[]

async def check_successes(ctx):
    global account_list
    if str(ctx.message.author) not in account_list:
        account_list.append(Account(str(ctx.message.author),success_list))
    account=account_list[account_list.index(str(ctx.message.author))]
    account.add_success(success_list)#Compatibilité avec les anciens comptes
    embeds=account(ctx)
    pickle.dump(account_list,file=open('data\\accounts.DAT',mode='wb'))
    for embed in embeds:
        await ctx.send(embed=embed)
    return True

def setup(bot):
    bot.add_check(check_successes)
    global hidden
    hidden=0
    for command in bot.commands:
        if command.hidden:
            hidden+=1
