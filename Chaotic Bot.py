"""MIT License

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
SOFTWARE."""

from asyncio import all_tasks
from datetime import datetime
from os import path

import aiohttp
import asyncpg
import dbl
from discord import Embed, Game
from discord.ext import commands
from github import Github

class chaotic_bot(commands.Bot):
    """The subclassed bot class"""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.first_on_ready = True

        self.load_extension('data.data')

        if self.dbl_token:
            self.dbl_client = dbl.DBLClient(self, self.dbl_token, autopost=True)

        if self.github_token:
            self.github = Github(self.github_token)
        self.prefix_dict = {}

    async def on_ready(self):
        await self.change_presence(activity=Game(f"{self.default_prefix}help"))
        if self.first_on_ready:
            self.first_on_ready = False
            self.pool = await asyncpg.create_pool(database="chaotic", host="127.0.0.1", min_size=20, max_size=100, **self.postgre_connection)
            async with self.pool.acquire(timeout=5) as db:
                for row in await db.fetch("SELECT * FROM public.prefixes"):
                    self.prefix_dict[row["ctx_id"]] = row["prefix"]
            self.aio_session = aiohttp.ClientSession()
            self.last_update = datetime.utcnow()
            self.log_channel = self.get_channel(self.log_channel_id)
            self.suggestion_channel = self.get_channel(self.suggestion_channel_id)
            report = []
            success = 0
            for ext in self.extensions_list:
                    if not ext in self.extensions:
                        try:
                            self.load_extension(ext)
                            report.append(f"✅ | **Extension loaded** : `{ext}`")
                            success+=1
                        except commands.ExtensionFailed as e:
                            report.append(f"❌ | **Extension error** : `{ext}` ({type(e.original)} : {e.original})")
                        except commands.ExtensionNotFound:
                            report.append(f"❌ | **Extension not found** : `{ext}`")
                        except commands.NoEntryPointError:
                            report.append(f"❌ | **setup not defined** : `{ext}`")

            embed = Embed(title = f"{success} extensions were loaded & {len(self.extensions_list) - success} extensions were not loaded", description = '\n'.join(report), color = self.colors['green'])
            await self.log_channel.send(embed = embed)
        else:
            await self.log_channel.send("on_ready called again")

    async def on_guild_join(self,guild):
        await self.log_channel.send(guild.name+" joined")

    async def on_guild_remove(self,guild):
         await self.log_channel.send(guild.name+" left")

    async def close(self):
        await self.aio_session.close()
        await self.ksoft_client.close()
        for task in all_tasks(loop = self.loop):
            task.cancel()
        for ext in tuple(self.extensions):
            self.unload_extension(ext)
        await self.pool.close()
        await super().close()

    async def cog_reloader(self, ctx, extensions):
        self.last_update = datetime.utcnow()
        report = []
        success = 0
        self.reload_extension('data.data')
        M = len(self.extensions_list)
        if extensions:
            M = len(extensions)
            for ext in extensions:
                if ext in self.extensions_list:
                    try:
                        try:
                            self.reload_extension(ext)
                            success+=1
                            report.append(f"✅ | **Extension reloaded** : `{ext}`")
                        except commands.ExtensionNotLoaded:
                            self.load_extension(ext)
                            success+=1
                            report.append(f"✅ | **Extension loaded** : `{ext}`")
                    except commands.ExtensionFailed as e:
                        report.append(f"❌ | **Extension error** : `{ext}` ({type(e.original)} : {e.original})")
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
                        success+=1
                        report.append(f"✔️ | **Extension reloaded** : `{ext}`")
                    except commands.ExtensionNotLoaded:
                        self.load_extension(ext)
                        report.append(f"✔️ | **Extension loaded** : `{ext}`")
                except commands.ExtensionFailed as e:
                    report.append(f"❌ | **Extension error** : `{ext}` ({type(e.original)} : {e.original})")
                except commands.ExtensionNotFound:
                    report.append(f"❌ | **Extension not found** : `{ext}`")
                except commands.NoEntryPointError:
                    report.append(f"❌ | **setup not defined** : `{ext}`")

        embed = Embed(title = f"{success} {'extension was' if success == 1 else 'extensions were'} loaded & {M - success} {'extension was' if M - success == 1 else 'extensions were'} not loaded", description = '\n'.join(report), color = self.colors['green'])
        await self.log_channel.send(embed = embed)
        await ctx.send(embed = embed)

    async def get_m_prefix(self, message, not_print=True):
        if message.content.startswith("¤") and not_print:
            return '¤'
        elif message.content.startswith(f"{self.default_prefix}help") and not_print:
            return self.default_prefix
        return self.prefix_dict.get(self.get_id(message), self.default_prefix)

    async def httpcat(self, ctx, code, title = Embed.Empty, description = Embed.Empty):
        embed = Embed(title = title, color = self.colors['red'], description = description)
        embed.set_image(url = "https://http.cat/"+str(code)+".jpg")
        await ctx.send(embed=embed)

    @staticmethod
    def get_id(ctx):
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id

async def command_prefix(bot,message):
    return await bot.get_m_prefix(message)

bot = chaotic_bot(command_prefix = command_prefix, description = "A bot for fun", fetch_offline_members = True)

if __name__ == "__main__":
    bot.run(bot.token)
