#!/usr/bin/python3
#coding=utf-8

from core.common import Unit
from core.data_structure import *

class Face:
    def __init__(self, face_id):
        self.face_id= face_id
        self.downstream= None
        self.upstream= None
        self.can_recv= True
        self.can_send= True

    def download(self, packet):  # 接收一个包
        if self.can_recv:
            self.downstream(self.face_id, packet)

    def upload(self, packet):  # 发送一个包
        if self.can_send:
            self.upstream(packet)

#=======================================================================================================================
class NoLoopChecker:
    def __init__(self, *args):
        pass

    def isLoop(self, packet):
        return False


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

#-----------------------------------------------------------------------------------------------------------------------
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

# if __name__ == '__main__':
#     from constants import *
#     rc= RepeatChecker()
#
#     def preCheck():
#         p= rc.isRepeat(0, debug_ip)
#         print('preCheck', p)
#     clock.timing(1, preCheck)
#
#     p= rc.isRepeat(0, debug_ip)
#     print(p)
#
#     p= rc.isRepeat(0, debug_ip)
#     print(p)
#
#     clock.step()
#
#     p= rc.isRepeat(0, debug_ip)
#     print(p)


#-----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet
from core.packet import Name

class FaceUnit(Unit):
    def __init__(self, loop_checker, repeat_checker):
        Unit.__init__(self)
        self.table= Dict()  # {faceId:Face, ...}
        self.loop_checker= loop_checker
        self.repeat_checker= repeat_checker

    def install(self, announces, api):
        super().install(announces, api)
        # 提供的 API
        api['Face::create']= self.create
        api['Face::destroy']= self.destroy
        api['Face::getCanSendIds']= self.getCanSendIds
        api['Face::send']= self.send

    #--------------------------------------------------------------------------
    def create(self, face_id, in_channel, out_channel):  # API
        """
            Channel                       Face                           FaceUnit
        +-------------+               +----------+                  +----------------+
        | dst_channel | <--upstream---| can_send |<----upload-----  | |repeat check| |<-- send ---
        +-------------+               |          |                  | ============== |>> outPacket
        | in_channel  | ---download-->| can_recv |---downstream-->  | | loop check | |>> inPacket
        +-------------+               +----------+                  +----------------+
        :param face_id:Any
        :param in_channel:isinstance(Channel)
        :param out_channel:isinstance(Channel)
        :return:None
        """
        self.destroy(face_id) #不破不立

        face= self.table.setdefault( face_id, Face(face_id) )
        in_channel.append(face.download)
        face.upstream= out_channel
        face.downstream= self.receive

    def destroy(self, face_id):
        face= self.table.pop(face_id)
        if face is not None:
            face.downstream= EMPTY_FUNC  # 不会再下发数据包

    def getCanSendIds(self):
        send_ids= [ face_id
            for face_id, face in self.table.items()
                if face.can_send
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

# if __name__ == '__main__':
#     print('test Face', __file__)
#     log.level= 4
#     api= CallTable()
#     announces= AnnounceTable()
#
#     face= FaceUnit(LoopChecker(10000), RepeatChecker())
#     face.install(announces, api)
#
#     app= Announce()
#
#     api['Face::create']('F1',app, print )
#
#     #announces['sendData']( {'F1'}, 'Data')
#
#     dp= Packet(Name(['A',1]), Packet.TYPE.DATA)
#     app(dp)
#
#     face.destroy('F1')
#     app(dp)
#
#     appnew= Announce()
#     api['Face::create']('F1',appnew, print )
#     app(dp)
#     appnew(dp)



