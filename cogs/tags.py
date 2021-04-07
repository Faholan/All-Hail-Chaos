"""MIT License.

Copyright (c) 2020-2021 Faholan

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
SOFTWARE.
"""

import asyncio

import discord
from discord.ext import commands
from pytz import utc


class TagName(commands.clean_content):
    """Converter for tag name."""

    def __init__(self, *, lower=False) -> None:
        """Initialize the converter."""
        self.lower = lower
        super().__init__()

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        """Convert to tag name."""
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            raise commands.BadArgument("Missing tag name.")

        if len(lower) > 100:
            raise commands.BadArgument(
                "Tag name is a maximum of 100 characters.")

        first_word, _, _ = lower.partition(" ")

        # get tag command.
        root = ctx.bot.get_command("tag")
        if first_word in root.all_commands:
            raise commands.BadArgument(
                "This tag name starts with a reserved word.")

        return converted if not self.lower else lower


class Tags(commands.Cog):
    """Tag system."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Tags."""
        self.bot = bot
        self.tags_being_made = {}

    def check_tag(self, name: str, guild: int, author: int) -> bool:
        """Check that the tag isn't being made."""
        tag_author = self.tags_being_made.get((guild, name))
        return not tag_author or tag_author == author

    async def search_tag(self, name: str, location_id: int, database) -> str:
        """Search for a tag."""
        rows = await database.fetch(
            "SELECT name FROM public.tag_lookup WHERE location_id=$1 AND name "
            "% $2 ORDER BY similarity(name, $2) DESC LIMIT 3",
            location_id,
            name,
        )
        return "\n".join([row["name"] for row in rows])

    @commands.group(invoke_without_command=True, aliases=["t"])
    @commands.guild_only()
    async def tag(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Tag some text to retrieve it later."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            if not row:
                rows = await self.search_tag(name, location_id, database)
                if rows:
                    await ctx.send(f"Tag not found. Did you mean :\n{rows}")
                    return
                await ctx.send("Tag not found")
                return
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE id=$1",
                row["tag_id"],
            )
            if not tag:
                await ctx.send("Tag not found")
                await self.delete_aliases(row["tag_id"], database)
                return
            await database.execute(
                "UPDATE public.tags SET use_count=use_count+1 WHERE id=$1",
                tag["id"],
            )
            await database.execute(
                "UPDATE public.tag_lookup SET use_count=use_count+1 WHERE "
                "name=$1 AND location_id=$2",
                name,
                location_id,
            )
        await ctx.send(tag["content"])

    async def create_tag(
        self,
        ctx: commands.Context,
        name: str,
        content: str,
        location_id: int = None,
    ) -> None:
        """Create a tag."""
        if location_id is None:
            location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            if row:
                await ctx.send("A tag already exists with that name")
                return
            await database.execute(
                "INSERT INTO public.tags VALUES ($1, $2, $3, $4)",
                location_id,
                ctx.author.id,
                name,
                content,
            )
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            await database.execute(
                "INSERT INTO public.tag_lookup VALUES ($1, $2, $3, $4)",
                name,
                location_id,
                ctx.author.id,
                tag["id"],
            )

    async def delete_aliases(self, tag_id: int, database) -> None:
        """Delete all aliases of a tag."""
        await database.execute(
            "DELETE FROM public.tag_lookup WHERE tag_id=$1",
            tag_id,
        )

    @tag.command(name="alias")
    @commands.guild_only()
    async def tag_alias(
        self,
        ctx: commands.Context,
        name: TagName(lower=True),
        *,
        alias: TagName(lower=True),
    ) -> None:
        """Create an alias to a tag under which it can be retrieved."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE location_id=$1 and name=$2",
                location_id,
                name,
            )
            if not row:
                await ctx.send(f"No tag named {name} found")
                return
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE id=$1",
                row["tag_id"],
            )
            if not tag:
                await ctx.send(f"No tag named {name} found")
                await self.delete_aliases(row["tag_id"], database)
                return
            existing_alias = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE location_id=$1 and name=$2",
                location_id,
                alias,
            )
            if existing_alias:
                await ctx.send(f"An alias named {alias} already exists")
                return
            await database.execute(
                "INSERT INTO public.tag_lookup VALUES ($1, $2, $3, $4)",
                alias,
                location_id,
                ctx.author.id,
                row["tag_id"],
            )
            await ctx.send(f"Alias {alias} for tag {tag['name']} created successfully")

    @tag.command(name="claim")
    @commands.guild_only()
    async def tag_claim(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Become the owner of an unclaimed tag."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            alias = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            if not alias:
                await ctx.send(f"No tag or alias named {name} found")
                return
            try:
                owner = ctx.guild.get_member(
                    alias["owner_id"]
                ) or await ctx.guild.fetch_member(alias["owner_id"])
            except discord.NotFound:
                owner = None

            if owner:
                await ctx.send(
                    f"{name} isn't unclaimed : {owner} has claimed it"
                )
                return

            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE id=$1",
                alias["tag_id"],
            )
            if not tag:
                await ctx.send(f"No tag or alias named {name} found")
                await self.delete_aliases(alias["tag_id"], database)
                return

            try:
                owner = ctx.guild.get_member(
                    tag["owner_id"]
                ) or await ctx.guild.fetch_member(tag["owner_id"])
            except discord.NotFound:
                owner = None

            await database.execute(
                "UPDATE public.tag_lookup SET owner_id=$1 WHERE name=$2 AND "
                "location_id=$3",
                ctx.author.id,
                name,
                location_id,
            )
            if owner is None:
                await database.execute(
                    "UPDATE public.tags SET owner_id=$1 WHERE id=$2",
                    ctx.author.id,
                    tag["id"],
                )
                waswere = f"and alias {name} were" if name != tag["name"] else "was"
                await ctx.send(
                    f"Tag {tag['name']} " f"{waswere} successfully claimed"
                )
                return
            await ctx.send(f"Alias {name} successfully claimed")

    @tag.command(name="create")
    @commands.guild_only()
    async def tag_create(
        self,
        ctx: commands.Context,
        name: TagName(lower=True),
        *,
        content: str,
    ) -> None:
        """Create a tag with the given name and content."""
        location_id = self.bot.get_id(ctx)
        if not self.check_tag(name, location_id, ctx.author.id):
            await ctx.send("Someone is already making a tag with this name")
            return
        self.tags_being_made[(location_id, name)] = ctx.author.id
        await self.create_tag(ctx, name, content)
        await ctx.send(f"Tag {name} created successfully")
        del self.tags_being_made[(location_id, name)]

    @tag.command(name="delete", aliases=["remove"])
    @commands.guild_only()
    async def tag_delete(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Use this to delete a tag."""
        override = ctx.author.id == self.bot.owner_id or (
            ctx.author.guild_permissions.manage_messages if ctx.guild else (
                False)
        )
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            if override:
                alias = await database.fetchrow(
                    "SELECT * FROM public.tag_lookup WHERE location_id=$1 "
                    "AND name=$2",
                    location_id,
                    name,
                )
            else:
                alias = await database.fetchrow(
                    "SELECT * FROM public.tag_lookup WHERE location_id=$1 "
                    "AND name=$2 AND owner_id=$3",
                    location_id,
                    name,
                    ctx.author.id,
                )
            if not alias:
                await ctx.send(
                    f"No tag or alias named {name} found. Are you sure that "
                    "it exists and that you own it ?"
                )
                return
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE id=$1",
                alias["tag_id"],
            )
            if not tag:
                await ctx.send(
                    f"No tag or alias named {name} found. Are you sure that "
                    "it exists and that you own it ?",
                )
                await self.delete_aliases(alias["tag_id"], database)
                return
            if tag["name"] == alias["name"]:
                await ctx.send(
                    f"Tag {name} and associated aliases successfully deleted"
                )
                await database.execute(
                    "DELETE FROM public.tags WHERE id=$1",
                    tag["id"],
                )
                await self.delete_aliases(tag["id"], database)
            else:
                await ctx.send(f"Alias {tag} deleted successfully")
                await database.execute(
                    "DELETE FROM public.tag_lookup WHERE location_id=$1 AND name=$2",
                    location_id,
                    alias["name"],
                )

    @tag.command(name="info")
    @commands.guild_only()
    async def tag_info(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Retrieve information about a tag."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            if not row:
                await ctx.send(f"No tag named {name} found")
                return
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE id=$1",
                row["tag_id"],
            )
            if not tag:
                await ctx.send(f"No tag named {name} found")
                await self.delete_aliases(row["tag_id"], database)
                return

            aliases = await database.fetch(
                "SELECT * FROM public.tag_lookup WHERE tag_id=$1",
                row["tag_id"],
            )

        embed = discord.Embed(
            title=f"Informations about tag {tag['name']}",
            colour=discord.Color.blue(),
        )
        try:
            owner = ctx.guild.get_member(
                tag["owner_id"]
            ) or await ctx.guild.fetch_member(tag["owner_id"])
        except discord.NotFound:
            owner = None
        embed.add_field(
            name="Owner :",
            value=f"{owner.mention if owner else 'Unclaimed'}",
        )
        embed.add_field(name="Usages :", value=tag["use_count"])
        if len(aliases) > 1:
            alias_content = []
            for alias in aliases:
                if alias["name"] != tag["name"]:
                    try:
                        owner = ctx.guild.get_member(
                            alias["owner_id"]
                        ) or await ctx.guild.fetch_member(alias["owner_id"])
                    except discord.NotFound:
                        owner = None
                    alias_content.append(
                        f"{alias['name']} : "
                        f"{owner.mention if owner else 'Unclaimed'}"
                    )
            embed.add_field(name="Aliases :", value="\n".join(alias_content))
        if name != tag["name"]:
            embed.set_footer(text="Alias created at :")
        else:
            embed.set_footer(text="Tag created at :")
        embed.timestamp = row["created_at"].astimezone(utc)
        await ctx.send(embed=embed)

    @tag.command(name="make")
    @commands.guild_only()
    async def tag_make(self, ctx: commands.Context) -> None:
        """Make a tag interactively."""
        location_id = self.bot.get_id(ctx)
        await ctx.send("Okay, what will the tag's name be ?")

        def check(message: discord.Message) -> bool:
            """Check the author."""
            return message.author == ctx.author and (message.channel == ctx.channel)

        try:
            name = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to answer. Cancelling.")
            return

        original = ctx.message
        converter = TagName()
        try:
            ctx.message = name
            name = await converter.convert(ctx, name.content)
        except commands.BadArgument as error:
            await ctx.send(
                f'{error}. Redo the command "{ctx.prefix}tag make" to retry.'
            )
            return
        finally:
            ctx.message = original

        if not self.check_tag(name, location_id, ctx.author.id):
            await ctx.send(
                "Someone is already making a tag with that name. Try again later."
            )
            return

        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            if row:
                await ctx.send(
                    "A tag, or an alias to a tag, already exists with that name"
                )
                return

        self.tags_being_made[(location_id, name)] = ctx.author.id

        await ctx.send(
            f"Okay, the tag's name is {name}. What will be its content?\nYou "
            f"can type `{ctx.prefix}abort` to escape this process"
        )
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            del self.tags_being_made[(location_id, name)]
            await ctx.send("You took too long. I'm canelling this")
            return

        content = msg.content
        if content == f"{ctx.prefix}abort":
            del self.tags_being_made[(location_id, name)]
            await ctx.send("Aborted")
            return
        clean_content = await commands.clean_content().convert(ctx, content)
        if msg.attachments:
            clean_content += f"\n{msg.attachments[0].url}"
        await ctx.send(f"Tag {name} created successfully")
        await self.create_tag(ctx, name, clean_content)
        del self.tags_being_made[(location_id, name)]

    @tag.command(name="purge")
    @commands.has_guild_permissions(manage_messages=True)
    async def tag_purge(
        self,
        ctx: discord.Member,
        member: discord.Member,
    ) -> None:
        """Delete all local tags made by a user."""
        location_id = self.bot.get_id(ctx)
        counter = 0
        async with self.bot.pool.acquire() as database:
            for tag in await database.fetch(
                "SELECT * FROM public.tags WHERE owner_id=$1 AND location_id=$2",
                member.id,
                location_id,
            ):
                counter += 1
                await database.execute(
                    "DELETE FROM public.tags WHERE id=$1",
                    tag["id"],
                )
                await self.delete_aliases(tag["id"], database)
        await ctx.send(
            f"{counter} tag{'s' if counter > 1 else ''} owned by "
            f"{member.mention} {'were' if counter > 1 else 'was'} deleted"
            if counter
            else f"{member} hasn't created any tag"
        )

    @tag.command(name="search")
    @commands.guild_only()
    async def tag_search(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Search for a tag."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            rows = await self.search_tag(name, location_id, database)
        if rows:
            await ctx.send(f"Possible tags matching this query :\n{rows}")
        else:
            await ctx.send("I didn't find any tag matching this query")

    @tag.command(name="transfer", aliases=["give"])
    @commands.guild_only()
    async def tag_transfer(
        self,
        ctx: commands.Context,
        name: TagName(lower=True),
        *,
        member: discord.Member,
    ) -> None:
        """Transfer a tag, or alias, you own to a new user."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            alias = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND "
                "location_id=$2 AND owner_id=$3",
                name,
                location_id,
                ctx.author.id,
            )
            if not alias:
                await ctx.send(
                    f"No tag or alias named {name} found. Are  you sure that"
                    " it exists and you own it ?"
                )
                return

            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE name=$1 AND owner_id=$2 AND "
                "location_id=$3",
                name,
                ctx.author.id,
                location_id,
            )
            await database.execute(
                "UPDATE public.tag_lookup SET owner_id=$1 WHERE name=$2 AND "
                "location_id=$3",
                member.id,
                name,
                location_id,
            )
            if tag:
                await database.execute(
                    "UPDATE public.tags SET owner_id=$1 WHERE name=$2 AND "
                    "location_id=$3",
                    member.id,
                    name,
                    location_id,
                )
                await ctx.send("Tag successfully transferred")
                return
            await ctx.send("Alias successfully transferred")

    @tag.group(name="global", invoke_without_command=True)
    @commands.guild_only()
    async def tag_global(self, ctx: commands.Context) -> None:
        """Run a command about a gglobal tag."""
        await ctx.send_help("tag global")

    @tag_global.command(name="put")
    @commands.guild_only()
    async def global_put(
        self,
        ctx: commands.Context,
        *,
        alias: TagName(lower=True),
    ) -> None:
        """Make a tag global. Only the owner of the tag can use this."""
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            aliasrow = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND owner_id=$2"
                " AND location_id=$3",
                alias,
                ctx.author.id,
                location_id,
            )
            if not aliasrow:
                await ctx.send(
                    f"I didn't find any tag with the name {alias}. Are you "
                    "sure that it exists and that you own it ?"
                )
                return
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE id=$1 AND owner_id=$2",
                aliasrow["tag_id"],
                ctx.author.id,
            )
            if not tag:
                await ctx.send(
                    f"I didn't find any tag with the name {alias}. "
                    "Are you sure that it exists and that you own it ?"
                )
                return
            already_existing = await database.fetchrow(
                "SELECT * FROM public.tags WHERE name=$1 AND location_id=0",
                alias,
            )
            if already_existing:
                await ctx.send(
                    "A global tag with that name already exists. Try creating "
                    "an alias to your tag and globalizing it under this name"
                )
                return
            await self.create_tag(ctx, alias, tag["content"], 0)
        await ctx.send(f"Global tag {alias} created successfully")

    @tag_global.command(name="delete", aliases=["remove"])
    @commands.guild_only()
    async def global_delete(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Remove a tag from the global database.

        This has no effect on local versions of this tag
        You must be the tag's owner to use that
        """
        async with self.bot.pool.acquire() as database:
            aliasrow = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND "
                "owner_id=$2 AND location_id=0",
                name,
                ctx.author.id,
            )
            if not aliasrow:
                await ctx.send(
                    f"No global tag named {name} found. Are you sure that it "
                    "exists and you own it ?"
                )
                return
            await database.execute(
                "DELETE FROM public.tags WHERE id=$1",
                aliasrow["tag_id"],
            )
            await ctx.send(f"Global tag {name} deleted succesfully")
            await self.delete_aliases(aliasrow["tag_id"], database)

    @tag_global.command(name="retrieve")
    @commands.guild_only()
    async def global_retrieve(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Retrieve a tag from the global database."""
        alias = name
        location_id = self.bot.get_id(ctx)
        async with self.bot.pool.acquire() as database:
            tag = await database.fetchrow(
                "SELECT * FROM public.tags WHERE name=$1 AND location_id=0",
                name,
            )
            if not tag:
                rows = await self.search_tag(name, 0, database)
                if rows:
                    await ctx.send(f"Global tag not found. Did you mean\n{rows}")
                    return
                await ctx.send(f"No global tag named {name} found")
                return
            await database.execute(
                "UPDATE public.tags SET use_count=use_count+1 WHERE id=$1",
                tag["id"],
            )
            already_exists = await database.fetchrow(
                "SELECT * FROM public.tag_lookup WHERE name=$1 AND location_id=$2",
                name,
                location_id,
            )
            if already_exists:
                await ctx.send(
                    "A local tag with this name already exists. "
                    "Please enter a new name under which I shall save this tag"
                    f".\nEnter **{ctx.prefix}abort** to quit"
                )

                def check(message: discord.Message) -> bool:
                    """Check the author."""
                    return message.channel == ctx.channel and (
                        message.author == ctx.author
                    )

                try:
                    alias = await self.bot.wait_for(
                        "message",
                        check=check,
                        timeout=300,
                    )
                except asyncio.TimeoutError:
                    await ctx.send("You didn't reply in time. Aborting")
                    return

                converter = TagName()
                original = ctx.message

                try:
                    ctx.message = alias
                    alias = await converter.convert(ctx, alias.content)
                except commands.BadArgument as error:
                    await ctx.send(
                        f'{error}. Redo the command "{ctx.prefix}tag global '
                        'retrieve" to retry.'
                    )
                    return
                finally:
                    ctx.message = original

                if not self.check_tag(alias, ctx.guild.id, ctx.author.id):
                    await ctx.send(
                        "Someone is already making a tag with that name. Sorry"
                    )
                    return

                already_exists = await database.fetchrow(
                    "SELECT * FROM public.tag_lookup WHERE name=$1 AND "
                    "location_id=$2",
                    alias,
                    location_id,
                )
                if already_exists:
                    await ctx.send(
                        "A tag with that name already exists. Aborting"
                    )
                    return

            await self.create_tag(ctx, alias, tag["content"])
            await ctx.send(f"Tag {alias} created successfully")

    @tag_global.command(name="search")
    @commands.guild_only()
    async def global_search(
        self,
        ctx: commands.Context,
        *,
        name: TagName(lower=True),
    ) -> None:
        """Search for a global tag."""
        async with self.bot.pool.acquire() as database:
            rows = await self.search_tag(name, 0, database)
        if rows:
            await ctx.send(f"Possible global tags matching this query :\n{rows}")
        else:
            await ctx.send("I didn't find any global tag matching this query")


def setup(bot):
    """Load the Tags cog."""
    bot.add_cog(Tags(bot))
