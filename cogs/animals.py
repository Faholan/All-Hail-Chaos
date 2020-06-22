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

from datetime import datetime
from random import choice

import discord
from discord.ext import commands, tasks

class Pic():
    def __init__(self, url:str, tag:str=discord.Embed.Empty) -> None:
        self.url = url
        self.title = tag

class Animals(commands.Cog):
    """Get cute pics of animals"""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.catfact_update.start()

    @tasks.loop(hours=12)
    async def catfact_update(self) -> None:
        async with self.bot.aio_session.get("https://cat-fact.herokuapp.com/facts") as response:
            self.all_facts = await response.json()

    @commands.command(ignore_extra=True)
    async def aww(self, ctx: commands.Context) -> None:
        """Get random cute pictures, mostly animals."""
        await self.reddit_sender(ctx, await self.bot.ksoft_client.images.random_aww())

    @commands.command(ignore_extra=True)
    async def birb(self, ctx: commands.Context) -> None:
        """Get random birb image"""
        await self.image_sender(ctx, await self.bot.ksoft_client.images.random_image(tag="birb"))

    @commands.command()
    async def cat(self, ctx: commands.Context) -> None:
        """Sens a random cat picture"""
        async with self.bot.aio_session.get("https://aws.random.cat/meow") as response:
            picture = await response.json()
            await self.image_sender(ctx, Pic(picture["file"], "Cat"))

    @commands.command()
    async def catfact(self, ctx: commands.Context) -> None:
        """Sends a random cat fact"""
        fact = choice(self.all_facts["all"])
        await ctx.send(fact["text"])

    @commands.command(ignore_extra=True)
    async def dog(self, ctx: commands.Context) -> None:
        """Get random dog image"""
        if choice([True, False]):
            await self.image_sender(ctx, await self.bot.ksoft_client.images.random_image(tag="dog"))
        else:
            async with self.bot.aio_session.get("https://random.dog/woof.json") as response:
                picture = await response.json()
                await self.image_sender(ctx, Pic(picture["url"], "Dog"))

    @commands.command()
    async def fox(self, ctx: commands.Context) -> None:
        """Sends a random fox picture"""
        async with self.bot.aio_session.get("https://randomfox.ca/floof/") as response:
            picture = await response.json()
            await self.image_sender(ctx, Pic(picture["image"], "Fox"))

    async def image_sender(self, ctx: commands.Context, image) -> None:
        """Embeds an image then sends it"""
        if hasattr(image, "code"):
            return await ctx.send(image.message)
        if not image.url:
            return await self.bot.httpcat(ctx, 404)
        embed = discord.Embed(timestamp=datetime.utcnow(), colour=self.bot.colors["blue"])
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def reddit_sender(self, ctx: commands.Context, image) -> None:
        """Embeds a Reddit image then sends it"""
        if hasattr(image, "error"):
            return await ctx.send(image.message)
        embed = discord.Embed(title=image.title, url=image.source, timestamp=datetime.fromtimestamp(image.created_at), colour=self.bot.colors["blue"])
        if not image.image_url:
            await self.bot.httpcat(ctx, 404)
        embed.set_image(url=image.image_url)
        embed.set_footer(text=f"👍 {image.upvotes} | 👎 {image.downvotes} | 💬 {image.comments}")
        embed.set_author(name=f"Posted by {image.author} in {image.subreddit}", icon_url="https://i.redd.it/qupjfpl4gvoy.jpg", url=f"https://reddit.com"+image.author)
        await ctx.send(embed=embed)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Animals(bot))
