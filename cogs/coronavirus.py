from discord.ext import commands,tasks
from discord import Embed, utils
from random import choice
from data import data
import traceback

#coronatracker
from collections import namedtuple
from datetime import datetime
import requests

TotalStats = namedtuple('TotalStats', 'confirmed deaths recovered')
Country = namedtuple('Country', 'total_stats id last_updated areas name lat long')
SubArea = namedtuple('SubArea', 'total_stats id last_updated areas name lat long')  # for US States etc

class CoronaTracker:
    ENDPOINT = 'https://api.covid19api.com/summary'
    def __init__(self,bot):
        self.bot = bot
        self.countries = []
        self.total_stats = None

    async def fetch_results(self):
        async with self.bot.aio_session.get(self.ENDPOINT) as r:
            if r.status==200:
                _data=await r.json()

                self.total_stats = _data["Global"]

                self.countries = _data["Countries"]
            else:
                embed=Embed(title=f"Error {r.status} in fetch_results() :",description=await r.text(),color=self.bot.colors['red'])
                await self.bot.log_channel.send(embed=embed)

    def get_country(self,country):
        return utils.find(lambda c:c["Slug"]==country,self.countries)

#coronatracker


before_dict={"é":"e","è":"e","ê":"e","ë":"e","à":"a","ç":"c","â":"a","ä":"a","ñ":"n","ì":"i","à":"a","ù":"u"}

country_dict={"usa":"united-states",
"unitedstates":"united-states",
"us":"united-states",
"etatsunis":"united-states",
"italie":"italy",
"espagne":"spain",
"spain":"spain",
"chine":"china",
"allemagne":"germany",
"england":"united-kingdom",
"unitedkingdom":"united-kingdom",
"royaumeuni":"united-kingdom",
"suisse":"switzerland",
"belgique":"belgium",
"paysbas":"netherlands",
"turquie":"turkey",
"coreedusud":"korea-south",
"southkorea":"korea-south",
"autriche":"austria",
"australie":"australia",
"norvege":"norway",
"bresil":"brazil",
"suede":"sweden",
"tchequie":"czech-republic",
"republiquetcheque":"czech-republic",
"czech":"czech-republic",
"czechrepublic":"czech-republic",
"malaisie":"malaysia",
"irlande":"ireland",
"danemark":"denmark",
"chili":"chile",
"roumanie":"romania",
"pologne":"poland",
"equateur":"ecuador",
"japon":"japan",
"russie":"russia",
"thailande":"thailand",
"arabiesaoudite":"saudi-arabia",
"saudiarabia":"saudi-arabiae",
"indonesie":"indonesia",
"afriquedusud":"south-africa",
"southafrica":"south-africa",
"finlande":"finland",
"inde":"india",
"grece":"greece",
"islande":"iceland",
"mexique":"mexico",
"argentine":"argentina",
"perou":"peru",
"republiquedominicaine":"dominican-republic",
"dominicanrepublic":"dominican-republic",
"singapour":"singapore",
"colombie":"colombia",
"croatie":"croatia",
"serbie":"serbia",
"slovenie":"slovenia",
"estonie":"estonia",
"hongkong":"hong-kong-sar-china",
"egypte":"egypt",
"irak":"iraq",
"emiratsarabesunis":"united-arab-emirates",
"unitedarabemirates":"united-arab-emirates",
"nouvellezelande":"new-zealand",
"newzealand":"new-zealand",
"algerie":"algeria",
"maroc":"morocco",
"lituanie":"lithuania",
"bahrein":"bahrain",
"hongrie":"hungary",
"armenie":"armenia",
"liban":"lebanon",
"lettonie":"latvia",
"bosniehersegovine":"bosnia-and-herzegovina",
"bosniaandherzegovina":"bosnia-and-herzegovina",
"andorre":"andorra",
"tunisie":"tunisia",
"bulgarie":"bulgaria",
"slovaquie":"slovakia",
"costarica":"costa-rica",
"macedoine":"macedonia",
"azerbaidjan":"azerbaijan",
"jordanie":"jordan",
"koweit":"kuwait",
"burkinafaso":"burkina-faso",
"sanmarino":"san-marino",
"saintmarin":"san-marino",
"chypre":"cyprus",
"reunion":"réunion",
"lareunion":"réunion",
"albanie":"albania",
"puertorico":"puerto-rico",
"portorico":"puerto-rico",
"cotedivoire":"cote-divoire",
"faroeislands":"faroe-islands",
"ilesferoe":"faroe-islands",
"ouzbekistan":"uzbekistan",
"malte":"malta",
"cameroun":"cameroon",
"maurice":"mauritius",
"bruneidarussalam":"brunei",
"srilanka":"sri-lanka",
"cambodge":"cambodia",
"georgie":"georgia",
"bolivie":"bolivia",
"kirghizistan":"kyrgyzstan",
"trinidadandtobago":"trinidad-and-tobago",
"triniteettobago":"trinidad-and-tobago",
"guernesey":"guernsey",
"isleofman":"isle-of-man",
"iledeman":"isle-of-man",
"frenchguiana":"french-guiana",
"guyanefrancaise":"french-guiana",
"macau":"macao-sar-china",
"macao":"macao-sar-china",
"jamaique":"jamaica",
"frenchpolynesia":"french-polynesia",
"polynesiefrançaise":"french-polynesia",
"zambie":"zambia",
"barbade":"barbados",
"ouganda":"uganda",
"virginislands":"virgin-islands",
"ilesvierges":"virgin-islands",
"elsalvador":"el-salvador",
"salvador":"el-salvador",
"bermudes":"bermuda",
"ethiopie":"ethiopia",
"guinee":"guinea",
"tanzanie":"tanzania",
"erythree":"eritrea",
"newcaledonia":"new-caledonia",
"nouvellecaledonie":"new-caledonia",
"equatorialguinea":"equatorial-guinea",
"guineeequatoriale":"equatorial-guinea",
"mongolie":"mongolia",
"caymanislands":"cayman-islands",
"ilescaimans":"cayman-islands",
"namibie":"namibia",
"dominique":"dominica",
"groenland":"greenland",
"syrie":"syria",
"grenade":"grenada",
"saintlucia":"saint-lucia",
"saintelucie":"saint-lucia",
"guineabissau":"guinea-bissau",
"libye":"libya",
"antiguaandbarbuda":"antigua-and-barbuda",
"antiguaetbarbuda":"antigua-and-barbuda",
"vatican":"holy-see-vatican-city-state",
"saintbarthelemy":"saint-barthélemy",
"soudan":"sudan",
"capeverde":"cape-verde",
"mauritanie":"mauritania",
"tchad":"chad",
"fidji":"fiji",
"turksandcaicosislands":"turks-and-caicos-islands",
"ilesturquesetcaiques":"turks-and-caicos-islands",
"gambie":"gambia",
"bhoutan":"bhutan",
"somalie":"somalia",
"centralafricanrepublic":"central-african-republic",
"republiquecentrafricaine":"central-african-republic",
"britishvirginislands":"british-virgin-islands",
"ilesviergesbritanniques":"british-virgin-islands",
"northernmarianaislands":"northern-mariana-islands",
"ilesmariannesdunord":"northern-mariana-islands",
"stvincentandthegrenadines":"saint-vincent-and-the-grenadines",
"saintvincentetlesgrenadines":"saint-vincent-and-the-grenadines",
"papuanewguinea":"papua-new-guinea",
"papouasienouvelleguinee":"papua-new-guinea",
"timorleste":"timor-leste"
}

