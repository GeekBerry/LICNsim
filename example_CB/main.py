#!/usr/bin/python3
#coding=utf-8
from core.algorithm import FixedAsk, PossionAsk, UniformPosition, ZipfPosition
from core.channel import OneStepChannel
from core.clock import clock
from core.cs import SimulatCSUnit
from core.filer import Filer, TimePlugin, PacketTracePlugin
from core.icn_net import ICNNetHelper, AskGenerator
from core.packet import Name, Packet
from debug import GraphGrid100X100, GraphBA10000, GraphTree3X8
from example_CB.experiment_net import ExperimentMonitor, UniformityPlugin
from example_CB.experiment_node import ExperimentNode

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
def main(date, graph_name, sim_second, cs_mode, cs_time, numfunc, lam, posfunc, alpha= 1.2, repeat=0):
    packet_name= Name()
    ipacket= Packet(packet_name, Packet.INTEREST, size=1)
    dpacket= Packet(packet_name, Packet.DATA, size=1)

    graph_info= GRAPH_S[graph_name]
    sim_second= int(sim_second)
    cs_time= int(cs_time)
    lam= int(lam)
    alpha= float(alpha)

    ratio= lam * 2 * graph_info.diameter  # 单位(step/s)
    sim_num_func= NUM_FUNC_S[numfunc](1)
    sim_pos_func= POS_FUNC_S[posfunc](graph_info.graph, graph_info.center, alpha)

    filename= f'result/{date}_{graph_name}_SIZE{len(graph_info.graph)}_{cs_mode}{cs_time}_{numfunc}{lam}_{posfunc}_test{repeat}.txt'  # TODO 创建文件夹
    print("实验", filename)
    #--------------------------------------------------------------------------
    # ICNNET
    ICNNetHelper.setup(graph_info.graph, ExperimentNode, OneStepChannel)
    # 数据库
    db= ExperimentMonitor(graph_info.graph)
    # 文件系统配置
    uniformity_plugin= UniformityPlugin(graph_info.graph, graph_info.center, packet_name)
    packet_track_plugin= PacketTracePlugin(packet_name, db)
    Filer(filename, ratio, [TimePlugin(), packet_track_plugin, uniformity_plugin], print_screen= True)
    # 初始化缓存
    for node in ICNNetHelper.nodes(graph_info.graph):
        node.api['CS::setMode'](CS_MODES[cs_mode])
    for node in ICNNetHelper.nodes(graph_info.graph):
            node.api['CS::setLifeTime'](cs_time * ratio)
    ICNNetHelper.node(graph_info.graph, graph_info.center).api['CS::setMode'](SimulatCSUnit.MODE.MANUAL)  # 要在设置全局mode之后
    ICNNetHelper.node(graph_info.graph, graph_info.center).api['CS::store'](dpacket)  # 要在CS类型配置之后,才会被正确驱逐
    # 请求发生器
    ask_gen= AskGenerator(graph_info.graph, sim_num_func, sim_pos_func, ipacket, delta=ratio//lam)
    ask_gen.start(0)
    #--------------------------------------------------------------------------
    for i in range(0, sim_second*ratio + 1):# 发送间隔为响应最大延迟
        clock.step()
    print("结束",filename)


#=======================================================================================================================
# from core.common import getSysKwargs
# main( **getSysKwargs() )

# 单例测试
main(date='', graph_name='Grid', sim_second=100, cs_mode='FIFO', cs_time=60, numfunc='Fixed', lam=20, posfunc='Uniform')
