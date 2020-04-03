from discord.ext import commands

def j2_boats(size):
    """Permet de placer de manière aléatoire les bateaux sur la grille"""
    j2,boats,cases=[],[],[]
    for i in range(10):
        j2.append([0]*10)
    for i in size:
        test=True
        while test:
            test=False
            a,b=[randint(0,9),randint(0,9)],randint(0,1)# 0 : horizontale, 1 : verticale
            if b:
                if a[1]<=10-i:
                    if a[1]!=0:
                        if j2[a[0]][a[1]-1]!=0:
                            test=True
                        if a[0]!=0:
                            if j2[a[0]-1][a[1]-1]!=0:
                                test=True
                        if a[0]!=9:
                            if j2[a[0]+1][a[1]-1]!=0:
                                test=True
                    if a[1]+i<10:
                        if j2[a[0]][a[1]+i]!=0:
                            test=True
                        if a[0]!=9:
                            if j2[a[0]+1][a[1]+i]!=0:
                                test=True
                        if a[0]!=0:
                            if j2[a[0]-1][a[1]+i]!=0:
                                test=True
                    if not test:
                        if a[0]==0:
                            for j in range(i):
                                if j2[0][a[1]+j]!=0 or j2[1][a[1]+j]!=0:
                                    test=True
                        elif a[0]==9:
                            for j in range(i):
                                if j2[9][a[1]+j]!=0 or j2[8][a[1]+j]!=0:
                                    test=True
                        else:
                            for j in range(i):
                                if j2[a[0]][a[1]+j]!=0 or j2[a[0]+1][a[1]+j]!=0 or j2[a[0]-1][a[1]+j]!=0 :
                                    test=True
                else:
                    test=True
                if not test:
                    boat=[]
                    for j in range(i):
                        j2[a[0]][a[1]+j]=1
                        boat.append((a[0],a[1]+j))
                    boats.append(boat)
                    cases=cases+boat
            else:
                if a[0]<=10-i:
                    if a[0]!=0:
                        if j2[a[0]-1][a[1]]!=0:
                            test=True
                        if a[1]!=0:
                            if j2[a[0]-1][a[1]-1]!=0:
                                test=True
                        if a[1]!=9:
                            if j2[a[0]-1][a[1]+1]!=0:
                                test=True
                    if a[0]+i<10:
                        if j2[a[0]+i][a[1]]!=0:
                            test=True
                        if a[1]!=9:
                            if j2[a[0]+i][a[1]+1]!=0:
                                test=True
                        if a[1]!=0:
                            if j2[a[0]+i][a[1]-1]!=0:
                                test=True
                    if not test:
                        if a[1]==0:
                            for j in range(i):
                                if j2[a[0]+j][0]!=0 or j2[a[0]+j][1]!=0:
                                    test=True
                        elif a[1]==9:
                            for j in range(i):
                                if j2[a[0]+j][9]!=0 or j2[a[0]+j][8]!=0:
                                    test=True
                        else:
                            for j in range(i):
                                if j2[a[0]+j][a[1]]!=0 or j2[a[0]+j][a[1]+1]!=0 or j2[a[0]+j][a[1]-1]!=0:
                                    test=True
                else:
                    test=True
                if not test:
                    boat=[]
                    for j in range(i):
                        j2[a[0]+j][a[1]]=1
                        boat.append((a[0]+j,a[1]))
                    boats.append(boat)
                    cases=cases+boat
    return(boats,cases)
def ma_fonc(d,f):
    """Pas touche !(joe, candice)"""
    e=[]
    for i in range(10):
        for j in range(round(10/d)):
            e.append((i,d*j+i%d))
    for i in f:
        if i in e:
            e.remove(i)
    return e

