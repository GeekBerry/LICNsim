#!/usr/bin/python3
#coding=utf-8

from core.common import *
from core.data_structure import *


class ContentStoreUnit(Unit):
    def __init__(self, capacity):# 安装在系统上
        super().__init__()
        self.table = {}  # DictDecorator({})
        self.capacity= capacity

    def install(self, announces, api):
        """
        :param announces:
            csHit(Packet)
            csMiss(Packet)
            csStore(Packet)
            csEvict(Packet)
        :param api:
        :return:
        """
        self.publish = announces
        self.api= api
        #提供的 API
        api['CS::size']= self.size
        api['CS::setCapacity']= self.setCapacity
        api['CS::store']= self.store
        api['CS::match']= self.match


    def size(self):
        return len(self.table)

    def setCapacity(self, capacity):
        if capacity < 0:
            raise RuntimeError('必须 capacity >= 0')

        self.capacity= capacity
        self._limit(self.capacity)

    def store(self, packet):
        if self.capacity <= 0:
            log.track(label[self], 'NoCache')
            return

        if packet.name not in self.table:# 检查Data的更新
            self._limit(self.capacity - 1)
            self.publish['csStore'](packet)
        else:pass# 更新不算插入

        self.table[packet.name]= packet.fission()# fission意味着在此插入算一个新的数据包

    def match(self, packet):
        if packet.name in self.table: # FIXME 匹配方式
            data= self.table[packet.name]
            self.publish['csHit'](data)
            return data
        else:
            self.publish['csMiss'](packet)
            return None

    def _limit(self, size):
        while self.size() > size:
            name= self.api['Policy::replace']()
            packet= self.table.pop(name)
            self._evict(name, packet)

    def _evict(self, name, packet):
        self.publish['csEvict']( packet )

# if __name__ == '__main__' and 0:
#     t= ContentStoreUnit(1)
#
#     t.store(debug_dp)
#     t.store(debug_dp2)
#
#     print(t.table)

#=======================================================================================================================
class SimulatCSUnit(ContentStoreUnit):
    """
    模拟一个繁忙的CS, 即数据包插入后一段时间就会被'替换'
    有两种替换模式(FIFO, LRU),默认为不替换(MANUAL)
    """
    class MODE:
        MANUAL, FIFO, LRU= 0, 1, 2

    def __init__(self, capacity, life_time):
        super().__init__(capacity)

        self.table= TimeDictDecorator(self.table, life_time)# 对时间进行限制
        self.table.evict_callback= self._evict

        label[self.table]= label[self], '.table'

    def install(self, announces, api):
        super().install(announces, api)
        api['CS::setMode']= self.setMode
        api['CS::setLifeTime']= self.setLifeTime

    def setMode(self, mode):
        if mode == self.MODE.MANUAL: self.table.life_time= INF
        elif mode == self.MODE.FIFO: self.table.get_refresh= False
        elif mode == self.MODE.LRU:  pass
        else: pass

    def setLifeTime(self, life_time):
        self.table.life_time= life_time


if __name__ == '__main__':
    log.level= 0
    cs= SimulatCSUnit(10, life_time= 2)

    cs.mode= SimulatCSUnit.MODE.FIFO

    cs.store(debug_dp)
    cs.store(debug_dp1)
    clock.step()
    print(cs.table)

    cs.match(debug_dp)
    clock.step()
    print(cs.table)

    #cs.match(debug_dp)
    clock.step()
    print(cs.table)

    clock.step()
    print(cs.table)

