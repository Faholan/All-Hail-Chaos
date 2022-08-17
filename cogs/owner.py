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

import io
import textwrap
import traceback
import typing as t
from contextlib import redirect_stdout

import discord
from discord.ext import commands


class OwnerError(commands.CheckFailure):
    """Error specific to this cog."""


class Owner(commands.Cog, command_attrs={"help": "Owner command"}):
    """Owner-specific commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Owner."""
        self.bot = bot
        self._last_result = None

    @staticmethod
    def cleanup_code(content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Decide if you can run the command."""
        if await ctx.bot.is_owner(ctx.author):
            return True
        raise OwnerError()

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Call that on error."""
        if isinstance(error, OwnerError):
            await ctx.send("Only my owner can use the command " + ctx.invoked_with)
            return
        raise error

    @commands.command(name="eval")
    async def _eval(self, ctx: commands.Context, *, body: str) -> None:
        """Evaluate a Python code."""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as error:
            await ctx.send(f"```py\n{error.__class__.__name__}: {error}\n```")
            return

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except discord.DiscordException:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")

    @commands.command()
    async def system(
        self,
        ctx: commands.Context,
        user: discord.User = None,
        *,
        message: str,
    ) -> None:
        """Make the bot send a message to the specified user."""
        if not user:
            await ctx.send("I couldn't find this user")
            return
        async with self.bot.pool.acquire() as database:
            result = await database.fetchrow(
                "SELECT * FROM block WHERE id=$1",
                user.id,
            )
            if result:
                await ctx.send("This user blocked me. Sorry")
                return
            embed = discord.Embed(
                title="Message from my owner",
                description=message,
                url=self.bot.support,
            )
            embed.set_author(
                name=f"{ctx.author.name}#{ctx.author.discriminator}",
                icon_url=str(ctx.author.avatar_url),
            )
            prefix = discord.utils.escape_markdown(
                await self.bot.get_m_prefix(ctx.message, False)
            )
            embed.set_footer(
                text=(
                    f"Use the command `{prefix}block` if you don't want me to"
                    " DM you anymore"
                ),
            )
            try:
                await user.send(
                    f"Use `{prefix}contact` to answer this message, or click "
                    "on the title to go to my support server",
                    embed=embed,
                )
            except discord.Forbidden:
                await ctx.send("This user blocked his DM. I can't message him")
            else:
                await ctx.send("DM successfully sent !")

    @commands.command(ignore_extra=True)
    async def logout(self, ctx: commands.Context) -> None:
        """Kill the bot."""
        await ctx.send("Logging out...")
        await self.bot.close()

    @commands.command(ignore_extra=True)
    async def load(self, ctx: commands.Context, *extensions) -> None:
        """Load an extension."""
        if not extensions:
            await ctx.send("Please specify at least one extension to unload")
            return
        total_ext = len(extensions)
        report = []
        success = 0
        for ext in extensions:
            try:
                try:
                    self.bot.reload_extension(ext)
                    report.append(f"✅ | **Extension reloaded** : `{ext}`")
                except commands.ExtensionNotLoaded:
                    self.bot.load_extension(ext)
                    report.append(f"✅ | **Extension loaded** : `{ext}`")
                success += 1
            except commands.ExtensionFailed as error:
                report.append(
                    f"❌ | **Extension error** : `{ext}` "
                    f"({type(error.original)} : {error.original})"
                )
            except commands.ExtensionNotFound:
                report.append(f"❌ | **Extension not found** : `{ext}`")
            except commands.NoEntryPointError:
                report.append(f"❌ | **setup not defined** : `{ext}`")

        failure = total_ext - success
        embed = discord.Embed(
            title=(
                f"{success} "
                f"{'extension was' if success == 1 else 'extensions were'} "
                f"loaded & {failure} "
                f"{'extension was' if failure == 1 else 'extensions were'}"
                " not loaded"
            ),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.bot.log_channel.send(embed=embed)
        await ctx.send(embed=embed)
        await ctx.bot.tree.sync()

    @commands.command()
    async def reload(self, ctx: commands.Context, *extensions) -> None:
        """Reload extensions."""
        report: t.List[str] = []
        success = 0

        if not extensions:
            extensions = self.extensions_list

        total_reload = len(extensions)

        for ext in extensions:
            if ext in extensions_list:
                try:
                    try:
                        await self.bot.reload_extension(ext)
                        success += 1
                        report.append(f"✅ | **Extension reloaded** : `{ext}`")
                    except commands.ExtensionNotLoaded:
                        await self.bot.load_extension(ext)
                        success += 1
                        report.append(f"✅ | **Extension loaded** : `{ext}`")
                except commands.ExtensionFailed as error:
                    report.append(
                        f"❌ | **Extension error** : `{ext}` "
                        f"({type(error.original)} : {error.original})"
                    )
                except commands.ExtensionNotFound:
                    report.append(f"❌ | **Extension not found** : `{ext}`")
                except commands.NoEntryPointError:
                    report.append(f"❌ | **setup not defined** : `{ext}`")
            else:
                report.append(f"❌ | `{ext}` is not a valid extension")

        not_loaded = total_reload - success
        embed = discord.Embed(
            title=(
                f"{success} "
                f"{'extension was' if success == 1 else 'extensions were'} "
                f"loaded & {total_reload - success} "
                f"{'extension was' if not_loaded == 1 else 'extensions were'}"
                " not loaded"
            ),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.bot.log_channel.send(embed=embed)
        await ctx.send(embed=embed)
        await ctx.bot.tree.sync()

    @commands.command()
    async def unload(self, ctx: commands.Context, *extensions) -> None:
        """Unload extensions."""
        if "cogs.owner" in extensions:
            await ctx.send("You shouldn't unload me")
            return
        if not extensions:
            await ctx.send("Please specify at least one extension to unload")
            return
        total_ext = len(extensions)
        report = []
        success = 0
        for ext in extensions:
            try:
                await self.bot.unload_extension(ext)
                success += 1
                report.append(f"✅ | **Extension unloaded** : `{ext}`")
            except commands.ExtensionNotLoaded:
                report.append(f"❌ | **Extension not loaded** : `{ext}`")

        failure = total_ext - success
        embed = discord.Embed(
            title=(
                f"{success} "
                f"{'extension was' if success == 1 else 'extensions were'} "
                f"unloaded & {failure} "
                f"{'extension was' if failure == 1 else 'extensions were'} "
                "not unloaded"
            ),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.bot.log_channel.send(embed=embed)
        await ctx.send(embed=embed)
        await ctx.bot.tree.sync()


async def setup(bot: commands.Bot) -> None:
    """Load the Owner cog."""
    await bot.add_cog(Owner(bot))
