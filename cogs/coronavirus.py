from discord.ext import commands,tasks
from discord import Embed
from random import choice
from data import data

#coronatracker
from collections import namedtuple
from datetime import datetime
import requests
import aiohttp

TotalStats = namedtuple('TotalStats', 'confirmed deaths recovered')
Country = namedtuple('Country', 'total_stats id last_updated areas name lat long')
SubArea = namedtuple('SubArea', 'total_stats id last_updated areas name lat long')  # for US States etc

class CoronaTracker:
    ENDPOINT = 'https://bing.com/covid/data'
    def __init__(self):
        self.countries = []
        self.total_stats = None

        self._data = {}
        self.__aio_session = None

    def fetch_results(self):
        r = requests.get(self.ENDPOINT)

        self._data = r.json()
        self.countries = self.generate_areas(self._data['areas'])

    async def aio_fetch_results(self):
        if self.__aio_session is None:
            self.__aio_session = aiohttp.ClientSession()

        r = await self.__aio_session.get(self.ENDPOINT)

        self._data = await r.json()
        self.countries = self.generate_areas(self._data['areas'])

    def generate_areas(self, areas, *, cls=Country):
        ret = []

        for area in areas:
            sub_areas = []

            if len(area['areas']) > 0:
                sub_areas = self.generate_areas(area['areas'], cls=SubArea)

            lu = area.get('lastUpdated')
            if lu:
                last_updated = datetime.fromisoformat(area['lastUpdated'][:-1])
            else:
                last_updated = datetime.utcnow()

            ret.append(cls(TotalStats(area['totalConfirmed'], area['totalDeaths'], area['totalRecovered']), area['id'],
                       last_updated, sub_areas, area['displayName'], area['lat'], area['long']))

        return ret

    def get_country(self, name):
        for c in self.countries:
            if c.name == name:
                return c
#coronatracker


before_dict={"é":"e","è":"e","ê":"e","ë":"e","à":"a","ç":"c","â":"a","ä":"a","ñ":"n","ì":"i","à":"a","ù":"u"}

