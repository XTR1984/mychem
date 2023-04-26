import random
from  mychem import Space,Atom,PI
from math import *
random.seed(1)
space = Space()
for i in range(1,20):
	for j in range(1,10):
		space.appendatom(Atom(350+25*i, 200+16*j, 2,PI/2,r=8))
#space.appendmixer(10)
#space.recording = True
space.stoptime = 24*60*20
space.go()        

