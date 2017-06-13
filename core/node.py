#!/usr/bin/python3
#coding=utf-8
from common import Hardware, Unit
from core.data_structure import Announce


class NodeBase(Hardware):
    def __init__(self, name):
        super().__init__(f'Node({name})')


# =======================================================================================================================
from core.data_structure import SizeLeakyBucket


class NodeBufferUnit(Announce, Unit):
    def __init__(self, rate, buffer_size):
        Announce.__init__(self)
        self._bucket= SizeLeakyBucket(rate, buffer_size)

    @property
    def buffer_size(self):
        return self._bucket.max_size

    @buffer_size.setter
    def buffer_size(self, value):
        self._bucket.max_size= value

    @property
    def rate(self):
        return self._bucket.rate

    @rate.setter
    def rate(self, value):
        self._bucket.rate= value

    def install(self, announces, api):
        self.callbacks+= announces['inPacket'].callbacks  # 复制原有列表
        announces['inPacket']= self  # 覆盖announces['inPacket']
        Unit.install(self, announces, api)

        self._bucket.callbacks['full']= self.announces['drop']
        self._bucket.callbacks['end']= super().__call__  # XXX super 指 Announce

    def __call__(self, faceid, packet):
        self._bucket.append(1, faceid, packet)  # size= 1: rate, buffer_size的单位为(包); size=len(packet): rate, buffer_size的单位为(bytes)


# ----------------------------------------------------------------------------------------------------------------------
class AppUnit(Unit):
    def __init__(self):
        self.app_channel= Announce()  # 用于发送兴趣包的通道

    def install(self, announces, api):
        super().install(announces, api)
        # 提供的 API
        api['APP.ask']= self._ask
        # 调用的 API
        api['Face.setInChannel']('APP', self.app_channel)
        api['Face.setOutChannel']('APP', self._respond)

        # api['Face.create']('APP', self.app_channel, self._respond)  # 调用Face的api建立连接

    def _ask(self, packet):
        self.announces['ask'](packet)
        self.app_channel(packet)  # 发送packet

    def _respond(self, packet):
        self.announces['respond'](packet)

# ----------------------------------------------------------------------------------------------------------------------
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






