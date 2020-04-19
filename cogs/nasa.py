from discord.ext import commands, tasks
import discord
import requests
from random import choice

class NASA(commands.Cog):
    """It's so easy to hack the NASA"""
    def __init__(self,bot):
        self.bot=bot
        self.api_key=bot.nasa
        self.apod_update.start()

    @tasks.loop(hours=1)
    async def apod_update(self):
        R=requests.get("https://api.nasa.gov/planetary/apod",{"hd":True,"api_key":self.api_key})
        self.apod=R.json()

    @commands.command(ignore_extra=True)
    async def apod(self,ctx):
        """Get the Astronomy Picture Of The Day"""
        embed=discord.Embed(title=self.apod.get("title","Astronomy Picture Of the Day"),description=self.apod.get("explanation"),colour=self.bot.get_color())
        embed.set_image(url=self.apod.get("hdurl"))
        embed.set_author(name=self.apod.get("copyright","NASA's APOD"))
        await ctx.send(embed=embed)

    @commands.command()
    async def epic(self,ctx,Max:int=1):
        """Retrieve images from DSCOVR's Earth Polychromatic Imaging Camera. You can specify a maximum number of images to retrieve (default : 1)"""
        r=requests.get("https://epic.gsfc.nasa.gov/api/images.php").json()
        for i in range(min(Max,len(r))):
            embed=discord.Embed(title="EPIC image",description=r[i].get("caption"),colour=self.bot.get_color())
            embed.set_image(url="https://epic.gsfc.nasa.gov/epic-archive/jpg/"+r[i]["image"]+".jpg")
            await ctx.send(embed=embed)

    @commands.command()
    async def mars(self,ctx,date,rover=choice(("curiosity","opportunity","spirit")),n=1):
        """Get images from Mars. You must specify the date (in the form YYYY-MM-DD), and you can specify the rover (one of Curiosity, Opportunity and Spirit) and the number of images to retrieve (default : 1)"""
        if not rover.lower() in ("curiosity","opportunity","spirit"):
            return await ctx.send("Sorry but this rover doesn't exist")
        if " " in date:
            return await ctx.send("The date cannot contain whitespasces")
        r=requests.get("https://api.nasa.gov/mars-photos/api/v1/rovers/"+rover.lower()+"/photos",{"earth_date":date,"api_key":self.api_key})
        images=r.json()
        if images.get("photos",[])==[]:
            return await ctx.send("I didn't find anything for your query")
        for i in range(min(n,len(images["photos"]))):
            embed=discord.Embed(title="Picture from "+rover.capitalize(),description="Picture taken from the "+images["photos"][i]["camera"]["full_name"],colour=self.bot.get_color())
            embed.set_image(url=images["photos"][i]["img_src"])
            embed.set_footer(text="Picture taken on"+images["photos"][i]["earth_date"])
            await ctx.send(embed=embed)

    @commands.command()
    async def nasasearch(self,ctx,*,query):
        """Search for an image in the NASA database"""
        result=requests.get("https://images-api.nasa.gov/search",{"q":query,"media_type":"image"})
        jresult=result.json()
        data=jresult["collection"]["items"][0]["data"][0]
        embed=discord.Embed(title=data["title"],description=data["description"],colour=self.bot.get_color())
        imageq=requests.get("https://images-api.nasa.gov/asset/"+data["nasa_id"])
        imagej=imageq.json()
        embed.set_image(url=imagej["collection"]["items"][0]["href"])
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(NASA(bot))
