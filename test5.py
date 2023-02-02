import random
from  mychem import Space,Atom

from math import *
random.seed(1)
space = Space()
for i in range(1,100):
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 1,r=6));
for i in range(1,20):	
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 2,r=8,m=16));
for i in range(1,40):		
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 4,m=12));

for i in range(0,15):
        space.appendatom(Atom(100+i*21,400,4,fixed=True))

space.appendmixer(1)
space.go()