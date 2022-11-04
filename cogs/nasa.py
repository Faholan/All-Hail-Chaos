"""MIT License.

Copyright (c) 2020-2022 Faholan

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
SOFTWARE.
"""

import typing as t
from random import choice

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import escape_markdown


class NASA(commands.Cog):
    """It's so easy to hack the NASA."""

    def __init__(self, bot: commands.Bot) -> None:
        """Hack the NASA."""
        self.bot = bot
        self.api_key = bot.raw_config.get("apis", {}).get("nasa")
        if not self.api_key:
            raise ValueError("No NASA API key found")
        self.apod_update.start()
        self.apod_pic = {  # Default picture in case of error
            "hdurl": (
                "https://apod.nasa.gov/apod/image/2004/atmosphere_geo5_"
                "2018235_eq2400.jpg"
            ),
            "title": (
                "Just Another Day on Aerosol Earth - There was an error "
                "while updating the APOD"
            ),
            "explanation": (
                "It was just another day on aerosol Earth. For August 23, "
                "2018, the identification and distribution of aerosols in "
                "the Earth's atmosphere is shown in this dramatic, "
                "planet-wide digital visualization. Produced in real time,"
                " the Goddard Earth Observing System Forward Processing "
                "(GEOS FP) model relies on a combination of "
                "Earth-observing satellite and ground-based data to "
                "calculate the presence of types of aerosols, tiny solid "
                "particles and liquid droplets, as they circulate above "
                "the entire planet. This August 23rd model shows black "
                "carbon particles in red from combustion processes, like "
                "smoke from the fires in the United States and Canada, "
                "spreading across large stretches of North America and "
                "Africa. Sea salt aerosols are in blue, swirling above "
                "threatening typhoons near South Korea and Japan, and the "
                "hurricane looming near Hawaii. Dust shown in purple hues "
                "is blowing over African and Asian deserts. The location "
                "of cities and towns can be found from the concentrations "
                "of lights based on satellite image data of the Earth at "
                "night. Celebrate: Earth Day at Home"
            ),
        }

    @tasks.loop(hours=1)
    async def apod_update(self) -> None:
        """Update the APOD in the cache."""
        async with self.bot.aio_session.get(
            "https://api.nasa.gov/planetary/apod",
            params={"hd": "True", "api_key": self.api_key},
        ) as response:
            if response.status != 200:
                await self.bot.log_channel.send(f"Got a {response.status} from NASA APOD")
                return
            self.apod_pic: t.Dict[
                str, str
            ] = await response.json()  # Update the cache !

    @app_commands.command()
    async def apod(self, interaction: discord.Interaction) -> None:
        """Get the Astronomy Picture Of The Day."""
        embed = discord.Embed(
            title=self.apod_pic.get("title", "Astronomy Picture Of the Day"),
            description=self.apod_pic.get("explanation", None),
            colour=discord.Colour.purple(),
        )
        if self.apod_pic.get("media_type") == "video":
            # Extract information from the data, & do things with it
            if "embed" in self.apod_pic.get("url", "nope"):
                preview = self.apod_pic.get("url", "").split("/")[-1].split("?")[0]
            else:
                preview = self.apod_pic.get("url", "").split("=")[-1]
            embed.set_image(url=f"https://img.youtube.com/vi/{preview}/hqdefault.jpg")
            if embed.description is None:
                embed.description = ""
            embed.description += (
                "\nWatch the video using [This link]("
                f'{self.apod_pic.get("url")} "{self.apod_pic.get("title")}")'
            )
        else:
            embed.set_image(
                url=self.apod_pic.get("hdurl", self.apod_pic.get("url")),
            )
        embed.set_author(name=self.apod_pic.get("copyright", "NASA's APOD"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def epic(
        self,
        interaction: discord.Interaction,
        max_n: app_commands.Range[int, 1, 10] = 1,
    ) -> None:
        """Retrieve images from DSCOVR's Earth Polychromatic Imaging Camera.

        You can specify a maximum number of images to retrieve (default : 1)
        """
        async with self.bot.aio_session.get(
            "https://epic.gsfc.nasa.gov/api/images.php"
        ) as response:
            if response.status != 200:
                await interaction.response.send_message(
                    "Houston, we have a problem. NASA is not responding.",
                    ephemeral=True,
                )
                await self.bot.log_channel.send(f"Got a {response.status} from NASA EPIC")
                return
            json: t.List[t.Dict[str, str]] = await response.json()
            embeds = []

            for i in range(min(max_n, len(json))):
                embed = discord.Embed(
                    title="EPIC image",
                    description=json[i].get("caption"),
                    colour=discord.Colour.blurple(),
                )
                embed.set_image(
                    url=(
                        "https://epic.gsfc.nasa.gov/epic-archive/jpg/"
                        f"{json[i]['image']}.jpg"
                    )
                )
                embeds.append(embed)
            if embeds:
                await interaction.response.send_message(embeds=embeds)
            else:
                await interaction.response.send_message("No images found")

    @app_commands.command()
    async def mars(
        self,
        interaction: discord.Interaction,
        date: str,
        rover: t.Optional[str] = None,
        number: app_commands.Range[int, 1, 10] = 1,
    ) -> None:
        """Get images from Mars.

        You must specify the date (in the form YYYY-MM-DD)
        You can specify the rover (one of Curiosity, Opportunity and Spirit)
        You can also enter the number of images to retrieve (default : 1)
        """
        if rover is None:
            rover = choice(("curiosity", "opportunity", "spirit"))

        if rover.lower() not in {"curiosity", "opportunity", "spirit"}:
            await interaction.response.send_message(
                "Sorry but this rover doesn't exist"
            )
            return
        async with self.bot.aio_session.get(
            "https://api.nasa.gov/mars-photos/api/v1/rovers/"
            + rover.lower()
            + "/photos",
            params={"earth_date": date, "api_key": self.api_key},
        ) as response:
            if response.status != 200:
                await interaction.response.send_message(
                    "Houston, we have a problem. NASA is not responding.",
                    ephemeral=True,
                )
                await self.bot.log_channel.send(
                    f"Got a {response.status} from NASA MARS\n"
                    f"Date: {date}\nRover: {rover}\nNumber: {number}"
                )
                return

            images = await response.json()
            if not images.get("photos"):
                await self.bot.httpcat(
                    interaction,
                    404,
                    "I didn't find anything for your query. It's probably "
                    f"because the rover {rover.capitalize()} wasn't in "
                    "activity at this time",
                )
                return
            embeds = []
            for i in range(min(number, len(images["photos"]))):
                embed = discord.Embed(
                    title=f"Picture from {rover.capitalize()}",
                    description=(
                        "Picture taken from the "
                        + images["photos"][i]["camera"]["full_name"]
                    ),
                    colour=discord.Colour.purple(),
                )
                embed.set_image(url=images["photos"][i]["img_src"])
                embed.set_footer(
                    text="Picture taken on" + images["photos"][i]["earth_date"]
                )
                embeds.append(embed)
            await interaction.response.send_message(embeds=embeds)

    @app_commands.command()
    async def nasasearch(self, interaction: discord.Interaction, *, query: str) -> None:
        """Search for an image in the NASA database."""
        async with self.bot.aio_session.get(
            "https://images-api.nasa.gov/search",
            params={"q": query, "media_type": "image"},
        ) as response:
            if response.status != 200:
                await interaction.response.send_message(
                    "Houston, we have a problem. NASA is not responding.",
                    ephemeral=True,
                )
                await self.bot.log_channel.send(
                    f"Got a {response.status} from NASA Search\nQuery: {query}"
                )
                return

            jresult = await response.json()
        try:
            data = jresult["collection"]["items"][0]["data"][0]
        except (KeyError, IndexError):
            await interaction.response.send_message(
                f"I didn't find anything for your query `{escape_markdown(query)}`"
            )
            return
        converter = self.bot.markdownhtml()
        description = converter.feed(data["description"])
        if len(description) > 2048:
            description = f"{description[:2045].strip()}..."
        embed = discord.Embed(
            title=data["title"],
            description=description,
            colour=discord.Colour.blurple(),
            url=f"https://images.nasa.gov/details-{data['nasa_id']}",
        )
        async with self.bot.aio_session.get(
            "https://images-api.nasa.gov/asset/" + data["nasa_id"]
        ) as imageq:
            imagej = await imageq.json()
        embed.set_image(url=imagej["collection"]["items"][0]["href"])
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Load the NASA cog."""
    await bot.add_cog(NASA(bot))
