from data import data
from time import time
from discord import Embed

class Business_guy():
    def __init__(self,user):
        self.id=user.id
        self.name=str(user)
        self.avatar_url=str(user.avatar_url)
        self.money=0
        self.bank=0
        self.bank_max=5000
        self.streak=1
        self.last_daily=0
        self.steal_streak=0

    def __eq__(self,other):
        return self.id==other.id

    def daily(self):
        if time()<self.last_daily+172800:
            if self.streak<5:
                self.streak+=1
        else:
            self.streak=1
        self.last_daily=time()
        self.money+=100*self.streak
        return 'You gained '+str(100*self.streak)+' GP'

    def gift(self,guild):
        self.money+=500
        return 'You took '+guild+"'s 500 daily GP.'"

    def money_out(self):
        embed=Embed(title='Banque de '+self.name,colour=data.get_color())
        embed.set_author(name=self.name,icon_url=self.avatar_url)
        embed.set_thumbnail(url='https://storge.pic2.me/cm/5120x2880/866/57cb004d6a2e2.jpg') #A modifier
        embed.add_field(name='Banked :',value=str(self.bank)+'/'+str(self.bank_max))
        embed.add_field(name='Pocketed :',value=str(self.money))
        return embed

    def deposit(self,money):
        if self.money<money:
            return f"Sorry, but you only have {self.money} GP"
        else:
            M=self.bank_max-self.bank
            if money<=M:
                self.money-=money
                self.bank+=money
                return f"{money} GP deposited"
            else:
                self.money-=M
                self.bank+=M
                return f"{M} GP deposited. {M-money} GP couldn't be deposited (capacity of {self.bank_max} GP reached)"

    def steal(self,other):
        a=randint(round(0.05*other.money),round(0.1*other.money))
        self.money+=a
        other.money-=a
        return a
