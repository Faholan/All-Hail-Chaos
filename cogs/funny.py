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

from discord.ext import commands
from random import randint,choice
import pickle
import asyncio
import discord

file=open('data\\deaths.txt','r',encoding='utf-8')
death=file.readlines()
file.close()
file=open('data\\paillard.txt','r',encoding='utf-8')
chanson_paillarde=file.readlines()
file.close()
file=open('data\\Excuses.txt','r',encoding='utf-8')
excuses=file.readlines()
file.close()
file=open('data\\weapons.txt','r',encoding='utf-8')
weapons=file.readlines()
file.close()

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
    return (('{attacking} just hurt himself !','','Fumble',attacking.avatar_url),(m.format(victim=attacking.display_name),d,attack,url))
def armor(attacking,victim,weapons):
    m,d,attack,url=victim.hit(choice(weapons).split('|'))
    attacking.pv-=round(int(d)/2)
    return (("{defending} wore a thorny armor, and {attacking} thus hurts himself for half the damage !",'',"Thorny armor",'https://66.media.tumblr.com/e68eb510217f17f96e1a7249294a01ee/tumblr_p7yj5oWrO91rvzucio1_1280.jpg'),(m,d,attack,url))
def steal(attacking,victim,weapons):
    m,d,attack,url=victim.hit(choice(weapons).split('|'))
    attacking.pv+=round(int(d)/2)
    return (('{attacking}, thanks to a demonic ritual to the glory of our lord Satan, steals half the HP lost by {defending}.','',"Life steal",attacking.avatar_url),(m,d,attack,url))
def depression(attacking,victim,weapons):
    return (("{defending} thinks he is basically a piec of shit (which isn't totally false, by the way), making him pretty much easier to hit",'','Depression',victim.avatar_url),(victim.hit(choice(weapons).split('|'),10)))
def bottle(attacking,victim,weapons):
    return (("{attacking} tried drinking from the hornet-filled bottle. He logically cannot very well aim for {defending}",'','Hornet bottle',attacking.avatar_url),(victim.hit(choice(weapons).split('|'),-10)))


chaos=[pink,tp,combustion,election,mishap,double,intervention,fumble,armor,steal,depression,bottle]

class fighter():
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

