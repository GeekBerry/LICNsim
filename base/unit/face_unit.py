#!/usr/bin/python3
#coding=utf-8

import logging
logging.basicConfig(level=logging.WARNING)

from collections import deque
from base.channel import Channel
from base.core import EMPTY_FUNC, TimeDictDecorator, Bind, Timer, clock
from common import Unit


class FaceBase:
    def download(self, packet):  # 由 FaceUnit 进行 Bind, 由使用者或信道进行调用
        raise NotImplementedError

    def upload(self, packet):  # 由 FaceUnit 进行调用
        raise NotImplementedError


class NetFace(FaceBase):
    """
    in_channel.callbacks['arrived'](packet)  ==>  self.download  ==>  self.api['Face.recevie'](face_id, packet)
    out_channel.send(packet)  <==  [Queue]  <==  self.upload
    """
    def __init__(self):
        self.in_channel= None
        self.out_channel= None
        # TODO self.in_queue
        self.out_queue= deque()

    def setInChannel(self, channel):
        # unset
        if isinstance(self.in_channel, Channel):
            self.in_channel.callbacks['arrived']= EMPTY_FUNC
        # set
        assert isinstance(channel, Channel)
        self.in_channel= channel
        self.in_channel.callbacks['arrived']= self.download

    def setOutChannel(self, channel):
        # unset
        if isinstance(self.out_channel, Channel):
            self.out_channel.callbacks['idle']= EMPTY_FUNC
        # set
        assert isinstance(channel, Channel)
        self.out_channel= channel
        self.out_channel.callbacks['idle']= self.checkPop

    def upload(self, packet):  # Packet 传到 Net 上
        if self.out_channel:
            self.out_queue.append(packet)
            self.checkPop()
        else:
            raise Exception('没有 out_channel 不能发送', )

    def checkPop(self):
        if self.out_queue  and  not self.out_channel.isBusy():
            packet= self.out_queue.popleft()
            self.out_channel.send(packet)


# ======================================================================================================================
# TODO

class LoopChecker:
    def __init__(self, nonce_life_time):
        self.info_set= TimeDictDecorator({}, nonce_life_time)  # 当做set来用

    def isLoop(self, packet):
        if packet.head() in self.info_set:  # 循环包
            return True
        else:
            self.add(packet)
            return False

    def add(self, packet):  # 标记发送该 Packet
        self.info_set.setdefault( packet.head() )


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
class RepeatChecker:  # 在 1 个step内保证不会往一个 faceid 发送,相同类型(PACKET.TYPE)和名字(Name)的包(Packet)
    def __init__(self):
        self.info_set= set()  # 手动管理
        self.record_time= clock.time()

    def isRepeat(self, face_id, packet):
        self.checkReset()

        info_tuple= (face_id, packet.name, packet.type)
        if info_tuple in self.info_set:  # 重复包
            # logging.info(f'repeat {face_id} {packet}')
            return True
        else:
            self.info_set.add(info_tuple)
            return False

    def checkReset(self):
        cur_time= clock.time()
        if self.record_time != cur_time:
            self.info_set.clear()
        self.record_time= cur_time


# ----------------------------------------------------------------------------------------------------------------------
class FaceUnit(Unit):
    def __init__(self, loop_checker=None, repeat_checker=None):
        self.table= {}  # {faceId:Face, ...}
        self.loop_checker= loop_checker
        self.repeat_checker= repeat_checker

    def install(self, announces, api):
        super().install(announces, api)
        self.api['Face.get']= self.get
        self.api['Face.access']= self.access
        self.api['Face.send']= self.send
        self.api['Face.receive']= self.receive
        api['Face.netIds']= self.netIds

    def netIds(self):
        return filter( lambda face_id: isinstance( self.table[face_id], NetFace ), self.table.keys() )

    # -------------------------------------------------------------------------
    def get(self, face_id):
        return self.table.get(face_id, None)

    def access(self, face_id, FaceFactory):
        if face_id not in self.table:
            self.table[face_id]= FaceFactory()
            self.table[face_id].download= Bind(self.receive, face_id)
            self.announces['createFace'](face_id)
        return self.table[face_id]

    def send(self, face_ids, packet):  # API: call By Forwarder
        for face_id in face_ids:
            assert face_id in self.table
            if self.repeat_checker and self.repeat_checker.isRepeat(face_id, packet):  # 排除重复包
                self.announces['repeatePacket'](face_id, packet)
            else:
                self.table[face_id].upload(packet)  # 发送
                self.announces['outPacket'](face_id, packet)  # FIXME 真正发送时???
        self.loop_checker.add(packet)

    def receive(self, face_id, packet):  # API: call By Face Bind
        if self.loop_checker and self.loop_checker.isLoop(packet):
            self.announces['loopPacket'](face_id, packet)
        else:
            self.announces['inPacket'](face_id, packet)


# ======================================================================================================================
def unfoldFaceTypes(face_unit):
    for face_id, face in face_unit.table.items():
        if isinstance(face, NetFace):
            out_queue= str(face.out_queue)
        else:
            out_queue= None

        yield face_id, face.__class__.__name__, out_queue

FaceUnit.UI_ATTRS= {
    'FaceTable':{
        'type':'Table',
        'range': ('FaceId', 'FaceType', 'OutQueue'),
        'getter': unfoldFaceTypes
    }
}


