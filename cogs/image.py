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

def sha(m):
    """Renvoie le haché du message d'après le protocole SHA-256"""
    et=lambda x,y:''.join([str(int(x[i]) and int(y[i])) for i in range(len(x))])
    ou=lambda x,y:''.join([str(int(x[i]) or int(y[i])) for i in range(len(x))])
    xor=lambda x,y:''.join([str(int(x[i])^int(y[i])) for i in range(len(x))])
    complement=lambda x:''.join([str((int(x[i])+1)%2) for i in range(len(x))])

    dec_g=lambda x,n:x[n:]+'0'*n
    dec_d=lambda x,n:'0'*n+x[:len(x)-n]

    SHR=lambda n,x:dec_g(x,n)
    ROTR=lambda n,x:ou(dec_d(x,n),dec_g(x,32-n))
    Ch=lambda x,y,z:xor(et(x,y),et(complement(x),z))
    Maj=lambda x,y,z:xor(xor(et(x,y),et(x,z)),et(y,z))
    E_0=lambda x:xor(xor(ROTR(2,x),ROTR(13,x)),ROTR(22,x))
    E_1=lambda x:xor(xor(ROTR(6,x),ROTR(11,x)),ROTR(25,x))
    o_0=lambda x:xor(xor(ROTR(7,x),ROTR(18,x)),SHR(3,x))
    o_1=lambda x:xor(xor(ROTR(17,x),ROTR(19,x)),SHR(10,x))

    K=['428a2f98','71374491','b5c0fbcf','e9b5dba5','3956c25b','59f111f1','923f82a4','ab1c5ed5','d807aa98','12835b01','243185be','550c7dc3','72be5d74','80deb1fe','9bdc06a7','c19bf174','e49b69c1','efbe4786','0fc19dc6','240ca1cc','2de92c6f','4a7484aa','5cb0a9dc','76f988da','983e5152','a831c66d','b00327c8','bf597fc7','c6e00bf3','d5a79147','06ca6351','14292967','27b70a85','2e1b2138','4d2c6dfc','53380d13','650a7354','766a0abb','81c2c92e','92722c85','a2bfe8a1','a81a664b','c24b8b70','c76c51a3','d192e819','d6990624','f40e3585','106aa070','19a4c116','1e376c08','2748774c','34b0bcb5','391c0cb3','4ed8aa4a','5b9cca4f','682e6ff3','748f82ee','78a5636f','84c87814','8cc70208','90befffa','a4506ceb','bef9a3f7','c67178f2']
    K=[bin(int(i,base=16))[2:] for i in K]
    K=['0'*(32-len(i))+i for i in K]

    H=['6a09e667','bb67ae85','3c6ef372','a54ff53a','510e527f','9b05688c','1f83d9ab','5be0cd19']
    H=[bin(int(i,base=16))[2:] for i in H]
    H=['0'*(32-len(i))+i for i in H]

    if type(m) is not str:
        raise TypeError('Message must be of type str')

    m=bin(int(bytes(m,encoding='utf-8').hex(),base=16))[2:]

    I=bin(len(m))[2:]
    I='0'*(64-len(I))+I

    k=(447-len(m))%512

    m+='1'+'0'*k+I

    M=[[m[i:i+512][32*j:32*(j+1)] for j in range(16)] for i in range(0,len(m),512)]

    for i in range(len(M)):
        W=[M[i][t] for t in range(16)]
        for t in range(16,64):
            w=bin((int(o_1(W[t-2]),base=2)+int(W[t-7],base=2)+int(o_0(W[t-15]),base=2)+int(W[t-16],base=2))%2**32)[2:]
            W.append('0'*(32-len(w))+w)
        a,b,c,d,e,f,g,h=H
        for t in range(64):
            T1=bin((int(h,base=2)+int(E_1(e),base=2)+int(Ch(e,f,g),base=2)+int(K[t],base=2)+int(W[t],base=2))%2**32)[2:]
            T1='0'*(32-len(T1))+T1
            T2=bin((int(E_0(a),base=2)+int(Maj(a,b,c),base=2))%2**32)[2:]
            T2='0'*(32-len(T2))+T2
            h,g,f=g,f,e
            e=bin((int(d,base=2)+int(T1,base=2))%2**32)[2:]
            e='0'*(32-len(e))+e
            d,c,b=c,b,a
            a=bin((int(T1,base=2)+int(T2,base=2))%2**32)[2:]
            a='0'*(32-len(a))+a
        for j in range(8):
            H[j]=bin((int([a,b,c,d,e,f,g,h][i],base=2)+int(H[j],base=2))%2**32)[2:]
            H[j]='0'*(32-len(H[j]))+H[j]
    return ''.join([hex(int(H[i],base=2))[2:] for i in range(len(H))])

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
        embed=discord.Embed(title=hash,color=0x000000)
        embed.set_image(url="https://robohash.org/"+sha(hash)+".png?set=set4")
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True,hidden=True,aliases=["im_nsfw"])
    async def image_nsfw(self,ctx):
        """Retrieve the list of all available NSFW tags"""
        tag_list=await self.bot.ksoft_client.images.tags()
        embed=discord.Embed(timestamp=datetime.utcnow(),color=self.bot.get_color())
        embed.add_field(name="NSFW tags",value='\n'.join(tag_list.nsfw_tags))
        embed.set_author(name=ctx.author.display_name,icon_url=str(ctx.author.avatar_url))
        await ctx.send(embed=embed)

    @commands.command()
    async def monster(self,ctx,*,hash):
        """Get a monster image from an input"""
        embed=discord.Embed(title=hash)
        embed.set_image(url="https://robohash.org/"+sha(hash)+".png?set=set2")
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
        await self.reddit_sender(ctx,await self.bot.ksoft_client.images.random_nsfw())

    @commands.command(ignore_extra=True)
    async def meme(self,ctx):
        """Retrieves a random meme from Reddit"""
        await self.reddit_sender(ctx,await self.bot.ksoft_client.images.random_meme())

    @commands.command(ignore_extra=True)
    async def pat(self,ctx):
        """Get random pat image"""
        await self.image_sender(ctx,await self.rand_im("pat"))

    @commands.command(ignore_extra=True)
    async def pepe(self,ctx):
        """Get random pepe image"""
        await self.image_sender(ctx,await self.rand_im("pepe"))

    @commands.command(enabled=False)
    async def reddit(self,ctx,subreddit): #the Ksoft.SI API used in this command is broken. Waiting for the devs to debug it
        """Retrieve images from the specified subreddit.
        This command may return NSFW results only in NSFW channels"""
        try:
            await self.reddit_sender(ctx,await self.bot.ksoft_client.images.random_reddit(subreddit.split('r/')[-1],remove_nsfw=not check_channel(ctx.channel)))
        except Exception as e:
            await ctx.send(type(e).__name__+' : '+str(e))
            await self.bot.httpcat(ctx,404,"I didn't find any image for your query")

    @commands.command()
    async def robot(self,ctx,*,hash):
        """Get a robot image from an input"""
        embed=discord.Embed(title=hash)
        embed.set_image(url="https://robohash.org/"+sha(hash)+".png?set=set1")
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    async def tickle(self,ctx):
        """Get random tickle image"""
        await self.image_sender(ctx,await self.rand_im("tickle"))

    @commands.command(ignore_extra=True)
    async def wikihow(self,ctx):
        """Retrieves weird images from WikiHow."""
        image=await self.bot.ksoft_client.images.random_wikihow()
        embed=discord.Embed(title=image.title,url=image.article_url,colour=self.bot.colors['blue'])
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def rand_im(self,tag,nsfw=False):
        try:
            return await self.bot.ksoft_client.images.random_image(tag=tag,nsfw=nsfw)
        except:
            return PicError()

    async def image_sender(self,ctx,image):
        """Embeds an image then sends it"""
        if hasattr(image,"code"):
            return await self.bot.httpcat(ctx,image["code"])
        if not image.url:
            return await self.bot.httpcat(ctx,404)
        embed=discord.Embed(title=image.tag,timestamp=datetime.utcnow(),colour=self.bot.colors['blue'])
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def reddit_sender(self,ctx,image):
        """Embeds a Reddit image then sends it"""
        if hasattr(image,"error"):
            return await ctx.send(image.message)
        embed=discord.Embed(title=image.title,url=image.source,timestamp=datetime.fromtimestamp(image.created_at),colour=self.bot.colors['blue'])
        if not image.image_url:
            return await self.bot.httpcat(ctx,404)
        embed.set_image(url=image.image_url)
        embed.set_footer(text=f"👍 {image.upvotes} | 👎 {image.downvotes} | 💬 {image.comments}")
        embed.set_author(name=f"Posted by {image.author} in {image.subreddit}",icon_url="https://i.redd.it/qupjfpl4gvoy.jpg",url=f"https://reddit.com"+image.author)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))
