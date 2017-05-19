
import numpy

# x1= (0,0)
# x2= (1,1)
#
# p= numpy.arctan2(1, 0) * 180 / numpy.pi
# print(p)


from collections import defaultdict

dct= defaultdict( lambda :{'color':[1,2,3], 'size':0.5, 'text':''} )


p= dct[1]
p2= dct[2]

p2['color'][2]= 100

print(dct)
