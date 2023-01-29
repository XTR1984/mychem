import random
from mychem import Space,Atom
from math import *
random.seed(1)
space = Space()

for i in range(1,150    ):
    a1 = Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 1)
    a2 = Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 4)
    a2.m=10
    space.appendatom(a1)
    space.appendatom(a2)
#space.gravity = True
space.appendmixer(5)
space.go()