country_dict={"usa":"États-Unis",
"unitedstates":"États-Unis",
"us":"États-Unis",
"etatsunis":"États-Unis",
"italy":"Italie",
"italie":"Italie",
"espagne":"Espagne",
"spain":"Espagne",
"chine":"Chine (continentale)",
"china":"Chine (continentale)",
"allemagne":"Allemagne",
"germany":"Allemagne",
"france":"France",
"iran":"Iran",
"england":"Royaume-Uni",
"unitedkingdom":"Royaume-Uni",
"royaumeuni":"Royaume-Uni",
"suisse":"Suisse",
"switzerland":"Suisse",
"belgique":"Belgique",
"belgium":"Belgique",
"paysbas":"Pays-Bas",
"netherlands":"Pays-Bas",
"turquie":"Turquie",
"turkey":"Turquie",
"coreedusud":"Corée du Sud",
"southkorea":"Corée du Sud",
"autriche":"Autriche",
"austria":"Autriche",
"canada":"Canada",
"portugal":"Portugal",
"israel":"Israël",
"australie":"Australie",
"australia":"Australie",
"norvege":"Norvège",
"norway":"Norvège",
"bresil":"Brésil",
"suede":"Suède",
"sweden":"Suède",
"tchequie":"Tchéquie",
"republiquetcheque":"Tchéquie",
"czech":"Tchéquie",
"czechrepublic":"Tchéquie",
"malaisie":"Malaisie",
"malaysia":"Malaisie",
"irlande":"Irlande",
"ireland":"Irlande",
"danemark":"Danemark",
"denmark":"Danemark",
"chili":"Chili",
"chile":"Chili",
"roumanie":"Roumanie",
"romania":"Roumanie",
"pologne":"Pologne",
"poland":"Pologne",
"luxembourg":"Luxembourg",
"equateur":"Équateur",
"ecuador":"Équateur",
"japon":"Japon",
"japan":"Japon",
"pakistan":"Pakistan",
"russie":"Russie",
"russia":"Russie",
"thailande":"Thaïlande",
"thailand":"Thaïlande",
"philippines":"Philippines",
"arabiesaoudite":"Arabie saoudite",
"saudiarabia":"Arabie saoudite",
"indonesie":"Indonésie",
"indonesia":"Indonésie",
"afriquedusud":"Afrique du Sud",
"southafrica":"Afrique du Sud",
"finlande":"Finlande",
"finland":"Finlande",
"inde":"Inde",
"india":"Inde",
"grece":"Grèce",
"greece":"Grèce",
"islande":"Islande",
"iceland":"Islande",
"panama":"Panama",
"mexique":"Mexique",
"mexico":"Mexique",
"argentine":"Argentine",
"argentina":"Argentine",
"perou":"Pérou",
"peru":"Pérou",
"republiquedominicaine":"République dominicaine",
"dominicanrepublic":"République dominicaine",
"singapour":"Singapour",
"singapore":"Singapour",
"colombie":"Colombie",
"colombia":"Colombie",
"croatie":"Croatie",
"croatia":"Croatie",
"serbie":"Serbie",
"serbia":"Serbie",
"slovenie":"Slovénie",
"solvenia":"Slovénie",
"estonie":"Estonie",
"estonia":"Estonie",
"qatar":"Qatar",
"hongkong":"Hong Kong (R.A.S.)",
"egypte":"Égypte",
"egypt":"Égypte",
"irak":"Irak",
"iraq":"Irak",
"emiratsarabesunis":"Émirats arabes unis",
"unitedarabemirates":"Émirats arabes unis",
"nouvellezelande":"Nouvelle-Zélande",
"newzealand":"Nouvelle-Zélande",
"algerie":"Algérie",
"algeria":"Algérie",
"maroc":"Maroc",
"morocco":"Maroc",
"ukraine":"Ukraine",
"lituanie":"Lituanie",
"lithuania":"Lituanie",
"bahrein":"Bahreïn",
"bahrain":"Bahreïn",
"hongrie":"Hongrie",
"hungary":"Hongrie",
"armenie":"Arménie",
"armenia":"Arménie",
"liban":"Liban",
"lebanon":"Liban",
"lettonie":"Lettonie",
"latvia":"Lettonie",
"bosniehersegovine":"Bosnie-Herzégovine",
"bosniaandherzegovina":"Bosnie-Herzégovine",
"andorre":"Andorre",
"andorra":"Andorre",
"tunisia":"Tunisie",
"tunisie":"Tunisie",
"bulgarie":"Bulgarie",
"bulgaria":"Bulgarie",
"slovaquie":"Slovaquie",
"slovakia":"Slovaquie",
"costarica":"Costa Rica",
"kazakhstan":"Kazakhstan",
"taiwan":"Taïwan",
"uruguay":"Uruguay",
"moldova":"Moldova",
"northmacedonia":"Macédoine du Nord",
"macedoinedunord":"Macédoine du Nord",
"azerbaijan":"Azerbaïdjan",
"azerbaidjan":"Azerbaïdjan",
"jordan":"Jordanie",
"jordanie":"Jordanie",
"kuwait":"Koweït",
"koweit":"Koweït",
"burkinafaso":"Burkina Faso",
"sanmarino":"Saint-Marin",
"saintmarin":"Saint-Marin",
"cyprus":"Chypre",
"chypre":"Chypre",
"reunion":"La Réunion",
"lareunion":"La Réunion",
"albania":"Albanie",
"albanie":"Albanie",
"vietnam":"Vietnam",
"oman":"Oman",
"puertorico":"Porto Rico",
"portorico":"Porto Rico",
"cuba":"Cuba",
"cotedivoire":"Côte d’Ivoire",
"faroeislands":"Îles Féroé",
"ilesferoe":"Îles Féroé",
"senegal":"Sénégal",
"uzbekistan":"Ouzbékistan",
"ouzbekistan":"Ouzbékistan",
"malta":"Malte",
"malte":"Malte",
"ghana":"Ghana",
"belarus":"Bélarus",
"honduras":"Honduras",
"cameroon":"Cameroun",
"cameroun":"Cameroun",
"venezuela":"Venezuela",
"nigeria":"Nigéria",
"mauritius":"Maurice",
"maurice":"Maurice",
"brunei":"Brunéi Darussalam",
"bruneidarussalam":"Brunéi Darussalam",
"srilanka":"Sri Lanka",
"afghanistan":"Afghanistan",
"palestinianauthority":"Autorité palestinienne",
"autoritepalestinienne":"Autorité palestinienne",
"paletine":"Autorité palestinienne",
"cambodia":"Cambodge",
"cambodge":"Cambodge",
"georgia":"Géorgie",
"georgie":"Géorgie",
"guadeloupe":"Guadeloupe",
"kosovo":"Kosovo",
"bolivia":"Bolivie",
"bolivie":"Bolivie",
"kyrgyzstan":"Kirghizistan",
"kirghizistan":"Kirghizistan",
"martinique":"Martinique",
"montenegro":"Monténégro",
"trinidadandtobago":"Trinité-et-Tobago",
"triniteettobago":"Trinité-et-Tobago",
"mayotte":"Mayotte",
"jersey":"Jersey",
"congo":"Congo (RDC)",
"rdc":"Congo (RDC)",
"drc":"Congo (RDC)",
"rwanda":"Rwanda",
"gibraltar":"Gibraltar",
"paraguay":"Paraguay",
"liechtenstein":"Liechtenstein",
"guernsey":"Guernesey",
"guernesey":"Guernesey",
"guam":"Guam",
"aruba":"Aruba",
"kenya":"Kenya",
"isleofman":"Île de Man",
"iledeman":"Île de Man",
"bangladesh":"Bangladesh",
"monaco":"Monaco",
"madagascar":"Madagascar",
"frenchguiana":"Guyane française",
"guyanefrancaise":"Guyane française",
"macau":"Macao (R.A.S.)",
"guatemala":"Guatemala",
"jamaica":"Jamaïque",
"jamaique":"Jamaïque",
"frenchpolynesia":"Polynésie française",
"polynesiefrançaise":"Polynésie française",
"zambia":"Zambie",
"zambie":"Zambie",
"togo":"Togo",
"barbados":"Barbade",
"barbade":"Barbade",
"uganda":"Ouganda",
"ouganda":"Ouganda",
"usvirginislands":"Îles Vierges des États-Unis",
"ilesviergesdesetatsunis":"Îles Vierges des États-Unis",
"elsalvador":"Salvador",
"salvador":"Salvador",
"bermuda":"Bermudes",
"bermudes":"Bermudes",
"niger":"Niger",
"mali":"Mali",
"ethiopia":"Éthiopie",
"ethiopie":"Éthiopie",
"guinea":"Guinée",
"guinee":"Guinée",
"tanzania":"Tanzanie",
"tanzanie":"Tanzanie",
"congo":"Congo",
"djibouti":"Djibouti",
"maldives":"Maldives",
"eritrea":"Érythrée",
"erythree":"Érythrée",
"newcaledonia":"Nouvelle-Calédonie",
"nouvellecaledonie":"Nouvelle-Calédonie",
"bahamas":"Bahamas",
"myanmar":"Myanmar",
"equatorialguinea":"Guinée équatoriale",
"guineeequatoriale":"Guinée équatoriale",
"mongolia":"Mongolie",
"mongolie":"Mongolie",
"caymanislands":"Îles Caïmans",
"ilescaimans":"Îles Caïmans",
"namibia":"Namibie",
"namibie":"Namibie",
"saintmartin":"Saint-Martin",
"curacao":"Curaçao",
"dominica":"Dominique",
"dominique":"Dominique",
"greenland":"Groenland",
"groenland":"Groenland",
"syria":"Syrie",
"syrie":"Syrie",
"grenada":"Grenade",
"grenade":"Grenade",
"eswatini":"Eswatini",
"saintlucia":"Sainte-Lucie",
"saintelucie":"Sainte-Lucie",
"haiti":"Haïti",
"guyana":"Guyana",
"guineabissau":"Guinée-Bissau",
"suriname":"Suriname",
"laos":"Laos",
"seychelles":"Seychelles",
"libya":"Libye",
"libye":"Libye",
"mozambique":"Mozambique",
"angola":"Angola",
"antiguaandbarbuda":"Antigua-et-Barbuda",
"antiguaetbarbuda":"Antigua-et-Barbuda",
"gabon":"Gabon",
"zimbabwe":"Zimbabwe",
"vatican":"État de la Cité du Vatican",
"saintbarthelemy":"Saint-Barthélemy",
"sudan":"Soudan",
"soudan":"Soudan",
"benin":"Bénin",
"caboverde":"Cabo Verde",
"mauritania":"Mauritanie",
"mauritanie":"Mauritanie",
"chad":"Tchad",
"tchad":"Tchad",
"montserrat":"Montserrat",
"fiji":"Fidji",
"fidji":"Fidji",
"turksandcaicosislands":"Îles Turques-et-Caïques",
"ilesturquesetcaiques":"Îles Turques-et-Caïques",
"nepal":"Népal",
"nicaragua":"Nicaragua",
"gambia":"Gambie",
"gambie":"Gambie",
"bhutan":"Bhoutan",
"bhoutan":"Bhoutan",
"somalia":"Somalie",
"somalie":"Somalie",
"liberia":"Libéria",
"belize":"Belize",
"botswana":"Botswana",
"centralafricanrepublic":"République centrafricaine",
"republiquecentrafricaine":"République centrafricaine",
"anguilla":"Anguilla",
"britishvirginislands":"Îles Vierges britanniques",
"ilesviergesbritanniques":"Îles Vierges britanniques",
"northernmarianaislands":"Îles Mariannes du Nord",
"ilesmariannesdunord":"Îles Mariannes du Nord",
"stvincentandthegrenadines":"Saint-Vincent-et-les-Grenadines",
"saintvincentetlesgrenadines":"Saint-Vincent-et-les-Grenadines",
"papuanewguinea":"Papouasie-Nouvelle-Guinée",
"papouasienouvelleguinee":"Papouasie-Nouvelle-Guinée",
"timorleste":"Timor-Leste"
}

