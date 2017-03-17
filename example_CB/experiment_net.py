#!/usr/bin/python3
#coding=utf-8

from core.net import *
from core.common import *

#-----------------------------------------------------------------------------------------------------------------------
class ExperimentMonitorDataBase(MonitorDataBase):
    def __init__(self, net):
        super().__init__(net)
        net.loadAnnounce('ask', self._ask)
        net.loadAnnounce('respond', self._respond)

        self.info_table={'ask_count':0, 'dist_count':0, 'resp_count':0, 'time_count':0}
        self.content_table.addFields(dist=list, time=list)

    def _ask(self, nodename, packet, distance):
        entry= self.content_table[packet.name]
        entry.pend.add(nodename)
        entry.dist.append( distance )

    def _respond(self, nodename, packet, asktime):
        entry= self.content_table[packet.name]
        entry.pend.discard(nodename)
        entry.time.append( clock.time() - asktime )
#-----------------------------------------------------------------------------------------------------------------------
class StoreProvider:# 储存服务提供者
    def __init__(self, net, db_monitor):
        net.storeAPI('Net::getPath', self.getPath )
        self._graph= net.graph
        self._db_monitor= db_monitor

    def getPath(self, nodename, packet):
        content_nodes= self._db_monitor.content_table[packet.name].content
        return graphNearestPath(self._graph, nodename, content_nodes)
#-----------------------------------------------------------------------------------------------------------------------
def listMean(l)->str:
    if len(l) > 0:
        return "%6f"%( numpy.mean(l) )
    else: return 'NaN'

def division(dividend, divisor)->str:
    if divisor != 0:
        return "%6f"%( dividend/divisor )
    else: return 'NaN'

class Filer:
    def __init__(self, filename, db_monitor, packet_name, delta, print_screen):
        self.file= open(filename, 'w')
        self.delta= delta
        self.print_screen= print_screen
        self.db= db_monitor #FIXME
        self.packet_name= packet_name #FIXME
        # 表头
        self.head()
        # 定时器
        self.timer= Timer(self.write)
        self.timer.timing(self.delta)

    def head(self):
        fields= ['Time',
                'CSNum', 'StoreNum', 'EvictNum',
                'AskNum', 'CurDist', 'AvgDist',
                'RespNum', 'CurTime', 'AvgTime',]
        string= "".join([ "%8s\t"%(field) for field in fields ])

        if self.print_screen:
            print(string)
        self.file.write(string+'\n')

    def write(self):
        content_entry= self.db.content_table[self.packet_name]
        # 前置记录
        self.db.info_table['ask_count']+= len(content_entry.dist)
        self.db.info_table['resp_count']+= len(content_entry.time)
        self.db.info_table['dist_count']+= sum(content_entry.dist)
        self.db.info_table['time_count']+= sum(content_entry.time)
        # 拼记录
        string= "%8d\t"%( clock.time() )
        string+= "%8d\t"%( len(content_entry.content) )
        string+= "%8d\t"%( content_entry.store )
        string+= "%8d\t"%( content_entry.evict )
        string+= "%8d\t"%( len(content_entry.dist) )
        string+= "%8s\t"%( listMean(content_entry.dist) )
        string+= "%8s\t"%( division(self.db.info_table['dist_count'], self.db.info_table['ask_count']) )
        string+= "%8d\t"%( len(content_entry.time) )
        string+= "%8s\t"%( listMean(content_entry.time) )
        string+= "%8s\t"%( division(self.db.info_table['time_count'], self.db.info_table['resp_count']) )
        #打印
        if self.print_screen:
            print(string)
        self.file.write(string+'\n')
        # 清理重置
        self.db.content_table[self.packet_name].store= 0
        self.db.content_table[self.packet_name].evict= 0
        content_entry.dist.clear()
        content_entry.time.clear()
        # 定时器
        self.timer.timing(self.delta)

    def close(self):
        self.file.close()

#-----------------------------------------------------------------------------------------------------------------------
from core.cs import SimulatCSUnit
from core.packet import Name, Packet
class Simulation:
    def __init__(self, net, num_func, pos_func):
        """
        :param num_func: def(int)->int 请求量生成函数,
        :param pos_func: def(int)->[nodename,...] 位置生成函数
        """
        self.name= Name([''])
        self.ipacket= Packet(self.name, Packet.TYPE.INTEREST)
        self.dpacket= Packet(self.name, Packet.TYPE.DATA)

        self.net= net
        self.num_func= num_func
        self.pos_func= pos_func

        self.db_monitor= ExperimentMonitorDataBase(self.net)
        StoreProvider(self.net, self.db_monitor)

    def setCSMode(self, mode):#配置CS类型
        for node in self.net.nodes():
            node.api['CS::setMode'](mode)

    def setCSTime(self, time):#配置CS时间
        for node in self.net.nodes():
            node.api['CS::setLifeTime'](time)

    def setSourceNode(self, nodename):
        self.net.node( nodename ).api['CS::setMode'](SimulatCSUnit.MODE.MANUAL)# 源节点: 替换 or 不被替换
        self.net.node( nodename ).api['CS::store']( self.dpacket )# 要在CS类型配置之后,才会被正确驱逐

    def asks(self, nodenames):
        for nodename in nodenames:
            self.net.node(nodename).api['APP::ask']( self.ipacket.fission() )

    def simulate(self, steps):
        for i in range(0, steps):
            nodenum= self.num_func(i) # FIXME i 如何对应 t
            nodenames= self.pos_func( nodenum )
            self.asks(nodenames)

            clock.step()

