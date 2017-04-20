# import numpy
#
# def calculateForces(graph, node, pos, ratio):
#     force= numpy.array([0.0, 0.0])
#
#     weight= len( graph[node] )
#     for other in graph.nodes():
#         vec= pos[other]- pos[node]
#         vls= numpy.sum(numpy.square(vec))
#
#         if vls>0:
#             force -= (vec/vls) * ratio# 空间中节点间为排斥力
#             if other in graph[node]:
#                 force += vec/weight # 连接的节点间为吸引力
#         else:pass # 点重合
#
#     pos[node] += force * 0.9 #系数不能为1
#
#
# def graphLayout(graph, pos= None, length= 1, iterations= 100):
#     if pos is None:
#         pos= { node:numpy.random.rand(2) for node in graph }
#
#     ratio= length*length / len(graph)
#     for i in range(0, iterations):
#         for node in pos:
#             calculateForces(graph, node, pos, ratio)
#
#     return pos