class Bataille_navale(commands.Cog, name="Bataille navale"):
    def __init__(self,bot):
        self.bot=bot
        self.size=[5,4,3,3,2]
        self.arbitre=None
        self.is_playing=0
    def init(self):
        self.must_fire=[]
        self.dist=2
        self.not_possible=[]
        self.enemy_fire=ma_fonc(self.dist,self.not_possible)
        self.touched_player=[0,0,0,0,0]
        self.enemy_boats,self.check_enemy=j2_boats(self.size)

    def check(self,coups,b):
        for i in b:
            if i[0]!=0:
                self.not_possible.append((i[0]-1,i[1]))
                if (i[0]-1,i[1]) in coups:
                    coups.remove((i[0]-1,i[1]))
                if i[1]!=0:
                    self.not_possible.append((i[0]-1,i[1]-1))
                    if (i[0]-1,i[1]-1) in coups:
                        coups.remove((i[0]-1,i[1]-1))
                if i[1]!=9:
                    self.not_possible.append((i[0]-1,i[1]+1))
                    if (i[0]-1,i[1]+1) in coups:
                        coups.remove((i[0]-1,i[1]+1))
            if i[0]!=9:
                self.not_possible.append((i[0]+1,i[1]))
                if (i[0]+1,i[1]) in coups:
                    coups.remove((i[0]+1,i[1]))
                if i[1]!=0:
                    self.not_possible.append((i[0]+1,i[1]-1))
                    if (i[0]+1,i[1]-1) in coups:
                        coups.remove((i[0]+1,i[1]-1))
                if i[1]!=9:
                    self.not_possible.append((i[0]+1,i[1]+1))
                    if (i[0]+1,i[1]+1) in coups:
                        coups.remove((i[0]+1,i[1]+1))
        return coups

    def ia(self):
        """Le nom est assez explicite, à priori..."""
        if self.must_fire==[]: #Bon je sais c'est du random mais bon...
            fire=self.enemy_fire[randint(0,len(self.enemy_fire)-1)]
            if fire in self.check_player:
                self.must_fire.append(1)
                self.must_fire.append(fire)
                if fire[0]!=0:
                    self.must_fire.append((fire[0]-1,fire[1]))
                if fire[0]!=9:
                    self.must_fire.append((fire[0]+1,fire[1]))
                if fire[1]!=0:
                    self.must_fire.append((fire[0],fire[1]-1))
                if fire[1]!=9:
                    self.must_fire.append((fire[0],fire[1]+1))
                for i in range(5):
                    if (fire[0],fire[1]) in self.player_boats[i]:
                        self.touched_player[i]+=1
            return fire
        elif self.must_fire[0]==1:
            fire=self.must_fire[randint(2,len(self.must_fire)-1)]
            while fire in self.not_possible:
                fire=self.must_fire[randint(2,len(self.must_fire)-1)]
            self.not_possible.append(fire)
            self.must_fire.remove(fire)
            if fire in self.check_player:
                original=self.must_fire[1]
                self.must_fire.clear()
                coulé=True
                for i in range(5):
                    if (fire[0],fire[1]) in self.player_boats[i]:
                        self.touched_player[i]+=1
                        if self.touched_player[i]==size[i]:
                            if i==4:
                                if self.dist==2:
                                    self.dist=3
                                    self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                            if self.touched_player[3]==self.touched_player[2]==3==self.dist:
                                self.dist=4
                                self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                            if self.touched_player[2]==4==self.dist:
                                self.dist=5
                                self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                            coulé=False
                            self.enemy_fire=check(self.enemy_fire,self.player_boats[i])
                if coulé:
                    self.must_fire.append(2)
                    self.must_fire.append(original)
                    if fire[1]==original[1]:
                        if fire[0]==0:
                            self.must_fire[0]=3
                            self.must_fire.append((original[0]+1,original[1]))
                        elif fire[0]==9:
                            self.must_fire[0]=3
                            self.must_fire.append((original[0]-1,original[1]))
                        elif original[0]==0:
                            self.must_fire[0]=3
                            self.must_fire.append((fire[0]+1,original[1]))
                        elif original[0]==9:
                            self.must_fire[0]=3
                            self.must_fire.append((fire[0]-1,original[1]))
                        elif fire[0]==original[0]+1:
                            self.must_fire.append((fire[0]+1,original[1]))
                            self.must_fire.append((original[0]-1,original[1]))
                        else:
                            self.must_fire.append((fire[0]-1,original[1]))
                            self.must_fire.append((original[0]+1,original[1]))
                    else:
                        if fire[1]==0:
                            self.must_fire[0]=3
                            self.must_fire.append((original[0],original[1]+1))
                        elif fire[1]==9:
                            self.must_fire[0]=3
                            self.must_fire.append((original[0],original[1]-1))
                        elif original[1]==0:
                            self.must_fire[0]=3
                            self.must_fire.append((original[0],fire[1]+1))
                        elif original[1]==9:
                            self.must_fire[0]=3
                            self.must_fire.append((original[1],fire[1]-1))
                        elif fire[1]==original[1]+1:
                            self.must_fire.append((original[0],fire[1]+1))
                            self.must_fire.append((original[0],original[1]-1))
                        else:
                            self.must_fire.append((original[0],fire[1]-1))
                            self.must_fire.append((original[0],original[1]+1))
            return fire
        elif self.must_fire[0]==2:
            fire=self.must_fire[randint(2,3)]
            while fire in self.not_possible:
                fire=self.must_fire[randint(2,3)]
            self.must_fire.remove(fire)
            self.not_possible.append(fire)
            if fire in self.enemy_fire:
                self.enemy_fire.remove(fire)
            if fire in self.check_player:
                for i in range(5):
                    if (fire[0],fire[1]) in self.player_boats[i]:
                        self.touched_player[i]+=1
                        if self.touched_player[i]==size[i]:
                            if i==4:
                                if self.dist==2:
                                    self.dist=3
                                    self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                            if self.touched_player[3]==self.touched_player[2]==3==self.dist:
                                self.dist=4
                                self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                            if self.touched_player[2]==4==self.dist:
                                self.dist=5
                                self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                            self.enemy_fire=check(self.enemy_fire,self.player_boats[i])
                            self.must_fire.clear()
                        else:
                            if fire[0]<self.must_fire[1][0]:
                                if fire[0]==0:
                                    self.must_fire[0]=3
                                else:
                                    self.must_fire.append((fire[0]-1,fire[1]))
                            elif fire[0]>self.must_fire[1][0]:
                                if fire[0]==0:
                                    self.must_fire[0]=3
                                else:
                                    self.must_fire.append((fire[0]+1,fire[1]))
                            elif fire[1]<self.must_fire[1][1]:
                                if fire[1]==0:
                                    self.must_fire[0]=3
                                else:
                                    self.must_fire.append((fire[0],fire[1]-1))
                            elif fire[1]>self.must_fire[1][1]:
                                if fire[0]==0:
                                    self.must_fire[0]=3
                                else:
                                    self.must_fire.append((fire[0],fire[1]+1))
            else:
                self.must_fire[0]=3
            return fire
        elif self.must_fire[0]==3:
            fire=self.must_fire[2]
            self.not_possible.append(fire)
            if fire in self.enemy_fire:
                self.enemy_fire.remove(fire)
            for i in range(5):
                if (fire[0],fire[1]) in self.player_boats[i]:
                    self.touched_player[i]+=1
                    if self.touched_player[i]==size[i]:
                        if i==4:
                            if self.dist==2:
                                self.dist=3
                                self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                        if self.touched_player[3]==self.touched_player[2]==3==self.dist:
                            self.dist=4
                            self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                        if self.touched_player[2]==4==self.dist:
                            self.dist=5
                            self.enemy_fire=ma_fonc(self.dist,self.not_possible)
                        self.enemy_fire=check(self.enemy_fire,self.player_boats[i])
                        self.must_fire.clear()
            if self.must_fire!=[]:
                self.must_fire.remove(fire)
                if fire[0]<self.must_fire[1][0]:
                    self.must_fire.append((fire[0]-1,fire[1]))
                elif fire[0]>self.must_fire[1][0]:
                    self.must_fire.append((fire[0]+1,fire[1]))
                elif fire[1]<self.must_fire[1][1]:
                        self.must_fire.append((fire[0],fire[1]-1))
                elif fire[1]>self.must_fire[1][1]:
                    self.must_fire.append((fire[0],fire[1]+1))

    @commands.command()
    async def game(self,ctx):
        """Lance une partie"""
        if self.is_playing==0:
            self.is_playing=1
            self.init()
            await ctx.send('$1-'+';'.join([':'.join([str(self.enemy_boats[i][j][0])+'|'+str(self.enemy_boats[i][j][1]) for j in range(len(self.enemy_boats[i]))]) for i in range(len(self.enemy_boats))]))
        else:
            await ctx.send("Je suis en partie. Attends que j'ai finit.")
            
    @commands.Cog.listener()
    async def on_message(self,message):
        if self.is_playing==1:
            if message.content.startswith('$2-'):
                pb=[message.content.split('-')[1].split(';')[i].split(':') for i in range(len(message.content.split('-')[1].split(';')))]
                self.player_boats=[]
                self.check_player=[]
                for i in range(len(pb)):
                    g=[]
                    for j in range(len(pb[i])):
                        k=pb[i][j].split('|')
                        k[0],k[1]=int(k[0]),int(k[1])
                        g.append(k)
                        self.check_player.append(k)
                    self.player_boats.append(g)
                self.is_playing=2

        elif self.is_playing==2:
            if message.content.startswith('$start'):
                self.arbitre=message.author
                self.is_playing=3
                if message.content.startswith('$start-1'):
                    case=self.ia()
                    await message.channel.send(['A','B','C','D','E','F','G','H','I','J'][case[0]]+str(case[1]+1))

        elif self.is_playing==3:
            if message.author==arbitre:
                if message.content.startswith('$go-1'):
                    case=self.ia()
                    await message.channel.send(['A','B','C','D','E','F','G','H','I','J'][case[0]]+str(case[1]+1))
                elif message.content.startswith('$end'):
                    self.is_playing=0
                    await message.channel.send('$K1')

def setup(bot):
    bot.add_cog(Bataille_navale(bot))
