import random
from  mychem import Space,Atom
from math import *
random.seed(1)
space = Space()
for i in range(1,20):
	for j in range(1,10):
		t = random.randint(1,4)
		a = Atom(200+30*i, 100+30*j, t)
		if t==1:
			a.r = 6
		elif t==2:
			a.m = 16
			a.r = 8
			a.q = -1
		elif t==3:
			a.m= 14
		elif t==4:
			a.m = 12
			a.r = 10
			a.q = -1

		space.appendatom(a)
space.appendmixer(5)        
space.go()        
