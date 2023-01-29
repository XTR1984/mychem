import random
from mychem import Space,Atom
from math import *
random.seed(1)
space = Space()

for i in range(1,20):
	for j in range(1,5):
		space.appendatom(Atom(100+25*i, 100+25*j, 2))
	space.appendatom(Atom(100+25*i, 100+25*j, 5))	
space.appendmixer(10)
space.go()
