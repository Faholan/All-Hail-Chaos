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
from discord import app_commands, ui
from discord.ext import commands


class OwnerError(app_commands.CheckFailure):
    """Error specific to this cog."""


class EvalInput(ui.Modal, title="Code input"):
    """Modal to input code."""

    code = ui.TextInput(label="Code", style=discord.TextStyle.paragraph)


class ExtensionSelector(ui.Modal, title="Extensions selector"):

    extensions = ui.Select()

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the selector."""
        super().__init__()
        for extension in bot.extensions_list:
            self.add_option(label=extension)

        self.max_values = len(bot.extensions_list)


class Owner(commands.Cog):
    """Owner-specific commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Owner."""
        self.bot = bot
        self._last_result = None

    async def cog_load(self) -> None:
        """Sync the custom commands."""
        await self.bot.tree.sync(694804646086312026)

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

    @app_commands.command(name="eval")
    @app_commands.guilds(694804646086312026)
    async def _eval(self, interaction: discord.Interaction) -> None:
        """Evaluate a Python code."""
        modal = EvalInput()
        await interaction.response.send_modal(modal)
        if await modal.wait():
            return
        body = modal.code.value

        env = {
            "bot": self.bot,
            "interaction": interaction,
            "channel": interaction.channel,
            "author": interaction.author,
            "guild": interaction.guild,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as error:
            await interaction.followup.send(
                f"```py\n{error.__class__.__name__}: {error}\n```"
            )
            return

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await interaction.followup.send(
                f"```py\n{value}{traceback.format_exc()}\n```"
            )
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await interaction.followup.send(f"```py\n{value}\n```")
                else:
                    await interaction.followup.send(
                        "Executed successfully", ephemeral=True
                    )
            else:
                self._last_result = ret
                await interaction.followup.send(f"```py\n{value}{ret}\n```")

    @app_commands.command()
    @app_commands.guilds(694804646086312026)
    async def logout(self, interaction: discord.Interaction) -> None:
        """Kill the bot."""
        await interaction.response.send_message("Logging out...", ephemeral=True)
        await self.bot.close()

    @app_commands.command()
    @app_commands.rename(reload_all="all")
    @app_commands.guilds(694804646086312026)
    async def reload(
        self, interaction: discord.Interaction, reload_all: bool = False
    ) -> None:
        """Reload extensions."""
        report: t.List[str] = []
        success = 0

        if reload_all:
            extensions = self.bot.extensions_list
            await interaction.defer(thinking=True)
        elif len(self.bot.extensions_list) > 25:
            await interaction.response.send_message("Too many extensions for a modal")
            return
        else:
            modal = ExtensionSelector(self.bot)
            await interaction.response.send_modal(modal)
            if await modal.wait():
                return  # Modal timed out
            extensions = modal.extensions.values

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
        await interaction.followup.send(embed=embed)
        await self.bot.tree.sync()


async def setup(bot: commands.Bot) -> None:
    """Load the Owner cog."""
    await bot.add_cog(Owner(bot))
