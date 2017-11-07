import numpy
from core import Timer, Bind, Unit

#
# class CSEvictUnit(Unit):
#     CONST, FIFO, LRU= 0, 1, 2
#
#     def __init__(self, life_time, mode):
#         self.table= {}  # {Name:Timer, ...}
#         self.life_time= life_time
#         self.setMode(mode)
#
#     def install(self, announces, api):
#         super().install(announces, api)
#         announces['csStore'].append(self.store)
#         announces['csEvict'].append(self.evict)
#         announces['csHit'].append(self.hit)
#         api['Evict.setMode']= self.setMode
#         self.csDiscard= api['CS.discard']
#
#     def setMode(self, mode):
#         if mode == 'CONST':
#             self.mode= self.CONST
#         elif mode == 'FIFO':
#             self.mode = self.FIFO
#         elif mode == 'LRU':
#             self.mode = self.LRU
#         else:
#             raise ValueError(f'未知模式{mode}')
#
#     def store(self, packet):
#         timer= self.table.setdefault(  packet.name, Timer( Bind(self.csDiscard, packet.name) )  )
#         if self.mode != self.CONST:
#             timer.timing(self.life_time)
#
#     def hit(self, packet):
#         assert packet.name in self.table
#         if self.mode == self.LRU:
#             self.table[packet.name].timing(self.life_time)
#
#     def evict(self, packet):
#         del self.table[packet.name]


class CSEvictUnit(Unit):
    def __init__(self, life_time, mode):
        self.table= {}  # {Name:Timer, ...}
        self.life_time= life_time
        self.setMode(mode)

    def install(self, announces, api):
        super().install(announces, api)
        announces['csStore'].append(self.store)
        announces['csEvict'].append(self.evict)
        announces['csHit'].append(self.hit)
        api['Evict.setMode']= self.setMode
        self.csDiscard= api['CS.discard']

    def setMode(self, mode):
        assert mode in ('CONST', 'FIFO', 'LRU', 'GEOMETRIC')
        self.mode= mode

    def store(self, packet):
        timer= self.table.setdefault(  packet.name, Timer( Bind(self.csDiscard, packet.name) )  )

        if self.mode in ('FIFO', 'LRU'):
            timer.timing(self.life_time)
        elif self.mode == 'GEOMETRIC':
            life_time= numpy.random.geometric( 1/self.life_time )  # 几何分布
            timer.timing(life_time)

    def hit(self, packet):
        assert packet.name in self.table
        if self.mode == 'LRU':
            self.table[packet.name].timing(self.life_time)

    def evict(self, packet):
        del self.table[packet.name]


if __name__ == '__main__':
    from core import clock, AnnounceTable, CallTable
    from unit import ContentStore
    from debug import *

    anno, api= AnnounceTable(), CallTable()

    cs= ContentStore()
    cs.install(anno, api)

    evict= CSEvictUnit(6, 'FIFO')
    evict.install(anno, api)

    cs.store(dp_A)

    for i in range(5):
        print(clock.time(), cs.table)
        clock.step()

    data= cs.match(ip_A)
    print(ip_A, data)

    for i in range(10):
        print(clock.time(), cs.table)
        clock.step()
