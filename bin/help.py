"""MIT License.

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
SOFTWARE.
"""

from inspect import Parameter
import textwrap
import typing

import discord
from discord.ext import commands, menus
import discord.utils


class HelpSource(menus.ListPageSource):
    """The Help menu."""

    def __init__(
            self,
            signature: typing.Callable[[commands.Command], str],
            filter_commands: typing.Callable[
                [typing.List[commands.Command]],
                typing.Awaitable,
            ],
            prefix: str,
            author: discord.User,
            cogs: typing.Dict[commands.Cog, typing.List[commands.Command]],
    ) -> None:
        """Create the menu."""
        self.get_command_signature = signature
        self.filter_commands = filter_commands
        self.prefix = prefix
        self.menu_author = author
        super().__init__(
            [(cog, cogs[cog]) for cog in sorted(
                cogs,
                key=lambda cog: cog.qualified_name if cog else "ZZ"
            ) if cogs[cog] and [
                command for command in cogs[cog] if not command.hidden
            ]],
            per_page=1,
        )

    async def format_page(
            self,
            menu: menus.Menu,
            page: typing.Tuple[commands.Cog, typing.List[commands.Command]],
    ) -> discord.Embed:
        """Format the pages."""
        cog, command_list = page
        embed = discord.Embed(
            title=(
                "Help for "
                f"{cog.qualified_name if cog else 'unclassified commands'}"
            ),
            description=textwrap.dedent(
                f"""
                Help syntax : `<Required argument>`. `[Optional argument]`
                Command prefix: `{self.prefix}`
                {cog.description if cog else ""}
                """
            ),
            color=0xffff00,
        )
        embed.set_author(
            name=self.menu_author.display_name,
            icon_url=str(self.menu_author.avatar_url),
        )
        for command in await self.filter_commands(command_list):
            embed.add_field(
                name=f"{self.prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_footer(
            text=f"Page {menu.current_page+1}/{self.get_max_pages()}"
        )
        return embed


class Help(commands.HelpCommand):
    """The Help cog."""

    def get_command_signature(self, command: commands.Command) -> str:
        """Retrieve the command's signature."""
        basis = f"{command.qualified_name}"
        for arg in command.clean_params.values():
            if arg.kind in (Parameter.VAR_KEYWORD, Parameter.VAR_POSITIONAL):
                basis += f" [{arg.name}]"
            elif (
                hasattr(getattr(arg.annotation, "type", None), "__args__")
                and len(arg.annotation.__args__) == 2
                and isinstance(arg.annotation.__args__[-1], type(None))
            ):
                basis += f" [{arg.name} = None]"
            elif isinstance(arg.annotation, commands.converter._Greedy):
                basis += f" [{arg.name} = (...)]"
            elif arg.default == Parameter.empty:
                basis += f" <{arg.name}>"
            else:
                basis += f" [{arg.name} = {arg.default}]"
        return basis

    async def send_bot_help(
        self,
        mapping: typing.Dict[commands.Cog, typing.List[commands.Command]]
    ) -> None:
        """Send the global help."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(None, ctx.message, False),
        )
        pages = menus.MenuPages(
            source=HelpSource(
                self.get_command_signature,
                self.filter_commands,
                prefix,
                ctx.author,
                mapping,
            ),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """Send help for a cog."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(None, ctx.message, False),
        )
        embed = discord.Embed(
            title=cog.qualified_name,
            description=textwrap.dedent(
                f"""
                Help syntax : `<Required argument>`. `[Optional argument]`
                Command prefix: `{prefix}`
                {cog.description}
                """
            ),
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=str(ctx.message.author),
            icon_url=str(ctx.message.author.avatar_url),
        )
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        for command in await self.filter_commands(cog.get_commands()):
            embed.add_field(
                name=f"{prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_footer(
            text=f"Are you interested in {cog.qualified_name}?",
            icon_url=str(ctx.bot.user.avatar_url),
        )
        await ctx.send(embed=embed)

    async def send_command_help(self, command: commands.Command) -> None:
        """Send help for a command."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(None, ctx.message, False),
        )
        embed = discord.Embed(
            title=f"{prefix}{self.get_command_signature(command)}",
            description=(
                "Help syntax : `<Required argument>`. "
                f"`[Optional argument]`\n{command.help}"
            ),
            color=discord.Color.blue(),
        )
        if command.aliases:
            embed.add_field(name="Aliases :", value="\n".join(command.aliases))
        embed.set_author(
            name=str(ctx.message.author),
            icon_url=str(ctx.message.author.avatar_url),
        )
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        if command.hidden:
            embed.set_footer(
                text=f"Wow, you found {command.name}!",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        else:
            embed.set_footer(
                text=f"Are you interested in {command.name}?",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        await ctx.send(embed=embed)

    async def send_group_help(self, group: commands.Group) -> None:
        """Send help for a group."""
        ctx = self.context
        prefix = discord.utils.escape_markdown(
            await ctx.bot.get_m_prefix(None, ctx.message, False),
        )
        embed = discord.Embed(
            title=(
                f"Help for group {prefix}"
                f"{self.get_command_signature(group)}"
            ),
            description=(
                "Help syntax : `<Required argument>`. "
                f"`[Optional argument]`\n{group.help}"
            ),
            color=discord.Color.blue(),
        )
        for command in await self.filter_commands(group.commands, sort=True):
            embed.add_field(
                name=f"{prefix}{self.get_command_signature(command)}",
                value=command.help,
                inline=False,
            )
        embed.set_author(
            name=str(ctx.message.author),
            icon_url=str(ctx.message.author.avatar_url),
        )
        embed.set_thumbnail(url=str(ctx.bot.user.avatar_url))
        if group.hidden:
            embed.set_footer(
                text=f"Wow, you found {group.name}!",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        else:
            embed.set_footer(
                text=f"Are you interested in {group.name}?",
                icon_url=str(ctx.bot.user.avatar_url),
            )
        await ctx.send(embed=embed)

    async def send_error_message(self, error: str) -> None:
        """Send an error message."""
        await self.context.bot.httpcat(self.context, 404, error)


def setup(bot: commands.Bot) -> None:
    """Add the help command."""
    bot.old_help_command = bot.help_command
    bot.help_command = Help(
        verify_checks=False,
        command_attrs={'hidden': True},
    )


def teardown(bot: commands.Bot) -> None:
    """Remove the help command."""
    bot.help_command = bot.old_help_command