class funny(commands.Cog):
    '''Some funny commands'''
    def __init__(self,bot):
        self.bot=bot
        self.diktat={'suggestion':'','s_kill':'of death','s_paillard':'of lewd','s_excuse':"d'excuse",'s_fight':'of fight'}

    async def adventure(self,ctx,*,aventure=None):
        try:
            from bin.story import adder
            self.aventures=adder(ctx)
        except:
            await ctx.send('Cette commande est en cours de développement.')

    @commands.command(ignore_extra=True)
    async def excuse(self,ctx):
        '''On fait tous des conneries, et on a tous besoin d'une bonne excuse. (french only)
        If you got any idea, use €s_excuse [idea]'''
        r='\n'
        await ctx.send(f"Je suis désolé, maître... c'est parce que {choice(excuses[0].split('|')).strip(r)} {choice(excuses[1].split('|')).strip(r)} dans {choice(excuses[2].split('|')).strip(r)} et tout ça à cause {choice(excuses[3].split('|')).strip(r)} {choice(excuses[4].split('|')).strip(r)} qui {choice(excuses[5].split('|')).strip(r)} donc c'est pas ma faute !")

    @commands.command(aliases=['baston'],ignore_extra=False)
    @commands.guild_only()
    async def fight(self,ctx,cible:discord.Member):
        '''To punch someone to death. We won't be hold accountable for any broken crane, ripped guts or any other painful death.
        If you got any idea, use €s_fight [idea]'''
        attacker=fighter(ctx.author)
        defender=fighter(cible)
        if defender.id==attacker.id:
            await ctx.send("You cannot fight alone. Try asking a friend you don't like pretty much.")
        elif defender.id==self.bot.user.id:
            await ctx.send("You cannot fight me : I'm juste the supreme judge.")
        else:
            combat=True
            fight=[defender,attacker]
            while combat:
                next=fight[0]
                fight.reverse()
                if randint(1,100)>=85:
                    data=choice(chaos)(fight[0],next,weapons)
                else:
                    data=([next.hit(choice(weapons).split('|'))])
                for m,d,attack,url in data:
                    embed=discord.Embed(title=attack,description=m.format(attacking=fight[0].display_name,defending=next.display_name,damage=d),colour=choice([0x11806a,0x2ecc71,0x1f8b4c,0x3498db,0x206694,0x9b59b6,0x71368a,0xe91e63,0xad1457,0xf1c40f,0xc27c0e,0xe67e22,0xa84300,0xe74c3c,0x992d22]))
                    embed.set_author(name=fight[0].display_name,icon_url=fight[0].avatar_url)
                    embed.set_thumbnail(url=url)
                    await ctx.send(embed=embed)
                embed=discord.Embed(title=fight[0].display_name,colour=choice([0x11806a,0x2ecc71,0x1f8b4c,0x3498db,0x206694,0x9b59b6,0x71368a,0xe91e63,0xad1457,0xf1c40f,0xc27c0e,0xe67e22,0xa84300,0xe74c3c,0x992d22]))
                embed.set_thumbnail(url=fight[0].avatar_url)
                embed.add_field(name='Remaining HP :',value=str(fight[0].pv))
                await ctx.send(embed=embed)
                embed=discord.Embed(title=next.display_name,colour=choice([0x11806a,0x2ecc71,0x1f8b4c,0x3498db,0x206694,0x9b59b6,0x71368a,0xe91e63,0xad1457,0xf1c40f,0xc27c0e,0xe67e22,0xa84300,0xe74c3c,0x992d22]))
                embed.set_thumbnail(url=next.avatar_url)
                embed.add_field(name='Remaining HP :',value=str(next.pv))
                await ctx.send(embed=embed)
                if next.pv>0 and fight[0].pv>0:
                    def check(m):
                        return m.author.id==next.id and m.content.lower().startswith('defend '+fight[0].display_name) and m.channel==ctx.channel
                    await ctx.send(next.mention+", send `defend {attacking}` in the next 30 seconds, or run away like a coward.".format(attacking=fight[0].display_name))
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
        If you have an idea for an horrible death, use €s_kill [idea]'''
        await ctx.send('\n'.join([choice(death).format(author=ctx.message.author.display_name,victim=dead) for dead in [kill]+kills]))

    @commands.command(ignore_extra=True)
    async def paillard(self,ctx):
        '''A utiliser en cas, hmmm... d'envie de rigoler, dirons-nous. (french only)
        If you got any idea, use €s_paillard [idea]'''
        await ctx.send(choice(chanson_paillarde).replace('|','\n'))

    @commands.command(aliases=['dice'])
    async def roll(self,ctx,*,dice):
        '''To roll dices'''
        def de(n,m):
            return n*randint(1,m)
        def roller(owo):
            if not owo[0].isdigit():
                raise ValueError("'"+owo[0]+"' is not a number")
            c=0
            while owo[c].isdigit():
                c+=1
                if c==len(owo):
                    return owo
            if owo[c] in ['+','-','*']:
                if c+1==len(owo):
                    raise ValueError()
                return owo[:c]+owo[c]+roller(owo[:c+1])
            elif owo[c]=='d':
                d=c+1
                if not owo[d].isdigit():
                    raise ValueError()
                while owo[d].isdigit():
                    d+=1
                    if d==len(owo):
                        return 'de('+owo[:c]+','+owo[c+1:]+')'
                if owo[d] in ['+','-','*']:
                    if d+1==len(owo):
                        raise ValueError("Please specify the value you wanna roll")
                    return 'de('+owo[:c]+','+owo[c+1:d]+')'+owo[d]+roller(owo[d+1:])
        await ctx.send(str(eval(roller(dice))))

    @commands.command(hidden=True,aliases=['s_kill','s_paillard','s_excuse','s_fight'])
    async def suggestion(self,ctx,idea,*ideas):
        '''Hidden command to make suggestions'''
        print(f'Idea {self.diktat[ctx.invoked_with]} of {str(ctx.message.author)}'+' '.join([idea]+list(ideas)),file=open('ideas.log',mode='a'))
        await ctx.send('Thanks for your idea.')

def setup(bot):
    bot.add_cog(funny(bot))
