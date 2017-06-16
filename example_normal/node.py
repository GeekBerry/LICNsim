# coding=utf-8


from core.node import ForwarderUnitBase
import random


class ForwarderUnit(ForwarderUnitBase):
    def _inInterest(self, face_id, packet):
        data= self.api['CS.match'](packet)
        if data is not None:
            self.api['Face.send']( [face_id], data )
        else:
            self.randomForward(face_id, packet)

    def _inData(self, face_id, packet):
        send_ids= self.api['Info.getPendingIds'](packet.name)
        if send_ids:
            self.api['Face.send'](send_ids, packet)  # 记录: info[send_id].outI == clock.life_time()
            self.api['CS.store'](packet)
        else:
            self.announces['unsolicited'](face_id, packet)

    def randomForward(self,  face_id, packet):
        face_ids= self.api['Face.getCanSendIds']() - {face_id, 'APP'}
        if face_ids:
            send_ids= random.sample(face_ids, min(len(face_ids), 2) )
            self.api['Face.send']( send_ids, packet )


# ----------------------------------------------------------------------------------------------------------------------
from random import randint
from core.node import NodeBase, NodeBufferUnit
from face import AppUnit
from common import Hardware
from core.cs import ContentStoreUnit
from core.face import FaceUnit, RepeatChecker, LoopChecker
from core.info_table import InfoUnit
from core.policy import FIFOPolicy, PolicyUnit
from constants import INF


class TestNode(NodeBase):
    def __init__(self, name):
        Hardware.__init__(self, f'Node {name}')
        # self.install('buffer', NodeBufferUnit(rate= INF, buffer_size= INF) )
        self.install('faces',  FaceUnit( LoopChecker(10000), RepeatChecker() )  )
        self.install('info',   InfoUnit(max_size= INF, life_time= 100000) )
        self.install('cs',     ContentStoreUnit(capacity=1)  )
        self.install('policy', PolicyUnit(FIFOPolicy) )
        self.install('app',    AppUnit() )
        self.install('fwd',    ForwarderUnit() )
