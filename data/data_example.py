"""Rename this file to data.py.

MIT License

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
SOFTWARE.
"""

from random import choice

from discord import Intents
import ksoftapi


def setup(bot):
    """Add all the data to the bot."""
    bot.extensions_list = [
        "cogs.animals",
        "cogs.battleship",
        "cogs.business",
        "cogs.funny",
        "cogs.games",
        "cogs.image",
        "cogs.moderation",
        "cogs.music",
        "cogs.nasa",
        "cogs.success",
        "cogs.tags",
        "cogs.utility",
        "bin.error",
        "bin.help",
        "bin.markdown",
        "bin.stats",
    ]
    if bot.first_on_ready:
        bot.postgre_connection = {
            "user": "user",
            "password": "password",
        }
        bot.lavalink_credentials = {
            "host": "127.0.0.1",
            "port": 2233,
            "password": "youshallnotpass",
            "region": "eu",
            "resume_key": "default_node",
        }

        bot.token = "THE BEAUTIFUL TOKEN OF MY DISCORD BOT"

        bot.http.user_agent = "chaotic_bot"
        bot.default_prefix = "€"

        bot.success_image = (
            "https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg"
        )

        bot.log_channel_id = 00000000000000000
        bot.suggestion_channel_id = 00000000000000000
        bot.contact_channel_id = 00000000000000000

        bot.invite_permissions = 808527942
        bot.support = "https://discord.gg/eFfjdyZ"

        bot.ksoft_client = ksoftapi.Client("MY KSOFT.SI TOKEN", bot.loop)
        bot.discord_rep = "MY DISCORDREP TOKEN"
        bot.nasa = "I AM HACKING THE NASA"  # NASA API token
        bot.dbl_token = None  # Discord Bot List Token
        bot.discord_bots = None  # discord.bots.gg Token
        bot.xyz = None  # bots.ondiscord.xyz token
        bot.discord_bot_list = None  # discordbotlist.com token

        bot.github_token = None  # Github token
        bot.github_repo = None  # Github repo for webhooks
        bot.github_link = "https://github.com/Faholan/All-Hail-Chaos"

        bot.top_gg = "https://top.gg/bot/636359675943583775"  # top.gg page
        bot.bots_on_discord = (
            "https://bots.ondiscord.xyz/bots/636359675943583775"
        )  # bots.ondiscord.xyz page
        bot.discord_bots_page = (
            "https://discord.bots.gg/bots/636359675943583775"
        )  # discord.bot.gg page
        bot.discord_bot_list_page = (
            "https://discordbotlist.com/bots/chaotic-bot"
        )  # discordbotlist.com page

        bot.colors = {
            'red': 0xff0000,
            'green': 0x006400,
            'yellow': 0xffff00,
            'blue': 0x00008b,
        }

        bot.get_color = lambda: choice([
            0x11806a,
            0x2ecc71,
            0x1f8b4c,
            0x3498db,
            0x206694,
            0x9b59b6,
            0x71368a,
            0xe91e63,
            0xad1457,
            0xf1c40f,
            0xc27c0e,
            0xe67e22,
            0xa84300,
            0xe74c3c,
            0x992d22,
        ])
