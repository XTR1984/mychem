import random
from  mychem import Space,Atom
from math import *
random.seed(1)
space = Space()
for i in range(1,20):
	for j in range(1,10):
		space.appendatom(Atom(100+25*i, 100+25*j, 2))
space.appendmixer(10)
a1 = Atom(200, 200, 4)
space.appendatom(a1)
a1 = Atom(300, 300, 4)
space.appendatom(a1)
#space.recording = True
space.stoptime = 24*60*20
space.go()        

