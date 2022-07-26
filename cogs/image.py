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
            [str(int(part1[i]) and int(part2[i])) for i in range(len(part1))])

    def sha_ou(part1: str, part2: str) -> str:
        return "".join(
            [str(int(part1[i]) or int(part2[i])) for i in range(len(part1))])

    def sha_xor(part1: str, part2: str) -> str:
        return "".join(
            [str(int(part1[i]) ^ int(part2[i])) for i in range(len(part1))])

    def complement(part1: str) -> str:
        return "".join(
            [str((int(part1[i]) + 1) % 2) for i in range(len(part1))])

    def dec_g(part1: str, number: int) -> str:
        return part1[number:] + "0" * number

    def dec_d(part1: str, number: int) -> str:
        return "0" * number + part1[:len(part1) - number]

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

    message = bin(int(bytes(message, encoding="utf-8").hex(), base=16))[2:]

    completion = bin(len(message))[2:]
    completion = "0" * (64 - len(completion)) + completion

    message += "1" + "0" * ((447 - len(message)) % 512) + completion

    M = [[message[i:i + 512][32 * j:32 * (j + 1)] for j in range(16)]
         for i in range(0, len(message), 512)]

    for i, elem in enumerate(M):
        W = [elem[t] for t in range(16)]
        for tt in range(16, 64):
            w = bin(
                (int(sha_o_1(W[tt - 2]), base=2) + int(W[tt - 7], base=2) +
                 int(sha_o_0(W[tt - 15]), base=2) + int(W[tt - 16], base=2)) %
                2**32)[2:]
            W.append("0" * (32 - len(w)) + w)
        a, b, c, d, e, f, g, h = list_h
        for tt in range(64):
            T1 = bin(
                (int(h, base=2) + int(sha_e_1(e), base=2) +
                 int(sha_ch(e, f, g), base=2) + int(constants_k[tt], base=2) +
                 int(W[tt], base=2)) % 2**32)[2:]
            T1 = "0" * (32 - len(T1)) + T1
            T2 = bin(
                (int(sha_e_0(a), base=2) + int(sha_maj(a, b, c), base=2)) %
                2**32)[2:]
            T2 = "0" * (32 - len(T2)) + T2
            h, g, f = g, f, e
            e = bin((int(d, base=2) + int(T1, base=2)) % 2**32)[2:]
            e = "0" * (32 - len(e)) + e
            d, c, b = c, b, a
            a = bin((int(T1, base=2) + int(T2, base=2)) % 2**32)[2:]
            a = "0" * (32 - len(a)) + a
        for j in range(8):
            list_h[j] = bin((int([a, b, c, d, e, f, g, h][i], base=2) +
                             int(list_h[j], base=2)) % 2**32)[2:]
            list_h[j] = "0" * (32 - len(list_h[j])) + list_h[j]
    return "".join(
        [hex(int(list_h[i], base=2))[2:] for i in range(len(list_h))])


class Images(commands.Cog):  # Thanks KSoft.si
    """Commands to get random images.

    You can try using the nsfw command, if you dare
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize Images."""
        self.bot = bot

    @commands.command()
    async def koala(self, ctx: commands.Context) -> None:
        """Get a random picture of a koala."""
        async with self.bot.aio_session.get(
                "https://some-random-api.ml/img/koala") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(title="Random Koala",
                                      colour=discord.Colour.gold())
                embed.set_image(url=data["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send("Something went wrong.")
                await self.bot.log_channel.send(f"Code {resp.status} in koala")

    @commands.command()
    async def monster(self, ctx: commands.Context, *, hashed: str) -> None:
        """Get a monster image from an input."""
        embed = discord.Embed(title=hashed)
        embed.set_image(url=f"https://robohash.org/{sha(hashed)}.png?set=set2")
        await ctx.send(embed=embed)

    @commands.command()
    async def panda(self, ctx: commands.Context) -> None:
        """Get a random picture of a panda."""
        async with self.bot.aio_session.get(
                "https://some-random-api.ml/img/panda") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(
                    title="Random Panda!",
                    colour=discord.Colour.gold(),
                )
                embed.set_image(url=data["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went boom! :( [CODE: {resp.status}]"
                               )
                await self.bot.log_channel.send(f"Code {resp.status} in panda")

    @commands.command()
    async def robot(self, ctx: commands.Context, *, hashed: str) -> None:
        """Get a robot image from an input."""
        embed = discord.Embed(title=hashed)
        embed.set_image(url=f"https://robohash.org/{sha(hashed)}.png?set=set1")
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Images cog."""
    bot.add_cog(Images(bot))
