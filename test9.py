import random
import mychem
from math import *


random.seed(1)
space = mychem.Space()
f = 0
R = 120

for i in range(1,20):
        x = cos(f)*R
        y = sin(f)*R
        a1= mychem.Atom(300+x, 200+y, 5)
        #a2= mychem.Atom(600+x, 200+y, 1)
        space.appendatom(a1)
        #space.appendatom(a2)
        f+=2*mychem.PI/20
space.go()

