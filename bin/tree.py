"""MIT License

Copyright (c) 2022 Faholan

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

from io import StringIO
import traceback
import typing as t

import discord
from discord import app_commands


def display_time(num_seconds: int) -> str:
    """Convert a number of seconds in human-readable format."""
    human_readable: t.List[str] = []
    if num_seconds >= 86400:
        human_readable.append(f"{num_seconds//86400} days")
        num_seconds %= 86400
    if num_seconds >= 3600:
        human_readable.append(f"{num_seconds//3600} hours")
        num_seconds %= 3600
    if num_seconds >= 60:
        human_readable.append(f"{num_seconds//60} minutes")
        num_seconds %= 60
    if num_seconds > 0:
        human_readable.append(f"{num_seconds} seconds")
    return ", ".join(human_readable)


OPTION_TYPES = {  # Convert the options into human readable format
    discord.AppCommandOptionType.subcommand: "a subcommand",
    discord.AppCommandOptionType.subcommand_group: "a subcommand group",
    discord.AppCommandOptionType.string: "a string",  # Wait, what ?
    discord.AppCommandOptionType.integer: "an integer",
    discord.AppCommandOptionType.boolean: "a boolean",
    discord.AppCommandOptionType.number: "a number",
    discord.AppCommandOptionType.user: "a Discord user",
    discord.AppCommandOptionType.channel: "a channel",
    discord.AppCommandOptionType.role: "a role",
    discord.AppCommandOptionType.mentionable: "a mention",
    discord.AppCommandOptionType.attachment: "an attached file",
}


class CommandTree(app_commands.CommandTree):
    """Custom command tree with error management."""

    async def sync(
        self, *, guild: t.Optional[discord.abc.Snowflake] = None
    ) -> t.List[app_commands.AppCommand]:
        """Synchronize the command Tree."""
        if guild:
            await self.client.log_channel.send(
                f"Synchronizing command tree for guild id {guild.id}..."
            )
        else:
            await self.client.log_channel.send("Synchronizing global command tree...")
        return await super().sync(guild=guild)

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Manage app command errors."""
        if isinstance(error, app_commands.TransformerError):
            await self.client.httpcat(
                interaction,
                406,
                f"Failed to convert {error.value} into {OPTION_TYPES[error.type]}",
            )
            return

        if isinstance(error, app_commands.NoPrivateMessage):
            await self.client.httpcat(
                interaction, 403, "You cannot use this command in a private channel."
            )
            return

        if isinstance(error, app_commands.MissingRole):
            role = error.missing_role
            if isinstance(role, int) and interaction.guild:
                guild_role = interaction.guild.get_role(role)
                if guild_role is not None:
                    role = guild_role.name

            await self.client.httpcat(
                interaction,
                403,
                f"Sorry, but you need to have role {role} to use this command.",
            )
            return

        if isinstance(error, app_commands.MissingAnyRole):
            roles: t.List[str] = []  # List of names of needed roles
            for role in error.missing_roles:
                if isinstance(role, int) and interaction.guild is not None:
                    guild_role = interaction.guild.get_role(role)
                    if guild_role is not None:
                        role = guild_role.name

                if isinstance(role, str):
                    roles.append(role)

            await self.client.httpcat(
                interaction,
                403,
                (
                    "Sorry, but you need to have one of "
                    "the following roles to use this command"
                ),
                "-" + "\n-".join(roles),
            )
            return

        if isinstance(error, app_commands.MissingPermissions):
            await self.client.httpcat(
                interaction,
                401,
                "Try again with the following permission(s)",
                "-" + "\n-".join(error.missing_permissions),
            )
            return

        if isinstance(error, app_commands.BotMissingPermissions):
            await self.client.httpcat(
                interaction,
                401,
                "\n-".join(["I need these permissions :"] + error.missing_permissions),
            )
            return

        if isinstance(error, app_commands.CommandOnCooldown):
            await self.client.httpcat(
                interaction,
                429,
                (
                    "Calm down, breath and try again in "
                    f"{display_time(round(error.retry_after))}"
                ),
            )
            return

        if isinstance(error, app_commands.CheckFailure):
            await self.client.httpcat(
                interaction,
                401,
                "You don't have the rights to use this command",
            )
            return

        if isinstance(error, app_commands.CommandSignatureMismatch):
            await self.client.httpcat(
                interaction, 502, "Outdated command. Updating command list..."
            )
            await self.client.tree.sync()
            if interaction.guild:
                await self.client.tree.sync(interaction.guild)
            return

        if isinstance(error, app_commands.CommandNotFound):
            await self.client.httpcat(
                interaction, 404, "Command not found. Updating command list..."
            )
            await self.client.tree.sync()
            if interaction.guild:
                await self.client.tree.sync(interaction.guild)
            return

        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original  # type: ignore

        await self.client.httpcat(
            interaction,
            500,
            "Internal error",
            (
                "An error ocurred while calling the command. "
                "Reporting the error to the developers..."
            ),
        )

        # Send the errors into the log channel
        embed = discord.Embed(colour=0xFF0000)
        embed.set_author(
            name=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )
        embed.title = f"{interaction.user.id} caused an error in {interaction.command}"
        embed.description = f"{type(error).__name__} : {error}"

        if (
            interaction.guild
            and interaction.channel
            and not isinstance(interaction.channel, discord.PartialMessageable)
        ):  # Correct typehints - in a guild
            embed.description += (
                f"\nin {interaction.guild} ({interaction.guild_id})"
                f"\n   in {interaction.channel.name} ({interaction.channel_id})"
            )
        else:
            embed.description += f"\nin a Private Channel ({interaction.channel_id})"

        formatted_traceback = "".join(traceback.format_tb(error.__traceback__))
        embed.description += f"```\n{formatted_traceback}```"
        embed.set_footer(
            text=f"{self.client.user.name} Logging",
            icon_url=self.client.user.display_avatar.url,
        )
        embed.timestamp = discord.utils.utcnow()
        try:
            await self.client.log_channel.send(embed=embed)
        except discord.DiscordException:
            await self.client.log_channel.send(
                file=discord.File(
                    StringIO(f"{embed.title}\n\n{embed.description}"),  # type: ignore
                    # Sneaky way of sending the file content
                    filename="error.md",
                )
            )
            # Send errors in files if they are too big
