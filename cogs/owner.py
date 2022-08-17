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
from discord import app_commands
from discord.ext import commands


class OwnerError(app_commands.CheckFailure):
    """Error specific to this cog."""


class Owner(commands.Cog):
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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Decide if you can run the command."""
        raise OwnerError()
        if await self.bot.is_owner(interaction.user):
            return True
        raise OwnerError()

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        """Catch the errors."""
        if isinstance(error, OwnerError):
            await self.bot.httpcat(
                interaction,
                400,
                "Only my owner can use the command "
                + interaction.command.qualified_name,
                ephemeral=True,
            )
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

    @app_commands.command()
    async def logout(self, interaction: discord.Interaction) -> None:
        """Kill the bot."""
        await interaction.response.send_message("Logging out...", ephemeral=True)
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
