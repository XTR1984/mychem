import random
from mychem import Space,Atom,PI
from math import *

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


def makesuperstar(ox,oy, n):
    D=20
    f = 0
    R = D*n/PI/4*2
    for i in range(0,n):
            x = ox+cos(f)*R
            y = oy-sin(f)*R
            a1= Atom(x, y, 3,2*PI/n*i)
            space.appendatom(a1)
            x = ox+cos(f)*(R+D)
            y = oy-sin(f)*(R+D)
            a1= Atom(x, y, 2, 2*PI/n*i)
            space.appendatom(a1)
            x = ox+cos(f)*(R+D*2)
            y = oy-sin(f)*(R+D*2)
            a1= Atom(x, y, 1,2*PI/n*i+PI)
            space.appendatom(a1)
            f+=2*PI/n

def makepoly1(x,y,n=5): 
    D=20
    a1= Atom(x-D, y, 1)
    space.appendatom(a1)
    a1= Atom(x+n*D, y, 1,PI)
    space.appendatom(a1)
    for i in range(0,n):
        a1= Atom(x+i*D, y, 5, PI if i%2!=0 else 0)
        space.appendatom(a1)
        if i%2==0:
            a1= Atom(x+i*D, y-D, 2, PI/2)
            space.appendatom(a1)
            a1= Atom(x+i*D, y-2*D, 1, PI/2*3)
            space.appendatom(a1)
        else:
            a1= Atom(x+i*D, y+D, 2, PI/2*3)
            space.appendatom(a1)
            a1= Atom(x+i*D, y+2*D, 1, PI/2)
            space.appendatom(a1)




random.seed(1)
space = Space()


makeethan(50,100)
makestar1(160,100)
makesuperstar(400,200,20)
makesuperstar(600,200,10)
makesuperstar(400,400,5)
makesuperstar(600,400,6)
makepoly1(100,220)
#space.appendmixer(5)
#   space.stoptime =1
space.go()

