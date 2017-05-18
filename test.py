
import numpy

# x1= (0,0)
# x2= (1,1)
#
# p= numpy.arctan2(1, 0) * 180 / numpy.pi
# print(p)

def getAngle(p1, p2):
    return numpy.arctan2( p2[1] - p1[1], p2[0] - p1[0] ) * 180 / numpy.pi



a= getAngle( (0,0), (-1,-1) )
print(a)
