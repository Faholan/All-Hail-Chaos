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

from discord.ext import commands,tasks
import pickle
import discord
import typing
import asyncio
from sys import version
import requests
from datetime import datetime
import aiohttp
import psutil

from os import path

def check_admin(): #Checks if the user has admin rights on the bot
    def predictate(ctx):
        return str(ctx.author) in ctx.bot.admins or ctx.bot.is_owner(ctx.author)
    return commands.check(predictate)

def check_administrator():
    def predictate(ctx):
        if isinstance(ctx.channel,discord.TextChannel):
            return ctx.channel.permissions_for(ctx.author).administrator
        return True
    return commands.check(predictate)

def secondes(s):
    r=[]
    if s>=86400:
        r.append(f'{s//86400} days')
        s%=86400
    if s>=3600:
        r.append(f'{s//3600} hours')
        s%=3600
    if s>=60:
        r.append(f'{s//60} minutes')
        s%=60
    if s>0:
        r.append(f'{s} seconds')
    return ', '.join(r)

class Utility(commands.Cog):
    '''Some functions to manage the bot or get informations about it'''
    def __init__(self,bot):
        self.bot=bot
        if self.bot.graphic_interface:
            import tkinter
            self.interface.start()
        if self.bot.discord_bots:
            self.discord_bots.start()
        self.process=psutil.Process()
        self.process.cpu_percent()
        psutil.cpu_percent()

    @commands.command(ignore_extra=True)
    async def add(self,ctx):
        '''Returns a link to add the bot to a new server'''
        await ctx.send(f"You can add me using this link : {discord.utils.oauth_url(str(self.bot.user.id),permissions=self.bot.invite_permissions)}")

    @commands.command(ignore_extra=True)
    async def code(self,ctx):
        '''Returns stats about the bot's code
        Credits to Dutchy#6127 for this command'''
        total = 0
        file_amount = 0
        list_of_files=[]
        import codecs
        import os
        import pathlib
        for p, subdirs, files in os.walk('.'):
            for name in files:
                    if name.endswith('.py'):
                        file_lines=0
                        file_amount += 1
                        with codecs.open('./' + str(pathlib.PurePath(p, name)), 'r', 'utf-8') as f:
                            for i, l in enumerate(f):
                                if l.strip().startswith('#') or len(l.strip())==0:  # skip commented lines.
                                    pass
                                else:
                                    total += 1
                                    file_lines+=1
                        final_path=p+path.sep+name
                        list_of_files.append(final_path.split('.'+path.sep)[-1]+f" : {file_lines} lines")
        embed=discord.Embed(colour=self.bot.get_color())
        embed.add_field(name=f"{self.bot.user.name}'s structure",value="\n".join(list_of_files))
        embed.set_footer(text=f'I am made of {total} lines of Python, spread across {file_amount} files !')
        await ctx.send(embed=embed)

    @commands.command(aliases=["convert"])
    async def currency(self,ctx,original,goal,value:float):
        """Converts money from one currency to another one"""
        if not len(original)==len(goal)==3:
            return await ctx.send("To get currency codes, refer to https://en.wikipedia.org/wiki/ISO_4217#Active_codes")
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ksoft.si/kumo/currency', params={"from": original, "to": goal, "value" :str(value)}, headers={"Authorization": f"Token {self.bot.ksoft_token}"}) as resp:
                data = await resp.json()
        if hasattr(data,"error"):
            return await ctx.send(data["message"])
        await ctx.send(f"The value of {value} {original} is {data['pretty']}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_webhooks=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    async def github(self,ctx):
        """Creates or deletes a webhook to get updates about the bot's development"""
        if not hasattr(self.bot,"github") or not self.bot.github_repo:
            return await ctx.send("This command hasn't been configured by the developer yet")
        for hook in await ctx.channel.webhooks():
            if hook.user==self.bot.user:
                await ctx.send("I already have created a webhook in this channel. Do you want me to delete it (y/n)")
                def check(m):
                    return m.author==ctx.author and (m.content.lower().startswith('y') or m.content.lower().startswith('n')) and m.channel==ctx.channel
                try:
                    msg=await self.bot.wait_for('message',check=check,timeout=30.0)
                except asyncio.TimeoutError:
                    return await ctx.send("The webhook wasn't deleted")
                if msg.content.lower().startswith("y"):
                    repo = self.bot.github.get_repo(self.bot.github_repo)
                    for webhook in repo.get_hooks():
                        if webhook.config['url'].startswith(hook.url):
                            webhook.delete()
                            break
                    await hook.delete()
                    return await ctx.send("Webhook deleted")
                else:
                    return await ctx.send("The webhook wasn't deleted")

        repo = self.bot.github.get_repo(self.bot.github_repo)
        hook = await ctx.channel.create_webhook(name=f"{self.bot.user.name} github updates webhook")
        repo.create_hook("web",{"url":hook.url+"/github", "content_type":"json"},["fork","create","delete","fork","pull_request","push","issue_comment","project","project_card","project_column"])
        await ctx.send("Webhook successfully created !")
        await self.bot.log_channel.send(f"Webhook created : {ctx.guild} - {ctx.channel} ({ctx.author})")

    @commands.command(ignore_extra=True)
    async def info(self,ctx):
        """Some info about me"""
        delta=datetime.utcnow()-self.bot.last_update
        app=await self.bot.application_info()
        embed=discord.Embed(title=f'Informations about {self.bot.user}',description=f'[Invite Link]({discord.utils.oauth_url(str(self.bot.user.id),permissions=self.bot.invite_permissions)} "Please stay at home and use bots")',colour=self.bot.get_color())
        embed.set_author(name=str(ctx.author),icon_url=str(ctx.author.avatar_url))
        embed.set_footer(text=f"Discord.py version {discord.__version__}, Python version {version.split(' ')[0]}")
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        embed.add_field(name="My owner (please respect him a lil bit) :",value=str(app.owner),inline=False)
        artist=self.bot.get_user(372336190919147522)
        if artist:
            embed.add_field(name="Credits for the superb profile pic :",value=str(artist),inline=False)
        embed.add_field(name="I'm very social. Number of servers i'm in :",value=len(self.bot.guilds),inline=False)
        embed.add_field(name="I know pretty much everybody.",value=f"In fact I only know {len(list(self.bot.get_all_members()))} members",inline=False)
        embed.add_field(name="Libraries used :",value='[KSoft.si](https://ksoft.si) : Whole Images Cog, currency, reputation\n[DiscordRep](https://discordrep.com/) : Reputation\n[Lavalink](https://github.com/Frederikam/Lavalink/ "I thank chr1sBot for learning about this") : Whole Music Cog\n[discord.py](https://discordapp.com/ "More exactly discord.ext.commands") : Basically this whole bot\n[NASA](https://api.nasa.gov/ "Yes I hacked the NASA") : Whole NASA Cog',inline=False)
        embed.add_field(name="Time since last update :",value=secondes(delta.seconds+86400*delta.days))
        embed.add_field(name="CPU usage - bot (total)",value=f"{self.process.cpu_percent():.2f} % ({psutil.cpu_percent():.2f} %)")
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    @commands.guild_only()
    @commands.check_any(check_admin(),commands.has_permissions(administrator=True))
    async def quit(self,ctx):
        '''Makes the bot quit the server
        Only a server admin can use this'''
        await ctx.send("See you soon !")
        await ctx.guild.leave()

    @commands.command(aliases=['close'],ignore_extra=True)
    @check_admin()
    async def logout(self,ctx):
        '''You need to be a bot administrator to use this.'''
        await ctx.send('Logging out...')
        await self.bot.close()

    @commands.command()
    @check_administrator()
    async def prefix(self,ctx,*,p=None):
        """Changes the bot's prefix for this guild or private channel"""
        if p:
            try:
                prefixes=pickle.load(open("data"+path.sep+"prefixes.DAT",mode="rb"))
            except:
                prefixes={}
            prefixes[self.bot.get_id(ctx)]=p
            pickle.dump(prefixes,open(f"data{path.sep}prefixes.DAT",mode="wb"))
            return await ctx.send(f"Prefix changed to `{discord.utils.escape_markdown(p)}`")
        await ctx.send(f"The prefix for this channel is `{discord.utils.escape_markdown(self.bot.get_m_prefix(ctx.message,False))}`")

    @commands.command(ignore_extra=True)
    @check_admin()
    async def reload(self,ctx):
        """Reloads the bot. You need to be one of the bot's admins to use this command"""
        await ctx.send("Reloading...")
        await self.bot.cog_reloader()

    @commands.command(ignore_extra=True,aliases=['succes'])
    async def success(self,ctx):
        '''Sends back your successes'''
        account_list=pickle.load(open("data"+path.sep+"accounts.DAT",mode='rb'))
        account=account_list[account_list.index(str(ctx.author))]
        gotten,locked,total=account.get_successes()
        embed=discord.Embed(title=f'Success list ({len(gotten)}/{total})',colour=self.bot.get_color())
        embed.set_author(name=str(ctx.author),icon_url=str(ctx.author.avatar_url))
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        for succ in gotten:
            embed.add_field(name=f"{succ.name} - Unlocked",value=succ.description,inline=False)
        for succ in locked:
            embed.add_field(name=succ.name+succ.advance(self.bot),value=succ.locked,inline=False)
        await ctx.send(embed=embed)

    def cog_unload(self):
        self.interface.cancel()

    #Tkinter graphic interface
    @tasks.loop(seconds=0.1)
    async def interface(self):
        self.fenetre.update_idletasks()
        self.fenetre.update()

    @interface.before_loop
    async def before_interface(self):
        self.fenetre=tkinter.Tk()
        self.users=tkinter.Listbox(self.fenetre,width=90,height=40,bd=1,highlightthickness=1,highlightbackground='#a0a0a0',highlightcolor='#a0a0a0')
        self.commandante=tkinter.Listbox(self.fenetre,width=50,height=40,bd=1,highlightthickness=1,highlightbackground='#a0a0a0',highlightcolor='#a0a0a0')
        self.fenetre.title(f"{self.bot.user}'s control panel")
        t_bot=tkinter.Entry(self.fenetre,width=25,relief=FLAT,borderwidth=0,disabledforeground='black')
        t_owner=tkinter.Entry(self.fenetre,width=25,relief=FLAT,borderwidth=0,disabledforeground='black')

        app=await self.bot.application_info()

        t_bot.insert(END,f"Bot : {self.bot.user}")
        t_bot.config(state=DISABLED)
        t_bot.grid(column=1,row=0,sticky=W)

        t_owner.insert(END,f"Owner : {app.owner}")
        t_owner.config(state=DISABLED)
        t_owner.grid(column=2,row=0,sticky=W)

        def deconnection():
            asyncio.create_task(self.bot.close())

        def reload():
            asyncio.create_task(self.bot.cog_reloader())

        reloader=tkinter.Button(self.fenetre,text="RELOAD",command=reload,bg="green3",fg="white")
        reloader.grid(column=3,row=0,sticky=E)

        deco=tkinter.Button(self.fenetre,text='SELF-DESTRUCTION',command=deconnection,bg='red3',fg='white')
        def update():
            self.users.delete(0,END)
            self.users.insert(END,'Guilds the bot is connected to :')
            for guild in self.bot.guilds:
                self.users.insert(END,f'Guild {guild.name} ({len(guild.members)})')
                online,idle,dnd,offline=[],[],[],[]
                i=0
                if not guild.large:
                    for member in guild.members:
                        if member.bot:
                            i+=1
                            m=f'{member} ({member.display_name}) - BOT'
                            if member.status==discord.Status.online:
                                online=[m]+online
                            elif member.status==discord.Status.idle:
                                idle=[m]+idle
                            elif member.status==discord.Status.dnd:
                                dnd=[m]+dnd
                            elif member.status==discord.Status.offline:
                                offline=[m]+offline
                        else:
                            m=f'{member} ({member.display_name})'
                            if member==guild.owner:
                                m+=' - ★'
                            if member.status==discord.Status.online:
                                online.append(m)
                            elif member.status==discord.Status.idle:
                                idle.append(m)
                            elif member.status==discord.Status.dnd:
                                dnd.append(m)
                            elif member.status==discord.Status.offline:
                                offline.append(m)
                def insertor(n,l):
                    self.users.insert(END,f'   └{n}')
                    for i in l:
                        self.users.insert(END,f'        └{i}')
                if online!=[]:
                    insertor(f'Online ({len(online)}/{guild.member_count}) :',online)
                if idle!=[]:
                    insertor(f'Idle ({len(idle)}/{guild.member_count}) :',idle)
                if dnd!=[]:
                    insertor(f'Do Not Disturb ({len(dnd)}/{guild.member_count}) :',dnd)
                if offline!=[]:
                    insertor(f'Offline ({len(offline)}/{guild.member_count}) :',offline)

        self.commandante.insert(END,"Bot's commands :")
        for cog in self.bot.cogs:
            self.commandante.insert(END,self.bot.get_cog(cog).qualified_name)
            for command in self.bot.get_cog(cog).get_commands():
                self.commandante.insert(END,f'   └{command.name}')
        c=[]
        for command in self.bot.commands:
            if command.cog==None:
                c.append(command)
        if c!=[]:
            self.commandante.insert(END,'Unclassified commands :')
            for command in c:
                self.commandante.insert(END,f'   └{command.name}')
        update()
        updater=Button(self.fenetre,text='REFRESH',command=update,bg='gray30',fg='white')
        updater.grid(column=0,row=0,sticky=W)
        deco.grid(column=4,row=0,sticky=E)
        self.users.grid(column=0,row=1,columnspan=3,rowspan=2)
        self.commandante.grid(column=3,row=1,columnspan=2,rowspan=2)

    @interface.after_loop
    async def after_interface(self):
        if self.interface.is_being_cancelled():
            self.fenetre.destroy()

    @tasks.loop(minutes=30)
    async def discord_bots(self):
        requests.post(f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",json={"guildCount":len(self.bot.guilds)},headers={"authorization":self.bot.discord_bots})

def setup(bot):
    bot.add_cog(Utility(bot))
