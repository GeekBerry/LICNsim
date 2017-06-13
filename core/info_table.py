#!/usr/bin/python3
#coding=utf-8

from constants import INF
from common import Unit
from core.clock import clock
from core.data_structure import defaultdict, SizeDictDecorator, TimeDictDecorator, SheetTable
from core.packet import Packet

# ----------------------------------------------------------------------------------------------------------------------
class InfoUnit(Unit):
    """
    sheet_table:
            faceid1     faceid2     ...
    name1   Cell        Cell        ...
    name2   Cell        Cell        ...
    ...     ...         ...         ...

    """
    class Cell:
        """
                type1   type2   ...
        recv:   Time    Time    ...
        send:   Time    Time    ...
        """
        def __init__(self):
            self.recv= defaultdict(lambda:-INF)  # {Packet.TYPE:life_time, ...}
            self.send= defaultdict(lambda:-INF)  # {Packet.TYPE:life_time, ...}

        def isPending(self):  # face同时接收到I和D, 该face不算Pending
            return (self.recv[Packet.DATA] < self.recv[Packet.INTEREST]
                and self.send[Packet.DATA] < self.recv[Packet.INTEREST])

        def sendInterestPast(self):  # 返回兴趣包等待回应时长
            if (self.send[Packet.DATA] < self.send[Packet.INTEREST]  # 没有再发出数据包
            and self.recv[Packet.DATA] < self.send[Packet.INTEREST]):  # 没有接收到数据包
                return clock.time() - self.send[Packet.INTEREST]  # 返回经历时长
            else:
                return INF  # 没有等待相当于经历无穷久

    def __init__(self, max_size, life_time):
        super().__init__()
        # 进行默认参数装饰
        self.sheet_table= SheetTable()
        # 进行尺寸限制装饰
        self.size_table= SizeDictDecorator(self.sheet_table, max_size)  # FIXME  defaultdict会导致max_size=0失效
        # 进行时间限制装饰
        self.table= TimeDictDecorator(self.size_table, life_time)
        self.table.before_delete_callback= self.infoEvictCallBack

    @property
    def life_time(self):
        return self.table.life_time

    @life_time.setter
    def life_time(self, value):
        self.table.life_time= value

    @property
    def max_size(self):
        return self.size_table.max_size

    @max_size.setter
    def max_size(self, value):
        self.size_table.max_size= value

    def install(self, announces, api):
        super().install(announces, api)
        # 监听的 Announce
        announces['inPacket'].append(self.inPacket)
        announces['outPacket'].append(self.outPacket)
        announces['createFace'].append(self.insertFaceid)
        announces['destroyFace'].append(self.dropFaceid)
        # 提供的 API
        # api['Info.getCell']= self.getCell
        api['Info.getPendingIds']= self.getPendingIds
        api['Info.getCooledIds']= self.getCooledIds
        # 调用的 API

    def infoEvictCallBack(self, name, packet):
        self.announces['evictInfo'](name, packet)

    def insertFaceid(self, faceid):
        self.sheet_table.addField(faceid, InfoUnit.Cell)  # SheetTable

    def dropFaceid(self, faceid):
        self.sheet_table.dropField(faceid)  # SheetTable

    def inPacket(self, face_id, packet):
        self.table[packet.name][face_id].recv[packet.type]= clock.time()

    def outPacket(self, face_id, packet):
        self.table[packet.name][face_id].send[packet.type]= clock.time()

    # def getCell(self, packet_name, faceid):
    #     return self.table[packet_name][faceid]

    def getPendingIds(self, name)->set:
        _ids= [ faceid
            for faceid, cell in self.table[name].items()
                if cell.isPending()
        ]
        return set(_ids)

    def getCooledIds(self, name, cool_delay)->set:
        _ids= [ faceid
            for faceid, cell in self.table[name].items()
                if cell.sendInterestPast() > cool_delay
        ]
        return set(_ids)