class Coronavirus(commands.Cog):
    """Pandemy detected"""
    def __init__(self,bot):
        self.bot=bot
        self.corona=CoronaTracker(bot)
        self.fetching=False
        self.corona_update.start()

    @commands.command(aliases=["cv", "corona", "coronavirus"])
    async def covid(self,ctx,*,country):
        """Displays information regarding COVID-19."""
        if self.fetching:
            return await ctx.send("I'm currently updating my database. Please try again in a few seconds")
        country_name=country_dict.get(''.join([before_dict.get(i,i) for i in country.lower()]).replace(' ','').replace("'","").replace("-",""),''.join([before_dict.get(i,i) for i in country.lower()]).replace(' ','').replace("'","").replace("-",""))
        corona_country=self.corona.get_country(country_name)
        if corona_country==None:
            return await self.bot.httpcat(ctx,404,"I didn't find this country.")
        embed=Embed(title=f"Coronavirus stats for {country}",colour=self.bot.colors['blue'])
        embed.add_field(name="Confirmed cases",value=corona_country.get("TotalRecovered",0))
        embed.add_field(name="Deaths",value=corona_country.get("TotalDeaths",0))
        embed.add_field(name="Recovered",value=corona_country.get("TotalRecovered",0))
        embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url="https://d3i6fh83elv35t.cloudfront.net/static/2020/01/RTS301GM-1024x576.jpg")
        await ctx.send(embed=embed)

    @tasks.loop(minutes=30)
    async def corona_update(self):
        self.fetching=True
        try:
            await self.corona.fetch_results()
        except Exception as error:
            embed = Embed(color=0xFF0000)
            embed.title = f"Error in corona.fetch_results()"
            embed.description = type(error).__name__+" : "+str(error)
            tb = "".join(traceback.format_tb(error.__traceback__))
            embed.description += f"```\n{tb}```"
            embed.set_footer(text=f"{self.bot.user.name} Logging", icon_url=self.bot.user.avatar_url_as(static_format="png"))
            embed.timestamp = datetime.utcnow()
            await self.bot.log_channel.send(embed=embed)
        self.fetching=False

def setup(bot):
    bot.add_cog(Coronavirus(bot))
