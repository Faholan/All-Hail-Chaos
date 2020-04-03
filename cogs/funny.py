from discord.ext import commands
from random import randint,choice
import pickle
import asyncio
import discord

file=open('data\\morts.txt','r',encoding='utf-8')
mort=file.readlines()
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

def rose(attaquant,victime,weapons):
    return (('Les énergies chaotiques vous rendent rose pour 3 tour','','Je vois la vie en rose',attaquant.avatar_url),(victime.coup(choice(weapons).split('|'))))
def tp(attaquant,victime,weapons):
    return [('Vous avez été téléporté à 20km dans une direction aléatoire, et ratez donc votre attaque','','Téléportation',attaquant.avatar_url)]
def combustion(attaquant,victime,weapons):
    attaquant.pv-=100
    return (('{attaquant} prend inexpliquablement feu, et perd 100 points de vie','','Combustion spontanée','https://i.ytimg.com/vi/ymsiLGVsi_k/maxresdefault.jpg'),(victime.coup(choice(weapons).split('|'))))
def election(attaquant,victime,weapons):
    return ((victime.coup(choice(weapons).split('|'))),('Suite à son élection, Donald Trump a construit un mur séparant {attaquant} de {defenseur}. Ce dernier est forcé de passer son tour','','Élection de Donald Trump','https://d.newsweek.com/en/full/607858/adsgads.jpg'),(victime.coup(choice(weapons).split('|'))))
def erreur(attaquant,victime,weapons):
    a=list(str(attaquant.pv))
    a.reverse()
    attaquant.pv=int(''.join(a))
    v=list(str(victime.pv))
    v.reverse()
    victime.pv=int(''.join(v))
    return (('Suite à une erreur de transcription, les PV des deux participants ont été renversés. Bonne journée','','Erreur de transcription','https://i.ytimg.com/vi/-dKG0gQKA3I/maxresdefault.jpg'),(victime.coup(choice(weapons).split('|'))))
def double(attaquant,victime,weapons):
    attaquant.pv,victime.pv=victime.pv,attaquant.pv
    return (('Le dieu du chaos a décidé que les PV de {attaquant} et de {defenseur} devaient être échangés.','','Double possession trigonométrique renversée',attaquant.avatar_url),(victime.coup(choice(weapons).split('|'))))
#Fureur de Crom : attaque berserk
def intervention(attaquant,victime,weapons):
    attaquant.pv,victime.pv=1000,1000
    return (('Michel, dieu des mauvaises blagues, a décidé de recommencer le combat : les deux participants ont maintenant 1000 PV','','Intervention de Michel',attaquant.avatar_url),(victime.coup(choice(weapons).split('|'))))
def echec(attaquant,victime,weapons):
    m,d,attaque,url=attaquant.coup(choice(weapons).split('|'))
    return (('{attaquant} se blesse !','','Echec critique',attaquant.avatar_url),(m.format(victime=attaquant.display_name),d,attaque,url))
def armure(attaquant,victime,weapons):
    m,d,attaque,url=victime.coup(choice(weapons).split('|'))
    attaquant.pv-=round(int(d)/2)
    return (('{defenseur} portait une armure d\'épines, et {attaquant} subit donc la moitié des dégâts infligés !','',"Armure d'épines",'https://66.media.tumblr.com/e68eb510217f17f96e1a7249294a01ee/tumblr_p7yj5oWrO91rvzucio1_1280.jpg'),(m,d,attaque,url))
def vol(attaquant,victime,weapons):
    m,d,attaque,url=victime.coup(choice(weapons).split('|'))
    attaquant.pv+=round(int(d)/2)
    return (('{attaquant} active une amulette sanglante, volant la moitié des points de vie perdus par {defenseur}.','',"Vol de vie",attaquant.avatar_url),(m,d,attaque,url))
def tabac(attaquant,victime,weapons):
    return (("{defenseur} est en train d'essayer de décrocher, en plein mois sans tabac. Il est donc bien plus simple à toucher",'','Mois sans tabac',victime.avatar_url),(victime.coup(choice(weapons).split('|'),10)))
