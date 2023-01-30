import random
import mychem
from math import *


random.seed(1)
space = mychem.Space()
f = 0
R = 200

for i in range(1,80):
        x = cos(f)*R
        y = sin(f)*R
        a1= mychem.Atom(300+x, 200+y, 4)
        #a2= mychem.Atom(600+x, 200+y, 1)
        space.appendatom(a1)
        #space.appendatom(a2)
        f+=2*mychem.PI/80
space.appendmixer()
space.go()

