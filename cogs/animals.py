from discord.ext import commands, tasks
import discord
from random import choice
from datetime import datetime

class Pic():
    def __init__(self, url, tag = discord.Embed.Empty):
        self.url = url
        self.title = tag

class Animals(commands.Cog):
    """Get cute pics of animals"""
    def __init__(self, bot):
        self.bot = bot
        self.catfact_update.start()

    @tasks.loop(hours = 12)
    async def catfact_update(self):
        async with self.bot.aio_session.get("https://cat-fact.herokuapp.com/facts") as response:
            self.all_facts = await response.json()

    @commands.command(ignore_extra = True)
    async def aww(self, ctx):
        """Get random cute pictures, mostly animals."""
        await self.reddit_sender(ctx, await self.bot.ksoft_client.images.random_aww())

    @commands.command(ignore_extra = True)
    async def birb(self,ctx):
        """Get random birb image"""
        await self.image_sender(ctx, await self.bot.ksoft_client.images.random_image(tag = "birb"))

    @commands.command()
    async def cat(self, ctx):
        """Sens a random cat picture"""
        async with self.bot.aio_session.get("https://aws.random.cat/meow") as response:
            picture = await response.json()
            await self.image_sender(ctx, Pic(picture['file'], 'Cat'))

    @commands.command()
    async def catfact(self, ctx):
        """Sends a random cat fact"""
        fact = choice(self.all_facts['all'])
        await ctx.send(fact['text'])

    @commands.command(ignore_extra = True)
    async def dog(self, ctx):
        """Get random dog image"""
        if choice([True, False]):
            await self.image_sender(ctx, await self.bot.ksoft_client.images.random_image(tag = "dog"))
        else:
            async with self.bot.aio_session.get("https://random.dog/woof.json") as response:
                picture = await response.json()
                await self.image_sender(ctx, Pic(picture['url'], 'Dog'))

    @commands.command()
    async def fox(self,ctx):
        """Sends a random fox picture"""
        async with self.bot.aio_session.get("https://randomfox.ca/floof/") as response:
            picture = await response.json()
            await self.image_sender(ctx, Pic(picture['image'], "Fox"))

    async def image_sender(self,ctx,image):
        """Embeds an image then sends it"""
        if hasattr(image, "code"):
            return await ctx.send(image.message)
        if not image.url:
            return await self.bot.httpcat(ctx, 404)
        embed = discord.Embed(timestamp = datetime.utcnow(), colour = self.bot.colors['blue'])
        embed.set_image(url = image.url)
        await ctx.send(embed = embed)

    async def reddit_sender(self,ctx,image):
        """Embeds a Reddit image then sends it"""
        if hasattr(image, "error"):
            return await ctx.send(image.message)
        embed = discord.Embed(title = image.title, url = image.source, timestamp = datetime.fromtimestamp(image.created_at), colour = self.bot.colors['blue'])
        if not image.image_url:
            await self.bot.httpcat(ctx, 404)
        embed.set_image(url = image.image_url)
        embed.set_footer(text = f"👍 {image.upvotes} | 👎 {image.downvotes} | 💬 {image.comments}")
        embed.set_author(name = f"Posted by {image.author} in {image.subreddit}", icon_url = "https://i.redd.it/qupjfpl4gvoy.jpg", url = f"https://reddit.com"+image.author)
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Animals(bot))
