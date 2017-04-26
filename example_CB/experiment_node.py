#!/usr/bin/python3
#coding=utf-8

from core.clock import clock
from core.node import ForwarderUnitBase, AppUnit
from core.data_structure import Dict
from core.packet import Packet

#=======================================================================================================================
class ExperimentForwarderUnit(ForwarderUnitBase):
    def __init__(self, outI_cd):
        self.outI_cd= outI_cd  # out interest cool delay

    def _inInterest(self, face_id, packet):
        data= self.api['CS::match'](packet)
        if data is None:
            # 对path进行检查
            if len(packet.pathI) <= 0:
                path= self.api['Net::getPath'](packet)
                if path:
                    path.pop(0)  # 当前节点标号
                    packet.pathI= path
            # 转发
            sendid= packet.pathI.pop(0)  # 将头部摘取出来, 基于net的设定, NodeName= FaceID
            if sendid in self.api['Info::getCooledIds'](packet.name, self.outI_cd):
                self.api['Face::send']( {sendid}, packet )
        else:
            self.api['Face::send']( {face_id}, data )  # 记录: info[send_id].outD == clock.life_time()

    def _inData(self, face_id, packet):
        send_ids= self.api['Info::getPendingIds'](packet.name)
        if len(send_ids) > 0:
            self.api['Face::send'](send_ids, packet)  # 记录: info[send_id].outI == clock.life_time()
            self.api['CS::store'](packet)  # FIXME 未经请求包储存??
        else:
            self.announces['unsolicited'](face_id, packet)

#-----------------------------------------------------------------------------------------------------------------------
class ExperimentAppUnit(AppUnit):
    def __init__(self):
        super().__init__()
        self.pending= Dict()  # {packet_name:start_time, ...}

    def _ask(self, packet):
        if packet.type == Packet.INTEREST:
            self.pending.setdefault( packet.name, [] )  # [] 请求时间列表
            self.pending[packet.name].append(clock.time())

            # 距离等于路径节点间隔, 如[1,2,3], distance == 2
            path= self.api['Net::getPath'](packet)
            setattr(packet, 'pathI', path[1:] )  # 不要第0位, 去掉路劲中的当前节点名

            # announces 要先于 app_channel 调用
            # 1: 避免app_channel中修改packet
            # 2: 避免 announces['respond'] 先于 announces['ask'] 产生(CS命中的情况下)
            self.announces['ask'](packet, len(packet.pathI))
            self.app_channel(packet)  # 发送packet


    def _respond(self, packet):
        if packet.type == Packet.DATA  and  packet.name in self.pending:
            ask_time_list= self.pending.pop(packet.name)
            for ask_time in ask_time_list:
                if clock.time()-ask_time > 200:  # 200 网络最大响应时间
                    # FIXME 注意, 如果环路问题没解决, 会出现以下问题
                    # t0: I-> 但是loop, t10000: I->, t10010: <-D responed为[t1, t10000] 则 响应时间为[10010, 10]
                    # 所以需要设置个时间来取出合理响应时间,
                    # log.error(label[self], '超时', ask_time_list)
                    pass
                else:
                    self.announces['respond'](packet, ask_time)


#-----------------------------------------------------------------------------------------------------------------------
from core.node import NodeBufferUnit
from core.node import NodeBase
from core.cs import SimulatCSUnit
from core.face import FaceUnit, RepeatChecker, NoLoopChecker
from core.info_table import InfoUnit
from core.policy import FIFOPolicy, PolicyUnit

from constants import INF
class ExperimentNode(NodeBase):
    def __init__(self, name):
        super().__init__(name)
        # self.install('buffer', NodeBufferUnit(rate= INF, buffer_size=INF) )  # 使得节点变成有缓存的, 此处设置为INF仅为测试
        self.install('faces',  FaceUnit( NoLoopChecker(None), RepeatChecker() )  )  # 因为路由策略的保障, 不检查兴趣包的循环
        self.install('info',   InfoUnit(max_size= 2, life_time= 100000) )
        self.install('cs',     SimulatCSUnit(capacity= 1, life_time= None) )  # capacity=1: 实验为一个包测试, life_time=None:使得必须在之后被设置
        self.install('policy', PolicyUnit(FIFOPolicy) )
        self.install('app',    ExperimentAppUnit() )
        self.install('fwd',    ExperimentForwarderUnit(outI_cd= 100) )  # 100来自于100*100网格平均响应时间

