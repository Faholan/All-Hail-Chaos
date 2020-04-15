import discord
import pickle
from discord.ext import commands
from os import path
import typing

class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        try:
            self.reactions=pickle.load(open("data"+path.sep+"moderation.DAT",mode='rb'))
        except:
            self.reactions={}

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self,ctx,who:commands.Greedy[typing.Union[discord.Role,discord.Member]],reason=None):
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
                                await ctx.send("I cannot ban the guild owner")
                            elif member!=ctx.me:
                                if not member in banning:
                                    banning.append(member)
                            else:
                                await ctx.send("I cannot ban myself")
                else:
                    await ctx.send(f"You cannot ban the role {banned.name} : it is higher than your highest role")
            else:
                if banned==ctx.me:
                    await ctx.send("I cannot ban myself")
                elif ctx.me.roles[-1]<=banned.roles[-1]:
                    await ctx.send(f"I cannot ban {banned.name} : he has a higher role than me")
                elif banned==ctx.guild.owner:
                    await ctx.send(f"I cannot ban {banned.name} : he is the guild owner")
                elif not member in banning:
                    banning.append(member)
        r='\n'
        if reason:
            await ctx.send(f"You're about to ban {len(banning)} members because of `{reason}` :{r}{r+' -'.join([member.mention for member in banning])}{r}Do you want to proceed ? (y/n)")
        else:
            await ctx.send(f"You're about to ban {len(banning)} members :{r}{r+' -'.join([member.mention for member in banning])}{r}Do you want to proceed ? (y/n)")
        def check(m):
            return m.author==ctx.author and (m.content.lower().startswith('y') or m.content.lower.startswith('n')) and m.channel==ctx.channel
        try:
            msg=await self.bot.wait_for('message',check=check,timeout=30.0)
            proceed=msg.content.lower().startswith('y')
        except asyncio.TimeoutError:
            await ctx.send('Cancelling the ban')
            proceed=False
        if proceed:
            for m in banning:
                await m.ban(reason=reason)
            if roles:
                if reason:
                    await ctx.send(f"You're about to delete {len(roles)} roles because of `{reason}` :{r}{r+' -'.join([role.mention if role.mentionable else role.name for role in roles])}{r}Do you want to proceed ? (y/n)")
                else:
                    await ctx.send(f"You're about to delete {len(roles)} roles :{r}{r+' -'.join([role.mention if role.mentionable else role.name for role in roles])}{r}Do you want to proceed ? (y/n)")
                try:
                    msg=await self.bot.wait_for('message',check=check,timeout=30.0)
                    proceed=msg.content.lower().startswith('y')
                except asyncio.TimeoutError:
                    await ctx.send('Cancelling the deletion')
                    proceed=False
                if proceed:
                    for role in roles:
                        await role.delete(reason=reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self,ctx,who:commands.Greedy[typing.Union[discord.Role,discord.Member]],reason=None):
        """Command used to kick users. You can specify members or roles. The bot will then kick all the members you specified, and all the members having the specified role. You can specify at the end a reason for the kick
        You need the `kick members` permission, and your highest role needs to be higher than the others'. The bot then deletes the kicked roles"""
        kicking=[]
        roles=[]
        for kicked in who:
            if isinstance(kicked,discord.Role):
                if kicked.is_default():
                    await ctx.send("You cannot kick the default role.")
                elif ctx.me.roles[-1]<=kicked:
                    await ctx.send(f"I cannot kick the role {kicked.name} : it is higher than my highest role")
                elif ctx.author.roles[-1]>kicked:
                    if not kicked in roles:
                        roles.append(kicked)
                        for member in kicked.members:
                            if member==ctx.guild.owner:
                                await ctx.send("I cannot kick the guild owner")
                            elif member!=ctx.me:
                                if not member in kicking:
                                    kicking.append(member)
                            else:
                                await ctx.send("I cannot kick myself")
                else:
                    await ctx.send(f"You cannot kick the role {kicked.name} : it is higher than your highest role")
            else:
                if kicked==ctx.me:
                    await ctx.send("I cannot kick myself")
                elif ctx.me.roles[-1]<=kicked.roles[-1]:
                    await ctx.send(f"I cannot kick {kicked.name} : he has a higher role than me")
                elif kicked==ctx.guild.owner:
                    await ctx.send(f"I cannot kick {kicked.name} : he is the guild owner")
                elif not member in kicking:
                    kicking.append(member)
        r='\n'
        if reason:
            await ctx.send(f"You're about to kick {len(kicking)} members because of `{reason}` :{r}{r+' -'.join([member.mention for member in kicking])}{r}Do you want to proceed ? (y/n)")
        else:
            await ctx.send(f"You're about to kick {len(kicking)} members :{r}{r+' -'.join([member.mention for member in kicking])}{r}Do you want to proceed ? (y/n)")
        def check(m):
            return m.author==ctx.author and (m.content.lower().startswith('y') or m.content.lower.startswith('n')) and m.channel==ctx.channel
        try:
            msg=await self.bot.wait_for('message',check=check,timeout=30.0)
            proceed=msg.content.lower().startswith('y')
        except asyncio.TimeoutError:
            await ctx.send('Cancelling the kick')
            proceed=False
        if proceed:
            for m in kicking:
                await m.kick(reason=reason)
            if roles:
                if reason:
                    await ctx.send(f"You're about to delete {len(roles)} roles because of `{reason}` :{r}{r+' -'.join([role.mention if role.mentionable else role.name for role in roles])}{r}Do you want to proceed ? (y/n)")
                else:
                    await ctx.send(f"You're about to delete {len(roles)} roles :{r}{r+' -'.join([role.mention if role.mentionable else role.name for role in roles])}{r}Do you want to proceed ? (y/n)")
                try:
                    msg=await self.bot.wait_for('message',check=check,timeout=30.0)
                    proceed=msg.content.lower().startswith('y')
                except asyncio.TimeoutError:
                    await ctx.send('Cancelling the deletion')
                    proceed=False
                if proceed:
                    for role in roles:
                        await role.delete(reason=reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self,ctx,message:discord.Message, role:commands.Greedy[discord.Role], emoji:discord.PartialEmoji):
        """This command allows you to automatically give a role to anyone who reacts with a given emoji to a given message. The order is : message, role, emoji
        You can also use this command to cancel the assignation, or use it multiple times/with different roles to add multiple roles on reaction
        We both need the `manage messages` permission for that."""
        if role in self.reactions.get((message.id,emoji),[]):
            self.reactions[(message.id,emoji)].remove(role)
        else:
            self.reactions[(message.id,emoji)]=self.reactions.get((message.id,emoji),[])+[role]
        if self.reactions[(message.id,emoji)]==[]:
            self.reactions.pop((message.id,emoji))
        pickle.dump(self.reactions,open("data"+path.sep+"moderation.DAT",mode='wb'))
        await ctx.send("Role assignment updated")

    @commands.Cog.listener('on_raw_reaction_add')
    async def role_adder(self,payload):
        if payload.guild_id:
            if (payload.message_id,payload.emoji) in self.reactions:
                await payload.member.edit(roles=payload.member.roles+[r for r in self.reactions[(payload.message,payload.emoji)] if not r in payload.member.roles])

    @commands.Cog.listener('on_raw_reaction_remove')
    async def role_remover(self,payload):
        if payload.guild_id:
            if (payload.message_id,payload.emoji) in self.reactions:
                member=self.bot.get_guild(payload.guild_id).get_member(payload.member_id)
                await member.edit(roles=[r for r in member.roles if not r in self.reactions[(payload.message,payload.emoji)]])

def setup(bot):
    bot.add_cog(Moderation(bot))
