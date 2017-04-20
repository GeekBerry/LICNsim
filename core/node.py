#!/usr/bin/python3
#coding=utf-8
from core.common import Hardware, Unit
from core.data_structure import Announce
from debug import showCall

class NodeBase(Hardware):
    def __init__(self, name):
        super().__init__(f'Node({name})')

#=======================================================================================================================
from core.data_structure import SizeLeakyBucket
class NodeBufferUnit(Announce, Unit):
    def __init__(self, rate, buffer_size):
        Announce.__init__(self)
        Unit.__init__(self)
        self._bucket= SizeLeakyBucket( super().__call__, rate=rate, max_size= buffer_size )  # XXX super应该指Announce

    def install(self, announces, api):
        self.callbacks+= announces['inPacket'].callbacks  # 复制原有列表
        announces['inPacket']= self     # 重新接入announces['inPacket']
        super().install(announces, api)

    def __call__(self, faceid, packet):
        if not self._bucket(faceid, packet, size= 1):  # size= 1: rate, buffer_size的单位为(包); size=len(packet): rate, buffer_size的单位为(bytes)
            self.announces['drop'](faceid, packet)

    def __str__(self):
        return f'rate:{self._bucket.rate} buffer_size:{self._bucket.max_size}'


# class NodeBuffer(Announce):
#     def __init__(self, callback, rate, buffer_size):
#         super().__init__()
#         self._bucket= SizeLeakyBucket(rate, buffer_size, callback)
#
#     def __call__(self, faceid, packet):
#         if not self._bucket.append(1, (faceid, packet,)):
#             self.announces['drop'](faceid, packet)

#-----------------------------------------------------------------------------------------------------------------------
class AppUnit(Unit):
    def __init__(self):
        super().__init__()
        self.app_channel= Announce()  # 用于发送兴趣包的通道

    def install(self, announces, api):
        super().install(announces, api)
        # 提供的 API
        api['APP::ask']= self._ask
        # 调用的 API
        api['Face::create']('APP', self.app_channel, self._respond)  # 调用Face的api建立连接

    def _ask(self, packet):
        self.announces['ask'](packet)
        self.app_channel(packet)  # 发送packet

    def _respond(self, packet):
        self.announces['respond'](packet)

#-----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet
class ForwarderUnitBase(Unit):
    def install(self, announces, api):
        super().install(announces, api)
        # 监听的Announce
        announces['inPacket'].append(self._inPacket)
        # 调用的 API

    def _inPacket(self, face_id, packet):
        if packet.type == Packet.INTEREST:
            self._inInterest(face_id, packet)
        elif packet.type == Packet.DATA:
            self._inData(face_id, packet)
        else:pass

    def _inInterest(self, face_id, packet):
        pass

    def _inData(self, face_id, packet):
        pass








