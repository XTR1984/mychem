import random
from  mychem import Space,Atom

from math import *
random.seed(1)
space = Space()
for i in range(1,50):
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 1));
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 2));
	space.appendatom(Atom(random.randrange(1,space.WIDTH), random.randrange(1,space.HEIGHT), 4));
space.appendmixer(5)
space.go()