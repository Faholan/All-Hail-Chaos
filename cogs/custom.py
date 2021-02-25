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
import re

import discord
from discord.ext import commands
from pytz import utc


class Custom(commands.Cog):
    """Create your own commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Custom."""
        self.bot = bot
        self.type_name = {"user": "member", "server": "guild"}
        self.type_dict = {
            "member": commands.MemberConverter,
            "channel": commands.TextChannelConverter,
            "role": commands.RoleConverter,
            "int": int,
        }

    def cog_check(self, ctx: commands.Context) -> bool:
        """Use these commands in a guild."""
        if ctx.guild:
            return True
        raise commands.NoPrivateMessage("These commands are guild only")

    @commands.group(invoke_without_command=True)
    async def custom(self, ctx: commands.Context) -> None:
        """Set of commands for creating custom commands."""
        await ctx.send_help("custom")

    @custom.command()
    async def create(self, ctx: commands.Context) -> None:
        """Interactively create a custom command."""

        def check(message: discord.Message) -> bool:
            """Check author and channel."""
            if message.author == ctx.author:
                return message.channel == ctx.channel
            return False

        await ctx.send("What will be the command's name ?")
        try:
            name = await self.bot.wait_for("message", check=check)
            name = name.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply. I'm aborting this")
            return

        if " " in name:
            await ctx.send(
                ":x: Well tried, but custom command names can't include spaces"
            )
            return

        if name in self.bot.all_commands:
            await ctx.send(":x: Sorry, but a bot command already exists with this name")
            return

        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.custom WHERE name=$1 AND guild_id=$2",
                name,
                ctx.guild.id,
            )
            if row:
                await ctx.send(f"A custom command named {name} already exists")
                return

        await ctx.send(
            f"So the name's {name}. What about the description "
            "(enter * to skip this)"
        )
        try:
            description = await self.bot.wait_for("message", check=check)
            description = description.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply. I'm aborting this")
            return

        if description == "*":
            description = None

        await ctx.send(
            "What arguments will this command take (separate them with spaces)"
            " ? You can annotate them using {name}:{type}\n"
            "The types currently supported are : int, Role, Member, Channel, "
            "str (the default type)"
        )

        try:
            args = await self.bot.wait_for("message", check=check)
            args = args.content.split(" ")
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply. I'm aborting this")
            return

        arguments = []

        for raw_arg in args:
            if raw_arg.count(":") > 1:
                await ctx.send(
                    "An argument can contain only up to 1 time `:`. "
                    f"This is wrong : {raw_arg}"
                )
                return
            if raw_arg.count(":") == 1:
                raw_name, raw_type = raw_arg.split(":")
            else:
                raw_name = raw_arg
                raw_type = "str"

            if not re.fullmatch("[A-Za-z_][A-Za-z0-9_]+", raw_name):
                await ctx.send(f"{raw_name} isn't a valid argument name")
                return

            raw_type = self.type_name.get(raw_type.lower(), raw_type.lower())

            if raw_type not in self.type_dict:
                raw_type = "str"

            arguments.append([raw_name, raw_type])

        await ctx.send("Okay, now what will this command return ?")
        try:
            effect = await self.bot.wait_for("message", check=check)
            effect = effect.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply. I'm aborting this")
            return

        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.custom WHERE guild_id=$1 AND name=$2",
                ctx.guild.id,
                name,
            )
            if row:
                await ctx.send(f":x: There is already a custom command named {name}")
                return
            await database.execute(
                "INSERT INTO public.custom VALUES ($1, $2, $3, $4, $5, $6)",
                ctx.guild.id,
                ctx.author.id,
                name,
                description,
                arguments,
                effect,
            )
        await ctx.send(f"Custom command {name} created successfully")

    @custom.command()
    async def delete(self, ctx: commands.Context, name: str) -> None:
        """Delete a custom command that you own."""
        async with self.bot.pool.acquire() as database:
            row = await database.fetchrow(
                "SELECT * FROM public.custom WHERE name=$1 AND guild_id=$2"
                " AND owner_id=$3",
                name,
                ctx.guild.id,
                ctx.author.id,
            )
            if not row:
                await ctx.send(
                    f"I didn't find any command named {name}. Are you sure "
                    "that it exists and you own it ?"
                )
                return
            await database.execute(
                "DELETE FROM public.custom WHERE name=$1 AND guild_id=$2 "
                "AND owner_id=$3",
                name,
                ctx.guild.id,
                ctx.author.id,
            )
        await ctx.send(f"Custom command {name} successfully deleted")

    @custom.command()
    async def info(self, ctx: commands.Context, name: str) -> None:
        """Retrieve information about a custom command."""
        async with self.bot.pool.acquire() as database:
            command = await database.fetchrow(
                "SELECT * FROM public.custom WHERE name=$1 AND guild_id=$2",
                name,
                ctx.guild.id,
            )
        if not command:
            await ctx.send(f"No custom command named {name} found in your guild")
            return
        embed = discord.Embed(
            title=f"Informations about custom command {name}",
            description=command["description"]
            if command["description"]
            else (discord.Embed.Empty),
            colour=0x00008B,
        )
        try:
            owner = ctx.guild.get_member(command["owner_id"]) or (
                await ctx.guild.fetch_member(command["owner_id"])
            )
            embed.set_author(
                name=owner.display_name,
                icon_url=str(owner.avatar_url),
            )
        except discord.NotFound:
            embed.set_author(
                name="Unclaimed command",
                icon_url=str(ctx.bot.user.avatar_url),
            )

        embed.timestamp = command["created_at"].astimezone(utc)
        await ctx.send(embed=embed)

    @commands.Cog.listener("on_message")
    async def custom_invoke(self, message: discord.Message) -> None:
        """Invoke the custom command."""
        prefix = await self.bot.get_prefix(message)

        if not message.content.startswith(prefix) or not message.guild:
            return

        async with self.bot.pool.acquire() as database:
            command = await database.fetchrow(
                "SELECT * FROM public.custom WHERE guild_id=$1 AND name=$2",
                message.guild.id,
                message.content[len(prefix):].split(" ")[0],
            )
            if not command:
                return

        effect = command["effect"]
        full_args = command["arguments"]

        kwargs = {}
        args = message.content.split(" ")[1:]
        arg_n = 0

        ctx = await self.bot.get_context(message)

        try:
            for name, raw_type in full_args:
                arg = args[arg_n]
                arg_n += 1
                converter = self.type_dict.get(raw_type, str)
                if converter in {str, int}:
                    kwargs[name] = converter(arg)
                else:
                    kwargs[name] = await converter().convert(ctx, arg)
        except ValueError:
            await message.channel.send(f"Couldn't convert {arg} to int")
            return
        except IndexError:
            await message.channel.send("You didn't provide enough arguments")
            return
        except commands.BadArgument:
            await message.channel.send(
                f"Couldn't convert {arg} into {raw_type.capitalize()}"
            )
            return

        try:
            await message.channel.send(
                effect.format(
                    author=message.author,
                    guild=message.guild,
                    server=message.guild,
                    message=message.content,
                    **kwargs,
                )
            )
        except ValueError:
            try:
                owner = self.bot.get_user(command["owner_id"]) or (
                    await self.bot.fetch_user(command["owner_id"])
                )
                await message.channel.send(
                    "The custom command isn't correctly formatted. Please "
                    f"contact {owner.mention} about that issue"
                )
            except discord.NotFound:
                await message.channel.send("The custom command raised an error")
        except (discord.DiscordException, KeyError):
            try:
                owner = self.bot.get_user(command["owner_id"]) or (
                    await self.bot.fetch_user(command["owner_id"])
                )
                await message.channel.send(
                    "The custom command raised an error. Please contact "
                    f"{owner.mention} about that issue"
                )
            except discord.NotFound:
                await message.channel.send("The custom command raised an error")


def setup(bot: commands.Bot) -> None:
    """Load the Custom cog."""
    bot.add_cog(Custom(bot))
