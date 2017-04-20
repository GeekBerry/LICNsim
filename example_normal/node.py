#!/usr/bin/python3
#coding=utf-8


from core.node import ForwarderUnitBase
from core.info_table import isPending
import random

class ForwarderUnit(ForwarderUnitBase):
    def _inInterest(self, face_id, packet):
        data= self.api['CS::match'](packet)
        if data is not None:
            self.api['Face::send']( [face_id], data )
        else:
            self.randomForward(face_id, packet)

    def _inData(self, face_id, packet):
        info= self.api['Info::getInfo'](packet)

        send_ids= [ each_id for each_id, entry in info.items()
            if isPending(entry)
        ]

        if send_ids:
            self.api['Face::send'](send_ids, packet)  # 记录: info[send_id].outI == clock.life_time()
            self.api['CS::store'](packet)
        else:
            self.announces['unsolicited'](face_id, packet)

    def randomForward(self,  face_id, packet):
        face_ids= self.api['Face::getCanSendIds']() - {face_id, 'APP'}
        if face_ids:
            send_ids= random.sample(face_ids, min(len(face_ids), 2) )
            self.api['Face::send']( send_ids, packet )


#-----------------------------------------------------------------------------------------------------------------------
from core.node import NodeBufferUnit, AppUnit
from core.common import Hardware
from core.cs import ContentStoreUnit
from core.face import FaceUnit, RepeatChecker, LoopChecker, NoLoopChecker
from core.info_table import InfoUnit
from core.policy import FIFOPolicy
from constants import INF

class Node(Hardware):
    def __init__(self, name):
        super().__init__(name)
        self.install('buffer', NodeBufferUnit(rate= INF, buffer_size=INF) )  # 使得节点变成有缓存的, 此处设置为INF仅为测试
        self.install('faces',  FaceUnit( LoopChecker(10000), RepeatChecker() )  )
        self.install('info',   InfoUnit(max_size= 2, life_time= 100000) )
        self.install('cs',     ContentStoreUnit(capacity= 2) )
        self.install('policy', FIFOPolicy() )
        self.install('app',    AppUnit() )
        self.install('fwd',    ForwarderUnit() )  # 100来自于100*100网格平均响应时间
