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

from discord.ext import commands
import discord
from datetime import datetime
from random import choice

def check_channel(channel):
    if isinstance(channel,discord.TextChannel):
        return channel.is_nsfw()
    return True

class Pic():
    def __init__(self,url,tag):
        self.url=url
        self.tag=tag

class PicError():
    def __init__(self):
        self.code=404

class Images(commands.Cog): #Thanks KSoft.si
    '''Commands to get random images
    You can try using the nsfw command, if you dare'''
    def __init__(self,bot):
        self.bot=bot

    @commands.command(ignore_extra=True)
    async def dab(self,ctx):
        """Get random dab image"""
        await self.image_sender(ctx,await self.rand_im("dab"))

    @commands.command(ignore_extra=True)
    async def doge(self,ctx):
        """Get random doge image"""
        await self.image_sender(ctx,await self.rand_im("doge"))

    @commands.command(ignore_extra=True)
    async def fbi(self,ctx):
        """Get random FBI image"""
        await self.image_sender(ctx,await self.rand_im("fbi"))

    @commands.command(ignore_extra=True,hidden=True)
    @commands.is_nsfw()
    async def hentai(self,ctx):
        """Get random hentai image"""
        await self.image_sender(ctx,await self.rand_im("hentai",True))

    @commands.command(ignore_extra=True,hidden=True)
    @commands.is_nsfw()
    async def hentai_gif(self,ctx):
        """Get random hentai GIF"""
        await self.image_sender(ctx,await self.rand_im("hentai_gif",True))

    @commands.command(ignore_extra=True)
    async def hug(self,ctx):
        """Get random hug image"""
        await self.image_sender(ctx,await self.rand_im("hug"))

    @commands.command(ignore_extra=True)
    async def kappa(self,ctx):
        """Get random kappa image"""
        await self.image_sender(ctx,await self.rand_im("kappa"))

    @commands.command(ignore_extra=True)
    async def kiss(self,ctx):
        """Get random kiss image"""
        await self.image_sender(ctx,await self.rand_im("kiss"))

    #@commands.command()
    async def kitten(self,ctx,*,hash): #This command doesn't work because of robohash
        """Get a kitten image from an input"""
        embed=discord.Embed(title=hash)
        embed.set_image(url="https://robohash.org/"+hash+".png?set=set4")
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True,hidden=True,aliases=["im_nsfw"])
    async def image_nsfw(self,ctx):
        """Retrieve the list of all available NSFW tags"""
        tag_list=await self.bot.client.images.tags()
        embed=discord.Embed(timestamp=datetime.utcnow(),color=self.bot.get_color())
        embed.add_field(name="NSFW tags",value='\n'.join(tag_list.nsfw_tags))
        embed.set_author(name=ctx.author.display_name,icon_url=str(ctx.author.avatar_url))
        await ctx.send(embed=embed)

    @commands.command()
    async def monster(self,ctx,*,hash):
        """Get a monster image from an input"""
        embed=discord.Embed(title=hash)
        embed.set_image(url="https://robohash.org/"+hash+".png?set=set2")
        await ctx.send(embed=embed)

    @commands.command(hidden=True,ignore_extra=True)
    @commands.is_nsfw()
    async def neko(self,ctx):
        """Get random neko image"""
        await self.image_sender(ctx,await self.rand_im("neko",nsfw=True))

    @commands.command(hidden=True,ignore_extra=True)
    @commands.is_nsfw()
    async def nsfw(self,ctx):
        """Retrieves random NSFW pics.
        To find the other NSFW commands : use im_nsfw or reddit with an NSFW subreddit"""
        await self.reddit_sender(ctx,await self.bot.client.images.random_nsfw())

    @commands.command(ignore_extra=True)
    async def meme(self,ctx):
        """Retrieves a random meme from Reddit"""
        await self.reddit_sender(ctx,await self.bot.client.images.random_meme())

    @commands.command(ignore_extra=True)
    async def pat(self,ctx):
        """Get random pat image"""
        await self.image_sender(ctx,await self.bot.client.random_image(tag="pat"))

    @commands.command(ignore_extra=True)
    async def pepe(self,ctx):
        """Get random pepe image"""
        await self.image_sender(ctx,await self.rand_im("pepe"))

    @commands.command(enabled=False)
    async def reddit(self,ctx,subreddit): #the Ksoft.SI API used in this command is broken. Waiting for the devs to debug it
        """Retrieve images from the specified subreddit.
        This command may return NSFW results only in NSFW channels"""
        try:
            await self.reddit_sender(ctx,await self.bot.client.images.random_reddit(subreddit.split('r/')[-1],remove_nsfw=not check_channel(ctx.channel)))
        except Exception as e:
            await ctx.send(type(e).__name__+' : '+str(e))
            await self.bot.httpcat(ctx,404,"I didn't find any image for your query")

    @commands.command()
    async def robot(self,ctx,*,hash):
        """Get a robot image from an input"""
        embed=discord.Embed(title=hash)
        embed.set_image(url="https://robohash.org/"+hash+".png")
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    async def tickle(self,ctx):
        """Get random tickle image"""
        await self.image_sender(ctx,await self.rand_im("tickle"))

    @commands.command(ignore_extra=True)
    async def wikihow(self,ctx):
        """Retrieves weird images from WikiHow."""
        image=await self.bot.client.images.random_wikihow()
        embed=discord.Embed(title=image.title,url=image.article_url,colour=self.bot.get_color())
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def rand_im(self,tag,nsfw=False):
        try:
            return await self.bot.client.images.random_image(tag=tag,nsfw=nsfw)
        except:
            return PicError()

    async def image_sender(self,ctx,image):
        """Embeds an image then sends it"""
        if hasattr(image,"code"):
            return await self.bot.httpcat(ctx,image["code"])
        if not image.url:
            return await self.bot.httpcat(ctx,404)
        embed=discord.Embed(title=image.tag,timestamp=datetime.utcnow(),colour=self.bot.get_color())
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def reddit_sender(self,ctx,image):
        """Embeds a Reddit image then sends it"""
        if hasattr(image,"error"):
            return await ctx.send(image.message)
        embed=discord.Embed(title=image.title,url=image.source,timestamp=datetime.fromtimestamp(image.created_at),colour=self.bot.get_color())
        if not image.image_url:
            return await self.bot.httpcat(ctx,404)
        embed.set_image(url=image.image_url)
        embed.set_footer(text=f"👍 {image.upvotes} | 👎 {image.downvotes} | 💬 {image.comments}")
        embed.set_author(name=f"Posted by {image.author} in {image.subreddit}",icon_url="https://i.redd.it/qupjfpl4gvoy.jpg",url=f"https://reddit.com"+image.author)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))
