import random
from mychem import Space,Atom,PI
from math import *
from examples import makeCO2, makeformaldehyde, makeriboza,makeH2O

random.seed(1)
space = Space()


for i in range(0,3):
        for j in range(0,3):
                makeformaldehyde(space,80+i*50,100+j*50)
                makeH2O(space,400+i*45,100+j*50)
                makeCO2(space,600+i*30,100+j*50)

for i in range(0,5):
        space.appendatom(Atom(300+i*2*20,400,4,fixed=True))

#space.stoptime = 1
space.appendmixer(2)
#space.recording = True
#space.stoptime = 24*60*20
space.go()

