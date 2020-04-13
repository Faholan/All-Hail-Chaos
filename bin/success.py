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

import pickle
from discord.ext import commands
from data.success_data import *
from os import path

success_list=[
Success(name='First command',description="Begin using the bot",condition=nombre_de_commandes,extra_data=[0,1],avancement=avancement_n_commandes),
Success(name="Bot regular",description="Launch 100 commands",condition=nombre_de_commandes,extra_data=[0,100],avancement=avancement_n_commandes),
Success(name='Bot master',description="Launch 1000 commands",condition=nombre_de_commandes,extra_data=[0,1000],avancement=avancement_n_commandes),
Success(name='The secrets of the bot',description="Find every single hidden command",condition=commandes_cachees,extra_data=[],avancement=n_commandes_cachees),
Success(name='The dark side of the chaos',description='Find the hidden prefix',condition=prefix,description_is_visible=False)
]

try:
    account_list=pickle.load(open('data'+path.sep+'accounts.DAT',mode='rb'))
except:
    account_list=[]

async def check_successes(ctx):
    global account_list
    if str(ctx.message.author) not in account_list:
        account_list.append(Account(str(ctx.message.author),success_list))
    account=account_list[account_list.index(str(ctx.message.author))]
    account.add_success(success_list)#Compatibilité avec les anciens comptes
    embeds=account(ctx)
    pickle.dump(account_list,file=open('data'+path.sep+'accounts.DAT',mode='wb'))
    for embed in embeds:
        await ctx.send(embed=embed)
    return True

def setup(bot):
    bot.add_check(check_successes)
