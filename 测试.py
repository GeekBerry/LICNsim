"""
时间                 事件   GUI   数据库  日志
1.1165840101882998  17708  F     F      F   15859
1.3813271920328496  17643  T     F      F   12772
2.1172993152170325  17917  F     T      F   8462
2.4736256371034027  17790  F     F      T   7191

2.5083391268727113  17837  T     T      F   7111
2.753827975164681   17837  T     F      T   6477
3.509122704932883   17715  F     T      T   5048
3.7262336222814616  17878  T     T      T   4797
"""

# print(17878 // 3.7262336222814616)

# l = [] #[1,2,3]
#
# p= l.pop(0)
#
# print(p, l)
#

from core import TupleClass


A= TupleClass('x', 'y')

a= A(1,2)

print(dict(a))



from collections import defaultdict

d= defaultdict()

