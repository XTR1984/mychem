import random
from mychem import Space,Atom,PI
from math import *


random.seed(1)
space = Space()

def makesomething(x,y):
        D=20
        for i in range(0,7):
                space.appendatom(Atom(x+D*i,y,5,PI))
                space.appendatom(Atom(x+D*i,y+D,4))
                space.appendatom(Atom(x+D*i,y+6*D,5,0))
                space.appendatom(Atom(x+D*i,y+5*D,4))
        for i in range(0,2):
                for j in range(0,3):
                        space.appendatom(Atom(x+D*(i+5),y+D*(j+2),4))
        for j in range(0,7):
               space.appendatom(Atom(x+D*7,y+D*j,1,PI))
        space.appendatom(Atom(x-D,y,1))
        space.appendatom(Atom(x-D,y+D,1))
        space.appendatom(Atom(x-D,y+5*D,1))
        space.appendatom(Atom(x-D,y+6*D,1))

#space.stoptime = 10
makesomething(150,250)
makesomething(350,250)
for i in range(0,50):
        space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 1));
#space.appendmixer(20)
#space.recording = True
#space.stoptime = 2
space.go()

