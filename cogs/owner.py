from discord.ext import commands
import discord

class OwnerError(commands.CheckFailure):
    """Error specific to this cog"""

class Owner(commands.Cog, command_attrs = dict(help = "Owner command")):
    """Owner-specific commands"""
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        if str(ctx.author) in ctx.bot.admins or await ctx.bot.is_owner(ctx.author):
            return True
        raise OwnerError()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, OwnerError):
            return await ctx.bot.httpcat(ctx, 401, "Only my owner can use the command" + ctx.invoked_with)
        raise

    @commands.command()
    async def system(self, ctx, user:discord.User = None, *, message):
        if not user:
            return await ctx.send("I couldn't find this user")
        await self.bot.db.execute("CREATE TABLE IF NOT EXISTS block (id INT)")
        cur = await self.bot.db.execute('SELECT * FROM block WHERE id=?', (user.id,))
        result = await cur.fetchone()
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
        await ctx.send('Logging out...')
        await self.bot.close()

    @commands.command()
    async def reload(self, ctx, *extensions):
        await self.bot.cog_reloader(ctx, extensions)


def setup(bot):
    bot.add_cog(Owner(bot))
