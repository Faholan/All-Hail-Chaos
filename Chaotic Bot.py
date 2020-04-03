from discord.ext import commands
from discord import Embed,Game,Status
from data import data
import asyncio
import ksoftapi

import aiohttp
import aiosqlite3
import coronatracker

bot=commands.Bot(command_prefix=('€','¤'),description="A bot for fun",help_command=None,fetch_offline_members=True)

bot.http.user_agent=data.user_agent

def get_first_prefix(obj):
        if type(obj)==str:
            return obj
        else:
            return obj[0]

@bot.command(hidden=True,ignore_extra=True)
async def help(ctx,*command_help):
    """Sends the help message
    Trust me, there's nothing to see here. Absolutely nothing."""
    if len(command_help)==0:
        #Aide générale
        embed=Embed(title='Help',description="Everything to know about my glorious self",colour=data.get_color())
        embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
        embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
        embed.set_footer(text=f"To get more information, use {get_first_prefix(bot.command_prefix)}help [subject].",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
        for cog in bot.cogs:
            if bot.get_cog(cog).get_commands():
                command_list=[get_first_prefix(bot.command_prefix)+command.name+' : '+command.short_doc for command in bot.get_cog(cog).get_commands() if not command.hidden]
                embed.add_field(name=bot.get_cog(cog).qualified_name,value='\n'.join(command_list),inline=False)
        command_list=[get_first_prefix(bot.command_prefix)+command.name+' : '+command.short_doc for command in bot.commands if not command.cog and not command.hidden]
        if command_list:
            embed.add_field(name='Other commands',value='\n'.join(command_list))
        await ctx.send(embed=embed)
    else:
        for helper in command_help:
            cog=bot.get_cog(helper)
            if cog:
                if cog.get_commands():
                    #Aide d'un cog
                    embed=Embed(title=helper,description=cog.description,colour=data.get_color())
                    embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
                    embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    for command in cog.get_commands():
                        if not command.hidden:
                            aliases=[command.name]
                            if command.aliases!=[]:
                                aliases+=command.aliases
                            embed.add_field(name='/'.join(aliases),value=command.help,inline=False)
                    embed.set_footer(text=f"Are you interested in {helper} ?",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    await ctx.send(embed=embed)
            else:
                cog=bot.get_command(helper)
                if cog:
                    #Aide d'une commande spécifique
                    embed=Embed(title=get_first_prefix(bot.command_prefix)+helper,description=cog.help,colour=data.get_color())
                    if cog.aliases!=[]:
                        embed.add_field(name="Aliases :",value="\n".join(cog.aliases))
                    embed.set_author(name=str(ctx.message.author),icon_url=str(ctx.message.author.avatar_url))
                    embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    if cog.hidden:
                        embed.set_footer(text=f"Wow, you found {helper} !",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    else:
                        embed.set_footer(text=f"Are you interested in {helper} ?",icon_url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"I couldn't find {helper}")

async def cog_reloader(self):
    print("Reloading extensions...")
    for ext in data.extensions:
        if not "success" in ext:
            self.reload_extension(ext)


@bot.event
async def on_ready():
    bot.lavalink_host = data.lavalink_host
    bot.lavalink_port = data.lavalink_port
    bot.lavalink_pw = data.lavalink_pw
    bot.lavalink_region = data.lavalink_region
    bot.log_channel = bot.get_channel(data.log_channel)
    bot.session = aiohttp.ClientSession()
    bot.ksoft_token=data.ksoft_token
    bot.client=ksoftapi.Client(bot.ksoft_token,bot,bot.loop)
    bot.cog_reloader=cog_reloader
    await bot.change_presence(activity=Game(get_first_prefix(bot.command_prefix)+'help'))
    for ext in data.extensions:
            if not ext in bot.extensions:
                bot.load_extension(ext)

bot.run(data.token)
