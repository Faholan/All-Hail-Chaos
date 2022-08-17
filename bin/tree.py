import discord
from discord import app_commands

from io import StringIO

import typing as t


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


OPTION_TYPES = {
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

    async def sync(self, *, guild: t.Optional[int] = None) -> None:
        """Synchronize the command Tree."""
        if guild:
            await self.client.log_channel.send(
                f"Synchronizing command tree for guild id {694804646086312026}..."
            )
        else:
            await self.client.log_channel.send("Synchronizing global command tree...")
        await super().sync(guild=guild)

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
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
            if isinstance(role, int):
                guild_role = interaction.guild.get_role(role)
                if guild_role is None:
                    role = str(role)
                else:
                    role = guild_role.name

            await self.client.httpcat(
                interaction,
                403,
                f"Sorry, but you need to have role {role} to use this command.",
            )
            return

        if isinstance(error, app_commands.MissingAnyRole):
            roles: t.List[str] = []
            for role in error.missing_roles:
                if isinstance(role, int):
                    guild_role = interaction.guild.get_role(role)
                    if guild_role is None:
                        role = str(role)
                    else:
                        role = guild_role.name
                roles.append(role)

            await self.client.httpcat(
                interaction,
                403,
                f"Sorry, but you need to have one of the following roles to use this command",
                "-" + "\n-".join(roles),
            )
            return

        if isinstance(error, app_commands.MissingPermissions):
            await self.client.httpcat(
                interaction,
                401,
                "Try again with the following permission(s)",
                "-" + "\n-".join(error.missing_perms),
            )
            return

        if isinstance(error, app_commands.BotMissingPermissions):
            await self.client.httpcat(
                interaction,
                401,
                "\n-".join(["I need these permissions :"] + error.missing_perms),
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
            error = error.original

        await self.client.httpcat(
            interaction,
            500,
            "Internal error",
            "An error ocurred while calling the command. Reporting the error to the developers...",
        )

        embed = discord.Embed(colour=0xFF0000)
        embed.set_author(
            name=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )
        embed.title = f"{interaction.user.id} caused an error in {interaction.command}"
        embed.description = f"{type(error).__name__} : {error}"

        if interaction.guild:
            embed.description += (
                f"\nin {interaction.guild} ({interaction.guild_id})\n   in {interaction.channel.name} "
                f"({interaction.channel_id})"
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
                    StringIO(f"{embed.title}\n\n{embed.description}"),
                    filename="error.md",
                )
            )
            # Send errors in files if they are too big
