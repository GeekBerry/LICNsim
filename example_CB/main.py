#!/usr/bin/python3
#coding=utf-8

import time
from itertools import product

import networkx

from core.common import *
from example_CB.experiment_net import Simulation, Filer
from example_CB.experiment_node import SimulatCSUnit
#-----------------------------------------------------------------------------------------------------------------------
log.level= log.LEVEL.WARING

GRAPH_NAME= 'BA'

if GRAPH_NAME == 'Grid':
    DIAMETER= 100  # 100*100 == 10000 == SIZE
    DATANODE= (DIAMETER//2, DIAMETER//2)  # 中心点
    graph= networkx.grid_2d_graph(DIAMETER, DIAMETER)
elif GRAPH_NAME == 'BA':
    DATANODE= 0 # FIXME networkx构建的中心点有数据 BA网络中心点一般在0
    graph= networkx.random_graphs.barabasi_albert_graph(10000, 1)
    DIAMETER= graphApproximateDiameter(graph)

    p= graphNodeAvgDistance(graph, DATANODE)  # DEBUG
    print('graphNodeAvgDistance', p)          # DEBUG

elif GRAPH_NAME == 'Tree':
    DATANODE= 0
    DIAMETER= 8 * 2 # h*2
    graph= networkx.balanced_tree(r=3, h=8)#r= 3, h= 8
else:
    raise RuntimeError("必须选一种graph类型")

graph= networkx.DiGraph( graph ) # 必须变成有向图
#-----------------------------------------------------------------------------------------------------------------------
DATE= time.strftime("%y%m%d%H%M%S", time.localtime())

SIM_SECOND= 500# 500# 单位(s)
CS_MODES={
    # 'LRU':SimulatCSUnit.MODE.LRU,
    'FIFO':SimulatCSUnit.MODE.FIFO,
    }
CS_TIMES= [100] # [20, 40, 60, 80, 100] # 单位(s)

NUM_FUNC_S={
    #'Possion':possionAsk,
    'Fixed':FixedAsk,
    }

LAMBDAS= [20, 100] # [20, 40, 60, 80, 100]# 单位(个/s)

POS_FUNC_S= {
    'Uniform':UniformPosition(graph),# 均匀分布
    #'Zipf1.2':ZipfPosition(graph, DATANODE, 1.2),# zipf分布
}
#=======================================================================================================================
for     csmode,   cstime,   numfunc,    lam,     posfunc   in \
product(CS_MODES, CS_TIMES, NUM_FUNC_S, LAMBDAS, POS_FUNC_S):  # 笛卡尔积

    filename= "result//%s_%s_SIZE%d_%s%d_%s%d_%s.txt"%(DATE, GRAPH_NAME, len(graph), csmode, cstime, numfunc, lam, posfunc)
    print("实验", filename)
    starttime= time.clock()

    # ratio= lam * 2 * DIAMETER  # 单位(step/s)
    ratio= 4 * DIAMETER

    # num_func= Impulse(2*DIAMETER, NUM_FUNC_S[numfunc])  # 将 num_func 增加一个脉冲来控制间隔
    num_func= Impulse(ratio, NUM_FUNC_S[numfunc](lam))  # 将 num_func 增加一个脉冲来控制间隔

    announces= AnnounceTable()
    api= CallTable()

    sim= Simulation(graph, num_func=num_func, pos_func=POS_FUNC_S[posfunc])
    sim.install(announces, api)

    filer= Filer(filename, sim.name, ratio, print_screen= True)
    filer.install(announces, api)

    sim.setCSMode(CS_MODES[csmode])
    sim.setCSTime(cstime * ratio)
    sim.setSourceNode(DATANODE)  # 要在设置mode之后
    sim.simulate(steps= SIM_SECOND*ratio + 1)  # 发送间隔为响应最大延迟

    filer.close()

    clock.clear()
    print('用时:', time.clock()-starttime)

    # break # DEBUG

