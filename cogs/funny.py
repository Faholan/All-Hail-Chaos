"""MIT License

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
SOFTWARE."""

import asyncio
from os import path
from random import randint,choice

import discord
from discord.ext import commands

#All the data files necessary for the commands
file=open('data'+path.sep+'deaths.txt','r',encoding='utf-8')
death=file.readlines()
file.close()
file=open('data'+path.sep+'Excuses.txt','r',encoding='utf-8')
excuses=file.readlines()
file.close()
file=open('data'+path.sep+'weapons.txt','r',encoding='utf-8')
weapons=file.readlines()
file.close()

#Special effects for the fight command
def pink(attacking,victim,weapons):
    return (('Chaotic energies swirl around you, making you pink for 3 turns','','Life in pink',attacking.avatar_url),(victim.hit(choice(weapons).split('|'))))
def tp(attacking,victim,weapons):
    return [('Chaotic energies swirl around you. You were teleported 20 km away in a random direction, thus missing your attack','','Teleportation',attacking.avatar_url)]
def combustion(attacking,victim,weapons):
    attacking.pv-=100
    return (('{attacking} suddenly bursts into a fireball, losing 100 HP','','Spontaneous combustion','https://i.ytimg.com/vi/ymsiLGVsi_k/maxresdefault.jpg'),(victim.hit(choice(weapons).split('|'))))
def election(attacking,victim,weapons):
    return ((victim.hit(choice(weapons).split('|'))),('Right after his election, Donald Trump built a wall between {attacking} and {defending}. He must kip his turn','',"Donald Trump's election",'https://d.newsweek.com/en/full/607858/adsgads.jpg'),(victim.hit(choice(weapons).split('|'))))
def mishap(attacking,victim,weapons):
    a=list(str(attacking.pv))
    a.reverse()
    attacking.pv=int(''.join(a))
    v=list(str(victim.pv))
    v.reverse()
    victim.pv=int(''.join(v))
    return (("Because of a lunatic divine scribe, the two players' HP were reversed. Have a good day",'','Transcription mishap','https://i.ytimg.com/vi/-dKG0gQKA3I/maxresdefault.jpg'),(victim.hit(choice(weapons).split('|'))))
def double(attacking,victim,weapons):
    attacking.pv,victim.pv=victim.pv,attacking.pv
    return (("Bob, god of Chaos and Spaghettis, decided that {attacking}'s and {defending}'s shall be exhanged",'','Double trigonometric reversed possession',attacking.avatar_url),(victim.hit(choice(weapons).split('|'))))
#Crom's fury : Berserk attack
def intervention(attacking,victim,weapons):
    attacking.pv,victim.pv=1000,1000
    return (('Michel, god of dad jokes, decided to restart the fight : each player now has 1000 HP','',"Michel's intervention",attacking.avatar_url),(victim.hit(choice(weapons).split('|'))))
def fumble(attacking,victim,weapons):
    m,d,attack,url=attacking.hit(choice(weapons).split('|'))
    return (('{attacking} just hurt himself !','','Fumble',attacking.avatar_url),(m.format(defending=attacking.display_name,attacking=attacking.display_name, damage = d),d,attack,url))
def armor(attacking,victim,weapons):
    m,d,attack,url=victim.hit(choice(weapons).split('|'))
    attacking.pv-=round(int(d)/2)
    return (("{defending} wore a thorny armor, and {attacking} thus hurts himself for half the damage !",'',"Thorny armor",'https://66.media.tumblr.com/e68eb510217f17f96e1a7249294a01ee/tumblr_p7yj5oWrO91rvzucio1_1280.jpg'),(m,d,attack,url))
def steal(attacking,victim,weapons):
    m,d,attack,url=victim.hit(choice(weapons).split('|'))
    attacking.pv+=round(int(d)/2)
    return (('{attacking}, thanks to a demonic ritual to the glory of our lord Satan, steals half the HP lost by {defending}.','',"Life steal",attacking.avatar_url),(m,d,attack,url))
def depression(attacking,victim,weapons):
    return (("{defending} thinks he is basically a piece of shit (which isn't totally false, by the way), making him pretty much easier to hit",'','Depression',victim.avatar_url),(victim.hit(choice(weapons).split('|'),10)))
