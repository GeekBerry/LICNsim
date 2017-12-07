

import math

from itertools import count

def expNum():
    for i in count():
        yield math.exp(-i/1000)

for i, v in zip(range(1000), expNum()):
    print(i,v)
