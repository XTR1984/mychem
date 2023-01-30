import random
from mychem import Space,Atom,PI
from math import *


random.seed(1)
space = Space()

def makestar1(x,y):
        D=20
        space.appendatom(Atom(x,y,4))
        space.appendatom(Atom(x+D,y,2))
        space.appendatom(Atom(x+2*D,y,1,PI))
        space.appendatom(Atom(x-D,y,2))
        space.appendatom(Atom(x-2*D,y,1))
        space.appendatom(Atom(x,y+D,2,PI/2))
        space.appendatom(Atom(x,y+2*D,1,PI/2))
        space.appendatom(Atom(x,y-D,2,PI/2))
        space.appendatom(Atom(x,y-2*D,1,PI*3/2))


def makeethan(x,y):
        D=20
        space.appendatom(Atom(x,y,4))
        space.appendatom(Atom(x+D,y,4))
        space.appendatom(Atom(x-D,y,1))
        space.appendatom(Atom(x,y-D,1,PI*3/2))
        space.appendatom(Atom(x,y+D,1,PI/2))
        space.appendatom(Atom(x+D+D,y,1,PI))
        space.appendatom(Atom(x+D,y-D,1,PI*3/2))
        space.appendatom(Atom(x+D,y+D,1,PI/2))



for i in range(0,3):
        for j in range(0,3):
                makestar1(180+i*100,200+j*100)
for i in range(0,3):
        for j in range(0,3):
                makeethan(600+i*100,200+j*100)
#space.stoptime = 10
space.appendmixer(10)
space.recording = True
space.stoptime = 24*60*20
space.go()

