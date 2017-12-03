# import networkx
#
# graph= networkx.random_regular_graph(3,10)
#
# n= graph.nodes[0]
# print(type(n))
#
# graph.nodes[0]['age']= 10
#
#
# print(graph.nodes[0])

# from core import clock, LeakBucket

class A:
    def __init__(self, d):
        self.d= d

d= {}
d.__setitem__= print

d[1]= 100

