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

from asyncio import all_tasks
from datetime import datetime

import aiohttp
import asyncpg
import dbl
from discord import Embed, Forbidden, Game, Guild, Message
from discord.ext import commands
from github import Github


class ChaoticBot(commands.Bot):
    """The subclassed bot class."""

    def __init__(self) -> None:
        """Initialize the bot."""

        self.token = None
        self.intents = None

        self.first_on_ready = True
        self.last_update = datetime.utcnow()

        self.dbl_token = None
        self.github_token = None
        self.pool = None
        self.default_prefix = "€"
        self.postgre_connection = {}

        self.ksoft_client = None
        self.aio_session = None

        self.log_channel = None
        self.suggestion_channel = None
        self.log_channel_id = 0
        self.suggestion_channel_id = 0

        self.colors = {}

        self.extensions_list = []

        self.load_extension("data.data")

        if self.dbl_token:
            self.dbl_client = dbl.DBLClient(
                self,
                self.dbl_token,
                autopost=True,
            )

        if self.github_token:
            self.github = Github(self.github_token)
        self.prefix_dict = {}

        super().__init__(
            command_prefix=self.get_m_prefix,
            intents=self.intents,
        )

    async def on_ready(self) -> None:
        """Operations processed when the bot's ready."""
        await self.change_presence(activity=Game(f"{self.default_prefix}help"))
        if self.first_on_ready:
            self.first_on_ready = False
            self.pool = await asyncpg.create_pool(
                database="chaotic",
                host="127.0.0.1",
                min_size=20,
                max_size=100,
                **self.postgre_connection
            )
            query = "SELECT * FROM public.prefixes"
            async with self.pool.acquire(timeout=5) as database:
                for row in await database.fetch(query):
                    self.prefix_dict[row["ctx_id"]] = row["prefix"]
            self.aio_session = aiohttp.ClientSession()
            self.log_channel = self.get_channel(self.log_channel_id)
            self.suggestion_channel = self.get_channel(
                self.suggestion_channel_id
            )
            report = []
            success = 0
            for ext in self.extensions_list:
                if ext not in self.extensions:
                    try:
                        self.load_extension(ext)
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

            embed = Embed(
                title=(
                    f"{success} extensions were loaded & "
                    f"{len(self.extensions_list) - success} extensions were "
                    "not loaded"
                ),
                description="\n".join(report),
                color=self.colors["green"],
            )
            await self.log_channel.send(embed=embed)
        else:
            await self.log_channel.send("on_ready called again")

    async def on_guild_join(self, guild: Guild) -> None:
        """Log message on guild join."""
        await self.log_channel.send(f"{guild.name} joined")

    async def on_guild_remove(self, guild: Guild) -> None:
        """Log message on guild remove."""
        await self.log_channel.send(f"{guild.name} left")

    async def close(self) -> None:
        """Do some cleanup."""
        await self.aio_session.close()
        await self.ksoft_client.close()
        for task in all_tasks(loop=self.loop):
            task.cancel()
        for ext in tuple(self.extensions):
            self.unload_extension(ext)
        await self.pool.close()
        await super().close()

    async def cog_reloader(
            self,
            ctx: commands.Context,
            extensions: list
            ) -> None:
        """Reload cogs."""
        self.last_update = datetime.utcnow()
        report = []
        success = 0
        self.reload_extension("data.data")
        total_reload = len(extensions) or len(self.extensions_list)
        if extensions:
            for ext in extensions:
                if ext in self.extensions_list:
                    try:
                        try:
                            self.reload_extension(ext)
                            success += 1
                            report.append(
                                f"✅ | **Extension reloaded** : `{ext}`"
                            )
                        except commands.ExtensionNotLoaded:
                            self.load_extension(ext)
                            success += 1
                            report.append(
                                f"✅ | **Extension loaded** : `{ext}`"
                            )
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
        else:
            for ext in self.extensions_list:
                try:
                    try:
                        self.reload_extension(ext)
                        success += 1
                        report.append(f"✔️ | **Extension reloaded** : `{ext}`")
                    except commands.ExtensionNotLoaded:
                        self.load_extension(ext)
                        report.append(f"✔️ | **Extension loaded** : `{ext}`")
                except commands.ExtensionFailed as error:
                    report.append(
                        f"❌ | **Extension error** : `{ext}` "
                        f"({type(error.original)} : {error.original})"
                    )
                except commands.ExtensionNotFound:
                    report.append(f"❌ | **Extension not found** : `{ext}`")
                except commands.NoEntryPointError:
                    report.append(f"❌ | **setup not defined** : `{ext}`")
        not_loaded = total_reload - success
        embed = Embed(
            title=(
                f"{success} "
                f"{'extension was' if success == 1 else 'extensions were'} "
                f"loaded & {total_reload - success} "
                f"{'extension was' if not_loaded == 1 else 'extensions were'}"
                " not loaded"
            ),
            description="\n".join(report),
            colour=self.colors["green"],
        )
        await self.log_channel.send(embed=embed)
        await ctx.send(embed=embed)

    async def get_m_prefix(
            self,
            message: Message,
            not_print: bool = True) -> str:
        """Get the prefix from a message."""
        if message.content.startswith("¤") and not_print:
            return '¤'
        if message.content.startswith(
                f"{self.default_prefix}help") and not_print:
            return self.default_prefix
        return self.prefix_dict.get(
            self.get_id(message),
            self.default_prefix
        )

    async def httpcat(
            self,
            ctx: commands.Context,
            code: int,
            title: str = Embed.Empty,
            description: str = Embed.Empty) -> None:
        """Funny error picture."""
        embed = Embed(
            title=title,
            color=self.colors["red"],
            description=description
        )
        embed.set_image(url=f"https://http.cat/{code}.jpg")
        try:
            await ctx.send(embed=embed)
        except Forbidden:
            pass

    @staticmethod
    def get_id(ctx: commands.Context) -> int:
        """Get a context's id."""
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id

    def launch(self) -> None:
        """Launch the bot."""
        self.run(self.token)


if __name__ == "__main__":
    ChaoticBot().launch()
