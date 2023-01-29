import random
from  mychem import Space,Atom
from math import *
random.seed(1)
space = Space()
for i in range(1,20):
	for j in range(1,10):
		space.appendatom(Atom(200+30*i, 100+30*j, random.randint(1,4)))
space.appendmixer(5)        
space.go()        
