import random
import mychem
from math import *
random.seed(1)
space = mychem.Space()
def test7():
	for i in range(1,120):
		a1 = Atom(random.randrange(1,WIDTH), random.randrange(1,HEIGHT), 1)
		atoms.append(a1);
#		a1.r = ATOMRADIUS/2
	for i in range(1,50):
		atoms.append(Atom(random.randrange(1,WIDTH), random.randrange(1,HEIGHT), 2));		
	for i in range(1,50):
		a3 = Atom(random.randrange(1,WIDTH), random.randrange(1,HEIGHT), 4)
#		a3.r = ATOMRADIUS*2/3
		atoms.append(a3);		
