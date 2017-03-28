#!/usr/bin/python3
#coding=utf-8

import time
from itertools import product

import networkx

from core.channel import OneStepChannel
from core.common import *
from example_CB.experiment_net import ICNNet, Simulation, Filer
from example_CB.experiment_node import ExperimentNode, SimulatCSUnit


def graphApproximateDiameter(graph, sample_num= 10):#得到graph近似直径
    nodes= random.sample( graph.nodes(), sample_num )# sample_num: 取样测试偏心率的点数量 如果sample_num>len(graph), 会出现个采样错误
    ecce_dict= networkx.eccentricity(graph, nodes)# 计算测试点偏心率
    avg_ecce= numpy.mean( list(ecce_dict.values()) )
    return int(avg_ecce*1.5) # 近似直径 FIXME 圆面网络是3/2==1.5 但是得出的值总会偏大

#-----------------------------------------------------------------------------------------------------------------------
log.level= log.LEVEL.WARING

GRAPH_NAME= 'BA'

if GRAPH_NAME == 'Grid':
    DIAMETER= 100# 100*100 == 10000 == SIZE
    DATANODE= (DIAMETER//2, DIAMETER//2) #中心点
    graph= networkx.grid_2d_graph(DIAMETER, DIAMETER)
elif GRAPH_NAME == 'BA':
    DATANODE= 0 # FIXME networkx构建的中心点有数据 BA网络中心点一般在0
    graph= networkx.random_graphs.barabasi_albert_graph(10000, 1)
    DIAMETER= graphApproximateDiameter(graph)
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
CS_TIMES= [20] # [20, 40, 60, 80, 100] # 单位(s)

NUM_FUNC_S={
    #'Possion':possionAsk,
    'Fixed':fixedAsk,
    }

LAMBDAS= [20] # [20, 40, 60, 80, 100]# 单位(个/s)

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

    ratio= lam * 2 * DIAMETER  # 单位(step/s)

    num_func= Impulse(DIAMETER * 2, NUM_FUNC_S[numfunc])  # 将 num_func 增加一个脉冲来控制间隔

    net= ICNNet(graph, ExperimentNode, OneStepChannel)
    net.publish['transfer'].append(print)

    sim= Simulation(net, num_func=num_func, pos_func=POS_FUNC_S[posfunc])
    sim.setCSMode(CS_MODES[csmode])
    sim.setCSTime(cstime * ratio)
    sim.setSourceNode( DATANODE )  # 要在设置mode之后

    filer= Filer(filename, sim.db_monitor, sim.name,  delta= ratio, print_screen= True)
    sim.simulate(steps= SIM_SECOND*ratio + 1)  # 发送间隔为响应最大延迟
    filer.close()
    clock.clear()

    print('用时:', time.clock()-starttime)

    break # DEBUG

