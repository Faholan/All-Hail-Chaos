import discord
import pickle
from discord.ext import commands
from os import path
import typing

auto_swear_detection=["4r5e", "5h1t", "5hit", "a55", "anal", "anus", "ar5e", "arrse", "arse", "ass", "ass-fucker", "asses", "assfucker", "assfukka", "asshole", "assholes", "asswhole", "a_s_s", "b!tch", "b00bs", "b17ch", "b1tch", "ballbag", "balls", "ballsack", "bastard", "beastial", "beastiality", "bellend", "bestial", "bestiality", "bi+ch", "biatch", "bitch", "bitcher", "bitchers", "bitches", "bitchin", "bitching", "bloody", "blow job", "blowjob", "blowjobs", "boiolas", "bollock", "bollok", "boner", "boob", "boobs", "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "buceta", "bugger", "bum", "bunny fucker", "butt", "butthole", "buttmuch", "buttplug", "c0ck", "c0cksucker", "carpet muncher", "cawk", "chink", "cipa", "cl1t", "clit", "clitoris", "clits", "cnut", "cock", "cock-sucker", "cockface", "cockhead", "cockmunch", "cockmuncher", "cocks", "cocksuck", "cocksucked", "cocksucker", "cocksucking", "cocksucks", "cocksuka", "cocksukka", "cok", "cokmuncher", "coksucka", "coon", "cox", "crap", "cum", "cummer", "cumming", "cums", "cumshot", "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlick", "cuntlicker", "cuntlicking", "cunts", "cyalis", "cyberfuc", "cyberfuck", "cyberfucked", "cyberfucker", "cyberfuckers", "cyberfucking", "d1ck", "damn", "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "dirsa", "dlck", "dog-fucker", "doggin", "dogging", "donkeyribber", "doosh", "duche", "dyke", "ejaculate", "ejaculated", "ejaculates", "ejaculating", "ejaculatings", "ejaculation", "ejakulate", "f u c k", "f u c k e r", "f4nny", "fag", "fagging", "faggitt", "faggot", "faggs", "fagot", "fagots", "fags", "fanny", "fannyflaps", "fannyfucker", "fanyy", "fatass", "fcuk", "fcuker", "fcuking", "feck", "fecker", "felching", "fellate", "fellatio", "fingerfuck", "fingerfucked", "fingerfucker", "fingerfuckers", "fingerfucking", "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers", "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fuck", "fucka", "fucked", "fucker", "fuckers", "fuckhead", "fuckheads", "fuckin", "fucking", "fuckings", "fuckingshitmotherfucker", "fuckme", "fucks", "fuckwhit", "fuckwit", "fudge packer", "fudgepacker", "fuk", "fuker", "fukker", "fukkin", "fuks", "fukwhit", "fukwit", "fux", "fux0r", "f_u_c_k", "gangbang", "gangbanged", "gangbangs", "gaylord", "gaysex", "goatse", "God", "god-dam", "god-damned", "goddamn", "goddamned", "hardcoresex", "hell", "heshe", "hoar", "hoare", "hoer", "homo", "hore", "horniest", "horny", "hotsex", "jack-off", "jackoff", "jap", "jerk-off", "jism", "jiz", "jizm", "jizz", "kawk", "knob", "knobead", "knobed", "knobend", "knobhead", "knobjocky", "knobjokey", "kock", "kondum", "kondums", "kum", "kummer", "kumming", "kums", "kunilingus", "l3i+ch", "l3itch", "labia", "lmfao", "lust", "lusting", "m0f0", "m0fo", "m45terbate", "ma5terb8", "ma5terbate", "masochist", "master-bate", "masterb8", "masterbat*", "masterbat3", "masterbate", "masterbation", "masterbations", "masturbate", "mo-fo", "mof0", "mofo", "mothafuck", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked", "mothafucker", "mothafuckers", "mothafuckin", "mothafucking", "mothafuckings", "mothafucks", "mother fucker", "motherfuck", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "motherfuckings", "motherfuckka", "motherfucks", "muff", "mutha", "muthafecker", "muthafuckker", "muther", "mutherfucker", "n1gga", "n1gger", "nazi", "nigg3r", "nigg4h", "nigga", "niggah", "niggas", "niggaz", "nigger", "niggers", "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "orgasim", "orgasims", "orgasm", "orgasms", "p0rn", "pawn", "pecker", "penis", "penisfucker", "phonesex", "phuck", "phuk", "phuked", "phuking", "phukked", "phukking", "phuks", "phuq", "pigfucker", "pimpis", "piss", "pissed", "pisser", "pissers", "pisses", "pissflaps", "pissin", "pissing", "pissoff", "poop", "porn", "porno", "pornography", "pornos", "prick", "pricks", "pron", "pube", "pusse", "pussi", "pussies", "pussy", "pussys", "rectum", "retard", "rimjaw", "rimming", "s hit", "s.o.b.", "sadist", "schlong", "screwing", "scroat", "scrote", "scrotum", "semen", "sex", "sh!+", "sh!t", "sh1t", "shag", "shagger", "shaggin", "shagging", "shemale", "shi+", "shit", "shitdick", "shite", "shited", "shitey", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted", "shitter", "shitters", "shitting", "shittings", "shitty", "skank", "slut", "sluts", "smegma", "smut", "snatch", "son-of-a-bitch", "spac", "spunk", "s_h_i_t", "t1tt1e5", "t1tties", "teets", "teez", "testical", "testicle", "tit", "titfuck", "tits", "titt", "tittie5", "tittiefucker", "titties", "tittyfuck", "tittywank", "titwank", "tosser", "turd", "tw4t", "twat", "twathead", "twatty", "twunt", "twunter", "v14gra", "v1gra", "vagina", "viagra", "vulva", "w00se", "wang", "wank", "wanker", "wanky", "whoar", "whore", "willies", "willy", "xrated", "xxx"]

class Moderation(commands.Cog):
    """Manage your server like never before"""
    def __init__(self,bot):
        self.bot=bot
        try:
            self.reactions=pickle.load(open("data"+path.sep+"moderation.DAT",mode='rb'))
        except:
            self.reactions={}
        try:
            self.swear_words=pickle.load(open("data"+path.sep+"swear.DAT",mode='rb'))
        except:
            self.swear_words={}
        try:
            self.swear_off=pickle.load(open("data"+path.sep+"swear_off.DAT",mode='rb'))
        except:
            self.swear_off=[]
        try:
            self.auto_swear=pickle.load(open("data"+path.sep+"auto_swear.DAT",mode='rb'))
        except:
            self.auto_swear=[]

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self,ctx,who:commands.Greedy[typing.Union[discord.Role,discord.Member]],*,reason=None):
        """Command used to ban users. You can specify members or roles. The bot will then ban all the members you specified, and all the members having the specified role. You can specify at the end a reason for the ban
        You need the `ban members` permission, and your highest role needs to be higher than the others'. The bot then deletes the banned roles"""
        banning=[]
        roles=[]
        for banned in who:
            if isinstance(banned,discord.Role):
                if banned.is_default():
                    await ctx.send("You cannot ban the default role.")
                elif ctx.me.roles[-1]<=banned:
                    await ctx.send(f"I cannot ban the role {banned.name} : it is higher than my highest role")
                elif ctx.author.roles[-1]>banned:
                    if not banned in roles:
                        roles.append(banned)
                        for member in banned.members:
                            if member==ctx.guild.owner:
                                await self.bot.httpcat(ctx,403,"I cannot ban the guild owner")
                            elif member!=ctx.me:
                                if not member in banning:
                                    banning.append(member)
                            else:
                                await self.bot.httpcat(ctx,403,"I cannot ban myself")
                else:
                    await self.bot.httpcat(ctx,401,f"You cannot ban the role {banned.name} : it is higher than your highest role")
            else:
                if banned==ctx.me:
                    await self.bot.httpcat(ctx,403,"I cannot ban myself")
                elif ctx.me.roles[-1]<=banned.roles[-1]:
                    await self.bot.httpcat(ctx,403,f"I cannot ban {banned.name} : he has a higher role than me")
                elif banned==ctx.guild.owner:
                    await self.bot.httpcat(ctx,403,f"I cannot ban {banned.name} : he is the guild owner")
                elif not banned in banning:
                    banning.append(banned)
        r='\n'
        if reason:
            await ctx.send(f"You're about to ban {len(banning)} members because of `{reason}` :\n -{(r+' -').join([member.mention for member in banning])}\n\nDo you want to proceed ? (y/n)")
        else:
            await ctx.send(f"You're about to ban {len(banning)} members :\n -{(r+' -').join([member.mention for member in banning])}\n\nDo you want to proceed ? (y/n)")
        def check(m):
            return m.author==ctx.author and (m.content.lower().startswith('y') or m.content.lower().startswith('n')) and m.channel==ctx.channel
        try:
            msg=await self.bot.wait_for('message',check=check,timeout=30.0)
            proceed=msg.content.lower().startswith('y')
        except asyncio.TimeoutError:
            proceed=False
        if proceed:
            for m in banning:
                await m.ban(reason=reason)
            if roles:
                if reason:
                    await ctx.send(f"You're about to delete {len(roles)} roles because of `{reason}` :\n -{(r+' -').join([role.mention for role in roles])}\n\nDo you want to proceed ? (y/n)")
                else:
                    await ctx.send(f"You're about to delete {len(roles)} roles :\n -{(r+' -').join([role.mention for role in roles])}\n\nDo you want to proceed ? (y/n)")
                try:
                    msg=await self.bot.wait_for('message',check=check,timeout=30.0)
                    proceed=msg.content.lower().startswith('y')
                except asyncio.TimeoutError:
                    proceed=False
                if proceed:
                    for role in roles:
                        await role.delete(reason=reason)
                    await ctx.send(f"len(roles) roles deleted")
                else:
                    await ctx.send("No roles were deleted")
        else:
            await ctx.send("No members were banned")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self,ctx,who:commands.Greedy[typing.Union[discord.Role,discord.Member]],*,reason=None):
        """Command used to kick users. You can specify members or roles. The bot will then kick all the members you specified, and all the members having the specified role. You can specify at the end a reason for the kick
        You need the `kick members` permission, and your highest role needs to be higher than the others'. The bot then deletes the kicked roles"""
        kicking=[]
        roles=[]
        for kicked in who:
            if isinstance(kicked,discord.Role):
                if kicked.is_default():
                    await self.bot.httpcat(ctx,403,"You cannot kick the default role.")
                elif ctx.me.roles[-1]<=kicked:
                    await self.bot.httpcat(ctx,403,f"I cannot kick the role {kicked.name} : it is higher than my highest role")
                elif ctx.author.roles[-1]>kicked:
                    if not kicked in roles:
                        roles.append(kicked)
                        for member in kicked.members:
                            if member==ctx.guild.owner:
                                await self.bot.httpcat(ctx,403,"I cannot kick the guild owner")
                            elif member!=ctx.me:
                                if not member in kicking:
                                    kicking.append(member)
                            else:
                                await self.bot.httpcat(ctx,403,"I cannot kick myself")
                else:
                    await self.bot.httpcat(ctx,401,f"You cannot kick the role {kicked.name} : it is higher than your highest role")
            else:
                if kicked==ctx.me:
                    await self.bot.httpcat(ctx,403,"I cannot kick myself")
                elif ctx.me.roles[-1]<=kicked.roles[-1]:
                    await self.bot.httpcat(ctx,403,f"I cannot kick {kicked.name} : he has a higher role than me")
                elif kicked==ctx.guild.owner:
                    await self.bot.httpcat(ctx,403,f"I cannot kick {kicked.name} : he is the guild owner")
                elif not kicked in kicking:
                    kicking.append(kicked)
        r='\n'
        if reason:
            await ctx.send(f"You're about to kick {len(kicking)} members because of `{reason}` :\n -{(r+' -').join([member.mention for member in kicking])}\n\nDo you want to proceed ? (y/n)")
        else:
            await ctx.send(f"You're about to kick {len(kicking)} members :\n -{(r+' -').join([member.mention for member in kicking])}\n\nDo you want to proceed ? (y/n)")
        def check(m):
            return m.author==ctx.author and (m.content.lower().startswith('y') or m.content.lower.startswith('n')) and m.channel==ctx.channel
        try:
            msg=await self.bot.wait_for('message',check=check,timeout=30.0)
            proceed=msg.content.lower().startswith('y')
        except asyncio.TimeoutError:
            proceed=False
        if proceed:
            for m in kicking:
                await m.kick(reason=reason)
            if roles:
                if reason:
                    await ctx.send(f"{len(kicking)} members kicked\n\nYou're about to delete {len(roles)} roles because of `{reason}` :\n -{(r+' -').join([role.mention for role in roles])}\n\nDo you want to proceed ? (y/n)")
                else:
                    await ctx.send(f"You're about to delete {len(roles)} roles :\n -{(r+' -').join([role.mention for role in roles])}\n\nDo you want to proceed ? (y/n)")
                try:
                    msg=await self.bot.wait_for('message',check=check,timeout=30.0)
                    proceed=msg.content.lower().startswith('y')
                except asyncio.TimeoutError:
                    await ctx.send('Cancelling the deletion')
                    proceed=False
                if proceed:
                    for role in roles:
                        await role.delete(reason=reason)
                    await ctx.send(f"len(roles) roles deleted")
                else:
                    await ctx.send("No roles were deleted")
        else:
            await ctx.send("No members were kicked")

    @commands.command()
    async def reputation(self,ctx,*,other:typing.Union[discord.Member,int]):
        """Checks the reputation of an user.
        You can refer to him if he's in the same server, or just paste his ID"""
        if type(other)==int:
            ID=str(other)
            name="User "+ID
            url=ctx.bot.user.avatar_url
        else:
            ID=str(other.id)
            name=str(other)+f" [{ID}]"
            url=other.avatar_url

        async with self.bot.aio_session.get('https://discordrep.com/u/'+ID) as response:
            if response.status != 200:
                return await self.bot.httpcat(ctx,404,"I couldn't find this user.")

        async with self.bot.aio_session.get('https://discordrep.com/api/v3/rep/'+ID,headers={'Authorization':self.bot.discord_rep}) as response:
            reputation=await response.json()

        async with self.bot.aio_session.get('https://discordrep.com/api/v3/infractions/',headers={'Authorization':self.bot.discord_rep}) as response:
            infractions=await response.json()

        embed=discord.Embed(colour=self.bot.colors['green'],description="Source : [DiscordRep](https://discordrep.com) and [KSoft](https://ksoft.si)")
        embed.set_thumbnail(url=url)
        embed.set_author(name=name,icon_url=url,url="https://discordrep.com/u/"+ID)
        banning=[]
        if infractions.get("type") == "BAN":
            date=datetime.fromtimestamp(infractions["date"]//1000)
            embed.colour = self.bot.colors['yellow']
            banning.append(f"Warned on {date.day}-{date.month}-{date.year} {date.hour}:{date.minute}:{date.second} because of : `{infractions['reason']}`")
        elif infractions.get("type") == "WARN":
            date=datetime.fromtimestamp(infractions["date"]//1000)
            embed.colour = self.bot.colors['red']
            banning.append(f"Banned on {date.day}-{date.month}-{date.year} {date.hour}:{date.minute}:{date.second} because of : `{infractions['reason']}`")
        check_ban=await self.bot.client.bans_check(int(ID))
        if banning==[]:
            if not check_ban:
                embed.add_field(name="Bans",value="This user hasn't been banned from DiscordRep or KSoft",inline=False)
            else:
                embed.add_field(name="Bans from DiscordRep",value="This user hasn't been banned",inline=False)
        else:
            embed.add_field(name="Bans from DiscordRep",value="\n".join(banning))
            if not check_ban:
                embed.add_field(name="Bans from KSoft",value="This user hasn't been banned from KSoft.si",inline=False)
        if check_ban:
            BAN=await self.bot.client.bans_info(int(ID))
            embed.colour = self.bot.colors['red']
            embed.add_field(name="Bans from KSoft",value=f"Banned on {BAN.timestamp} because of [{BAN.reason}]({BAN.proof})",inline=False)

        embed.add_field(name="Reputation on DiscordRep",value=f"Rank : {[reputation['rank']]}\n\nUpvotes : {reputation['rank']}\nDownvotes : {reputation['downvotes']}\n\nTotal votes : {reputation['upvotes']-reputation['downvotes']}\n\nXP : {reputation['xp']}",inline=False)
        #embed.add_field(name="Bio on DiscordRep",value="```"+user["bio"]+"```",inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self,ctx,message:discord.Message, Roles:commands.Greedy[discord.Role], emoji):
        """This command allows you to automatically give a role to anyone who reacts with a given emoji to a given message. The order is : message, role, emoji
        You can also use this command to cancel the assignation, or use it multiple times/with different roles to add multiple roles on reaction.
        To specify the message, you can enter the message url, the message id if in the same channel, or a string {channel_id}-{message_id}
        We both need the `manage_roles` permission for that."""
        Reaction=discord.utils.get(message.reactions, emoji = emoji)
        if Reaction:
            if not Reaction.me:
                await message.add_reaction(emoji)
        else:
            try:
                await message.add_reaction(emoji)
            except discord.Forbidden:
                await ctx.send("I lack the permissions to add the first reaction")
        for Role in Roles:
            if Role.id in self.reactions.get((message.id,emoji),[]):
                self.reactions[(message.id,emoji)].remove(Role.id)
                await ctx.send(f"Role {Role.name} removed from assignment")
            else:
                self.reactions[(message.id,emoji)]=self.reactions.get((message.id,emoji),[])+[Role.id]
                await ctx.send(f"Role {Role.name} added to assignment")
            if self.reactions[(message.id,emoji)]==[]:
                self.reactions.pop((message.id,emoji))
                await ctx.send(f"Role assignment deleted")
                Reaction=discord.utils.get(message.reactions, emoji = emoji)
                if Reaction:
                    if Reaction.me:
                        await message.remove_reaction(emoji, ctx.me)
        pickle.dump(self.reactions,open("data"+path.sep+"moderation.DAT",mode='wb'))

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(administrator=True)
    async def swear(self,ctx,word=None):
        """You can specify a word to add/remove it from the list of forbidden words, or you can also don't specify one to check the swear filter's status. Specify on/off to turn it on/off, and auto to turn the autodetection on/off.
        NO SWEAR WORDS IN MY CHRISTIAN SERVER !"""
        if word:
            word=word.lower()
            if word=="on":
                if ctx.guild.id in self.swear_off:
                    self.swear_off.remove(ctx.guild.id)
                    pickle.dump(self.swear_off,open("data"+path.sep+"swear_off.DAT",mode='wb'))
                await ctx.send("Swear filter turned on")
            elif word=="off":
                if not ctx.guild.id in self.swear_off:
                    self.swear_off.append(ctx.guild.id)
                    pickle.dump(self.swear_off,open("data"+path.sep+"swear_off.DAT",mode='wb'))
                await ctx.send("Swear filter turned off")
            elif word=="auto":
                if ctx.guild.id in self.auto_swear:
                    self.auto_swear.remove(ctx.guild.id)
                    await ctx.send("Auto detection turned off")
                else:
                    self.auto_swear.append(ctx.guild.id)
                    await ctx.send("Auto detection turned on")
                pickle.dump(self.auto_swear,open("data"+path.sep+"auto_swear.DAT",mode='wb'))
            elif word in self.swear_words.get(ctx.guild.id,[]):
                self.swear_words[ctx.guild.id].remove(word)
                await ctx.send(f"`{word}` was removed from the list of swear words")
                if self.swear_words[ctx.guild.id]==[]:
                    self.swear_words.pop(ctx.guild.id)
            else:
                await ctx.send(f"`{word}` was added to the list of swear words")
                self.swear_words[ctx.guild.id]=self.swear_words.get(ctx.guild.id,[])+[word]
            pickle.dump(self.swear_words,open("data"+path.sep+"swear.DAT",mode='wb'))
        else:
            embed=discord.Embed(title=f"Swear words in {ctx.guild.name}",colour=self.bot.colors['yellow'])
            embed.add_field(name="Swear filter status",value="Offline" if ctx.guild.id in self.swear_off else "Online")
            embed.add_field(name="Auto filter status",value="Online" if ctx.guild.id in self.auto_swear else "Offline")
            embed.add_field(name="Guild-specific swear words",value="\n - ".join(self.swear_words.get(ctx.guild.id,[])) if ctx.guild.id in self.swear_words else "No swear words are defined for this guild",inline=False)
            await ctx.send(embed=embed)

    @commands.Cog.listener('on_raw_reaction_add')
    async def role_adder(self,payload):
        if payload.guild_id:
            if (payload.message_id,payload.emoji.name) in self.reactions:
                guild=self.bot.get_guild(payload.guild_id)
                roles=payload.member.roles
                for r in self.reactions[(payload.message_id,payload.emoji.name)]:
                    role=guild.get_role(r)
                    if role and not role in roles:
                        roles.append(role)
                await payload.member.edit(roles=roles)

    @commands.Cog.listener('on_raw_reaction_remove')
    async def role_remover(self,payload):
        if payload.guild_id:
            if (payload.message_id,payload.emoji.name) in self.reactions:
                guild=self.bot.get_guild(payload.guild_id)
                member=guild.get_member(payload.user_id)
                if member:
                    roles=member.roles
                    for r in self.reactions[(payload.message_id,payload.emoji.name)]:
                        role=guild.get_role(r)
                        if role and role in roles:
                            roles.remove(role)
                    await member.edit(roles=roles)

    @commands.Cog.listener("on_message")
    async def no_swear_words(self,message):
        if message.author==self.bot or not isinstance(message.author,discord.Member):
            return
        if message.channel.is_nsfw() or message.guild.id in self.swear_off or message.author.guild_permissions.administrator:
            return
        if message.guild.id in self.auto_swear:
            for s in auto_swear_detection:
                if s in message.content.lower().split(' '):
                    try:
                        await message.delete()
                    except discord.Forbidden:
                        dm=ctx.guild.owner.dm_channel
                        if not dm:
                            await ctx.guild.owner.create_dm()
                            dm=ctx.guild.owner.dm_channel
                        await dm.send(f"{message.author} used a swear word : `{s}`, but I lack the permissions to delete the message. Please give them back to me")
                    return

        for s in self.swear_words.get(message.guild.id,[]):
            if s in message.content.lower().split(' '):
                try:
                    await message.delete()
                except discord.Forbidden:
                    dm=ctx.guild.owner.dm_channel
                    if not dm:
                        await ctx.guild.owner.create_dm()
                        dm=ctx.guild.owner.dm_channel
                    await dm.send(f"{message.author} used a swear word : `{s}`, but I lack the permissions to delete the message. Please give them back to me")
                break

def setup(bot):
    bot.add_cog(Moderation(bot))