def noner(n):
    if n==None:
        return 0
    return n

class Coronavirus(commands.Cog):
    """Pandemy detected"""
    def __init__(self,bot):
        self.bot=bot
        self.corona=CoronaTracker()
        self.fetching=False
        self.corona_update.start()

    @commands.command(aliases=["cv", "corona", "coronavirus"])
    async def covid(self,ctx,*,country):
        """Displays information regarding COVID-19."""
        if self.fetching:
            return await ctx.send("I'm currently updating my database. Please try again in a few seconds")
        country_name=country_dict.get(''.join([before_dict.get(i,i) for i in country.lower()]).replace(' ','').replace("'","").replace("-",""))
        if country_name==None:
            return await self.bot.httpcat(ctx,404,"I don't know this country. Please try again.")
        corona_country=self.corona.get_country(country_name)
        if corona_country==None:
            return await self.bot.httpcat(ctx,404,"I didn't find this country.")
        embed=Embed(title=f"Coronavirus stats for {country}",description=f"Confirmed cases : {noner(corona_country.total_stats.confirmed)}\nDeaths : {noner(corona_country.total_stats.deaths)}\nRecovered : {noner(corona_country.total_stats.recovered)}",colour=data.get_color(),timestamp=corona_country.last_updated)
        for area in corona_country.areas:
            embed.add_field(name=area.name,value=f"Confirmed cases : {noner(area.total_stats.confirmed)}\nDeaths : {noner(area.total_stats.deaths)}\nRecovered : {noner(area.total_stats.recovered)}")
        embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url="https://d3i6fh83elv35t.cloudfront.net/static/2020/01/RTS301GM-1024x576.jpg")
        await ctx.send(embed=embed)

    @tasks.loop(hours=2)
    async def corona_update(self):
        self.fetching=True
        try:
            self.corona.fetch_results()
        except:
            await self.bot.log_channel.send("Error in corona.fetch_results()")
        self.fetching=False

def setup(bot):
    bot.add_cog(Coronavirus(bot))
