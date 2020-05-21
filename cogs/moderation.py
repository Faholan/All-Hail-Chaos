import discord
from discord.ext import commands
from os import path
import typing
import asyncio

auto_swear_detection=["4r5e", "5h1t", "5hit", "a55", "anal", "anus", "ar5e", "arrse", "arse", "ass", "ass-fucker", "asses", "assfucker", "assfukka", "asshole", "assholes", "asswhole", "a_s_s", "b!tch", "b00bs", "b17ch", "b1tch", "ballbag", "balls", "ballsack", "bastard", "beastial", "beastiality", "bellend", "bestial", "bestiality", "bi+ch", "biatch", "bitch", "bitcher", "bitchers", "bitches", "bitchin", "bitching", "bloody", "blow job", "blowjob", "blowjobs", "boiolas", "bollock", "bollok", "boner", "boob", "boobs", "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "buceta", "bugger", "bum", "bunny fucker", "butt", "butthole", "buttmuch", "buttplug", "c0ck", "c0cksucker", "carpet muncher", "cawk", "chink", "cipa", "cl1t", "clit", "clitoris", "clits", "cnut", "cock", "cock-sucker", "cockface", "cockhead", "cockmunch", "cockmuncher", "cocks", "cocksuck", "cocksucked", "cocksucker", "cocksucking", "cocksucks", "cocksuka", "cocksukka", "cok", "cokmuncher", "coksucka", "coon", "cox", "crap", "cum", "cummer", "cumming", "cums", "cumshot", "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlick", "cuntlicker", "cuntlicking", "cunts", "cyalis", "cyberfuc", "cyberfuck", "cyberfucked", "cyberfucker", "cyberfuckers", "cyberfucking", "d1ck", "damn", "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "dirsa", "dlck", "dog-fucker", "doggin", "dogging", "donkeyribber", "doosh", "duche", "dyke", "ejaculate", "ejaculated", "ejaculates", "ejaculating", "ejaculatings", "ejaculation", "ejakulate", "f u c k", "f u c k e r", "f4nny", "fag", "fagging", "faggitt", "faggot", "faggs", "fagot", "fagots", "fags", "fanny", "fannyflaps", "fannyfucker", "fanyy", "fatass", "fcuk", "fcuker", "fcuking", "feck", "fecker", "felching", "fellate", "fellatio", "fingerfuck", "fingerfucked", "fingerfucker", "fingerfuckers", "fingerfucking", "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers", "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fuck", "fucka", "fucked", "fucker", "fuckers", "fuckhead", "fuckheads", "fuckin", "fucking", "fuckings", "fuckingshitmotherfucker", "fuckme", "fucks", "fuckwhit", "fuckwit", "fudge packer", "fudgepacker", "fuk", "fuker", "fukker", "fukkin", "fuks", "fukwhit", "fukwit", "fux", "fux0r", "f_u_c_k", "gangbang", "gangbanged", "gangbangs", "gaylord", "gaysex", "goatse", "God", "god-dam", "god-damned", "goddamn", "goddamned", "hardcoresex", "hell", "heshe", "hoar", "hoare", "hoer", "homo", "hore", "horniest", "horny", "hotsex", "jack-off", "jackoff", "jap", "jerk-off", "jism", "jiz", "jizm", "jizz", "kawk", "knob", "knobead", "knobed", "knobend", "knobhead", "knobjocky", "knobjokey", "kock", "kondum", "kondums", "kum", "kummer", "kumming", "kums", "kunilingus", "l3i+ch", "l3itch", "labia", "lmfao", "lust", "lusting", "m0f0", "m0fo", "m45terbate", "ma5terb8", "ma5terbate", "masochist", "master-bate", "masterb8", "masterbat*", "masterbat3", "masterbate", "masterbation", "masterbations", "masturbate", "mo-fo", "mof0", "mofo", "mothafuck", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked", "mothafucker", "mothafuckers", "mothafuckin", "mothafucking", "mothafuckings", "mothafucks", "mother fucker", "motherfuck", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "motherfuckings", "motherfuckka", "motherfucks", "muff", "mutha", "muthafecker", "muthafuckker", "muther", "mutherfucker", "n1gga", "n1gger", "nazi", "nigg3r", "nigg4h", "nigga", "niggah", "niggas", "niggaz", "nigger", "niggers", "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "orgasim", "orgasims", "orgasm", "orgasms", "p0rn", "pawn", "pecker", "penis", "penisfucker", "phonesex", "phuck", "phuk", "phuked", "phuking", "phukked", "phukking", "phuks", "phuq", "pigfucker", "pimpis", "piss", "pissed", "pisser", "pissers", "pisses", "pissflaps", "pissin", "pissing", "pissoff", "poop", "porn", "porno", "pornography", "pornos", "prick", "pricks", "pron", "pube", "pusse", "pussi", "pussies", "pussy", "pussys", "rectum", "retard", "rimjaw", "rimming", "s hit", "s.o.b.", "sadist", "schlong", "screwing", "scroat", "scrote", "scrotum", "semen", "sex", "sh!+", "sh!t", "sh1t", "shag", "shagger", "shaggin", "shagging", "shemale", "shi+", "shit", "shitdick", "shite", "shited", "shitey", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted", "shitter", "shitters", "shitting", "shittings", "shitty", "skank", "slut", "sluts", "smegma", "smut", "snatch", "son-of-a-bitch", "spac", "spunk", "s_h_i_t", "t1tt1e5", "t1tties", "teets", "teez", "testical", "testicle", "tit", "titfuck", "tits", "titt", "tittie5", "tittiefucker", "titties", "tittyfuck", "tittywank", "titwank", "tosser", "turd", "tw4t", "twat", "twathead", "twatty", "twunt", "twunter", "v14gra", "v1gra", "vagina", "viagra", "vulva", "w00se", "wang", "wank", "wanker", "wanky", "whoar", "whore", "willies", "willy", "xrated", "xxx"]

class Moderation(commands.Cog):
    """Manage your server like never before"""
    def __init__(self,bot):
        self.bot=bot

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

        async with self.bot.aio_session.get('https://discordrep.com/api/v3/infractions/'+ID,headers={'Authorization':self.bot.discord_rep}) as response:
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
        check_ban=await self.bot.ksoft_client.bans.check(int(ID))
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
            BAN=await self.bot.ksoft_client.bans.info(int(ID))
            embed.colour = self.bot.colors['red']
            embed.add_field(name="Bans from KSoft",value=f"Banned on {BAN.timestamp} because of [{BAN.reason}]({BAN.proof})",inline=False)

        embed.add_field(name="Reputation on DiscordRep",value=f"Rank : {reputation['rank']}\n\nUpvotes : {reputation['upvotes']}\nDownvotes : {reputation['downvotes']}\n\nTotal votes : {reputation['upvotes']-reputation['downvotes']}\n\nXP : {reputation['xp']}",inline=False)
        #embed.add_field(name="Bio on DiscordRep",value="```"+user["bio"]+"```",inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx, action):
        """This command allows you to automatically give a role to anyone who reacts with a given emoji to a given message. Usage : `€role {action}` The action you select must be one of info, add, remove
        We both need the `manage_roles` permission for that."""
        if action.lower() == 'add':
            await ctx.send('Ping one or more roles in the next 30 seconds to select which ones you want to add')
            def check(message):
                print(f"{message.content} : {message.role_mentions}")
                return message.channel == ctx.channel and message.role_mentions and message.author == ctx.author

            try:
                message = await self.bot.wait_for('message', check = check, timeout = 30)
            except asyncio.TimeoutError:
                return await ctx.send("You didn't answer in time, I'm giving up on this")

            roles = message.role_mentions

            await ctx.send(f'React with an emoji in the next 30 seconds to a message to set up the assignation !')
            def check(payload):
                return payload.guild_id == ctx.guild.id and payload.member == ctx.author

            try:
                payload = await self.bot.wait_for('raw_reaction_add', check = check, timeout = 30)
            except asyncio.TimeoutError:
                return await ctx.send("You didn't react in time, I'm giving up on this.")

            message = await self.bot.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
            emoji = payload.emoji.name

            cur = await self.bot.db.execute('SELECT * FROM roles WHERE message_id=? AND emoji=?', (payload.message_id, emoji))
            result = await cur.fetchone()

            if result:
                ini_roles = []
                total = 0
                removed = 0
                for role_id in result['roleids'].split(','):
                    total+=1
                    Role = ctx.guild.get_role(int(role_id))
                    if Role:
                        ini_roles.append(Role)
                    else:
                        removed+=1
                removal = ' Those roles are :'
                if removed:
                    removal=f" {removed} of them didn't exist anymore, so I deleted them from my database. The remaining roles are :"
                joiner = '\n - '
                await ctx.send(f"{total} roles are already linked to this message and emoji.{removal}\n - {joiner.join([r.name for r in ini_roles])}\n\nDo you want me to replace them with the new ones, or add the new ones to the list. Send `replace` or `add` in the next 30 seconds to indicate your choice please.")
                def check(message):
                    return message.author == ctx.author and message.channel == ctx.channel and (message.content.lower().startswith('add') or message.content.lower().startswith('replace'))
                try:
                    answer = await self.bot.wait_for('message', check = check, timeout = 30)
                except asyncio.TimeoutError:
                    return await ctx.send("Cancelling the command...")
                if answer.content.lower().startswith('add'):
                    roles+=ini_roles
                await self.bot.db.execute('UPDATE roles SET roleids=? WHERE message_id=? AND emoji=?', (','.join([str(r.id) for r in roles]), payload.message_id, emoji))
            else:
                await self.bot.db.execute('INSERT INTO roles (message_id, channel_id, guild_id, emoji, roleids) VALUES (?, ?, ?, ?, ?)', (payload.message_id, payload.channel_id, payload.guild_id, emoji, ','.join([str(r.id) for r in roles])))
            try:
                await message.add_reaction(emoji)
            except:
                pass
            await ctx.send('The rule has been successfully updated')
        elif action.lower() == 'info':
            cur = await self.bot.db.execute('SELECT rowid, * FROM roles WHERE guild_id=?', (ctx.guild.id,))
            result = await cur.fetchall()
            deleted = 0
            m = f"No rules are currently defined for this guidl. Create the first one with `{ctx.prefix}role add`"
            if result:
                output = []
                for key in result:
                    try:
                        channel = self.bot.get_guild(key['guild_id']).get_channel(key['channel_id'])
                        await channel.fetch_message(key['message_id'])
                        output.append(dict(key))
                        output[-1]['roleids'] = ','.join([ID for ID in output[-1]['roleids'].split(',') if ctx.guild.get_role(int(ID))])
                        await self.bot.db.execute('UPDATE roles SET roleids=? WHERE message_id=?', (output[-1]['roleids'], key['message_id']))
                    except:
                        deleted+=1
                        await self.bot.db.execute('DELETE FROM roles WHERE message_id=?', (key['message_id'],))
                if output:
                    m = '\n'.join([f'- Rule number {key["rowid"]} : [Message](https://discord.com/channels/{key["guild_id"]}/{key["channel_id"]}/{key["message_id"]} "Link to the original message") | {key["emoji"]} | {", ".join([ctx.guild.get_role(int(ID)).name for ID in key["roleids"].split(",")])}' for key in output])

            embed = discord.Embed(title = f'Rules for guild {ctx.guild.name}', color = self.bot.colors['blue'], description = "List of all the rules defined. You need to use the rule number to use the `delete` action." + (f" {deleted} rules were deleted because the original message didn't exist anymore" if deleted else ''))
            embed.add_field(name = "The rules :", value = m)
            await ctx.send(embed = embed)
        elif action.lower() == 'remove':
            await ctx.send('Please enter the number associated to the rule you want to remove (partially or totally) in less than 30 seconds')
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()
            try:
                message = await self.bot.wait_for('message', check = check, timeout = 30)
            except asyncio.TimeoutError:
                return await ctx.send("You didn't answer in time. I'm ignoring this command")
            cur = await self.bot.db.execute('SELECT * FROM roles WHERE rowid=?', (int(message.content),))
            result = await cur.fetchone()
            if result:
                try:
                    await self.bot.get_guild(result['guild_id']).get_channel(result['channel_id']).fetch_message(result['message_id'])
                    if result['guild_id'] == ctx.guild.id:
                        roles = []
                        for role_id in result['roleids'].split(','):
                            R = ctx.guild.get_role(int(role_id))
                            if R:
                                roles.append((role_id, R.name))
                        await self.bot.db.execute('UPDATE roles SET roleids=? WHERE message_id=?',(','.join([str(r[0]) for r in roles]), result['message_id']))
                        embed = discord.Embed(title = f"Informations about rule number {message.content}")
                        embed.add_field(name = "Message :", value = f'[Click here](https://discord.com/channels/{result["guild_id"]}/{result["channel_id"]}/{result["message_id"]} "Link to the original message")')
                        embed.add_field(name = "Emoji :", value = result['emoji'])
                        embed.add_field(name = "Roles :", value = ' - '+'\n - '.join([f"Role n°{i+1} : {roles[i][1]}" for i in range(len(roles))]))
                        await ctx.send(embed = embed)
                        await ctx.send('Please enter a comma-separated list of the numbers of the roles you want to remove in less than 30 seconds')

                        def check(message):
                            return message.author == ctx.author and message.channel == ctx.channel and all([k.isdigit() for k in message.content.replace(' ','').split(',')])
                        try:
                            message = await self.bot.wait_for('message', check = check, timeout = 30)
                        except asyncio.TimeoutError:
                            await self.bot.db.commit()
                            return await ctx.send("You didn't answer in time. I'm ignoring this command")

                        role_numbers = [int(k) for k in message.content.replace(' ','').split(',')]

                        if not all([0 < k <= len(roles) for k in role_numbers]):
                            await ctx.send('You entered wrong values for the indexes. Please re-run the command with correct values.')
                        else:
                            await self.bot.db.execute("UPDATE roles set roleids=? WHERE message_id=?", (','.join([roles[i][0] for i in range(len(roles)) if not i+1 in role_numbers]), result['message_id']))
                            await ctx.send(f'I successfully removed those {len(role_numbers)} roles from the rule')
                        return self.bot.db.commit()
                except:
                    await self.bot.db.execute('DELETE FROM roles WHERE message_id=?', (result['message_id'],))
                    await self.bot.db.commit()
                    return await ctx.send('The message associated with this rule has been deleted. I thus removed the rule.')

            await ctx.send("The rule you're trying to access doesn't exist in this guild")
        else:
            await ctx.send('The action must be one of `add`, `info` and `remove`')
        await self.bot.db.commit()

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(administrator=True)
    async def swear(self,ctx,word=None):
        """You can specify a word to add/remove it from the list of forbidden words, or you can also don't specify one to check the swear filter's status. Specify on/off to turn it on/off, auto to turn the autodetection on/off, and notification if you want or not me to DM the guild owner if I can't delete a message (only him can use this).
        NO SWEAR WORDS IN MY CHRISTIAN SERVER !"""
        await self.bot.db.execute(f"CREATE TABLE IF NOT EXISTS guild_{ctx.guild.id}_swear_words (swear TINYTEXT)")
        if word:
            word=word.lower()
            if word == "on":
                await self.bot.db.execute('INSERT INTO swear (id, manual_on) VALUES (?, 1) ON DUPLICATE UPDATE manual_on=1', (ctx.guild.id,))
                await ctx.send("Swear filter turned on")
            elif word == "off":
                await self.bot.db.execute('INSERT INTO swear (id, manual_on) VALUES (?, 0) ON DUPLICATE UPDATE manual_on=0', (ctx.guild.id,))
                await ctx.send("Swear filter turned off")
            elif word == "auto":
                cur = await self.bot.db.execute('SELECT * FROM swear WHERE id=?', (ctx.guild.id,))
                result = await cur.fetchone()
                if result:
                    if result.get('notification'):
                        await self.bot.db.execute('UPDATE swear SET notification=0 WHERE id=?', (ctx.guild.id,))
                        await ctx.send('Autodetection turned off')
                    else:
                        await self.bot.db.execute('UPDATE swear SET autoswear=1 WHERE id=?', (ctx.guild.id,))
                        await ctx.send('Autodetection turned on')
                else:
                    await self.bot.db.execute('INSERT INTO swear (id, manual_on) VALUES (?, 1)', (ctx.guild.id,))
                    await ctx.send('Autodetection turned on')
            elif word == "notification":
                if not ctx.guild.owner == ctx.author:
                    return await ctx.send('As he is the one alerted, only the guild owner can change this setting')
                cur = await self.bot.db.execute('SELECT * FROM swear WHERE id=?', (ctx.guild.id,))
                result = await cur.fetchone()
                if result:
                    if result.get('autoswear'):
                        await self.bot.db.execute('UPDATE swear SET notification=0 WHERE id=?', (ctx.guild.id,))
                        await ctx.send('The alert has been disabled')
                    else:
                        await self.bot.db.execute('UPDATE swear SET notification=1 WHERE id=?', (ctx.guild.id,))
                        await ctx.send('The alert has been enabled')
                else:
                    await self.bot.db.execute("INSERT INTO swear (id, notification) VALUES (?, 0)", (ctx.guild.id,))
                    await ctx.send('The alert has been disabled')
            else:
                if len(word)>255:
                    return await ctx.send("The swear words can't have a length of more than 255")
                cur = await self.bot.db.execute(f"SELECT * FROM guild_{ctx.guild.id}_swear_words WHERE swear=?", (word,))
                result = await cur.fetchone()
                if result:
                    await self.bot.db.execute(f"DELETE FROM guild_{ctx.guild.id}_swear_words WHERE swear=?", (word,))
                    await ctx.send(f"The word {word} was remove from this guild's list of swear words")
                else:
                    await self.bot.db.execute(f"INSERT INTO guild_{ctx.guild.id}_swear_words VALUES (?)", (word,))
                    await ctx.send(f"The word {word} was added to this guild's list of swear words")
            await self.bot.db.commit()
        else:
            cur = await self.bot.db.execute('SELECT * FROM swear WHERE id=?',(ctx.guild.id,))
            status = await cur.fetchone()
            if status is None:
                status = {'manual_on':0, 'autoswear':0, 'notification':1}

            cur = await self.bot.db.execute(f'SELECT * from guild_{ctx.guild.id}_swear_words')
            swear_words = tuple(await cur.fetchall())

            embed = discord.Embed(title = f"Swear words in {ctx.guild.name}", colour=self.bot.colors['yellow'])
            embed.add_field(name = "Manual filter status", value = "Offline" if status['manual_on'] else "Online")
            embed.add_field(name = "Auto filter status", value = "Online" if status['autoswear'] else "Offline")
            embed.add_field(name = "Alert message status (in case I cannot delete a message)", value = "Enabled" if status['notification'] else "Disabled")
            embed.add_field(name = "Guild-specific swear words",value = " - " + "\n - ".join(swear_words) if swear_words else "No swear words are defined for this guild", inline=False)
            await ctx.send(embed = embed)

    @commands.Cog.listener('on_raw_reaction_add')
    async def role_adder(self,payload):
        cur = await self.bot.db.execute('SELECT rowid, * FROM roles WHERE message_id=? AND emoji=?', (payload.message_id, payload.emoji.name))
        result = await cur.fetchone()
        if result:
            guild = self.bot.get_guild(payload.guild_id)
            roles = (guild.get_role(int(r)) for r in result['roleids'].split(','))
            try:
                await payload.member.add_roles(*(r for r in roles if r), reason = f"Rule n°{result['rowid']}")
            except :
                pass

    @commands.Cog.listener('on_raw_reaction_remove')
    async def role_remover(self,payload):
        cur = await self.bot.db.execute('SELECT rowid, * FROM roles WHERE message_id=? AND emoji=?', (payload.message_id, payload.emoji.name))
        result = await cur.fetchone()
        if result:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            roles = (guild.get_role(int(r)) for r in result['roleids'].split(','))
            try:
                await member.remove_roles(*(r for r in roles if r), reason = f"Rule n°{result['rowid']}")
            except :
                pass

    @commands.Cog.listener("on_message")
    async def no_swear_words(self,message):
        if message.author == self.bot or not isinstance(message.author, discord.Member):
            return
        if message.channel.is_nsfw() or message.author.guild_permissions.manage_messages:
            return
        try:
            cur = await self.bot.db.execute('SELECT * FROM swear WHERE id=?',(message.guild.id,))
            status = await cur.fetchone()
            if status['autoswear']:
                for s in auto_swear_detection:
                    if s in message.content.lower().split(' '):
                        try:
                            await message.delete()
                        except discord.Forbidden:
                            await message.guild.owner.send(f"{message.author} used a swear word : `{s}`, but I lack the permissions to delete the message. Please give them back to me. You can use `€swear notification` to turn this alert off.")
                        return
            if status['manual_on']:
                cur = await self.bot.db.execute(f"SELECT * FROM guild_{ctx.guild.id}_swear_words")
                swear_words = tuple(await cur.fetchall())
                for s in swear_words:
                    if s in message.content.lower().split(' '):
                        try:
                            await message.delete()
                        except discord.Forbidden:
                            if status['notification']:
                                await message.guild.owner.send(f"{message.author} used a swear word : `{s}`, but I lack the permissions to delete the message. Please give them back to me. You can use `€swear notification` to turn this alert off.")
                        break
        except:
            pass

def setup(bot):
    bot.add_cog(Moderation(bot))
