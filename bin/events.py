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
from traceback import print_tb
from discord.ext.commands import CheckFailure,CheckAnyFailure,MissingRequiredArgument,PrivateMessageOnly,NoPrivateMessage,CommandNotFound,DisabledCommand,TooManyArguments,CommandOnCooldown,MissingPermissions,BotMissingPermissions,MissingRole,BotMissingRole,NSFWChannelRequired,CommandInvokeError,UnexpectedQuoteError,InvalidEndOfQuotedStringError,ExpectedClosingQuoteError,BadArgument,BadUnionArgument,ConversionError,MemberConverter,UserConverter,MessageConverter,TextChannelConverter,VoiceChannelConverter

def secondes(s):
    r=[]
    if s>=86400:
        r.append(str(s//86400)+' days')
        s%=86400
    if s>=3600:
        r.append(str(s//3600)+' hours')
        s%=3600
    if s>=60:
        r.append(str(s//60)+' minutes')
        s%=60
    if s>0:
        r.append(str(s)+' seconds')
    return ', '.join(r)

def checker(message):
    try:
        locked_channels=pickle.load(open('data\\locked_channels.DAT',mode='rb'))
    except:
        locked_channels=[]
    try:
        whitelist=pickle.load(open('data\\whitelist.DAT',mode='rb'))
    except:
        whitelist=[]
    if message.channel.id in whitelist:
        return True
    try:
        b=message.guild.id
    except:
        b=0
    return not message.channel.id in locked_channels and not b in locked_channels

async def di(message):
    '''All hail Chaos !'''
    if 'di' in message.content and checker(message) and message.content.split('di',maxsplit=1)[-1]!='':
        await message.channel.send(message.content.split('di',maxsplit=1)[-1])

async def modif(before,after):
    '''You shall not change !'''
    if checker(before) and before.content!=after.content:
        await before.channel.send(before.author.mention+' changed his message from "'+before.content+'" to "'+after.content+'". We should hang him')

async def deletor(message):
    '''You shall not disappear'''
    if checker(message):
        await message.channel.send('The message "'+message.content+'" of '+message.author.mention+" was deleted. He's now public enemy #1")

async def error_manager(ctx,error):
    '''Error manager'''
    if isinstance(error,CheckAnyFailure):
        await ctx.send("You don't have the rights to send use the command "+ctx.invoked_with)
    elif isinstance(error,(BadArgument,BadUnionArgument)):
        await ctx.send(str(error))
    elif isinstance(error,MissingRequiredArgument):
        await ctx.send("Hmmmm, looks like an argument is missing : "+error.param.name)
    elif isinstance(error,PrivateMessageOnly):
        await ctx.send("You must be in a private channel to use this command.")
    elif isinstance(error,NoPrivateMessage):
        await ctx.send("I can't dot this in private.")
    elif isinstance(error,CommandNotFound):
        pass
    elif isinstance(error,CommandInvokeError):
        await ctx.send(str(error))
    elif type(error)==DisabledCommand:
        await ctx.send('God said : this command is disabled. So it is.')
    elif isinstance(error,TooManyArguments):
        await ctx.send("You gave me too much arguments for me to process.")
    elif isinstance(error,CommandOnCooldown):
        await ctx.send('Calm down, breath and try again in '+secondes(round(error.retry_after)))
    elif isinstance(error,MissingPermissions):
        await ctx.send('\n-'.join(['Try again with the following permission(s) :']+error.missing_perms))
    elif isinstance(error,BotMissingPermissions):
        await ctx.send('\n-'.join(["I need these permissions :"]+error.missing_perms))
    elif isinstance(error,MissingRole):
        await ctx.send("Sorry, but you need to be a "+str(error.missing_role))
    elif isinstance(error,BotMissingRole):
        await ctx.send("Gimme the role "+str(error.missing_role)+" first, ok ?")
    elif isinstance(error,NSFWChannelRequired):
        await ctx.send("Woooh ! You must be in an NSFW channel to use this.")
    elif isinstance(error,UnexpectedQuoteError):
        await ctx.send("I didn't expected that quote...")
    elif isinstance(error,InvalidEndOfQuotedStringError):
        await ctx.send("You must separated the quoted argument from the others with spaces")
    elif isinstance(error,ExpectedClosingQuoteError):
        await ctx.send("I expected a closing quote")
    else:
        await ctx.send('The command raised an error')
        print(str(type(error))+' : '+str(error))
        print_tb(error.__traceback__)

async def guild_joiner(guild):
    print(guild.name+" joined")

async def guild_leaver(guild):
    print(guild.name+" leaved")

def setup(bot):
    #bot.add_listener(di,'on_message')
    #bot.add_listener(modif,'on_message_edit')
    #bot.add_listener(deletor,'on_message_delete')
    #These three lines cane make the bot even more "chaotic"
    bot.add_listener(error_manager,'on_command_error')
    bot.add_listener(guild_joiner,'on_guild_join')
    bot.add_listener(guild_leaver,'on_guild_remove')