def bouteille(attaquant,victime,weapons):
    return (("{attaquant} a eu la mauvaise idée de goûter au contenu de la bouteille avec le frelon. Il a donc quelques difficultés pour toucher {defendeur}",'','Frelon',attaquant.avatar_url),(victime.coup(choice(weapons).split('|'),-10)))


chaos=[rose,tp,combustion,election,erreur,double,intervention]

class fighter():
    def __init__(self,user):
        self.display_name=user.display_name
        self.id=user.id
        self.mention=user.mention
        self.avatar_url=str(user.avatar_url)
        self.pv=1000
    def coup(self,weapon,pbonus=0):
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
        self.diktat={'suggestion':'','s_kill':'de mort','s_paillard':'de chanson paillarde','s_excuse':"d'excuse",'s_fight':'de baston'}

    @commands.command(hidden=True,aliases=['s_kill','s_paillard','s_excuse','s_fight'])
    async def suggestion(self,ctx,idea,*ideas):
        '''Hidden command to make suggestions'''
        print(f'Idée {self.diktat[ctx.invoked_with]} soumise par {str(ctx.message.author)}'+' '.join([idea]+list(ideas)),file=open('ideas.log',mode='a'))
        await ctx.send('Thanks for your idea.')

    @commands.command()
    async def kill(self,ctx,kill,*kills):
        '''Just in case you wanna kill your neighbour.
        If you have an idea for an horrible death, use $s_kill [idea]'''
        await ctx.send('\n'.join([choice(mort).format(auteur=ctx.message.author.display_name,victime=dead) for dead in [kill]+kills]))

    @commands.command(ignore_extra=True)
    async def paillard(self,ctx):
        '''A utiliser en cas, hmmm... d'envie de rigoler, dirons-nous. (french only)
        If you got any idea, use $s_paillard [idea]'''
        await ctx.send(choice(chanson_paillarde).replace('|','\n'))

    @commands.command(ignore_extra=True)
    async def excuse(self,ctx):
        '''On fait tous des conneries, et on a tous besoin d'une bonne excuse. (french only)
        If you got any idea, use $s_excuse [idea]'''
        r='\n'
        await ctx.send(f"Je suis désolé, maître... c'est parce que {choice(excuses[0].split('|')).strip(r)} {choice(excuses[1].split('|')).strip(r)} dans {choice(excuses[2].split('|')).strip(r)} et tout ça à cause {choice(excuses[3].split('|')).strip(r)} {choice(excuses[4].split('|')).strip(r)} qui {choice(excuses[5].split('|')).strip(r)} donc c'est pas ma faute !")

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

    @commands.command(aliases=['baston'],ignore_extra=False)
    @commands.guild_only()
    async def fight(self,ctx,cible:discord.Member):
        '''To punch someone to death. We won't be hold accountable for any broken crane, ripped guts or any other painful death.
        If you got any idea, use $s_fight [idea]'''
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
                    data=([next.coup(choice(weapons).split('|'))])
                for m,d,attaque,url in data:
                    embed=discord.Embed(title=attaque,description=m.format(attaquant=fight[0].display_name,defenseur=next.display_name,degat=d),colour=choice([0x11806a,0x2ecc71,0x1f8b4c,0x3498db,0x206694,0x9b59b6,0x71368a,0xe91e63,0xad1457,0xf1c40f,0xc27c0e,0xe67e22,0xa84300,0xe74c3c,0x992d22]))
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
                    await ctx.send(next.mention+", send `defend {attaquant}` in the next 30 seconds, or run away like a coward.".format(attaquant=fight[0].display_name))
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

    async def adventure(self,ctx,*,aventure=None):
        try:
            from bin.story import adder
            self.aventures=adder(ctx)
        except:
            await ctx.send('Cette commande est en cours de développement.')

def setup(bot):
    bot.add_cog(funny(bot))
