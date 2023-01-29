import random
import mychem
from math import *
random.seed(1)
space = mychem.Space()
def test8():
	for i in range(1,100):
		a1 = Atom(random.randrange(1,WIDTH/2), random.randrange(1,HEIGHT), 1)
		a1.vx=1
		a2 = Atom(WIDTH/2+random.randrange(1,WIDTH/2), random.randrange(1,HEIGHT), 5)
		a2.vx=-1
		atoms.append(a1);

		atoms.append(a2);
