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

import typing as t
import importlib.util
import sys


import toml
import aiohttp
import psycopg_pool
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

import discord
from discord import app_commands
from discord.ext import commands


class ChaoticBot(commands.Bot):
    """The subclassed bot class."""

    def __init__(self, configpath: str = "data/config.toml") -> None:
        """Initialize the bot."""
        with open(configpath, "r", encoding="utf-8") as file:
            config = toml.load(file)

        if "bot" not in config:
            raise ValueError("No bot section in config")

        self.token: str = config["bot"].get("token", "")
        self.log_channel_id: int = config["bot"].get("log_channel_id", 0)
        self.suggestion_channel_id: int = config["bot"].get("suggestion_channel_id", 0)
        self.extensions_list: t.List[str] = config["bot"].get("extensions", [])
        self.support: t.Optional[str] = config["bot"].get("support")
        self.privacy: t.Optional[str] = config["bot"].get("privacy")
        self.invite_permissions: int = config["bot"].get("invite_permissions", 0)

        self.github_link: str = config.get("github", {}).get("link", "")

        parameters = config.get("database", {})
        if "type" in parameters:
            parameters.pop("type")

        self.pool = psycopg_pool.AsyncConnectionPool(
            make_conninfo(**parameters),
            open=False,
            # row_factory=dict_row,
        )

        intents = discord.Intents(**config.get("intents", {}))

        tree_location: t.Dict[str, str] = config["bot"].get("command_tree")
        if tree_location is not None:
            if not isinstance(tree_location, dict):
                raise ValueError("Tree location must be a table")
            if "module_name" not in tree_location:
                raise ValueError("Invalid tree location (no module name specified)")
            if "class_name" not in tree_location:
                raise ValueError("Invalid tree location (no class name specified)")

            module_name = tree_location["module_name"]
            class_name = tree_location["class_name"]
            package = tree_location.get("package")

            if (
                not isinstance(module_name, str)
                or not isinstance(class_name, str)
                or not (isinstance(package, str) or package is None)
            ):
                raise ValueError(
                    "Invalid tree location (module_name, class_name and package must be strings)"
                )

            name = importlib.util.resolve_name(
                module_name, tree_location.get("package", None)
            )
            spec = importlib.util.find_spec(name)

            if spec is None:
                raise ValueError("Couldn't find the command tree module.")

            lib = importlib.util.module_from_spec(spec)
            sys.modules[name] = lib

            try:
                spec.loader.exec_module(lib)
            except Exception:
                del sys.modules[name]
                raise

            try:
                tree_cls = getattr(lib, tree_location["class_name"])
            except AttributeError:
                raise ValueError(
                    f"No class {tree_location['class_name']} in module {name}"
                ) from None

            if not issubclass(tree_cls, app_commands.CommandTree):
                raise ValueError("Command tree class must be a subclass of CommandTree")

            super().__init__(  # type: ignore
                command_prefix=commands.when_mentioned,
                intents=intents,
                tree_cls=tree_cls,
                help_command=None,
            )
        else:
            super().__init__(  # type: ignore
                command_prefix=commands.when_mentioned,
                intents=intents,
                help_command=None,
            )

        self.log_channel: discord.abc.Messageable
        self.suggestion_channel: t.Optional[discord.abc.Messageable] = None
        self.aio_session: aiohttp.ClientSession

        self.raw_config = config

        # Music
        self.lavalink_nodes: t.List[t.Dict[str, t.Any]] = config.get(
            "lavalink_nodes", []
        )

    async def on_message(self, message: discord.Message) -> None:
        """Ignore messages (only slash commands used)."""
        if await self.is_owner(message.author):
            await self.process_commands(message)

    async def setup_hook(self) -> None:
        """Setup everything."""
        await self.pool.open()  # type: ignore
        try:
            channel = self.get_channel(self.log_channel_id) or await self.fetch_channel(
                self.log_channel_id
            )

            if not isinstance(channel, discord.abc.Messageable):
                print("LOG CHANNEL NOT MESSAGEABLE !")
                raise ValueError()
            self.log_channel = channel
        except discord.NotFound:
            print("LOG CHANNEL NOT FOUND !")
            await self.close()
            return
        except ValueError:
            await self.close()
            return

        channel = self.get_channel(self.suggestion_channel_id)
        if isinstance(channel, discord.abc.Messageable):
            self.suggestion_channel = channel

        self.aio_session = aiohttp.ClientSession()

        report = []
        success = 0
        for ext in self.extensions_list:
            try:
                await self.load_extension(ext)
                success += 1
                report.append(f"✅ | **Extension loaded** : `{ext}`")
            except commands.ExtensionNotFound:
                report.append(f"❌ | **Extension not found** : `{ext}`")
            except commands.ExtensionAlreadyLoaded:
                pass
            except commands.NoEntryPointError:
                report.append(f"❌ | **setup not defined** : `{ext}`")
            except commands.ExtensionFailed as error:
                report.append(
                    f"❌ | **Extension error** : `{ext}` "
                    f"({type(error.original)} : {error.original})"
                )

        embed = discord.Embed(
            title=(
                f"{success} extensions were loaded & "
                f"{len(self.extensions_list) - success} extensions were "
                "not loaded"
            ),
            description="\n".join(report),
            colour=discord.Colour.green(),
        )
        await self.log_channel.send(embed=embed)
        await self.tree.sync()

    async def close(self) -> None:
        """Cleanup upon closing."""
        await self.aio_session.close()
        await self.pool.close()
        await super().close()

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Log message on guild join."""
        await self.log_channel.send(f"{guild.name} joined")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Log message on guild remove."""
        await self.log_channel.send(f"{guild.name} left")

    async def httpcat(
        self,
        interaction: discord.Interaction,
        code: int,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
    ) -> None:
        """Funny error picture."""
        if title is None and description is None:
            return
        embed = discord.Embed(
            title=title, colour=discord.Colour.red(), description=description
        )
        embed.set_image(url=f"https://http.cat/{code}.jpg")

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

    def launch(self) -> None:
        """Launch the bot."""
        self.run(self.token)


if __name__ == "__main__":
    ChaoticBot().launch()  # Run if not imported
