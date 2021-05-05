"""MIT License.

Copyright (c) 2020-2021 Faholan

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

from datetime import datetime

import discord
from discord.ext import commands


def check_channel(channel: discord.abc.Messageable) -> bool:
    """Check for NSFW rights."""
    if isinstance(channel, discord.TextChannel):
        return channel.is_nsfw()
    return True


def sha(message: str) -> str:
    """Use SHA-256 to hash a string."""

    def sha_et(part1: str, part2: str) -> str:
        return "".join(
            [str(int(part1[i]) and int(part2[i])) for i in range(len(part1))]
        )

    def sha_ou(part1: str, part2: str) -> str:
        return "".join([str(int(part1[i]) or int(part2[i])) for i in range(len(part1))])

    def sha_xor(part1: str, part2: str) -> str:
        return "".join([str(int(part1[i]) ^ int(part2[i])) for i in range(len(part1))])

    def complement(part1: str) -> str:
        return "".join([str((int(part1[i]) + 1) % 2) for i in range(len(part1))])

    def dec_g(part1: str, number: int) -> str:
        return part1[number:] + "0" * number

    def dec_d(part1: str, number: int) -> str:
        return "0" * number + part1[: len(part1) - number]

    def sha_shr(number: int, part1: str) -> str:
        return dec_g(part1, number)

    def sha_rotr(number: int, part1: str) -> str:
        return sha_ou(dec_d(part1, number), dec_g(part1, 32 - number))

    def sha_ch(part1: str, part2: str, part3: str) -> str:
        return sha_xor(sha_et(part1, part2), sha_et(complement(part1), part3))

    def sha_maj(part1: str, part2: str, part3: str) -> str:
        return sha_xor(
            sha_xor(sha_et(part1, part2), sha_et(part1, part3)),
            sha_et(part2, part3),
        )

    def sha_e_0(part1: str) -> str:
        return sha_xor(
            sha_xor(sha_rotr(2, part1), sha_rotr(13, part1)),
            sha_rotr(22, part1),
        )

    def sha_e_1(part1: str) -> str:
        return sha_xor(
            sha_xor(sha_rotr(6, part1), sha_rotr(11, part1)),
            sha_rotr(25, part1),
        )

    def sha_o_0(part1: str) -> str:
        return sha_xor(
            sha_xor(sha_rotr(7, part1), sha_rotr(18, part1)),
            sha_shr(3, part1),
        )

    def sha_o_1(part1: str) -> str:
        return sha_xor(
            sha_xor(sha_rotr(17, part1), sha_rotr(19, part1)),
            sha_shr(10, part1),
        )

    constants_k = [
        "428a2f98",
        "71374491",
        "b5c0fbcf",
        "e9b5dba5",
        "3956c25b",
        "59f111f1",
        "923f82a4",
        "ab1c5ed5",
        "d807aa98",
        "12835b01",
        "243185be",
        "550c7dc3",
        "72be5d74",
        "80deb1fe",
        "9bdc06a7",
        "c19bf174",
        "e49b69c1",
        "efbe4786",
        "0fc19dc6",
        "240ca1cc",
        "2de92c6f",
        "4a7484aa",
        "5cb0a9dc",
        "76f988da",
        "983e5152",
        "a831c66d",
        "b00327c8",
        "bf597fc7",
        "c6e00bf3",
        "d5a79147",
        "06ca6351",
        "14292967",
        "27b70a85",
        "2e1b2138",
        "4d2c6dfc",
        "53380d13",
        "650a7354",
        "766a0abb",
        "81c2c92e",
        "92722c85",
        "a2bfe8a1",
        "a81a664b",
        "c24b8b70",
        "c76c51a3",
        "d192e819",
        "d6990624",
        "f40e3585",
        "106aa070",
        "19a4c116",
        "1e376c08",
        "2748774c",
        "34b0bcb5",
        "391c0cb3",
        "4ed8aa4a",
        "5b9cca4f",
        "682e6ff3",
        "748f82ee",
        "78a5636f",
        "84c87814",
        "8cc70208",
        "90befffa",
        "a4506ceb",
        "bef9a3f7",
        "c67178f2",
    ]
    constants_k = [bin(int(i, base=16))[2:] for i in constants_k]
    constants_k = ["0" * (32 - len(i)) + i for i in constants_k]

    list_h = [
        "6a09e667",
        "bb67ae85",
        "3c6ef372",
        "a54ff53a",
        "510e527f",
        "9b05688c",
        "1f83d9ab",
        "5be0cd19",
    ]
    list_h = [bin(int(i, base=16))[2:] for i in list_h]
    list_h = ["0" * (32 - len(i)) + i for i in list_h]

    if not isinstance(message, str):
        raise TypeError("Message must be of type str")

    message = bin(int(bytes(message, encoding="utf-8").hex(), base=16))[2:]

    completion = bin(len(message))[2:]
    completion = "0" * (64 - len(completion)) + completion

    message += "1" + "0" * ((447 - len(message)) % 512) + completion

    M = [
        [message[i: i + 512][32 * j: 32 * (j + 1)] for j in range(16)]
        for i in range(0, len(message), 512)
    ]

    for i in range(len(M)):
        W = [M[i][t] for t in range(16)]
        for t in range(16, 64):
            w = bin(
                (
                    int(sha_o_1(W[t - 2]), base=2)
                    + int(W[t - 7], base=2)
                    + int(sha_o_0(W[t - 15]), base=2)
                    + int(W[t - 16], base=2)
                )
                % 2 ** 32
            )[2:]
            W.append("0" * (32 - len(w)) + w)
        a, b, c, d, e, f, g, h = list_h
        for t in range(64):
            T1 = bin(
                (
                    int(h, base=2)
                    + int(sha_e_1(e), base=2)
                    + int(sha_ch(e, f, g), base=2)
                    + int(constants_k[t], base=2)
                    + int(W[t], base=2)
                )
                % 2 ** 32
            )[2:]
            T1 = "0" * (32 - len(T1)) + T1
            T2 = bin(
                (int(sha_e_0(a), base=2) + int(sha_maj(a, b, c), base=2)) % 2 ** 32
            )[2:]
            T2 = "0" * (32 - len(T2)) + T2
            h, g, f = g, f, e
            e = bin((int(d, base=2) + int(T1, base=2)) % 2 ** 32)[2:]
            e = "0" * (32 - len(e)) + e
            d, c, b = c, b, a
            a = bin((int(T1, base=2) + int(T2, base=2)) % 2 ** 32)[2:]
            a = "0" * (32 - len(a)) + a
        for j in range(8):
            list_h[j] = bin(
                (int([a, b, c, d, e, f, g, h][i], base=2) + int(list_h[j], base=2))
                % 2 ** 32
            )[2:]
            list_h[j] = "0" * (32 - len(list_h[j])) + list_h[j]
    return "".join([hex(int(list_h[i], base=2))[2:] for i in range(len(list_h))])


class Pic:
    """Picture placeholder."""

    def __init__(self, url, tag) -> None:
        """Initialize the "picture"."""
        self.url = url
        self.tag = tag


class PicError:
    """Error for pics."""

    def __init__(self) -> None:
        """Initialize the error."""
        self.code = 404


class Redditwrapper:
    """Wrap a reddit post in a class structure."""

    def __init__(self, json: dict):
        if json.get("error"):
            self.error = json["error"]
            self.code = json.get("code")
            self.message = json.get("message", "Error")
        elif json.get("detail"):
            self.error = True
            self.message = json["detail"]
        else:
            self.title = json["title"]
            self.image_url = json["image_url"]
            self.source = json["source"]
            self.subreddit = json["subreddit"]
            self.upvotes = json.get("upvotes", 0)
            self.downvotes = json.get("downvotes", 0)
            self.comments = json.get("comments", 0)
            self.created_at = json["created_at"]
            self.nsfw = json["nsfw"]
            self.author = json["author"]


class Images(commands.Cog):  # Thanks KSoft.si
    """Commands to get random images.

    You can try using the nsfw command, if you dare
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Images."""
        self.bot = bot

    @commands.command(ignore_extra=True)
    async def dab(self, ctx: commands.Context) -> None:
        """Get a random dab image."""
        await self.image_sender(ctx, await self.rand_im("dab"))

    @commands.command(ignore_extra=True)
    async def doge(self, ctx: commands.Context) -> None:
        """Get a random doge image."""
        await self.image_sender(ctx, await self.rand_im("doge"))

    @commands.command(ignore_extra=True)
    async def fbi(self, ctx: commands.Context) -> None:
        """Get a random FBI image."""
        await self.image_sender(ctx, await self.rand_im("fbi"))

    @commands.command(ignore_extra=True, hidden=True)
    @commands.is_nsfw()
    async def hentai(self, ctx: commands.Context) -> None:
        """Get a random hentai image."""
        await self.image_sender(ctx, await self.rand_im("hentai", True))

    @commands.command(ignore_extra=True, hidden=True)
    @commands.is_nsfw()
    async def hentai_gif(self, ctx: commands.Context) -> None:
        """Get a random hentai GIF."""
        await self.image_sender(ctx, await self.rand_im("hentai_gif", True))

    @commands.command(ignore_extra=True)
    async def hug(self, ctx: commands.Context) -> None:
        """Get a random hug image."""
        await self.image_sender(ctx, await self.rand_im("hug"))

    @commands.command(ignore_extra=True)
    async def kappa(self, ctx: commands.Context) -> None:
        """Get a random kappa image."""
        await self.image_sender(ctx, await self.rand_im("kappa"))

    @commands.command()
    async def koala(self, ctx) -> None:
        """Get a random picture of a koala."""
        async with self.bot.aio_session.get(
            "https://some-random-api.ml/img/koala"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    title="Random Koala", colour=discord.Colour.gold()
                )
                embed.set_image(url=data["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send("Something went wrong.")
                await self.bot.log_channel.send(f"Code {resp.status} in koala")

    @commands.command(ignore_extra=True)
    async def kiss(self, ctx: commands.Context) -> None:
        """Get a random kiss image."""
        await self.image_sender(ctx, await self.rand_im("kiss"))

    @commands.command(ignore_extra=True, hidden=True, aliases=["im_nsfw"])
    async def image_nsfw(self, ctx: commands.Context) -> None:
        """Retrieve the list of all available NSFW tags."""
        tag_list = await self.bot.ksoft_client.images.tags()
        embed = discord.Embed(
            timestamp=datetime.utcnow(), colour=discord.Colour.random()
        )
        embed.add_field(name="NSFW tags", value="\n".join(tag_list.nsfw_tags))
        embed.set_author(
            name=ctx.author.display_name, icon_url=str(ctx.author.avatar_url)
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def monster(self, ctx: commands.Context, *, hashed: str) -> None:
        """Get a monster image from an input."""
        embed = discord.Embed(title=hashed)
        embed.set_image(url=f"https://robohash.org/{sha(hashed)}.png?set=set2")
        await ctx.send(embed=embed)

    @commands.command(hidden=True, ignore_extra=True)
    @commands.is_nsfw()
    async def neko(self, ctx: commands.Context) -> None:
        """Get a random neko image."""
        await self.image_sender(ctx, await self.rand_im("neko", nsfw=True))

    @commands.command(hidden=True, ignore_extra=True)
    @commands.is_nsfw()
    async def nsfw(self, ctx: commands.Context) -> None:
        """Retrieve random NSFW pics.

        To find the other NSFW commands :
        use im_nsfw or reddit with an NSFW subreddit
        """
        async with self.bot.aio_session.get(
            "https://api.ksoft.si/images/random-nsfw",
            headers={"Authorization": f"Bearer {self.bot.ksoft_client.api_key}"},
        ) as response:
            await self.reddit_sender(
                ctx,
                Redditwrapper(await response.json()),
            )

    @commands.command(ignore_extra=True)
    async def meme(self, ctx: commands.Context) -> None:
        """Retrieve a random meme from Reddit."""
        await self.reddit_sender(
            ctx,
            await self.bot.ksoft_client.images.random_meme(),
        )

    @commands.command(ignore_extra=True)
    async def pat(self, ctx: commands.Context) -> None:
        """Get a random pat image."""
        await self.image_sender(ctx, await self.rand_im("pat"))

    @commands.command()
    async def panda(self, ctx) -> None:
        """Get a random picture of a panda."""
        async with self.bot.aio_session.get(
            "https://some-random-api.ml/img/panda"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    title="Random Panda!",
                    colour=discord.Colour.gold(),
                )
                embed.set_image(url=data["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went boom! :( [CODE: {resp.status}]")
                await self.bot.log_channel.send(f"Code {resp.status} in panda")

    @commands.command(ignore_extra=True)
    async def pepe(self, ctx: commands.Context) -> None:
        """Get a random pepe image."""
        await self.image_sender(ctx, await self.rand_im("pepe"))

    @commands.command()
    async def reddit(self, ctx: commands.Context, subreddit: str) -> None:
        """Retrieve images from the specified subreddit.

        This command may return NSFW results only in NSFW channels
        """
        sub = subreddit.split("r/")[-1]
        try:
            async with self.bot.aio_session.get(
                f"https://api.ksoft.si/images/rand-reddit/{sub}",
                headers={"Authorization": (
                    f"Bearer {self.bot.ksoft_client.api_key}")},
                params={
                    "remove_nsfw": str(not check_channel(ctx.channel)),
                    "span": "week",
                },
            ) as response:
                await self.reddit_sender(
                    ctx,
                    Redditwrapper(await response.json()),
                )
        except Exception:
            await ctx.send("Subreddit not found")

    @commands.command()
    async def robot(self, ctx: commands.Context, *, hashed: str) -> None:
        """Get a robot image from an input."""
        embed = discord.Embed(title=hashed)
        embed.set_image(url=f"https://robohash.org/{sha(hashed)}.png?set=set1")
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    async def tickle(self, ctx: commands.Context) -> None:
        """Get a random tickle image."""
        await self.image_sender(ctx, await self.rand_im("tickle"))

    @commands.command(ignore_extra=True)
    async def wikihow(self, ctx: commands.Context) -> None:
        """Retrieve a weird image from WikiHow."""
        image = await self.bot.ksoft_client.images.random_wikihow()
        embed = discord.Embed(
            title=image.title,
            url=image.article_url,
            colour=discord.Colour.blue(),
        )
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def rand_im(self, tag: str, nsfw: bool = False) -> object:
        """Random image lol."""
        try:
            return await self.bot.ksoft_client.images.random_image(tag=tag, nsfw=nsfw)
        except Exception:
            return PicError()

    async def image_sender(self, ctx: commands.Context, image) -> None:
        """Embeds an image then sends it."""
        if hasattr(image, "code"):
            await self.bot.httpcat(ctx, image["code"])
            return
        if not image.url:
            await self.bot.httpcat(ctx, 404)
            return
        embed = discord.Embed(
            title=image.tag,
            timestamp=datetime.utcnow(),
            colour=discord.Colour.blue(),
        )
        embed.set_image(url=image.url)
        await ctx.send(embed=embed)

    async def reddit_sender(self, ctx: commands.Context, image) -> None:
        """Embeds a Reddit image then sends it."""
        if hasattr(image, "error"):
            await ctx.send(image.message)
            return
        embed = discord.Embed(
            title=image.title,
            url=image.source,
            timestamp=datetime.fromtimestamp(image.created_at),
            colour=discord.Colour.blue(),
        )
        if not image.image_url:
            await self.bot.httpcat(ctx, 404)
            return
        embed.set_image(url=image.image_url)
        embed.set_footer(
            text=(
                f"👍 {image.upvotes} | 👎 {image.downvotes} |" f" 💬 {image.comments}")
        )
        embed.set_author(
            name=f"Posted by {image.author} in {image.subreddit}",
            icon_url="https://i.redd.it/qupjfpl4gvoy.jpg",
            url="https://reddit.com" + image.author,
        )
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Images cog."""
    bot.add_cog(Images(bot))
