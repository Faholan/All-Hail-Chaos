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

import asyncio
from datetime import datetime, timedelta
import pickle
import psutil
from os import path
from sys import version
import typing

import aiohttp
import discord
from discord.ext import commands, menus, tasks
from discord.utils import escape_mentions, get, sleep_until

import codecs
import os
import pathlib

class EmbedSource(menus.ListPageSource):
    def __init__(self, embeds_dict):
        super().__init__(embeds_dict, per_page = 1)

    async def format_page(self, menu, embed_dict):
        embed = discord.Embed(title = embed_dict["title"].format(message_number = menu.current_page + 1, max_number = self.get_max_pages()), color = 0xffff00)
        embed.set_author(name = embed_dict["author"]["name"], icon_url = embed_dict["author"]["icon_url"])
        for field in embed_dict["fields"]:
            embed.add_field(name = field["name"], value = field["value"], inline = False)
        embed.timestamp = embed_dict["timestamp"]
        return embed

def check_admin(): #Checks if the user has admin rights on the bot
    async def predictate(ctx):
        return str(ctx.author) in ctx.bot.admins or await ctx.bot.is_owner(ctx.author)
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
    def __init__(self, bot):
        self.bot = bot
        self.snipe_list = {}
        if self.bot.discord_bots:
            self.discord_bots.start()
        if self.bot.xyz:
            self.xyz.start()
        if self.bot.discord_bot_list:
            self.discord_bot_list.start()

        self.process = psutil.Process()
        self.process.cpu_percent()
        psutil.cpu_percent()
        self.poll_tasks = []
        asyncio.create_task(self.poll_initial())

    def cog_unload(self):
        for task in self.poll_tasks:
            if not task.done():
                task.cancel()

    @commands.command(ignore_extra=True)
    async def add(self,ctx):
        '''Returns a link to add the bot to a new server'''
        await ctx.send(f"You can add me using this link : {discord.utils.oauth_url(str(self.bot.user.id),permissions=discord.Permissions(self.bot.invite_permissions))}")

    @commands.command(ignore_extra = True)
    async def block(self, ctx):
        """Use this command if you don't want me to DM you (except if you DM me commands)"""
        async with self.bot.pool.acquire(timeout = 5) as db:
            result = await db.fetchrow('SELECT * FROM public.block WHERE id=$1', ctx.author.id)
            if result:
                await db.execute("DELETE FROM public.block WHERE id=$1", ctx.author.id)
                await ctx.send("You unblocked me")
            else:
                await db.execute("INSERT INTO public.block VALUES ($1)", ctx.author.id)
                await ctx.send("You blocked me")

    @commands.command(ignore_extra = True)
    async def code(self, ctx):
        '''Returns stats about the bot's code
        Credits to Dutchy#6127 for this command'''
        total = 0
        file_amount = 0
        list_of_files=[]
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
        embed = discord.Embed(colour = self.bot.colors['yellow'])
        embed.add_field(name = f"{self.bot.user.name}'s structure", value = "\n".join(list_of_files))
        embed.set_footer(text = f'I am made of {total} lines of Python, spread across {file_amount} files !')
        await ctx.send(embed=embed)

    @commands.command()
    async def contact(self, ctx, *, message):
        """Contact my staff for anything you think requires their attention"""
        embed = discord.Embed(title = f"Message from an user ({ctx.author.id})", description = message)
        embed.set_author(name = f"{ctx.author.name}#{ctx.author.discriminator}", icon_url = str(ctx.author.avatar_url))
        channel = self.bot.get_channel(self.bot.contact_channel_id)
        if channel:
            await channel.send(embed = embed)
            await ctx.send("Your message has been successfully sent")
        else:
            await ctx.send("Sorry but my owner hasn't correctly configured this")

    @commands.command(aliases=["convert"])
    async def currency(self,ctx,original,goal,value:float):
        """Converts money from one currency to another one. Syntax : €currency [Original currency code] [Goal currency code] [value]"""
        if not len(original) == len(goal) == 3:
            return await ctx.send("To get currency codes, refer to https://en.wikipedia.org/wiki/ISO_4217#Active_codes")
        async with self.bot.aio_session.get('https://api.ksoft.si/kumo/currency', params={"from": original, "to": goal, "value" :str(value)}, headers={"Authorization": f"Token {self.bot.ksoft_token}"}) as resp:
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
        if not hasattr(self.bot, "github") or not self.bot.github_repo:
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
        delta = datetime.utcnow()-self.bot.last_update
        app = await self.bot.application_info()
        embed = discord.Embed(title = f'Informations about {self.bot.user}', description = f'[Invite Link]({discord.utils.oauth_url(str(self.bot.user.id), permissions = discord.Permissions(self.bot.invite_permissions))} "Please stay at home and use bots")\n[Support Server Invite]({self.bot.support})', colour = self.bot.get_color())
        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        embed.set_footer(text = f"Discord.py version {discord.__version__}, Python version {version.split(' ')[0]}")
        embed.set_thumbnail(url = str(ctx.bot.user.avatar_url))
        embed.add_field(name = f"My owner{'s' if app.team else ''} :", value = ", ".join([str(member) for member in app.team.members]) if app.team else str(app.owner), inline = False)
        artist = self.bot.get_user(372336190919147522)
        if artist:
            embed.add_field(name = "Credits for the superb profile pic :", value = str(artist), inline = False)
        embed.add_field(name = "I'm very social. Number of servers i'm in :", value = len(self.bot.guilds), inline = False)
        embed.add_field(name = "I know pretty much everybody.", value = f"In fact I only know {len(self.bot.users)} users", inline = False)
        embed.add_field(name = "I've got many commands", value = f"More exactly {len(self.bot.commands)} commands", inline = False)
        embed.add_field(name = "Description page :", value = f'[top.gg page]({self.bot.top_gg} "Description on top.gg")\n[bots on discord page]({self.bot.bots_on_discord} "Description on bots on discord")\n[Discord bots page]({self.bot.discord_bots_page} "Description on discord bots")', inline = False)
        embed.add_field(name = "Libraries used :", value = '[KSoft.si](https://ksoft.si) : Whole Images Cog, currency, reputation\n[DiscordRep](https://discordrep.com/) : Reputation\n[Lavalink](https://github.com/Frederikam/Lavalink/ "I thank chr1sBot for learning about this") : Whole Music Cog\n[discord.py](https://discordapp.com/ "More exactly discord.ext.commands") : Basically this whole bot\n[NASA](https://api.nasa.gov/ "Yes I hacked the NASA") : Whole NASA Cog', inline = False)
        embed.add_field(name = "Time since last update :",value=secondes(delta.seconds+86400*delta.days))
        embed.add_field(name = "CPU usage - bot (total)", value = f"{self.process.cpu_percent():.2f} % ({psutil.cpu_percent():.2f} %)")
        await ctx.send(embed = embed)

    @commands.command(ignore_extra = True)
    @commands.guild_only()
    @commands.check_any(check_admin(), commands.has_permissions(administrator = True))
    async def quit(self, ctx):
        '''Makes the bot quit the server
        Only a server admin can use this'''
        await ctx.send("See you soon !")
        await ctx.guild.leave()

    @commands.command(ignore_extra = True, aliases = ["polls"])
    @commands.guild_only()
    async def poll(self, ctx):
        messages_to_delete = [await ctx.send("Welcome to the poll creation tool !\nPlease tell me what this poll will be about")]
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        try:
            subj_message = await self.bot.wait_for("message", check = check, timeout = 120)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't answer in time. I'm so sad !")
        subject = subj_message.content
        messages_to_delete.append(subj_message)
        messages_to_delete.append(await ctx.send("Now, how many possibilities does your poll have (2-10) ?"))
        def check2(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()
        try:
            num_message = await self.bot.wait_for("message", check = check2, timeout = 120)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't answer in time. I'm so sad !")
        num = int(num_message.content)
        if not 1 < num < 11:
            return await ctx.send("Invalid number passed !")
        messages_to_delete.append(num_message)
        answers = []
        for i in range(num):
            messages_to_delete.append(await ctx.send(f"What will be the content of option {i+1} ?"))
            try:
                message_subj = await self.bot.wait_for("message", check = check, timeout = 120)
            except asyncio.TimeoutError:
                return await ctx.send("You didn't answer in time. I'm so sad !")
            answers.append(message_subj.content)
            messages_to_delete.append(message_subj)
        messages_to_delete.append(await ctx.send("And now, for the final touch, how much time will this poll last ? Send it in the format <days>d <hours>h <minutes>m (only one of these is required)"))

        def converter(content):
            content = content.replace(" ", "")
            if not any(i in content for i in "dhm"):
                return False

            days, hours, minutes = 0, 0, 0

            if "m" in content:
                minutes, content = content.split("m", maxsplit = 1)
                if not minutes.isdigit():
                    return False
                minutes = int(minutes)
                hours += minutes // 60
                minutes %= 60

            if "h" in content:
                hours, content = content.split("h", masplit = 1)
                if not hours.isdigit():
                    return False
                hours += int(hours)
                days += hours//24
                hours %= 24

            if "d" in content:
                days, content = content.split("d", maxsplit = 1)
                if not days.isdigit():
                    return False
                days += int(days)

            if content:
                return False
            return (days, hours, minutes)

        def check3(message):
            return message.author == ctx.author and message.channel == ctx.channel and converter(message.content)

        try:
            message_time = await self.bot.wait_for("message", check = check3, timeout = 120)
        except asyncio.TimeoutError:
            return await ctx.send("You didn't answer in time. I'm so sad !")

        days, hours, minutes = converter(message_time.content)
        if days == hours == minutes == 0:
            return await ctx.send("A poll must last at least 1 minute")
        messages_to_delete.append(message_time)

        timestamp = datetime.utcnow() + timedelta(days = days, hours = hours, minutes = minutes)

        embed = discord.Embed(title = f"Poll lasting for{' ' + str(days) + 'days' if days else ''}{' ' + str(hours) + 'hours' if hours or days else ''} {minutes} minutes", description = escape_mentions(subject), colour = self.bot.get_color())
        embed.set_author(name = ctx.author.display_name, icon_url = ctx.author.avatar_url_as(format = "jpg"))
        embed.timestamp = timestamp
        for i, j in enumerate(answers):
            embed.add_field(name = f"Answer {i + 1}", value = escape_mentions(j), inline = False)

        message = await ctx.send(embed = embed)
        for i in range(1, min(10, len(answers) + 1)):
            await message.add_reaction(str(i) + "\N{variation selector-16}\N{combining enclosing keycap}")
        if len(answers) == 10:
            await message.add_reaction("\N{keycap ten}")

        async with self.bot.pool.acquire(timeout = 5) as db:
            await db.execute("INSERT INTO public.polls VALUES ($1, $2, $3, $4, $5, $6, $7)", message.id, ctx.channel.id, ctx.guild.id, ctx.author.id, timestamp, answers, subject)

        task = asyncio.create_task(self.poll_generator(message.id, ctx.channel.id, ctx.guild.id, ctx.author.id, timestamp, answers, subject)())
        self.poll_tasks.append(task)
        for M in messages_to_delete:
            try:
                await M.delete()
            except:
                continue

    async def poll_initial(self):
        async with self.bot.pool.acquire() as db:
            for D in await db.fetch("SELECT * FROM public.polls"):
                task = asyncio.create_task(self.poll_generator(**dict(D))())
                self.poll_tasks.append(task)

    def poll_generator(self, message_id, channel_id, guild_id, author_id, timestamp, answers, subject):
        async def predictate():
            await sleep_until(timestamp)
            async with self.bot.pool.acquire(timeout = 5) as db:
                await db.execute("DELETE FROM public.polls WHERE message_id=$1", message_id)
            channel = self.bot.get_guild(guild_id).get_channel(channel_id)
            try:
                message = await channel.fetch_message(message_id)
            except:
                return
            final = []
            for i, j in enumerate(answers):
                if i != 9:
                    reaction = get(message.reactions, emoji = str(i + 1) + "\N{variation selector-16}\N{combining enclosing keycap}")
                    if reaction:
                        final.append((reaction.count - 1 if reaction.me else reaction.count, j))
                    else:
                        final.append((0, j))
                else:
                    reaction = get(message.reactions, emoji = "\N{keycap ten}")
                    if reaction:
                        final.append((reaction.count - 1 if reaction.me else reaction.count, j))
                    else:
                        final.append((0, j))
            final = sorted(final, key = lambda two:two[0], reverse = True)
            embed = discord.Embed(title = f'The poll "{escape_mentions(subject)}" is finished !', description = f"*Vox populi, vox dei !*\n\nThe winner is : {final[0][1]}", colour = self.bot.get_color())
            embed.timestamp = timestamp
            author = channel.guild.get_member(author_id)
            if author:
                embed.set_author(name = author.display_name, icon_url = author.avatar_url_as(format = "jpg"))
            for i, j in final:
                embed.add_field(name = j, value = f"{i} people voted for that option !", inline = False)
            await channel.send(embed = embed)
        return predictate

    @commands.command()
    @check_administrator()
    async def prefix(self, ctx, *, p = None):
        """Changes the bot's prefix for this guild or private channel"""
        if p:
            async with self.bot.pool.acquire(timeout = 5) as db:
                ID = self.bot.get_id(ctx)
                await db.execute("INSERT INTO public.prefixes VALUES ($1, $2) ON CONFLICT (ctx_id) DO UPDATE SET prefix=$2", ID, p)
                self.bot.prefix_dict[ID] = p
                return await ctx.send(f"Prefix changed to `{discord.utils.escape_markdown(p)}`")
        await ctx.send(f"The prefix for this channel is `{discord.utils.escape_markdown(await self.bot.get_m_prefix(ctx.message, False))}`")

    @commands.command(ignore_extra = True)
    @commands.guild_only()
    async def snipe(self, ctx):
        """Returns up to the 20 most recently edited / deleted messages of the channel"""
        L = self.snipe_list.get(ctx.channel.id)
        if L:
            pages = menus.MenuPages(source = EmbedSource(L), clear_reactions_after=True)
            await pages.start(ctx)
        else:
            await ctx.send("I don't have any record for this channel yet")

    @commands.Cog.listener('on_message_edit')
    async def snipe_edit(self, before, after):
        if before.content != after.content:
            L = self.snipe_list.get(before.channel.id, [])
            E = {"title":"Message edited ({message_number}/{max_number})", "author":{"name":str(before.author), "icon_url":str(before.author.avatar_url)}, "fields":[]}
            if "`" in before.content:
                E["fields"] += [{"name":"Original message", "value":before.content}]
            else:
                E["fields"] += [{"name":"Original message", "value":f"```\n{before.content}\n```"}]
            if "`" in after.content:
                E["fields"] += [{"name":"Edited message", "value":after.content}]
            else:
                E["fields"] += [{"name":"Edited message", "value":f"```\n{after.content}\n```"}]
            E["timestamp"] = datetime.utcnow()
            L = [E] + L
            self.snipe_list[before.channel.id] = L[:20]

    @commands.Cog.listener('on_message_delete')
    async def snipe_delete(self, message):
        if message.content:
            L = self.snipe_list.get(message.channel.id, [])
            E = {"title":"Message deleted ({message_number}/{max_number})", "author":{"name":str(message.author), "icon_url" : str(message.author.avatar_url)}, "fields":[]}
            if "`" in message.content:
                E["fields"] += [{"name":"Original message", "value":message.content}]
            else:
                E["fields"] += [{"name":"Original message", "value":f"```\n{message.content}\n```"}]
            E["timestamp"] = datetime.utcnow()
            L = [E] + L
            self.snipe_list[message.channel.id] = L[:20]

    @commands.command()
    @commands.cooldown(2,600,commands.BucketType.user)
    async def suggestion(self,ctx,subject,*,idea):
        '''Command to make suggestions for the bot. Please note that your Discord name will be recorded and publicly associated to the idea in the support server.
        Syntax : €suggestion [subject] [idea]. If the subject includes whitespaces, surround it with double braces, "like this".'''
        #if ctx.author.id in self.blacklist_suggestion:
            #return await ctx.send("You cannot make suggestions anymore about the bot")
        embed = discord.Embed(title = f"Suggestion for **{subject}**", description = f"Subject of <@{ctx.author.id}>'s suggestion : {subject}", colour = self.bot.colors['yellow'])
        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
        embed.add_field(name = f"<@{ctx.author.id}>'s idea", value = idea)
        if bot.suggestion_channel:
            await self.bot.suggestion_channel.send(embed = embed)
            await ctx.send("Thanks for your participation in this project !")
        else:
            await ctx.send("Sorry but my owner hasn't correctly configured this command")

    @tasks.loop(minutes=30)
    async def discord_bots(self):
        await self.bot.aio_session.post(f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",json={"guildCount":len(self.bot.guilds)},headers={"authorization":self.bot.discord_bots})

    @tasks.loop(minutes=30)
    async def xyz(self):
        await self.bot.aio_session.post(f"https://bots.ondiscord.xyz/bot-api/bots/{self.bot.user.id}/guilds",json={"guildCount":len(self.bot.guilds)},headers={"Authorization":self.bot.xyz})

    @tasks.loop(minutes=30)
    async def discord_bot_list(self):
        await self.bot.aio_session.post(f"https://discordbotlist.com/api/bots/{self.bot.user.id}/stats",json={"guilds":len(self.bot.guilds),"users":len([*self.bot.get_all_members()])},headers={"Authorization":f"Bot {self.bot.discord_bot_list}"})


def setup(bot):
    bot.add_cog(Utility(bot))
