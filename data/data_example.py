"""Rename this file to data.py"""
from random import choice
token="THE BEAUTIFUL TOKEN OF MY DISCORD BOT"
admins="ALL THE DISCORD ACCOUNTS WHICH HAVE ADMIN RIGHTS FOR THE BOT"
extensions=["cogs.animals","cogs.battleship","cogs.business","cogs.coronavirus","cogs.funny","cogs.image","cogs.moderation","cogs.music","cogs.nasa","cogs.utility","bin.error","bin.success"]
user_agent="chaotic_bot"
default_prefix="€"

log_channel = 694804739270901801 #Change this by the channel in which you want the logs

graphic_interface=True

invite_permissions=None #Permissions to require when someone invites the bot in a server

ksoft_token = "MY KSOFT.SI TOKEN"
discord_rep = "MY DISCORDREP TOKEN"
nasa = "I AM HACKING THE NASA" #NASA API token
dbl_token = None #Discord Bot List Token

def get_color():
    return choice([0x11806a,0x2ecc71,0x1f8b4c,0x3498db,0x206694,0x9b59b6,0x71368a,0xe91e63,0xad1457,0xf1c40f,0xc27c0e,0xe67e22,0xa84300,0xe74c3c,0x992d22])
