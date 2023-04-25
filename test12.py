import random
from mychem import Space,Atom,PI
from math import *


random.seed(1)
space = Space()

def makesomething(x,y):
        D=20
        for i in range(0,30):
                space.appendatom(Atom(x+D*i,y-D,1,PI*3/2))
                space.appendatom(Atom(x+D*i,y,4))
                space.appendatom(Atom(x+D*i,y+D,2,PI/2))
                space.appendatom(Atom(x+D*i,y+2*D,2,PI/2))
                space.appendatom(Atom(x+D*i,y+3*D,2,PI/2))
                #space.appendatom(Atom(x+D*i,y+2*D,5,PI))
                space.appendatom(Atom(x+D*i,y+4*D,1,PI/2))

                space.appendatom(Atom(x+D*i,y+6*D,1,PI*3/2))
                space.appendatom(Atom(x+D*i,y+7*D,4,PI/2))
                space.appendatom(Atom(x+D*i,y+8*D,1,PI/2))


#space.stoptime = 10
makesomething(150,250)
space.appendmixer(10)
#space.recording = True
space.stoptime = 24*60*10
space.export = True
space.go()

