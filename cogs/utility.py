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
from pytz import utc
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

class TagName(commands.clean_content):
    def __init__(self, *, lower=False):
        self.lower = lower
        super().__init__()

    async def convert(self, ctx, argument):
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            raise commands.BadArgument('Missing tag name.')

        if len(lower) > 100:
            raise commands.BadArgument('Tag name is a maximum of 100 characters.')

        first_word, _, _ = lower.partition(' ')

        # get tag command.
        root = ctx.bot.get_command('tag')
        if first_word in root.all_commands:
            raise commands.BadArgument('This tag name starts with a reserved word.')

        return converted if not self.lower else lower

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

def check_administrator():
    def predictate(ctx):
        if isinstance(ctx.channel, discord.TextChannel):
            return ctx.channel.permissions_for(ctx.author).administrator
        return True
    return commands.check(predictate)

def secondes(s):
    r = []
    if s >= 86400:
        r.append(f"{s // 86400} days")
        s %= 86400
    if s >= 3600:
        r.append(f"{s // 3600} hours")
        s %= 3600
    if s >= 60:
        r.append(f"{s // 60} minutes")
        s %= 60
    if s > 0:
        r.append(f"{s} seconds")
    return ", ".join(r)

class Utility(commands.Cog):
    """Some functions to manage the bot or get informations about it"""
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

        self.tags_being_made = {}

    def cog_unload(self):
        for task in self.poll_tasks:
            if not task.done():
                task.cancel()

    @commands.command(ignore_extra=True)
    async def add(self,ctx):
        """Returns a link to add the bot to a new server"""
        await ctx.send(f"You can add me using this link : {discord.utils.oauth_url(str(self.bot.user.id),permissions=discord.Permissions(self.bot.invite_permissions))}")

    @commands.command(ignore_extra = True)
    async def block(self, ctx):
        """Use this command if you don't want me to DM you (except if you DM me commands)"""
        async with self.bot.pool.acquire(timeout = 5) as db:
            result = await db.fetchrow("SELECT * FROM public.block WHERE id=$1", ctx.author.id)
            if result:
                await db.execute("DELETE FROM public.block WHERE id=$1", ctx.author.id)
                await ctx.send("You unblocked me")
            else:
                await db.execute("INSERT INTO public.block VALUES ($1)", ctx.author.id)
                await ctx.send("You blocked me")

    @commands.command(ignore_extra = True)
    async def code(self, ctx):
        """Returns stats about the bot's code
        Credits to Dutchy#6127 for this command"""
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
        embed.add_field(name = "GitHub repository", value = f'[It\'s open source !]({self.bot.github_link} "Yeah click me !")')
        embed.add_field(name = "Description page :", value = f'[top.gg page]({self.bot.top_gg} "Description on top.gg")\n[bots on discord page]({self.bot.bots_on_discord} "Description on bots on discord")\n[Discord bots page]({self.bot.discord_bots_page} "Description on discord bots")\n[Discord bot list page]({self.bot.discord_bot_list_page} "Description on discord bot list")', inline = False)
        embed.add_field(name = "Libraries used :", value = '[KSoft.si](https://ksoft.si) : Whole Images Cog, currency, reputation\n[DiscordRep](https://discordrep.com/) : Reputation\n[Lavalink](https://github.com/Frederikam/Lavalink/ "I thank chr1sBot for learning about this") : Whole Music Cog\n[discord.py](https://discordapp.com/ "More exactly discord.ext.commands") : Basically this whole bot\n[NASA](https://api.nasa.gov/ "Yes I hacked the NASA") : Whole NASA Cog', inline = False)
        embed.add_field(name = "Time since last update :",value=secondes(delta.seconds+86400*delta.days))
        embed.add_field(name = "CPU usage - bot (total)", value = f"{self.process.cpu_percent():.2f} % ({psutil.cpu_percent():.2f} %)")
        await ctx.send(embed = embed)

    @commands.command(ignore_extra = True)
    @commands.guild_only()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def quit(self, ctx):
        '''Makes the bot quit the server
        Only a server admin can use this'''
        await ctx.send("See you soon !")
        await ctx.guild.leave()

    @commands.command(ignore_extra = True, aliases = ["polls"])
    @commands.guild_only()
    async def poll(self, ctx):
        """Command to make a poll. Everything is explained in it"""
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
                hours, content = content.split("h", maxsplit = 1)
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
    async def suggestion(self, ctx, subject, *, idea):
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

    def check_tag(self, name, guild, author):
        tag_author = self.tags_being_made.get((guild, name))
        return not tag_author or tag_author == author

    async def search_tag(self, name, ID, db):
        rows = await db.fetch("SELECT name FROM public.tag_lookup WHERE location_id=$1 AND name % $2 ORDER BY similarity(name, $2) DESC LIMIT 3", ID, name)
        return "\n".join([row["name"] for row in rows])

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx, *, name: TagName(lower = True)):
        """Tag some text to retrieve it later. This group contains subcommands"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", name, ID)
            if not row:
                rows = await self.search_tag(name, ID, db)
                if rows:
                    return await ctx.send(f"Tag not found. Did you mean :\n{rows}")
                return await ctx.send("Tag not found")
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE id=$1", row["tag_id"])
            if not tag:
                await ctx.send("Tag not found")
                return await self.delete_aliases(row["tag_id"], db)
            await db.execute("UPDATE public.tags SET use_count=use_count+1 WHERE id=$1", tag["id"])
            await db.execute("UPDATE public.tag_lookup SET use_count=use_count+1 WHERE name=$1 AND location_id=$2", name, ID)
        await ctx.send(tag["content"])

    async def create_tag(self, ctx, name, content, ID=None):
        if ID is None:
            ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", name, ID)
            if row:
                return await ctx.send("A tag already exists with that name")
            await db.execute("INSERT INTO public.tags VALUES ($1, $2, $3, $4)", ID, ctx.author.id, name, content)
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE name=$1 AND location_id=$2", name, ID)
            await db.execute("INSERT INTO public.tag_lookup VALUES ($1, $2, $3, $4)", name, ID, ctx.author.id, tag["id"])

    async def delete_aliases(self, tag_id, db):
        await db.execute("DELETE FROM public.tag_lookup WHERE tag_id=$1", tag_id)

    @tag.command(name="alias")
    @commands.guild_only()
    async def tag_alias(self, ctx, name: TagName(lower=True), *, alias: TagName(lower=True)):
        """Create an alias to a tag under which it can be retrieved"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE location_id=$1 and name=$2", ID, name)
            if not row:
                return await ctx.send(f"No tag named {name} found")
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE id=$1", row["tag_id"])
            if not tag:
                await ctx.send(f"No tag named {name} found")
                return await self.delete_aliases(row["tag_id"], db)
            existing_alias = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE location_id=$1 and name=$2", ID, alias)
            if existing_alias:
                return await ctx.send(f"An alias named {alias} already exists")
            await db.execute("INSERT INTO public.tag_lookup VALUES ($1, $2, $3, $4)", alias, ID, ctx.author.id, row["tag_id"])
            await ctx.send(f"Alias {alias} for tag {tag['name']} created successfully")

    @tag.command(name="claim")
    @commands.guild_only()
    async def tag_claim(self, ctx, *, name: TagName(lower=True)):
        """Become the owner of an unclaimed tag"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            alias = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", name, ID)
            if not alias:
                return await ctx.send(f"No tag or alias named {name} found")
            try:
                owner = ctx.guild.get_member(alias["owner_id"]) or await ctx.guild.fetch_member(alias["owner_id"])
            except discord.NotFound:
                owner = None

            if owner:
                return await ctx.send(f"{name} isn't unclaimed : {owner} has claimed it")

            tag = await db.fetchrow("SELECT * FROM public.tags WHERE id=$1", alias["tag_id"])
            if not tag:
                await ctx.send(f"No tag or alias named {name} found")
                return await self.delete_aliases(alias["tag_id"], db)

            try:
                owner = ctx.guild.get_member(tag["owner_id"]) or await ctx.guild.fetch_member(tag["owner_id"])
            except discord.NotFound:
                owner = None

            await db.execute("UPDATE public.tag_lookup SET owner_id=$1 WHERE name=$2 AND location_id=$3", ctx.author.id, name, ID)
            if owner is None:
                await db.execute("UPDATE public.tags SET owner_id=$1 WHERE id=$2", ctx.author.id, tag["id"])
                return await ctx.send(f"Tag {tag['name']} {'and alias '+name if name!=tag['name']+' were' else 'was'} successfully claimed")
            await ctx.send(f"Alias {name} successfully claimed")

    @tag.command(name="create")
    @commands.guild_only()
    async def tag_create(self, ctx, name: TagName(lower=True), *, content):
        """Create a tag with the given name and content, setting you as the author"""
        ID = self.bot.get_id(ctx)
        if not self.check_tag(name, ID, ctx.author.id):
            return await ctx.send("Someone is already making a tag with this name")
        self.tags_being_made[(ID, name)] = ctx.author.id
        await self.create_tag(ctx, name, content)
        await ctx.send(f"Tag {name} created successfully")
        del self.tags_being_made[(ID, name)]

    @tag.command(name="delete", aliases = ["remove"])
    @commands.guild_only()
    async def tag_delete(self, ctx, *, name:TagName(lower=True)):
        """Only the owner of the tag, or alias, or someone with manage_messages permissions can use this"""
        override = ctx.author.id == self.bot.owner_id or (ctx.author.guild_permissions.manage_messages if ctx.guild else False)
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            if override:
                alias = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE location_id=$1 AND name=$2", ID, name)
            else:
                alias = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE location_id=$1 AND name=$2 AND owner_id=$3", ID, name, ctx.author.id)
            if not alias:
                return await ctx.send(f"No tag or alias named {name} found. Are you sure that it exists and that you own it ?")
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE id=$1", alias["tag_id"])
            if not tag:
                await ctx.send(f"No tag or alias named {name} found. Are you sure that it exists and that you own it ?")
                return await self.delete_aliases(alias["tag_id"], db)
            if tag["name"] == alias["name"]:
                await ctx.send(f"Tag {name} and associated aliases successfully deleted")
                await db.execute("DELETE FROM public.tags WHERE id=$1", tag["id"])
                await self.delete_aliases(tag["id"], db)
            else:
                await ctx.send(f"Alias {tag} deleted successfully")
                await db.execute("DELETE FROM public.tag_lookup WHERE location_id=$1 AND name=$2", ID, alias["name"])

    @tag.command(name="info")
    @commands.guild_only()
    async def tag_info(self, ctx, *, name: TagName(lower=True)):
        """Retrieve information about a tag"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", name, ID)
            if not row:
                return await ctx.send(f"No tag named {name} found")
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE id=$1", row["tag_id"])
            if not tag:
                await ctx.send(f"No tag named {name} found")
                return await self.delete_aliases(row["tag_id"], db)

            aliases = await db.fetch("SELECT * FROM public.tag_lookup WHERE tag_id=$1", row["tag_id"])

        embed = discord.Embed(title=f"Informations about tag {tag['name']}", colour=self.bot.colors["blue"])
        try:
            owner = ctx.guild.get_member(tag["owner_id"]) or await ctx.guild.fetch_member(tag["owner_id"])
        except discord.NotFound:
            owner = None
        embed.add_field(name="Owner :", value=f"{owner.mention if owner else 'Unclaimed'}")
        embed.add_field(name="Usages :", value=tag["use_count"])
        if len(aliases) > 1:
            alias_content = []
            for alias in aliases:
                if alias["name"] != tag["name"]:
                    try:
                        owner = ctx.guild.get_member(alias["owner_id"]) or await ctx.guild.fetch_member(alias["owner_id"])
                    except discord.NotFound:
                        owner = None
                    alias_content.append(f"{alias['name']} : {owner.mention if owner else 'Unclaimed'}")
            embed.add_field(name="Aliases :", value="\n".join(alias_content))
        if name != tag["name"]:
            embed.set_footer(text = "Alias created at :")
        else:
            embed.set_footer(text = "Tag created at :")
        embed.timestamp = row["created_at"].astimezone(utc)
        await ctx.send(embed=embed)

    @tag.command(name="make")
    @commands.guild_only()
    async def tag_make(self, ctx):
        """Interactive alternative to create"""
        ID = self.bot.get_id(ctx)
        await ctx.send("Okay, what will the tag's name be ?")
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            name = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to answer. Cancelling.")

        original = ctx.message
        converter = TagName()
        try:
            ctx.message = name
            name = await converter.convert(ctx, name.content)
        except commands.BadArgument as e:
            return await ctx.send(f'{e}. Redo the command "{ctx.prefix}tag make" to retry.')
        finally:
            ctx.message = original

        if not self.check_tag(name, ID, ctx.author.id):
            return await ctx.send("Someone is already making a tag with that name. Try again later.")

        async with self.bot.pool.acquire() as db:
            row = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", name, ID)
            if row:
                return await ctx.send("A tag, or an alias to a tag, already exists with that name")

        self.tags_being_made[(ID, name)] = ctx.author.id

        await ctx.send(f"Okay, the tag's name is {name}. What will be its content ?\nYou can type `{ctx.prefix}abort` to escape this process")
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            del self.tags_being_made[(ID, name)]
            return await ctx.send("You took too long. I'm canelling this")

        content = msg.content
        if content == f"{ctx.prefix}abort":
            del self.tags_being_made[(ID, name)]
            return await ctx.send("Aborted")
        clean_content = await commands.clean_content().convert(ctx, content)
        if msg.attachments:
            clean_content += f"\n{msg.attachments[0].url}"
        await ctx.send(f"Tag {name} created successfully")
        await self.create_tag(ctx, name, clean_content)
        del self.tags_being_made[(ID, name)]

    @tag.command(name="purge")
    @commands.has_guild_permissions(manage_messages=True)
    async def tag_purge(self, ctx, member: discord.Member):
        """Deletes all local tags made by a user"""
        ID = self.bot.get_id(ctx)
        counter = 0
        async with self.bot.pool.acquire() as db:
            for tag in await db.fetch("SELECT * FROM public.tags WHERE owner_id=$1 AND location_id=$2", member.id, ID):
                counter += 1
                await db.execute("DELETE FROM public.tags WHERE id=$1", tag["id"])
                await self.delete_aliases(tag["id"], db)
        await ctx.send(f"{counter} tag{'s' if counter > 1 else ''} owned by {member.mention} {'were' if counter > 1 else 'was'} deleted" if counter else f"{member} hasn't created any tag")

    @tag.command(name="search")
    @commands.guild_only()
    async def tag_search(self, ctx, *, name: TagName(lower=True)):
        """Search for a tag"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            rows = await self.search_tag(name, ID, db)
        if rows:
            await ctx.send(f"Possible tags matching this query :\n{rows}")
        else:
            await ctx.send("I didn't find any tag matching this query")

    @tag.command(name="transfer", aliases=["give"])
    @commands.guild_only()
    async def tag_transfer(self, ctx, name: TagName(lower=True), *, member: discord.Member):
        """Transfer a tag, or alias, you own to a new user"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            alias = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2 AND owner_id=$3", name, ID, ctx.author.id)
            if not alias:
                return await ctx.send(f"No tag or alias named {name} found. Are  you sure that it exists and you own it ?")

            tag = await db.fetchrow("SELECT * FROM public.tags WHERE name=$1 AND owner_id=$2 AND location_id=$3", name, ctx.author.id, ID)
            await db.execute("UPDATE public.tag_lookup SET owner_id=$1 WHERE name=$2 AND location_id=$3", member.id, name, ID)
            if tag:
                await db.execute("UPDATE public.tags SET owner_id=$1 WHERE name=$2 AND location_id=$3", member.id, name, ID)
                return await ctx.send("Tag successfully transferred")
            await ctx.send("Alias successfully transferred")

    @tag.group(name="global", invoke_without_command=True)
    @commands.guild_only()
    async def tag_global(self, ctx):
        """Group including all the commands about global tags"""
        await ctx.send_help("tag global")

    @tag_global.command(name="put")
    @commands.guild_only()
    async def global_put(self, ctx, *, alias: TagName(lower=True)):
        """Command to make a tag global. Only the owner of the tag can use this"""
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            aliasrow = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND owner_id=$2 AND location_id=$3", alias, ctx.author.id, ID)
            if not aliasrow:
                return await ctx.send(f"I didn't find any tag with the name {alias}. Are you sure that it exists and that you own it ?")
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE id=$1 AND owner_id=$2", aliasrow["tag_id"], ctx.author.id)
            if not tag:
                return await ctx.send(f"I didn't find any tag with the name {alias}. Are you sure that it exists and that you own it ?")
            already_existing = await db.fetchrow("SELECT * FROM public.tags WHERE name=$1 AND location_id=0", alias)
            if already_existing:
                return await ctx.send("A global tag with that name already exists. Try creating an alias to your tag and globalizing it under this name")
            await self.create_tag(ctx, alias, tag["content"], 0)
        await ctx.send(f"Global tag {alias} created successfully")

    @tag_global.command(name="delete", aliases=["remove"])
    @commands.guild_only()
    async def global_delete(self, ctx, *, name: TagName(lower=True)):
        """Command to remove a tag from the global database. This has no effect on local versions of this tag
        You must be the tag's owner to use that"""
        async with self.bot.pool.acquire() as db:
            aliasrow = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND owner_id=$2 AND location_id=0", name, ctx.author.id)
            if not aliasrow:
                return await ctx.send(f"No global tag named {name} found. Are you sure that it exists and you own it ?")
            await db.execute("DELETE FROM public.tags WHERE id=$1", aliasrow["tag_id"])
            await ctx.send(f"Global tag {name} deleted succesfully")
            await self.delete_aliases(aliasrow["tag_id"], db)

    @tag_global.command(name="retrieve")
    @commands.guild_only()
    async def global_retrieve(self, ctx, *, name: TagName(lower=True)):
        """Retrieve a tag from the global database, adding it to your local tags"""
        alias = name
        ID = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as db:
            tag = await db.fetchrow("SELECT * FROM public.tags WHERE name=$1 AND location_id=0", name)
            if not tag:
                rows = await self.search_tag(name, 0, db)
                if rows:
                    return await ctx.send(f"Global tag not found. Did you mean\n{rows}")
                return await ctx.send(f"No global tag named {name} found")
            await db.execute("UPDATE public.tags SET use_count=use_count+1 WHERE id=$1", tag["id"])
            already_exists = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", name, ID)
            if already_exists:
                await ctx.send(f"A local tag with this name already exists. Please enter a new name under which I shall save this tag. \
                Enter **{ctx.prefix}abort** to quit")

                def check(message):
                    return message.channel == ctx.channel and message.author == ctx.author

                try:
                    alias = await self.bot.wait_for("message", check=check, timeout=300)
                except asyncio.TimeoutError:
                    return await ctx.send("You didn't reply in time. Aborting")

                converter = TagName()
                original = ctx.message

                try:
                    ctx.message = alias
                    alias = await converter.convert(ctx, alias.content)
                except commands.BadArgument as e:
                    return await ctx.send(f'{e}. Redo the command "{ctx.prefix}tag global retrieve" to retry.')
                finally:
                    ctx.message = original

                if not self.check_tag(alias, ctx.guild.id, ctx.author.id):
                    return await ctx.send("Someone is already making a tag with that name. Sorry")

                already_exists = await db.fetchrow("SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2", alias, ID)
                if already_exists:
                    return await ctx.send("A tag with that name already exists. Aborting")

            await self.create_tag(ctx, alias, tag["content"])
            await ctx.send(f"Tag {alias} created successfully")

    @tag_global.command(name="search")
    @commands.guild_only()
    async def global_search(self, ctx, *, name: TagName(lower=True)):
        """Search for a global tag"""
        async with self.bot.pool.acquire() as db:
            rows = await self.search_tag(name, 0, db)
        if rows:
            await ctx.send(f"Possible global tags matching this query :\n{rows}")
        else:
            await ctx.send("I didn't find any global tag matching this query")

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
