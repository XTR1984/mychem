import random
from  mychem import Space,Atom
from math import *
random.seed(1)
space = Space()
for i in range(1,25):
		#atoms.append(Atom(random.randrange(1,WIDTH), random.randrange(1,HEIGHT), 3));
	space.appendatom(Atom(200+22*i, 100, 1))
	space.appendatom(Atom(200+22*i, 130, 4))
	space.appendatom(Atom(200+22*i, 155, 1))
	space.appendatom(Atom(200+22*i, 190, 3))
	space.appendatom(Atom(200+22*i, 210, 1))
	space.appendatom(Atom(200+22*i, 245, 2))
space.appendmixer(5)            
#space.recording = True
space.stoptime = 24*60*20
space.go()
