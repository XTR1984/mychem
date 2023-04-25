import random
from  mychem import Space,Atom

from math import *
random.seed(2)
space = Space()
for i in range(1,180):
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 1,r=6));
for i in range(1,20):	
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 2,r=8,m=16,q=-1));
for i in range(1,100):		
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 4,m=12,q=-1));

space.appendmixer(1)
space.competitive = True
space.go()