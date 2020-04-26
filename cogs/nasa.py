from discord.ext import commands, tasks
import discord
from random import choice

class NASA(commands.Cog):
    """It's so easy to hack the NASA"""
    def __init__(self,bot):
        self.bot=bot
        self.api_key=bot.nasa
        self.apod_update.start()
        self.apod_pic={"hdurl":"https://apod.nasa.gov/apod/image/2004/atmosphere_geo5_2018235_eq2400.jpg","title":"Just Another Day on Aerosol Earth - There was an error while updating the APOD","explanation":"It was just another day on aerosol Earth. For August 23, 2018, the identification and distribution of aerosols in the Earth's atmosphere is shown in this dramatic, planet-wide digital visualization. Produced in real time, the Goddard Earth Observing System Forward Processing (GEOS FP) model relies on a combination of Earth-observing satellite and ground-based data to calculate the presence of types of aerosols, tiny solid particles and liquid droplets, as they circulate above the entire planet. This August 23rd model shows black carbon particles in red from combustion processes, like smoke from the fires in the United States and Canada, spreading across large stretches of North America and Africa. Sea salt aerosols are in blue, swirling above threatening typhoons near South Korea and Japan, and the hurricane looming near Hawaii. Dust shown in purple hues is blowing over African and Asian deserts. The location of cities and towns can be found from the concentrations of lights based on satellite image data of the Earth at night. Celebrate: Earth Day at Home"}

    @tasks.loop(hours=1)
    async def apod_update(self):
        async with self.bot.aio_session.get("https://api.nasa.gov/planetary/apod",params={"hd":"True","api_key":self.api_key}) as response:
            self.apod_pic=await response.json()

    @commands.command(ignore_extra=True)
    async def apod(self,ctx):
        """Get the Astronomy Picture Of The Day"""
        embed=discord.Embed(title=self.apod_pic.get("title","Astronomy Picture Of the Day"),description=self.apod_pic.get("explanation"),colour=self.bot.get_color())
        if self.apod_pic.get('media_type')=='video':
            if 'embed' in self.apod_pic.get('url','nope'):
                embed.set_image(url=f"https://img.youtube.com/vi/{self.apod_pic.get('url').split('/')[-1].split('?')[0]}/mqdefault.jpg")
            else:
                embed.set_image(url=f"https://img.youtube.com/vi/{self.apod_pic.get('url').split('=')[-1]}/mqdefault.jpg")
            embed.description+=f'\nWatch the video using [This link]({self.apod_pic.get("url")} "{self.apod_pic.get("title")}")'
        else:
            embed.set_image(url=self.apod_pic.get("hdurl",self.apod_pic.get("url")))
        embed.set_author(name=self.apod_pic.get("copyright","NASA's APOD"))
        await ctx.send(embed=embed)

    @commands.command()
    async def epic(self,ctx,Max:int=1):
        """Retrieve images from DSCOVR's Earth Polychromatic Imaging Camera. You can specify a maximum number of images to retrieve (default : 1)"""
        async with self.bot.aio_session.get("https://epic.gsfc.nasa.gov/api/images.php") as response:
            json=await response.json()
            for i in range(min(Max,len(json))):
                embed=discord.Embed(title="EPIC image",description=json[i].get("caption"),colour=self.bot.get_color())
                embed.set_image(url="https://epic.gsfc.nasa.gov/epic-archive/jpg/"+json[i]["image"]+".jpg")
                await ctx.send(embed=embed)

    @commands.command()
    async def mars(self,ctx,date,rover=choice(("curiosity","opportunity","spirit")),n=1):
        """Get images from Mars. You must specify the date (in the form YYYY-MM-DD), and you can specify the rover (one of Curiosity, Opportunity and Spirit) and the number of images to retrieve (default : 1)"""
        if not rover.lower() in ("curiosity","opportunity","spirit"):
            return await ctx.send("Sorry but this rover doesn't exist")
        if " " in date:
            return await ctx.send("The date cannot contain whitespasces")
        async with self.bot.aio_session.get("https://api.nasa.gov/mars-photos/api/v1/rovers/"+rover.lower()+"/photos",params={"earth_date":date,"api_key":self.api_key}) as response:
            images=await response.json()
            if images.get("photos",[])==[]:
                return await self.bot.httpcat(404,"I didn't find anything for your query")
            for i in range(min(n,len(images["photos"]))):
                embed=discord.Embed(title="Picture from "+rover.capitalize(),description="Picture taken from the "+images["photos"][i]["camera"]["full_name"],colour=self.bot.get_color())
                embed.set_image(url=images["photos"][i]["img_src"])
                embed.set_footer(text="Picture taken on"+images["photos"][i]["earth_date"])
                await ctx.send(embed=embed)

    @commands.command()
    async def nasasearch(self,ctx,*,query):
        """Search for an image in the NASA database"""
        async with self.bot.aio_session.get("https://images-api.nasa.gov/search",params={"q":query,"media_type":"image"}) as result:
            jresult=await result.json()
        data=jresult["collection"]["items"][0]["data"][0]
        embed=discord.Embed(title=data["title"],description=data["description"],colour=self.bot.get_color())
        async with self.bot.aio_session.get("https://images-api.nasa.gov/asset/"+data["nasa_id"]) as imageq:
            imagej=await imageq.json()
        embed.set_image(url=imagej["collection"]["items"][0]["href"])
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(NASA(bot))