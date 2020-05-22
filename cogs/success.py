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

from discord.ext import commands, tasks
from os import path
from discord import Embed
import asyncio
import traceback

class Success():
    """Class implementation of a Discord success"""
    def __init__(self, name, description, functions, column, initial, datatype, description_is_visible = True):
        self.name = name
        self.description = description
        self._checker, self._advancer = functions
        self.description_is_visible = description_is_visible
        self.column = column
        self.state_column = column + "_state"
        self.datatype = datatype
        self.initial = initial
        if description_is_visible:
            self.locked = description
        else:
            self.locked = "Hidden success"

    async def checker(self, ctx, data, identifier, db):
        test, data = await self._checker(self, ctx, data)
        await db.execute(f"UPDATE successes SET `{self.column}`=? WHERE id=?", (data, identifier))
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
            data+=ctx.command.name
        else:
            data = ctx.command.name
        return len(data.split(",")) == total(ctx.bot), data
    async def advancer(self, ctx, data):
        if data:
            return f" ({len(data.split(','))}/{total(ctx.bot)})"
        else:
            return f" (0/{total(ctx.bot)})"
    return checker, advancer

def prefix():
    async def checker(self, ctx, data):
        return ctx.prefix == "¤", None
    return checker, None

success_list = [
Success("First command", "Begin using the bot", command_count(1), "n_use_1", 1, "INT"),
Success("Bot regular", "Launch 100 commands", command_count(100), "n_use_10", 1, "INT"),
Success("Bot master", "Launch 1000 commands", command_count(1000), "n_use_100", 1, "INT"),
Success("The secrets of the bot", "Find every single hidden command", hidden_commands(), "hidden", "NULL", "TEXT"),
Success("The dark side of the chaos", "Find the hidden prefix", prefix(), "dark", 0, "BOOL", description_is_visible = False)
]

class Successes(commands.Cog):
    """Everything to know about successes"""
    def __init__(self, bot, success_list):
        self.bot = bot
        self.success_list = success_list
        self.ensure_database.start()

    @tasks.loop(count = 1)
    async def ensure_database(self):
        await self.bot.db.execute("CREATE TABLE IF NOT EXISTS successes (id INT PRIMARY KEY)")
        cur = await self.bot.db.execute("SELECT * FROM pragma_table_info('successes')")
        result = await cur.fetchall()
        columns = [R["name"] for R in result]
        for s in self.success_list:
            if (not s.column in columns) and s.column and s.datatype:
                await self.bot.db.execute(f"ALTER TABLE successes ADD COLUMN `{s.column}` `{s.datatype}` DEFAULT {s.initial}")
            if not s.state_column in columns:
                await self.bot.db.execute(f"ALTER TABLE successes ADD COLUMN `{s.state_column}` BOOL DEFAULT 0")

    @commands.command(ignore_extra=True,aliases=["succes", "successes"])
    async def success(self,ctx):
        """Sends back your successes"""
        cur = await self.bot.db.execute("SELECT * FROM successes WHERE id=?",(ctx.author.id,))
        state = await cur.fetchone()
        embed=Embed(title = f"Success list ({len([s for s in self.success_list if state[s.state_column]])}/{len(self.success_list)})",colour=self.bot.colors["green"])
        embed.set_author(name = str(ctx.author),icon_url=str(ctx.author.avatar_url))
        embed.set_thumbnail(url = str(ctx.bot.user.avatar_url))
        locked = []
        for succ in self.success_list:
            if state[succ.state_column]:
                embed.add_field(name = f"{succ.name} - Unlocked", value = succ.description, inline = False)
            else:
                locked.append(succ)
        for succ in locked:
            embed.add_field(name = succ.name + await succ.advancer(ctx, state[succ.column]), value = succ.locked, inline = False)
        await ctx.send(embed = embed)

    async def bot_check(self, ctx):
        cur = await ctx.bot.db.execute("SELECT * FROM successes WHERE id=?", (ctx.author.id,))
        result = await cur.fetchone()
        if not result:
            await ctx.bot.db.execute("INSERT INTO successes (id) VALUES (?)", (ctx.author.id,))
            cur = await ctx.bot.db.execute("SELECT * FROM successes WHERE id=?", (ctx.author.id,))
            result = await cur.fetchone()
        embeds = []
        for s in success_list:
            if not result[s.state_column]:
                if await s.checker(ctx, result[s.column], ctx.author.id, ctx.bot.db):
                    embed = Embed(title = "Succes unlocked !", description = s.name, colour = ctx.bot.get_color())
                    embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                    embed.set_thumbnail(url = "https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg")
                    embed.add_field(name = s.description, value = "Requirements met")
                    embeds.append(embed)
                    await ctx.bot.db.execute(f"UPDATE successes SET `{s.state_column}`=1 WHERE id=?", (ctx.author.id,))
        asyncio.create_task(ctx.bot.db.commit())
        i = 0
        for embed in embeds:
            i+=1
            await ctx.send(embed=embed)
            if i == 4:
                await asyncio.sleep(5)
                i = 0
        return True

def setup(bot):
    bot.add_cog(Successes(bot,success_list))
