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
from pytz import utc

import discord
from discord.ext import commands

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

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tags_being_made = {}

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

def setup(bot):
    bot.add_cog(Tags(bot))
