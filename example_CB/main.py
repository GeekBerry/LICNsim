#!/usr/bin/python3
#coding=utf-8


import networkx
from core.packet import Name, Packet
from core.clock import clock
from core.common import *
from core.data_structure import CallTable
from core.filer import Filer, TimePlugin, PacketTracePlugin
from core.cs import SimulatCSUnit
from core.icn_net import ICNNet, AskGenerator
from core.channel import OneStepChannel
from example_CB.experiment_node import ExperimentNode
from example_CB.experiment_net import ExperimentMonitorDB, UniformityPlugin
from constants import *

GRAPH_S={
    'Grid':GraphGrid100X100(),
    'BA':GraphBA10000(),
    'Tree':GraphTree3X8()
}

CS_MODES={
    'LRU':SimulatCSUnit.MODE.LRU,
    'FIFO':SimulatCSUnit.MODE.FIFO,
    }

NUM_FUNC_S={
    'Possion':PossionAsk,
    'Fixed':FixedAsk,
    }

POS_FUNC_S= {
    'Uniform':UniformPosition,  # 均匀分布
    'Zipf':ZipfPosition,  # zipf分布
}

#=======================================================================================================================
log.level= log.LEVEL.ERROR
def main(date, graph_name, sim_second, cs_mode, cs_time, numfunc, lam, posfunc, alpha= 1.2, repeat=0):
    only_name= Name()
    ipacket= Packet(only_name, Packet.TYPE.INTEREST)
    dpacket= Packet(only_name, Packet.TYPE.DATA)

    graph_info= GRAPH_S[graph_name]
    graph= networkx.DiGraph( graph_info.graph )  # 必须变成有向图
    sim_second= int(sim_second)
    cs_time= int(cs_time)
    lam= int(lam)
    alpha= float(alpha)

    ratio= lam * 2 * graph_info.diameter  # 单位(step/s)
    sim_num_func= NUM_FUNC_S[numfunc](1)
    sim_pos_func= POS_FUNC_S[posfunc](graph, graph_info.center, alpha)

    filename= f'result/{date}_{graph_name}_SIZE{len(graph)}_{cs_mode}{cs_time}_{numfunc}{lam}_{posfunc}_test{repeat}.txt'  # TODO 创建文件夹
    print("实验", filename)
    #--------------------------------------------------------------------------
    announces= AnnounceTable()
    api= CallTable()
    # ICNNET
    icn_net= ICNNet(graph, ExperimentNode, OneStepChannel)
    icn_net.install(announces, api)
    # 数据库
    db= ExperimentMonitorDB(graph)
    db.install(announces, api)
    # 文件系统配置
    uniformity_plugin= UniformityPlugin(graph, graph_info.center, only_name)
    packet_track_plugin= PacketTracePlugin(only_name, db)
    Filer(filename, ratio, [TimePlugin(), packet_track_plugin, uniformity_plugin], print_screen= False)
    # 初始化缓存
    for node in icn_net.nodes():
        node.api['CS::setMode'](CS_MODES[cs_mode])
    for node in icn_net.nodes():
            node.api['CS::setLifeTime'](cs_time * ratio)
    icn_net.node(graph_info.center).api['CS::setMode'](SimulatCSUnit.MODE.MANUAL)  # 要在设置全局mode之后
    icn_net.node(graph_info.center).api['CS::store'](dpacket)  # 要在CS类型配置之后,才会被正确驱逐
    # 请求发生器
    ask_gen= AskGenerator(icn_net, sim_num_func, sim_pos_func, ipacket, delta=ratio//lam)
    ask_gen.start()
    #--------------------------------------------------------------------------
    for i in range(0, sim_second*ratio + 1):# 发送间隔为响应最大延迟
        clock.step()
    print("结束",filename)


#=======================================================================================================================
from core.common import getSysKwargs
main( **getSysKwargs() )

# 单例测试
# main(date='', graph_name='Grid', sim_second=100, cs_mode='FIFO', cs_time=60, numfunc='Fixed', lam=20, posfunc='Uniform')
