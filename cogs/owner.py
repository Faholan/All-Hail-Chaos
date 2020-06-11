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

from contextlib import redirect_stdout
import io
import textwrap
import traceback

import discord
from discord.ext import commands

class OwnerError(commands.CheckFailure):
    """Error specific to this cog"""

class Owner(commands.Cog, command_attrs = dict(help = "Owner command")):
    """Owner-specific commands"""
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def cog_check(self, ctx):
        if str(ctx.author) in ctx.bot.admins or await ctx.bot.is_owner(ctx.author):
            return True
        raise OwnerError()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, OwnerError):
            return await ctx.bot.httpcat(ctx, 401, "Only my owner can use the command " + ctx.invoked_with)
        raise

    @commands.command(name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a Python code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command()
    async def system(self, ctx, user:discord.User = None, *, message):
        """Makes the bot send a message to the specified user"""
        if not user:
            return await ctx.send("I couldn't find this user")
        async with self.bot.pool.acquire() as db:
            result = await db.fetchrow('SELECT * FROM block WHERE id=$1', user.id)
            if result:
                return await ctx.send("This user blocked me. Sorry")
            embed = discord.Embed(title = "Message from my owner", description = message, url = discord.utils.oauth_url(str(self.bot.user.id), permissions = discord.Permissions(self.bot.invite_permissions)))
            embed.set_author(name = f"{ctx.author.name}#{ctx.author.discriminator}", icon_url = str(ctx.author.avatar_url))
            embed.set_footer(text = f"Use the command `{discord.utils.escape_markdown(await self.bot.get_m_prefix(ctx.message, False))}block` if you don't want me to DM you anymore")
            try:
                await user.send(f"Use `{discord.utils.escape_markdown(await self.bot.get_m_prefix(ctx.message, False))}contact` to answer this message, or click on the title to go to my support server", embed = embed)
            except discord.Forbidden:
                await ctx.send("This user blocked his DM. I can't message him")
            else:
                await ctx.send("DM successfully sent !")

    @commands.command(ignore_extra = True)
    async def logout(self,ctx):
        """Kills the bot"""
        await ctx.send('Logging out...')
        await self.bot.close()

    @commands.command()
    async def reload(self, ctx, *extensions):
        """Reloads extensions"""
        await self.bot.cog_reloader(ctx, extensions)

    @commands.command()
    async def unload(self, ctx, *extensions):
        """Unloads extensions"""
        if "cogs.owner" in extensions:
            return await ctx.send("You shouldn't unload me")
        if not extensions:
            return await ctx.send("Please specify at least one extension to unload")
        M = len(extensions)
        report = []
        success = 0
        for ext in extensions:
            try:
                self.bot.unload_extension(ext)
                success+=1
                report.append(f"✅ | **Extension unloaded** : `{ext}`")
            except commands.ExtensionNotLoaded:
                report.append(f"❌ | **Extension not loaded** : `{ext}`")

        embed = discord.Embed(title = f"{success} {'extension was' if success == 1 else 'extensions were'} unloaded & {M - success} {'extension was' if M - success == 1 else 'extensions were'} not unloaded", description = '\n'.join(report), color = self.bot.colors['green'])
        await self.bot.log_channel.send(embed = embed)
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Owner(bot))
