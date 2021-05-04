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

import typing
from asyncio import all_tasks
from datetime import datetime

import aiohttp
import asyncpg
import dbl
import discord
from discord.ext import commands
from github import Github


class ChaoticBot(commands.Bot):
    """The subclassed bot class."""

    used_intents = discord.Intents(
        guilds=True,
        members=False,
        bans=False,
        emojis=False,
        integrations=False,
        webhooks=False,
        invites=False,
        voice_states=True,
        presences=False,
        messages=True,
        reactions=True,
        typing=False,
    )

    def __init__(self) -> None:
        """Initialize the bot."""
        self.token: typing.Optional[str] = None

        self.default_prefix: str = "sudo "
        # This is replaced - value isn't important

        self.first_on_ready = True
        # makes it so on_ready behaves differently on first call
        self.last_update = datetime.utcnow()
        # used in the info command

        self.dbl_token: typing.Optional[str] = None
        self.github_token: typing.Optional[str] = None
        self.ksoft_client: typing.Any = None

        self.pool: asyncpg.pool.Pool = None
        self.postgre_connection: typing.Dict[str, typing.Any] = {}
        # PostgreSQL connection

        self.aio_session: aiohttp.ClientSession = None
        # Used for all internet fetches

        self.log_channel: discord.TextChannel = None
        self.suggestion_channel: discord.TextChannel = None
        self.log_channel_id = 0
        self.suggestion_channel_id = 0
        # Important channels

        self.extensions_list: typing.List[str] = []

        self.prefix_dict: typing.Dict[int, str] = {}

        super().__init__(
            command_prefix=self.get_m_prefix,
            intents=self.used_intents,
        )

        self.load_extension("data.data")
        # You can load an extension only after __init__ has been called

        if self.dbl_token:
            self.dbl_client = dbl.DBLClient(
                self,
                self.dbl_token,
                autopost=True,
            )

        if self.github_token:
            self.github = Github(self.github_token)

    async def on_ready(self) -> None:
        """Operations processed when the bot's ready."""
        await self.change_presence(
            activity=discord.Game(f"{self.default_prefix}help"),
        )
        if self.first_on_ready:
            self.first_on_ready = False

            self.pool = await asyncpg.create_pool(
                min_size=20, max_size=100, **self.postgre_connection
            )
            # postgresql setup

            query = "SELECT * FROM public.prefixes"
            async with self.pool.acquire(timeout=5) as database:
                for row in await database.fetch(query):
                    self.prefix_dict[row["ctx_id"]] = row["prefix"]
            # Load all prefixes in memory

            self.aio_session = aiohttp.ClientSession()

            self.log_channel = self.get_channel(self.log_channel_id)
            self.suggestion_channel = self.get_channel(
                self.suggestion_channel_id)
            # Load the channels

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
            # Load every single extension
            # Looping on the /cogs and /bin folders does not allow fine control

            embed = discord.Embed(
                title=(
                    f"{success} extensions were loaded & "
                    f"{len(self.extensions_list) - success} extensions were "
                    "not loaded"
                ),
                description="\n".join(report),
                color=discord.Color.green(),
            )
            await self.log_channel.send(embed=embed)
        else:
            await self.log_channel.send("on_ready called again")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Log message on guild join."""
        await self.log_channel.send(f"{guild.name} joined")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
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
        extensions: typing.List[str],
    ) -> None:
        """Reload cogs."""
        self.last_update = datetime.utcnow()
        report = []
        success = 0
        self.reload_extension("data.data")
        # First of all, reload the data file
        total_reload = len(extensions) or len(self.extensions_list)
        if extensions:
            for ext in extensions:
                if ext in self.extensions_list:
                    try:
                        try:
                            self.reload_extension(ext)
                            success += 1
                            report.append(
                                f"✅ | **Extension reloaded** : `{ext}`")
                        except commands.ExtensionNotLoaded:
                            self.load_extension(ext)
                            success += 1
                            report.append(
                                f"✅ | **Extension loaded** : `{ext}`")
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
        embed = discord.Embed(
            title=(
                f"{success} "
                f"{'extension was' if success == 1 else 'extensions were'} "
                f"loaded & {total_reload - success} "
                f"{'extension was' if not_loaded == 1 else 'extensions were'}"
                " not loaded"
            ),
            description="\n".join(report),
            colour=discord.Color.green(),
        )
        await self.log_channel.send(embed=embed)
        await ctx.send(embed=embed)

    async def get_m_prefix(
        self,
        _,
        message: discord.Message,
        not_print: bool = True,
    ) -> str:
        """Get the prefix from a message."""
        # not_print : this is not for displaying in a help command, but for
        # actual processing
        if message.content.startswith("¤") and not_print:
            return "¤"  # Hardcoded secret prefix. Because, that's why
        if message.content.startswith(f"{self.default_prefix}help") and not_print:
            return self.default_prefix
        return self.prefix_dict.get(self.get_id(message), self.default_prefix)

    async def httpcat(
        self,
        ctx: commands.Context,
        code: int,
        title: str = discord.Embed.Empty,
        description: str = discord.Embed.Empty,
    ) -> None:
        """Funny error picture."""
        embed = discord.Embed(
            title=title, color=discord.Color.red(), description=description
        )
        embed.set_image(url=f"https://http.cat/{code}.jpg")
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            pass

    async def fetch_answer(
        self, ctx: commands.Context, *content, timeout: int = 30
    ) -> discord.Message:
        """Get an answer."""
        # Helper function for getting an answer in a set of possibilities

        def check(message: discord.Message) -> bool:
            """Check the message."""
            return (
                message.author == ctx.author
                and (message.channel == ctx.channel)
                and message.content.lower() in content
            )

        return await self.wait_for("message", check=check, timeout=timeout)

    async def fetch_confirmation(
        self,
        ctx: commands.Context,
        question: str,
        timeout: int = 30,
    ) -> bool:
        """Get a yes or no reaction-based answer."""
        message = await ctx.send(question)
        await message.add_reaction("\U00002705")  # ✅
        await message.add_reaction("\U0000274c")  # ❌

        def check(payload: discord.RawReactionActionEvent) -> bool:
            """Decide whether or not to process the reaction."""
            return (payload.message_id, payload.channel_id, payload.user_id,) == (
                message.id,
                message.channel.id,
                ctx.author.id,
            ) and payload.emoji.name in {"\U00002705", "\U0000274c"}

        payload = await self.wait_for(
            "raw_reaction_add",
            check=check,
            timeout=timeout,
        )
        return payload.emoji.name == "\U00002705"

    @staticmethod
    def get_id(ctx: typing.Union[commands.Context, discord.Message]) -> int:
        """Get a context's id."""
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id

    def launch(self) -> None:
        """Launch the bot."""
        self.run(self.token)


if __name__ == "__main__":
    ChaoticBot().launch()  # Run if not imported
