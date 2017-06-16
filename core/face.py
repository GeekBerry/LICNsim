#!/usr/bin/python3
#coding=utf-8

from collections import deque

from common import Unit
from core.clock import Timer
from core.data_structure import EMPTY_FUNC, TimeDictDecorator
from core.channel import Channel


class NetFace(Unit):
    def __init__(self, face_id):
        self.__face_id= face_id

        self.in_channel= None
        self.out_channel= None
        self.out_queue= deque()

    def isCanSend(self)->bool:
        return self.out_channel is not None

    def setInChannel(self, channel):
        # unset
        if isinstance( self.in_channel, Channel):
            self.in_channel.callbacks['arrived']= EMPTY_FUNC
        # set
        assert isinstance(channel, Channel)
        self.in_channel= channel
        self.in_channel.callbacks['arrived']= self.download

    def setOutChannel(self, channel):
        # unset
        if isinstance( self.out_channel, Channel):
            self.out_channel.callbacks['idle']= EMPTY_FUNC
        # set
        assert isinstance(channel, Channel)
        self.out_channel= channel
        self.out_channel.callbacks['idle']= self._outPacket

    def download(self, packet):  # Packet 交给 FaceUnit
        self.api['Face.receive'](self.__face_id, packet)

    def upload(self, packet):  # Packet 传到 Net 上
        if self.out_channel:
            self.out_queue.append(packet)
            self._outPacket()
        # else: TODO raise

    def _outPacket(self):
        if self.out_queue  and  not self.out_channel.isBusy():
            packet= self.out_queue.popleft()
            self.out_channel.sendStart(packet)
            self.announces['outPacket'](self.__face_id, packet)


# ======================================================================================================================
class LoopChecker:
    def __init__(self, nonce_life_time):
        self.info_set= TimeDictDecorator({}, nonce_life_time)  # 当做set来用

    def isLoop(self, packet):
        if packet.head() in self.info_set:  # 循环包
            return True
        else:
            self.info_set[packet.head()]= None  # 当做set来用
            return False

# if __name__ == '__main__':
#     log.level= 4
#     lc= LoopChecker()
#     p= lc.isLoop(debug_dp)
#     print(p)
#     p= lc.isLoop(debug_dp)
#     print(p)
#
#     for recv in range(0, LoopChecker.NONCE_LIFE_TIME * 2):
#         clock.step()
#
#     p= lc.isLoop(debug_dp)
#     print(p)

# ----------------------------------------------------------------------------------------------------------------------
class RepeatChecker:  # 在 1个step内保证不会往一个faceid发送,相同类型(PACKET.TYPE)和名字(Name)的包(Packet)
    def __init__(self):
        self.info_set= set()  # 手动管理
        self.clear_timer= Timer(self.info_set.clear)

    def isRepeat(self, face_id, packet):
        info_tuple= (face_id, packet.name, packet.type)
        if info_tuple in self.info_set:  # 重复包
            return True
        else:
            self.info_set.add(info_tuple)
            if not self.clear_timer:
                self.clear_timer.timing(1, __to_head__=True)  # 下一个周期伊始即被删除
            return False


# ----------------------------------------------------------------------------------------------------------------------
class FaceUnit(Unit):
    def __init__(self, loop_checker=None, repeat_checker=None):
        self.table= {}  # {faceId:Face, ...}
        self.loop_checker= loop_checker
        self.repeat_checker= repeat_checker

    def install(self, announces, api):
        super().install(announces, api)
        # 提供的 API
        self.api['Face.access']= self.access
        self.api['Face.send']= self.send
        self.api['Face.receive']= self.receive

        api['Face.getCanSendIds']= self.getCanSendIds

    # -------------------------------------------------------------------------
    def getCanSendIds(self):
        return set([  face_id  for face_id, face in self.table.items()  if face.isCanSend() ])

    # -------------------------------------------------------------------------
    def access(self, face_id, FaceFactory):
        if face_id not in self.table:
            self.table[face_id]= FaceFactory(face_id)
            self.table[face_id].install(self.announces, self.api)
            self.announces['createFace'](face_id)
        return self.table[face_id]

    def send(self, face_ids, packet):  # API: call By Forwarder
        for face_id in face_ids:
            assert face_id in self.table
            if self.repeat_checker and self.repeat_checker.isRepeat(face_id, packet):  # 排除重复包
                self.announces['repeatePacket'](face_id, packet)
            else:
                self.table[face_id].upload(packet)  # 发送

    def receive(self, face_id, packet):  # API: call By Face
        if self.loop_checker and self.loop_checker.isLoop(packet):
            self.announces['loopPacket'](face_id, packet)
        else:
            self.announces['inPacket'](face_id, packet)


# ----------------------------------------------------------------------------------------------------------------------
class AppFace(Unit):
    def __init__(self, face_id):
        self.__face_id= face_id
        self.out_port= EMPTY_FUNC

    def install(self, announces, api):
        super().install(announces, api)
        api['APP.ask']= self.download

    def isCanSend(self):
        return True

    def upload(self, packet):  # Packet 传到 APP层
        self.announces['respond'](packet)

    def download(self, packet):  # Packet 交给 FaceUnit
        self.announces['ask'](packet)
        self.api['Face.receive'](self.__face_id, packet)


class AppUnit(Unit):
    def install(self, announces, api):
        api['Face.access']('APP', AppFace)


