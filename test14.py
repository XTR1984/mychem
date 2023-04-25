import random
from mychem import Space,Atom,PI
from math import *
from examples import makeriboza

random.seed(1)
space = Space()


for i in range(0,3):
        for j in range(0,3):
                makeriboza(space,180+i*150,200+j*100)
#space.stoptime = 10
space.appendmixer(10)
space.competitive = True
#space.recording = True
#space.stoptime = 24*60*20
space.go()

