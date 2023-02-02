import random
from mychem import Space,Atom,PI
from math import *
from examples import makeethan,makestar1

random.seed(1)
space = Space()


for i in range(0,3):
        for j in range(0,3):
                makestar1(space,180+i*100,200+j*100)
for i in range(0,3):
        for j in range(0,3):
                makeethan(space,600+i*100,200+j*100)
#space.stoptime = 10
space.appendmixer(10)
#space.recording = True
space.stoptime = 24*60*20
space.go()

