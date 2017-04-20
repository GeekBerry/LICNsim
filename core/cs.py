#!/usr/bin/python3
#coding=utf-8

from core.common import Unit
from core.data_structure import TimeDictDecorator
from debug import debug_dp, debug_dp1


class ContentStoreUnit(Unit):
    def __init__(self, capacity):  # 安装在系统上
        self.table = {}
        self.capacity= capacity

    def install(self, announces, api):
        super().install(announces,api)
        # 提供的 API
        api['CS::size']= self.__len__
        api['CS::setCapacity']= self.setCapacity
        api['CS::store']= self.store
        api['CS::match']= self.match
        # 调用的 API
        self.replace= api['Policy::replace']

    def __len__(self):
        return len(self.table)

    def setCapacity(self, value):
        if value < 0:
            raise RuntimeError('必须 capacity >= 0')
        self.capacity= value
        self._limit(value)

    def store(self, packet):
        if self.capacity <= 0:
            return

        if packet.name not in self.table:  # 检查Data的更新
            self._limit(self.capacity - 1)
            self.announces['csStore'](packet)
        else:pass  # 更新不算插入

        self.table[packet.name]= packet.fission()  # fission意味着在此插入算一个新的数据包

    def match(self, packet):
        if packet.name in self.table: # FIXME 匹配方式
            data= self.table[packet.name]
            self.announces['csHit'](data)
            return data
        else:
            self.announces['csMiss'](packet)
            return None

    def _limit(self, size):
        while len(self) > size:
            name= self.replace()
            packet= self.table.pop(name)
            self._evict(name, packet)

    def _evict(self, name, packet):
        self.announces['csEvict'](packet)

    def __str__(self):
        return f'length:{len(self)} capacity:{self.capacity}'

# if __name__ == '__main__':
#     from core.data_structure import CallTable, AnnounceTable
#     t= ContentStoreUnit(1)
#
#     announces= AnnounceTable()
#     api= CallTable()
#     t.install(announces, api)
#
#     api['CS::setCapacity'](5)
#
#     print(t.table)

#=======================================================================================================================
import constants
class SimulatCSUnit(ContentStoreUnit):
    """
    模拟一个繁忙的CS, 即数据包插入后一段时间就会被'替换'
    有两种替换模式(FIFO, LRU),默认为不替换(MANUAL)
    """
    class MODE:
        MANUAL, FIFO, LRU= 0, 1, 2

    def __init__(self, capacity, life_time):
        super().__init__(capacity)
        self.table= TimeDictDecorator(self.table, life_time)  # 对时间进行限制
        self.table.evict_callback= self._evict

    def install(self, announces, api):
        super().install(announces, api)
        api['CS::setMode']= self.setMode
        api['CS::setLifeTime']= self.setLifeTime

    def setMode(self, mode):
        if mode == self.MODE.MANUAL: self.table.life_time= constants.INF
        elif mode == self.MODE.FIFO: self.table.get_refresh= False
        elif mode == self.MODE.LRU:  pass
        else: pass

    def setLifeTime(self, life_time):
        self.table.life_time= life_time


# if __name__ == '__main__':
#     from core.clock import clock
#     cs= SimulatCSUnit(10, life_time= 2)
#
#     cs.mode= SimulatCSUnit.MODE.FIFO
#
#     cs.store(debug_dp)
#     cs.store(debug_dp1)
#     clock.step()
#     print(cs.table)
#
#     cs.match(debug_dp)
#     clock.step()
#     print(cs.table)
#
#     clock.step()
#     print(cs.table)
#
#     clock.step()
#     print(cs.table)

