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
from discord import Embed,Game
import discord.utils
from datetime import datetime

from data import data
import aiosqlite

import ksoftapi

from asyncio import all_tasks
import aiohttp

from os import path

import dbl
from github import Github

class chaotic_bot(commands.Bot):
    """The subclassed bot class"""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.colors = data.colors

        self.default_prefix=data.default_prefix

        self.http.user_agent=data.user_agent

        self.ksoft_token=data.ksoft_token

        self.nasa=data.nasa

        self.admins=data.admins
        self.graphic_interface=data.graphic_interface
        self.invite_permissions=data.invite_permissions
        self.discord_rep=data.discord_rep
        self.discord_bots=data.discord_bots
        self.xyz = data.xyz
        self.discord_bot_list = data.discord_bot_list

        self.support = data.support

        self.top_gg = data.top_gg
        self.bots_on_discord = data.bots_on_discord
        self.discord_bots_page = data.discord_bots_page

        #self.db=sqlite3.connect("data/prefixes.db") #Sqlite database for prefixes

        self.first_on_ready=True

        if data.dbl_token:
            self.dbl_client=dbl.DBLClient(self, data.dbl_token, autopost=True)

        if data.github_token:
            self.github=Github(data.github_token)
        self.github_repo=data.github_repo

    async def on_ready(self):
        await self.change_presence(activity=Game(self.default_prefix+'help'))
        if self.first_on_ready:
            self.first_on_ready = False
            self.db = await aiosqlite.connect('data'+path.sep+'database.db')
            self.db.row_factory = aiosqlite.Row
            await self.db.execute("CREATE TABLE IF NOT EXISTS swear (id INT PRIMARY KEY NOT NULL, manual_on BOOL DEFAULT 0, autoswear BOOL DEFAULT 0, notification BOOL DEFAULT 1)")
            await self.db.execute('CREATE TABLE IF NOT EXISTS roles (message_id INT, channel_id INT, guild_id INT, emoji TINYTEXT, roleids TEXT)')
            self.aio_session = aiohttp.ClientSession()
            self.last_update = datetime.utcnow()
            self.log_channel = self.get_channel(data.log_channel)
            self.suggestion_channel = self.get_channel(data.suggestion_channel)
            report = []
            for ext in data.extensions:
                    if not ext in bot.extensions:
                        try:
                            bot.load_extension(ext)
                            report.append("Extension loaded : "+ext)
                        except commands.ExtensionFailed as e:
                            report.append(e.name+" : " + str(type(e.original)) + " : " + str(e.original))
                        except:
                            report.append("Extension not loaded : "+ext)
            await self.log_channel.send('\n'.join(report))
        else:
            await self.log_channel.send("on_ready called again")

    async def on_guild_join(self,guild):
        await self.log_channel.send(guild.name+" joined")

    async def on_guild_remove(self,guild):
         await self.log_channel.send(guild.name+" leaved")

    async def close(self):
        await self.aio_session.close()
        await self.db.close()
        if hasattr(self,"session"):
            await self.session.close()
        for task in all_tasks(loop=self.loop):
            task.cancel()
        await super().close()

    async def cog_reloader(self):
        self.last_update=datetime.utcnow()
        from data import data as D
        report=[]
        for ext in D.extensions:
            try:
                self.reload_extension(ext)
                report.append("Extension reloaded : "+ext)
            except commands.ExtensionNotLoaded:
                try:
                    bot.load_extension(ext)
                    report.append("Extension loaded : "+ext)
                except commands.ExtensionFailed as e:
                    report.append(e.name+" : "+str(type(e.original))+" : "+str(e.original))
                except:
                    report.append("Extension not loaded : "+ext)
            except commands.ExtensionFailed as e:
                report.append(e.name+" : "+str(type(e.original))+" : "+str(e.original))
            except:
                report.append("Extension not loaded : "+ext)
        await self.log_channel.send('\n'.join(report))

    async def get_m_prefix(self, message, not_print=True):
        if message.content.startswith("¤") and not_print:
            return '¤'
        elif message.content.startswith(self.default_prefix+"help") and not_print:
            return self.default_prefix
        if not hasattr(self, 'db'):
            return "€"
        await self.db.execute('CREATE TABLE IF NOT EXISTS prefixes (ctx_id INT PRIMARY KEY, prefix TINYTEXT)')
        cur = await self.db.execute('SELECT * FROM prefixes WHERE ctx_id=?', (self.get_id(message),))
        result = await cur.fetchone()
        if result:
            return result['prefix']
        return self.default_prefix

    async def httpcat(self,ctx,code,title=discord.Embed.Empty,description=discord.Embed.Empty):
        embed=Embed(title=title,color=self.colors['red'],description=description)
        embed.set_image(url="https://http.cat/"+str(code)+".jpg")
        await ctx.send(embed=embed)

    @staticmethod
    def get_id(ctx):
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id

    @staticmethod
    def get_color():
        return data.get_color()

