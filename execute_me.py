"""MIT License.

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

import sys
from os import name, path, system

if sys.platform == "linux":
    white = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    yellow = '\033[93m'
else:
    white = red = green = orange = blue = purple = yellow = ""


def clear():
    _ = system("cls" if name == "nt" else "clear")


print(f"""
Hello there ! Welcome to Chaotic Bot's generation program version 1.0 !

============================= {red}WARNING{white} =============================

Please check that you have installed {red}PostgreSQL{white} please ?

You can get it by running {yellow}sudo apt install postgresql{white}

Please press Enter to confirm that you have read this warning
""")

_ = input()
clear()

print(f"""
========================== {red}REQUIRED STUFF{white} =========================

The bot cannot run without these, please enter correct value in those fields :


""")
token = input("Bot token :")
user = input("PostgreSQL username :")
password = input("PostgreSQL password :")

clear()
print(f"""
=================== {yellow}HIGHLY RECOMMENDED STUFF{white} ===================

Key functionalities of the bot.
It will not be able to run if you don't give a value to these fields.


All the ids here can be obtained throught Discord via the Developer Mode,
by right-clicking on the channel""")
try:
    log_channel_id = int(input("Log channel id :"))
except ValueError:
    log_channel_id = 0
try:
    suggestion_channel_id = int(input("Suggestion channel id :"))
except ValueError:
    suggestion_channel_id = 0
try:
    contact_channel_id = int(input("Contact channel id :"))
except ValueError:
    contact_channel_id = 0

print(
    f"\n\n{red}If you don't have the information required, please leave these"
    " fields blank. The things written between parenthesis are what "
    f"will be disabled{white}\n\n"
)

ksoft, nasa = (True for _ in range(2))

ksoft_token = input(
    "Ksoft.si token (Image + reputation command). Get one at "
    f"{blue}https://api.ksoft.si/{white} :"
)
if not ksoft_token:
    ksoft = False
nasa_token = input(
    f"Nasa API token (NASA). Get one at {blue}https://api.nasa.gov{white} :"
)
if not nasa_token:
    nasa = False
discord_rep = input(
    "Discordrep token (reputation command). Get one at "
    f"{blue}https://discordrep.com/{white} :"
)

github_token = input(
    "GitHub token (github command). Get one at "
    f"{blue}https://github.com/settings/tokens{white} :"
)
try:
    github_repo = int(input("GitHub repository index :"))
except ValueError:
    github_repo = 0

clear()
print(f"""
======================= {blue}DISCORD BOT LISTS{white} ========================

Those tokens will allow us to update your bot's presence on each of those sites


You must have posted your bot the site to be able to use this functionality""")

dbl_token = input(f"{blue}top.gg{white} :")
discord_bots = input(f"{blue}discord.bots.gg{white} :")
xyz = input(f"{blue}bots.ondiscord.xyz{white} :")
discord_bot_list = input(f"{blue}discordbotlist.com{white} :")

clear()

print(f"""
======================== {green}OPTIONAL STUFF{white} =========================


Those options don't change anything important. If left blank, they'll have
the default value indicated betweeen parenthesis.
""")

user_agent = input(
    "User agent to use in your internet connection (Default chaotic_bot) :"
)
default_prefix = input("Prefix of the bot (default €) :")
support = input(
    "Support server invite (default "
    f"{blue}https://discord.gg/eFfjdyZ{white}) :"
)
github_link = input(
    "Link to the GitHub repository (default "
    f"{blue}https://github.com/Faholan/All-Hail-Chaos{white}) :"
)
discord_bot_list_page = input(
    f"Link to your bot's page on {blue}discordbotlist.com{white} :"
)
user_id = input(
    "User id of your bot. Default value is my bot's user ID "
    "(used for the bot lists)"
)

clear()
print("Nice ! You've completed the configuration !\n\nCreating data/data.py")

o = "{"
c = "}"

newline = "\n"

ksoft_str = (
    f'ksoftapi.Client("{ksoft_token}", bot.loop)'
) if ksoft else "None"

if not github_link:
    github_link = 'https://github.com/Faholan/All-Hail-Chaos'

if not discord_bot_list_page:
    discord_bot_list_page = 'https://discordbotlist.com/bots/chaotic-bot'

print(f"""from random import choice
import ksoftapi


def setup(bot):
    bot.extensions_list = [
        "cogs.animals",
        "cogs.battleship",
        "cogs.business",
        "cogs.funny",
        "cogs.games",{newline + '"cogs.image",' if ksoft else ''}
        "cogs.moderation",
        "cogs.music",{newline + '"cogs.nasa",' if nasa else ''}
        "cogs.owner",
        "cogs.success",
        "cogs.tags",
        "cogs.utility",
        "bin.error",
        "bin.help",
        "bin.markdown"
    ]
    if bot.first_on_ready:
        bot.postgre_connection = {o}
            "user": "{user}",
            "password":"{password}"
        {c}
        bot.token = "{token}"
        bot.user_agent = "{user_agent if user_agent else 'chaotic_bot'}"
        bot.default_prefix = "{default_prefix if default_prefix else '€'}"

        bot.success_image = (
            "https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg"
        )

        bot.log_channel_id = {log_channel_id}
        bot.suggestion_channel_id = {suggestion_channel_id}
        bot.contact_channel_id = {contact_channel_id}

        bot.invite_permissions = 808527942
        bot.support = "{support if support else 'https://discord.gg/eFfjdyZ'}"

        bot.ksoft_client = {ksoft_str}
        bot.discord_rep = "{discord_rep}"
        bot.nasa = "{nasa_token}"

        bot.dbl_token = "{dbl_token}"
        bot.discord_bots = "{discord_bots}"
        bot.xyz = "{xyz}"
        bot.discord_bot_list = "{discord_bot_list}"

        bot.github_token = "{github_token}"
        bot.github_repo = {github_repo}
        bot.github_link = "{github_link}"

        bot.top_gg = f"https://top.gg/bot/{user_id}"
        bot.bots_on_discord = f"https://bots.ondiscord.xyz/bots/{user_id}"
        bot.discord_bots_page = f"https://discord.bots.gg/bots/{user_id}"
        bot.discord_bot_list_page = "{discord_bot_list_page}"

        bot.colors = {o}
            'red': 0xff0000,
            'green': 0x006400,
            'yellow': 0xffff00,
            'blue': 0x00008b
        {c}

        bot.get_color = lambda : choice(
            [
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
                0x992d22
            ]
        )
""", file=open(f"data{path.sep}data.py", mode="w"))
