import random
from  mychem import Space,Atom
from math import *
random.seed(1)
space = Space()

a1 = Atom(500, 100, 2)
a1.vx = 0.00
a1.vy = 0.00
a2 = Atom(550, 121, 1)
a2.vx = -0.01
#a2.vy = -0.6
#a3 = Atom(250, 150, 4)
#a4 = Atom(150, 250, 4)
space.appendatom(a1)
space.appendatom(a2)
space.go()	