async def command_prefix(bot,message):
    return await bot.get_m_prefix(message)

bot=chaotic_bot(command_prefix=command_prefix,description="A bot for fun",help_command=None,fetch_offline_members=True)

@bot.command(hidden=True,ignore_extra=True)
async def help(ctx,*command_help):
    """Sends the help message
    Trust me, there's nothing to see here. Absolutely nothing."""
    if len(command_help)==0:
        #Aide générale
        embed=Embed(title='Help',description=f'[Everything to know about my glorious self]({discord.utils.oauth_url(str(bot.user.id),permissions=discord.Permissions(data.invite_permissions))} "Invite link")\nThe prefix for this channel is `{discord.utils.escape_markdown(bot.get_m_prefix(ctx.message,False))}`',colour=data.colors['blue'])
        embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        embed.set_footer(text=f"To get more information, use {discord.utils.escape_markdown(bot.get_m_prefix(ctx.message,False))}help [subject].",icon_url=str(ctx.bot.user.avatar_url))
        for cog in bot.cogs:
            if bot.get_cog(cog).get_commands():
                command_list=[discord.utils.escape_markdown(bot.get_m_prefix(ctx.message,False))+command.name+' : '+command.short_doc for command in bot.get_cog(cog).get_commands() if not command.hidden]
                embed.add_field(name=bot.get_cog(cog).qualified_name,value='\n'.join(command_list),inline=False)
        command_list=[discord.utils.escape_markdown(bot.get_m_prefix(ctx.message,False))+command.name+' : '+command.short_doc for command in bot.commands if not command.cog and not command.hidden]
        if command_list:
            embed.add_field(name='Other commands',value='\n'.join(command_list))
        await ctx.send(embed=embed)
    else:
        for helper in command_help:
            cog=bot.get_cog(helper)
            if cog:
                if cog.get_commands():
                    #Aide d'un cog
                    embed=Embed(title=helper,description=cog.description,colour=data.colors['blue'])
                    embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
                    embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
                    for command in cog.get_commands():
                        if not command.hidden:
                            aliases=[command.name]
                            if command.aliases!=[]:
                                aliases+=command.aliases
                            embed.add_field(name='/'.join(aliases),value=command.help,inline=False)
                    embed.set_footer(text=f"Are you interested in {helper} ?",icon_url=str(ctx.bot.user.avatar_url))
                    await ctx.send(embed=embed)
            else:
                cog=bot.get_command(helper)
                if cog:
                    #Aide d'une commande spécifique
                    embed=Embed(title=bot.get_m_prefix(ctx.message,False)+helper,description=cog.help,colour=data.colors['blue'])
                    if cog.aliases!=[]:
                        embed.add_field(name="Aliases :",value="\n".join(cog.aliases))
                    embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
                    embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
                    if cog.hidden:
                        embed.set_footer(text=f"Wow, you found {helper} !",icon_url=str(ctx.bot.user.avatar_url))
                    else:
                        embed.set_footer(text=f"Are you interested in {helper} ?",icon_url=str(ctx.bot.user.avatar_url))
                    await ctx.send(embed=embed)
                else:
                    await ctx.bot.httpcat(ctx,404,f"I couldn't find {helper}")

bot.ksoft_client=ksoftapi.Client(bot.ksoft_token,bot.loop)
bot.run(data.token)