def bottle(attacking,victim,weapons):
    return (("{attacking} tried drinking from the hornet-filled bottle. He logically cannot very well aim for {defending}",'','Hornet bottle',attacking.avatar_url),(victim.hit(choice(weapons).split('|'),-10)))


chaos=[pink,tp,combustion,election,mishap,double,intervention,fumble,armor,steal,depression,bottle]

class fighter(): #Class for the fight command
    def __init__(self,user):
        self.display_name=user.display_name
        self.id=user.id
        self.mention=user.mention
        self.avatar_url=str(user.avatar_url)
        self.pv=1000
    def hit(self,weapon,pbonus=0):
        if len(weapon)==8:
            name,touche,m,M,p,rate,url,url2=weapon
        elif len(weapon)==7:
            name,touche,m,M,p,rate,url=weapon
            url2=url
        else:
            name,touche,m,M,p,rate=weapon
            url=url2=self.avatar_url
        pr=randint(1,100)+pbonus
        if pr>int(p):
            return rate,'',name,url2
        else:
            d=randint(int(m),int(M))
            self.pv-=d
            return touche,str(d),name,url

class Funny(commands.Cog):
    '''Some funny commands'''
    def __init__(self,bot):
        self.bot=bot

    async def adventure(self,ctx,*,aventure=None): #Let me finish story.py first
        try:
            from bin.story import adder
            self.adventures=adder(ctx)
        except:
            await ctx.send('This command is still in development.')

    @commands.command()
    async def chuck(self,ctx):
        """Get a random Chuck Norris joke"""
        if randint(0,1):
            async with self.bot.aio_session.get("https://api.chucknorris.io/jokes/random") as response:
                joke = await response.json()
                return await ctx.send(joke["value"])
        if ctx.guild:
            if not ctx.channel.is_nsfw():
                async with self.bot.aio_session.get("http://api.icndb.com/jokes/random?exclude=[explicit]") as response:
                    joke = await response.json()
                    return await ctx.send(joke["value"]["joke"])
        async with self.bot.aio_session.get("http://api.icndb.com/jokes/random") as response:
            joke = await response.json()
            await ctx.send(joke["value"]["joke"].replace('&quote','"'))

    @commands.command()
    async def dad(self,ctx):
        """Get a random dad joke"""
        async with self.bot.aio_session.get("https://icanhazdadjoke.com/slack") as response:
            joke = await response.json()
            await ctx.send(joke['attachments'][0]['text'])

    @commands.command()
    async def dong(self,ctx,dick:discord.Member=None):
        """How long is this person's dong ?"""
        if not dick:
            dick=ctx.author
        await ctx.send(f"{dick.mention}'s magnum dong is this long : 8{'='*randint(0,10)}>")

    @commands.command(ignore_extra=True)
    async def excuse(self,ctx):
        '''We all do mishaps, and we all need a good excuse once in a while.'''
        r='\n' #One cannot use backslash in a f-string
        await ctx.send(f"I'm sorry master... it's because {choice(excuses[0].split('|')).strip(r)} {choice(excuses[1].split('|')).strip(r)} in {choice(excuses[2].split('|')).strip(r)} and all of that because of {choice(excuses[3].split('|')).strip(r)} {choice(excuses[4].split('|')).strip(r)} which {choice(excuses[5].split('|')).strip(r)} so it's not my fault !")

    @commands.command(aliases=['baston'],ignore_extra=False)
    @commands.guild_only()
    async def fight(self,ctx,cible:discord.Member):
        '''To punch someone to death. We won't be hold accountable for any broken crane, ripped guts or any other painful death.
        If you got any idea, use €suggestion fight [idea]'''
        attacker=fighter(ctx.author)
        defender=fighter(cible)
        if defender.id==attacker.id:
            await self.bot.httpcat(ctx,403,"You cannot fight alone. Try asking a friend you don't like pretty much.")
        elif defender.id==self.bot.user.id:
            await self.bot.httpcat(ctx,403,"You cannot fight me : I'm juste the supreme judge.")
        else:
            combat=True
            fight=[defender,attacker]
            while combat:
                next=fight[0]
                fight.reverse()
                if randint(1,100)>=85:
                    data=choice(chaos)(fight[0],next,weapons) #15% chance of provoking a random effect
                else:
                    data=([next.hit(choice(weapons).split('|'))])
                for m,d,attack,url in data:
                    embed=discord.Embed(title=attack,description=m.format(attacking=fight[0].display_name,defending=next.display_name,damage=d),colour=self.bot.get_color())
                    embed.set_author(name=fight[0].display_name,icon_url=fight[0].avatar_url)
                    embed.set_thumbnail(url=url)
                    await ctx.send(embed=embed)
                embed=discord.Embed(title=fight[0].display_name,colour=self.bot.get_color())
                embed.set_thumbnail(url=fight[0].avatar_url)
                embed.add_field(name='Remaining HP :',value=str(fight[0].pv))
                await ctx.send(embed=embed)
                embed=discord.Embed(title=next.display_name,colour=self.bot.get_color())
                embed.set_thumbnail(url=next.avatar_url)
                embed.add_field(name='Remaining HP :',value=str(next.pv))
                await ctx.send(embed=embed)
                if next.pv>0 and fight[0].pv>0:
                    def check(m):
                        return m.author.id==next.id and m.content.lower().startswith(f"defend {fight[0].display_name.lower()}") and m.channel==ctx.channel
                    await ctx.send(f"{next.mention}, send `defend {fight[0].display_name}` in the next 30 seconds, or run away like a coward.")
                    try:
                        msg=await self.bot.wait_for('message',check=check,timeout=30.0)
                    except asyncio.TimeoutError:
                        await ctx.send(next.display_name+' is just a coward.')
                        combat=False
                elif next.pv<fight[0].pv:
                    combat=False
                    await ctx.send(fight[0].display_name+' annihilated '+next.display_name+'. What a show !')
                else:
                    combat=False
                    await ctx.send(next.display_name+' annihilated '+fight[0].display_name+'. What a show !')

    @commands.command()
    async def kill(self,ctx,kill,*kills):
        '''Just in case you wanna kill your neighbour.
        If you have an idea for an horrible death, use €suggestion fight [idea]'''
        await ctx.send('\n'.join([choice(death).format(author=ctx.message.author.display_name,victim=dead) for dead in [kill]+list(kills)]))

    @commands.command(aliases=['dice'])
    async def roll(self,ctx,*,expr):
        '''To roll dices
        Syntax example : €roll 1d5+7 - 3d8 (whitespaces are ignored)'''
        expr=expr.replace(" ","")
        char=[str(i) for i in range(10)]+["d","+","-"]
        for c in expr:
            if not c in char:
                return await ctx.send(f"Invalid character : `{c}` at position `{expr.index(c)}`")
        if not expr[0].isdigit() or not expr[-1].isdigit():
            return await ctx.send("The first and last characters must be digits")
        b=''
        a=''
        s='+'
        t=[]
        for i in expr:
            if i=='d':
                if a:
                    return await ctx.send("The expression you enterded isn't valid (d character used while rolling dice)")
                a='+'
            elif i.isdigit():
                if a:
                    a+=i
                else:
                    b+=i
            else:
                if b=='' or a=='+':
                    return await ctx.send('You cannot roll empty dices or empty times a dice')
                if a=='':
                    t.append(s+b)
                    b=''
                    s=i
                elif int(a)==0:
                    return await ctx.send("You cannot roll a 0-dice")
                else:
                    t.append([s+str(randint(1,int(a))) for _ in range(int(b))])
                    a=''
                    b=''
                    s=i
        if b=='':
            return await ctx.send('You cannot roll empty dices or empty times a dice')
        if a=='':
            t.append(s+b)
        elif int(a)==0:
            return await ctx.send("You cannot roll a 0-dice")
        else:
            t.append([s+str(randint(1,int(a))) for _ in range(int(b))])
        await ctx.send(self.summer(t,ctx.author.mention))

    def summer(self,l,author):
        k=[]
        t=0
        for n in l:
            if type(n)==str:
                k.append(str(int(n)))
                t+=int(n)
            elif len(n)==1:
                t+=int(n[0])
                k.append(str(int(n[0])))
            else:
                plus=sum([int(i) for i in n])
                k.append(''.join([j[0]+" "+j[1:]+" " for j in n])[1:] + f"= {plus}")
                t+=plus
        r = ',   '.join(k)
        if not r[0].isdigit():
            r=r[1:]
        return f"{author} rolled **{t}**. ({r})"

def setup(bot):
    bot.add_cog(Funny(bot))
