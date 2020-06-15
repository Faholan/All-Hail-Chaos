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

import asyncio
from os import path
import traceback

from discord import Embed
from discord.ext import commands, tasks

class Success():
    """Class implementation of a Discord success"""
    def __init__(self, name, description, functions, column, description_is_visible = True):
        self.name = name
        self.description = description
        self._checker, self._advancer = functions
        self.description_is_visible = description_is_visible
        self.column = column
        self.state_column = column + "_state"
        if description_is_visible:
            self.locked = description
        else:
            self.locked = "Hidden success"

    async def checker(self, ctx, data, identifier, db):
        test, data = await self._checker(self, ctx, data)
        await db.execute(f"UPDATE public.successes SET {self.column}=$1 WHERE id=$2", data, identifier)
        return test

    async def advancer(self, ctx, data):
        if self._advancer:
            return await self._advancer(self, ctx, data)
        return " - Locked"

def command_count(n):
    async def checker(self, ctx, data):
        return data >= n, data+1
    async def advancer(self, ctx, data):
        return f" ({data}/{n})"
    return checker, advancer

def hidden_commands():
    total = lambda bot : len([command for command in bot.commands if command.hidden])
    async def checker(self, ctx, data):
        if not ctx.command.hidden:
            return False, data
        if data:
            if ctx.command.name in data:
                return False, data
        if data:
            data.append(ctx.command.name)
        else:
            data = [ctx.command.name]
        return len(data) == total(ctx.bot), data
    async def advancer(self, ctx, data):
        if data:
            return f" ({len(data)}/{total(ctx.bot)})"
        else:
            return f" (0/{total(ctx.bot)})"
    return checker, advancer

def prefix():
    async def checker(self, ctx, data):
        return ctx.prefix == "¤", None
    return checker, None

success_list = [
Success("First command", "Begin using the bot", command_count(1), "n_use_1"),
Success("Bot regular", "Launch 100 commands", command_count(100), "n_use_100"),
Success("Bot master", "Launch 1000 commands", command_count(1000), "n_use_1000"),
Success("The secrets of the bot", "Find every single hidden command", hidden_commands(), "hidden"),
Success("The dark side of the chaos", "Find the hidden prefix", prefix(), "dark", description_is_visible = False)
]

class Successes(commands.Cog):
    """Everything to know about successes"""
    def __init__(self, bot, success_list):
        self.bot = bot
        self.success_list = success_list

    @commands.command(ignore_extra = True, aliases = ["succes", "successes"])
    async def success(self,ctx):
        """Sends back your successes"""
        async with self.bot.pool.acquire() as db:
            state = await db.fetchrow("SELECT * FROM public.successes WHERE id=$1", ctx.author.id)
            if not state:
                await db.execute("INSERT INTO public.successes (id) VALUES ($1)", ctx.author.id)
                state = await db.fetchrow("SELECT * FROM public.successes WHERE id=$1", ctx.author.id)
            embed = Embed(title = f"Success list ({len([s for s in self.success_list if state[s.state_column]])}/{len(self.success_list)})", colour = self.bot.colors["green"])
            embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
            embed.set_thumbnail(url = str(ctx.bot.user.avatar_url))
            locked = []
            for succ in self.success_list:
                if state[succ.state_column]:
                    embed.add_field(name = f"{succ.name} - Unlocked", value = succ.description, inline = False)
                else:
                    locked.append(succ)
            for succ in locked:
                embed.add_field(name = f"{succ.name}{await succ.advancer(ctx, state[succ.column])}", value = succ.locked, inline = False)
            await ctx.send(embed = embed)

    @commands.Cog.listener("on_command_completion")
    async def succ_sender(self, ctx):
        """Checks and sends the successes"""
        if ctx.invoked_with in ("logout", "reboot"):
            return
        if not hasattr(self, "_succ_conn"):
            self._succ_conn = await self.bot.pool.acquire()
            self._succ_con_lock = asyncio.Lock()
        async with self._succ_con_lock:
            result = await self._succ_conn.fetchrow("SELECT * FROM public.successes WHERE id=$1", ctx.author.id)
            if not result:
                await self._succ_conn.execute("INSERT INTO successes (id) VALUES ($1)", ctx.author.id)
                result = await self._succ_conn.fetchrow("SELECT * FROM public.successes WHERE id=$1", ctx.author.id)
            embeds = []
            for s in success_list:
                if not result[s.state_column]:
                    if await s.checker(ctx, result[s.column], ctx.author.id, self._succ_conn):
                        embed = Embed(title = "Succes unlocked !", description = s.name, colour = ctx.bot.get_color())
                        embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                        embed.set_thumbnail(url = "https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg")
                        embed.add_field(name = s.description, value = "Requirements met")
                        embeds.append(embed)
                        await self._succ_conn.execute(f"UPDATE public.successes SET {s.state_column}=$1 WHERE id=$2", True, ctx.author.id)
        i = 0
        for embed in embeds:
            i+=1
            await ctx.send(embed=embed)
            if i == 4:
                await asyncio.sleep(5)
                i = 0

    def cog_unload(self):
        if hasattr(self, "_succ_conn"):
            asyncio.create_task(self.bot.pool.release(self._succ_conn))

def setup(bot):
    bot.add_cog(Successes(bot,success_list))
