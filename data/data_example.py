"""Rename this file to data.py"""
from random import choice
token="THE BEAUTIFUL TOKEN OF MY DISCORD BOT"
admins="ALL THE DISCORD ACCOUNTS WHICH HAVE ADMIN RIGHTS FOR THE BOT"
extensions=["cogs.animals","cogs.battleship","cogs.business","cogs.coronavirus","cogs.funny","cogs.image","cogs.moderation","cogs.music","cogs.nasa", "cogs.success","cogs.utility","bin.error", "bin.help"]
user_agent="chaotic_bot"
default_prefix="€"

log_channel = 00000000000000000 #Change this to the channel in which you want the logs
suggestion_channel = 00000000000000000 #Change this to the channel in which you want the suggestions

graphic_interface=True

invite_permissions=None #Permissions to require when someone invites the bot in a server
support = "https://discord.gg/eFfjdyZ"

ksoft_token = "MY KSOFT.SI TOKEN"
discord_rep = "MY DISCORDREP TOKEN"
nasa = "I AM HACKING THE NASA" #NASA API token
dbl_token = None #Discord Bot List Token
discord_bots = None #discord.bots.gg Token
xyz = None #bots.ondiscord.xyz token
discord_bot_list = None #discordbotlist.com token

github_token = None #Github token
github_repo = None #Github repo for webhooks

top_gg = "https://top.gg/bot/636359675943583775" #top.gg page
bots_on_discord = "https://bots.ondiscord.xyz/bots/636359675943583775" #bots.ondiscord.xyz page
discord_bots_page = "https://discord.bots.gg/bots/636359675943583775" #discord.bot.gg page

colors = {'red':0xff0000, 'green':0x006400, 'yellow':0xffff00, 'blue':0x00008b}

def get_color():
    return choice([0x11806a,0x2ecc71,0x1f8b4c,0x3498db,0x206694,0x9b59b6,0x71368a,0xe91e63,0xad1457,0xf1c40f,0xc27c0e,0xe67e22,0xa84300,0xe74c3c,0x992d22])
