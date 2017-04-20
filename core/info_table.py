#!/usr/bin/python3
#coding=utf-8

from constants import INF
from core.common import Unit
from core.clock import clock
from core.data_structure import defaultdict, SizeDictDecorator, TimeDictDecorator

# ----------------------------------------------------------------------------------------------------------------------
class InfoUnit(Unit):
    """
    table={
        name1: Info{
            faceid1: NameEntry{
                send:{TYPE: Time, TYPE2: Time...}
                recv:{TYPE: Time, TYPE2: Time...}
                },
            ...
        },
        ...
    }
    """
    class Entry:
        def __init__(self):
            self.recv= defaultdict(lambda:-INF) # {Packet.TYPE:life_time, ...}
            self.send= defaultdict(lambda:-INF) # {Packet.TYPE:life_time, ...}

        def __repr__(self):
            return str( self.__dict__ )

    class Info(defaultdict):  # dict{FaceId:NameEntry, ...}
        def __init__(self):
            super().__init__(InfoUnit.Entry)


    def __init__(self, max_size, life_time):
        self.STRING= f'max_size:{max_size} life_time:{life_time}'
        super().__init__()
        # 进行默认参数装饰
        self.table= defaultdict( InfoUnit.Info )
        # 进行尺寸限制装饰
        self.table= SizeDictDecorator(self.table, max_size)
        # 进行时间限制装饰
        self.table= TimeDictDecorator(self.table, life_time)
        self.table.before_delete_callback= self.infoEvictCallBack

    def install(self, announces, api):
        super().install(announces, api)
        # 监听的 Announce
        announces['inPacket'].append(self.inPacket)
        announces['outPacket'].append(self.outPacket)
        # 提供的 API
        api['Info::getInfo']= self.getInfo
        # 调用的 API

    def inPacket(self, face_id, packet):
        self.table[packet.name][face_id].recv[packet.type]= clock.time()

    def outPacket(self, face_id, packet):
        self.table[packet.name][face_id].send[packet.type]= clock.time()

    def getInfo(self, packet):
        return self.table[packet.name]

    def infoEvictCallBack(self, name, packet):
        self.announces['evictInfo'](name, packet)

    def __str__(self):
        return self.STRING


# ----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet


def isPending(entry):  # face同时接收到I和D, 该face不算Pending
    return entry.recv[Packet.DATA] < entry.recv[Packet.INTEREST] \
           and \
           entry.send[Packet.DATA] < entry.recv[Packet.INTEREST]


def sendIPast(entry):  # 返回兴趣包等待回应时长
    if (entry.send[Packet.DATA] < entry.send[Packet.INTEREST]  # 没有再发出数据包
    and entry.recv[Packet.DATA] < entry.send[Packet.INTEREST] ): # 没有接收到数据包
        return clock.time() - entry.send[Packet.INTEREST]  # 返回经历时长
    else:
        return INF  # 没有等待相当于经历无穷久




