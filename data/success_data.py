"""This file resolves a pickle bug"""
from discord import Embed
from data import data

class Account():
    '''Class implementation of an account'''
    def __init__(self, identifier, succ):
        self.identifier = identifier
        self.succ = succ
        self.succ_state = []
        for s in self.succ:
            self.succ_state.append(False)

    def __str__(self):
        return self.identifier

    def __eq__(self, other):
        return self.identifier == other

    def __call__(self, ctx):
        embeds = []
        for i in range(len(self.succ)):
            if not self.succ_state[i]:
                s = self.succ[i](ctx)
                if s != None:
                    self.unlock_success(s)
                    embed = Embed(title = 'Succes unlocked !', description = s.name, colour = data.get_color())
                    embed.set_author(name = str(ctx.author), icon_url = str(ctx.author.avatar_url))
                    embed.set_thumbnail(url = 'https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg')
                    embed.add_field(name = s.description, value = 'Requirements met')
                    embeds.append(embed)
        return embeds

    def add_success(self, successes):
        '''In case the successes changed'''
        for s in successes:
            if s not in self.succ:
                self.succ.append(s)
                self.succ_state.append(False)
        for i in range(len(self.succ)):
            if self.succ[i] not in successes:
                self.succ.pop(i)
                self.succ_state.pop(i)

    def get_successes(self):
        gotten = []
        locked = []
        for s in range(len(self.succ_state)):
            if self.succ_state[s]:
                gotten.append(self.succ[s])
            else:
                locked.append(self.succ[s])
        return gotten,locked,len(self.succ)

    def reset(self):
        for i in range(len(self.succ_state)):
            self.succ_state[i] = False

    def unlock_success(self,success):
        self.succ_state[self.succ.index(success)] = True

class Success():
    '''Class implementation of a Discord success'''
    def __init__(self, name, description, condition, description_is_visible = True, extra_data = None, avancement=None):
        self.name = name
        self.description = description
        self.condition = condition
        self.description_is_visible = description_is_visible
        self.extra_data = extra_data
        self.avancement = avancement
        if description_is_visible:
            self.locked = description
        else:
            self.locked = 'Hidden success'

    def __eq__(self,other):
        if type(other) != type(self):
            return False
        return self.name == other.name

    def __call__(self,ctx):
        test,self.extra_data = self.condition(ctx, self.extra_data)
        if test:
            return self
        else:
            return None
    def advance(self,bot):
        if self.avancement == None:
            return ''
        else:
            return self.avancement(bot,self.extra_data)

def hidden(bot):
    return len([command for command in bot.commands if command.hidden])

#Les conditions des succès
def nombre_de_commandes(ctx,n):
    return n[0]+1 == n[1], [n[0]+1,n[1]]
def avancement_n_commandes(bot,n):
    return f' ({n[0]}/{n[1]})'
def commandes_cachees(ctx,commands):
    if ctx.command.name in commands or not ctx.command.hidden:
        return False, commands
    commands.append(ctx.command.name)
    return len(commands) == hidden(ctx.bot), commands
def n_commandes_cachees(bot,commands):
    return f' ({len(commands)}/{hidden(bot)})'
def prefix(ctx,nothing):
    return ctx.prefix == '¤',None
