#!/usr/bin/python3
#coding=utf-8

from common import Unit
from core.data_structure import *

class Face:
    def __init__(self, face_id, recv_callback):
        self.face_id= face_id
        self.in_channel= None
        self.out_channel= None
        self.recv_callback= recv_callback  # 接收时的回调操作

    def __bool__(self):
        return (self.in_channel is not None) or (self.out_channel is not None)

    def setInChannel(self, in_channel):
        self.unsetInChannel()
        self.in_channel= in_channel
        self.in_channel.append(self.download)

    def unsetInChannel(self):
        if isinstance(self.in_channel, Announce):
            self.in_channel.discard(self.download)
            self.in_channel= None

    def setOutChannel(self, out_channel):
        self.out_channel= out_channel

    def upload(self, packet):
        self.out_channel(packet)

    def download(self, packet):  # 接收一个包, 被动调用
        self.recv_callback(self.face_id, packet)


#=======================================================================================================================
class LoopChecker:
    def __init__(self, nonce_life_time):
        self.info_set= TimeDictDecorator({}, nonce_life_time)  # 当做set来用

    def isLoop(self, packet):
        if packet.head() in self.info_set:  # 循环包
            return True
        else:
            self.info_set[packet.head()]= None  # 当做set来用
            return False


class NoLoopChecker(LoopChecker):
    def isLoop(self, packet):
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


#-----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet
from name import Name


class FaceUnit(Unit):
    """
        Channel                       Face                           FaceUnit
    +-------------+               +----------+                  +----------------+
    | dst_channel | <--upstream---| can_send |<----upload-----  | |repeat check| |<-- send ---
    +-------------+               |          |                  | ============== |>> outPacket
    | in_channel  | ---download-->| can_recv |---downstream-->  | | loop check | |>> inPacket
    +-------------+               +----------+                  +----------------+
    """
    def __init__(self, loop_checker, repeat_checker):
        Unit.__init__(self)
        self.table= {}  # {faceId:Face, ...}
        self.loop_checker= loop_checker
        self.repeat_checker= repeat_checker

    def install(self, announces, api):
        super().install(announces, api)
        # 提供的 API
        api['Face.setInChannel']= self.setInChannel
        api['Face.setOutChannel']= self.setOutChannel
        api['Face.destroy']= self.destroy
        api['Face.getCanSendIds']= self.getCanSendIds
        api['Face.send']= self.send

    def accessFace(self, face_id):
        face= self.table.setdefault( face_id, Face(face_id, self.receive) )
        self.announces['createFace'](face_id)
        return face

    def setInChannel(self, face_id, in_channel):
        self.accessFace(face_id).setInChannel(in_channel)

    def setOutChannel(self, face_id, out_channel):
        self.accessFace(face_id).setOutChannel(out_channel)

    def destroy(self, face_id):
        if face_id in self.table:
            face= self.table.pop(face_id)
            face.unsetInChannel()  # 通知给face装传送数据的Channel删除对face的引用
        self.announces['destroyFace'](face_id)

    def getCanSendIds(self):
        send_ids= [ face_id
            for face_id, face in self.table.items()
                if face.out_channel
            ]
        return set(send_ids)

    #--------------------------------------------------------------------------
    def receive(self, face_id, packet):
        if self.loop_checker.isLoop(packet):
            self.announces['loopPacket'](face_id, packet)
        else:
            self.announces['inPacket'](face_id, packet)

    def send(self, faceids, packet):
        for face_id in faceids:
            if face_id not in self.table:  # 排除无效faceid
                continue

            if self.repeat_checker.isRepeat(face_id, packet):  # 排除重复包
                self.announces['repeatePacket'](face_id, packet)
                continue

            self.announces['outPacket'](face_id, packet)
            self.table[face_id].upload(packet)  # 发送

    def __str__(self):
        return f'faces:{list(self.table.keys())}'


if __name__ == '__main__':
    print('test Face', __file__)

    dp= Packet(Name('/A/1'), Packet.DATA)

    c12= Announce()
    c21= Announce()

    face1= Face(1, print)
    face2= Face(2, print)

    face1.setOutChannel(c12)
    face2.setInChannel(c12)

    face2.setOutChannel(c21)
    face1.setInChannel(c21)

    face1.download(dp)

