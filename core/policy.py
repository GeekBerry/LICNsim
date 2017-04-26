#!/usr/bin/python3
#coding=utf-8

import random
from core.common import Unit
from core.data_structure import deque

class PolicyUnit(Unit):
    def __init__(self, PolocyFactory):
        super().__init__()
        self.setPolicyType(PolocyFactory)

    def install(self, announces, api):
        super().install(announces, api)
        # 监听的 Announce
        announces['csStore'].append(self.store)
        announces['csEvict'].append(self.evict)
        announces['csHit'].append(self.hit)
        announces['csMiss'].append(self.miss)
        # 提供的 API
        api['Policy::setPolicy']= self.setPolicyType
        api['Policy::replace']= self.replace

    def uninstall(self, annouces, api):
        annouces['csStore'].remove(self.store)
        annouces['csEvict'].remove(self.evict)
        annouces['csHit'].remove(self.hit)
        annouces['csMiss'].remove(self.miss)

        if api['Policy::replace'] is self.replace:
            del api['Policy::replace']

        if api['Policy::setPolicy'] is self.setPolicyType:
            del api['Policy::setPolicy']

    def setPolicyType(self, PolocyFactory):
        self.policy= PolocyFactory()
        self.store= self.policy.store
        self.evict= self.policy.evict
        self.hit= self.policy.hit
        self.miss= self.policy.miss
        self.replace= self.policy.replace

    @property
    def PolicyType(self):
        return self.policy.__class__

    @PolicyType.setter
    def PolicyType(self, value):
        self.setPolicyType(value)

# ======================================================================================================================
class PolicyBase:
    def __init__(self):
        super().__init__()

    def store(self, packet): pass

    def hit(self, packet): pass

    def miss(self, packet): pass

    def evict(self, packet): pass

    def replace(self): return None


def searchPolicyInModule(module):
    for value in module.__dict__.values():
        if ( isinstance(value, type)
        and issubclass(value, PolicyBase)
        and (value is not PolicyBase) ):
            yield value
# ----------------------------------------------------------------------------------------------------------------------
class RandomPolicy(PolicyBase):
    def __init__(self):
        super().__init__()
        self._list= []

    def store(self, packet):
        self._list.append(packet.name)

    def evict(self, packet):
        self._list.remove(packet.name)

    def replace(self):
        return random.choice(self._list)


# ----------------------------------------------------------------------------------------------------------------------
class FIFOPolicy(PolicyBase):
    def __init__(self):
        super().__init__()
        self._deque= deque()

    def store(self, packet):
        self._deque.append(packet.name)

    def evict(self, packet):
        self._deque.remove(packet.name)

    def replace(self):
        return self._deque[0]# top


# ----------------------------------------------------------------------------------------------------------------------
class LRUPolicy(PolicyBase):
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
        return self._deque[0]  # top


# ----------------------------------------------------------------------------------------------------------------------
class LFUPolicy(PolicyBase):
    class Entry:
        def __init__(self, name, num):
            self.name= name
            self.num= num

        def __eq__(self, other):  # '==' 比较name名字
            return self.name == other.name

    def __init__(self):
        super().__init__()
        self._deque= deque()  # [ (name,used_num), ...]

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
        return self._deque[0]  # top



