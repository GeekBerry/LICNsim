

from algorithm.graph_algo import graphHoops
from exper_cb.test_bed_graph import test_bed_graph as graph

for i in graphHoops(graph, 'BUPT'):
    print(i)


import numpy

l= [1,2]
p= numpy.var(l)
print(p)
