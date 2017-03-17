#!/usr/bin/python3
#coding=utf-8

from core.common import Unit
from core.data_structure import deque

class ReplacePolicyBase(Unit):
    def __init__(self):
        super().__init__()

    def install(self, announces, api):
        #监听的 Announce
        announces['csStore'].append(self.store)
        announces['csEvict'].append(self.evict)
        announces['csHit'].append(self.hit)
        announces['csMiss'].append(self.miss)
        #发布的 Announce
        #提供的 API
        api['Policy::replace']= self.replace
        #调用的 API

    def uninstall(self, annouces, api):
        annouces['csStore'].remove(self.store)
        annouces['csEvict'].remove(self.evict)
        annouces['csHit'].remove(self.hit)
        annouces['csMiss'].remove(self.miss)

        if api['Policy::replace'] is self.replace:
            del api['Policy::replace']

    def store(self, packet): pass

    def hit(self, packet): pass

    def miss(self, packet): pass

    def evict(self, packet): pass

    def replace(self): return None
#-----------------------------------------------------------------------------------------------------------------------
class RandomPolicy(ReplacePolicyBase):
    def __init__(self):
        super().__init__()
        self._list= []

    def store(self, packet):
        self._list.append(packet.name)

    def evict(self, packet):
        self._list.remove(packet.name)

    def replace(self):
        return random.choice(self._list)
#-----------------------------------------------------------------------------------------------------------------------
class FIFOPolicy(ReplacePolicyBase):
    def __init__(self):
        super().__init__()
        self._deque= deque()

    def store(self, packet):
        self._deque.append(packet.name)

    def evict(self, packet):
        self._deque.remove(packet.name)

    def replace(self):
        return self._deque[0]# top
#-----------------------------------------------------------------------------------------------------------------------
class LRUPolicy(ReplacePolicyBase):
    def __init__(self):
        super().__init__()
        self._deque= deque()

    def store(self, packet):
        self._deque.append(packet.name)

    def hit(self, packet):
        self._deque.remove(packet.name)
        self._deque.append(packet.name)

    def evict(self, packet):
        self._deque.remove(packet.name)

    def replace(self):
        return self._deque[0]# top
#-----------------------------------------------------------------------------------------------------------------------
class LFUPolicy(ReplacePolicyBase):
    class Entry:
        def __init__(self, name, num):
            self.name= name
            self.num= num

        def __eq__(self, other):# '==' 比较name名字
            return self.name == other.name


    def __init__(self):
        super().__init__()
        self._deque= deque() #[ (name,used_num), ...]

    def store(self, packet):
        self._deque.append( self.Entry(packet.name, 1) )

    def hit(self, packet):
        i= self._deque.index( self.Entry(packet.name, None) )
        self._deque[i].num += 1

        # 冒泡排序, 注意是'>='
        while i<len(self._deque)-1 and self._deque[i].num >= self._deque[i+1].num:
            self._deque[i], self._deque[i+1]= self._deque[i+1], self._deque[i] #交换
            i+= 1

    def evict(self, packet):
        self._deque.remove( self.Entry(packet.name, None) )

    def replace(self):
        return self._deque[0]# top
