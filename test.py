# from core.common import *
# TODO 数据库
# TODO demo 数据采集
# TODO 物联网
# TODO 图形库

#=======================================================================================================================
# top_graph = networkx.random_graphs.barabasi_albert_graph(50, 1)
# top_graph= networkx.grid_2d_graph(10, 10)
# top_graph= networkx.balanced_tree(3, 4)
# top_graph= networkx.watts_strogatz_graph(20, 4, 0.3)
# top_graph= networkx.DiGraph(top_graph)
#
# pos = networkx.spring_layout(top_graph)
# networkx.draw(top_graph, pos, with_labels = True, node_size = 1)
# plt.show()
#
#
# def step(t):
#     # plt.clf()
#
#     global pos
#
#     a= plt.axis()
#     ret= plt.text(a[0],a[2], str(t))
#     pos = networkx.spring_layout(top_graph, pos= pos)
#     node_collection= networkx.draw_networkx_nodes(top_graph, pos, node_size = 1)
#     edge_collection = networkx.draw_networkx_edges(top_graph, pos, arrows= True)
#     # networkx.draw_networkx_labels(top_graph, pos)
#
#     return node_collection, edge_collection, ret
#     # plt.savefig( 'pic/%02d.png'%(i) )
#     # plt.show()
#     # plt.close()
#
#
# import matplotlib.animation as animation
# fig = plt.figure()
#
# ani = animation.FuncAnimation(
#     fig= fig, #(必要) 绘制的画布
#     func= step,# (必要) 每次执行此函数
#     fargs= None,# 每次调用func传给func 的参数
#     # frames= 100, #
#     # interval= 1, # 时间间隔
#     # init_func= init, #初始化画布
#     blit= True #重绘
# )
#
# plt.show()

#=======================================================================================================================
# pos= _graphLayout(graph)
# graph.draw(pos)




# import networkx
# import matplotlib.pyplot as plt


# top_graph= networkx.path_graph(3)
# top_graph = networkx.random_graphs.barabasi_albert_graph(20, 1)
# top_graph= networkx.grid_2d_graph(5, 5)
# top_graph= networkx.balanced_tree(2,2)
# top_graph= networkx.watts_strogatz_graph(20, 4, 0.3)

# top_graph= networkx.DiGraph(top_graph)


# ui_net= ICNNet(top_graph, SimpleNode, NoQueueChannel)

# width= []
# for src, dst in top_graph.edges():
#     width.append( random.random() )
#
# pos= networkx.spring_layout(top_graph)
# networkx.draw(top_graph, pos, with_labels = True, node_size = 1)
# plt.show()


#=======================================================================================================================
# d= {1:(0,200), 2:(100,0)}
#
# l= [[1,2],[3,4], [0,10]]
#
#
# max_x= max( d.values(), key= lambda key:key[0])
#
#
# def boundingRect(l):
#     min_x, max_x= INF, -INF
#     min_y, max_y= INF, -INF
#
#     for x, y in l:
#         if x < min_x: min_x= x
#         if max_x < x: max_x= x
#         if y < min_y: min_y= y
#         if max_y < y: max_y= y
#
#     return max_x-min_x, max_y-min_y, min_x, min_y
#
# def normalization(l, w, h, offset_x, offset_y):
#     return [ ((x-offset_x)/w,(h-offset_y)/h) for x, y in l]
#
# p= boundingRect(l)
# print(p)
#
# p= normalization(l, *p)
# print(p)





#=======================================================================================================================
from core.common import CppDll

main= CppDll('main')
d= {1:100}
p= main.foo(d)
print(p)

