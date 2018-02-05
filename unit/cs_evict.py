import numpy
from core import Timer, Unit, INF, Bind


class CSEvictUnit(Unit):
    """
    用于监听和实现CSUnit自动驱逐功能，用于虚拟一个包在节点中被替换的工作
    """
    MODE_TYPES = ['CONST', 'FIFO', 'LRU', 'GEOMETRIC']

    def __init__(self, mode=None, life_time=INF):
        self.table = {}  # {Name:Timer(self.discard), ...}
        self._mode = mode
        self.life_time = life_time

    def install(self, announces, api):
        super().install(announces, api)
        announces['csStore'].append(self.storeEvent)
        announces['csEvict'].append(self.evictEvent)
        announces['csHit'].append(self.hitEvent)

    def discard(self, name):
        self.api['CS.discard'](name)

    # -------------------------------------------------------------------------
    def storeEvent(self, packet):
        if packet.name not in self.table:
            self.table[packet.name] = Timer( Bind(self.discard, packet.name) )

        if self._mode in ('FIFO', 'LRU'):
            self.table[packet.name].timing(self.life_time)
        elif self._mode == 'GEOMETRIC':
            self.table[packet.name].timing( numpy.random.geometric(1/self.life_time) )  # 几何分布

    def evictEvent(self, packet):
        del self.table[packet.name]

    def hitEvent(self, packet):
        assert packet.name in self.table
        if self._mode == 'LRU':
            self.table[packet.name].timing(self.life_time)

    def missEvent(self, packet):
        pass


if __name__ == '__main__':
    from core import clock, AnnounceTable, CallTable
    from unit import ContentStoreUnit
    from debug import *

    anno, api = AnnounceTable(), CallTable()

    cs = ContentStoreUnit()
    cs.install(anno, api)

    evict = CSEvictUnit('FIFO', 6)
    evict.install(anno, api)

    cs.store(dp_A)

    for i in range(5):
        print(clock.time, cs.table)
        clock.step()

    data = cs.match(ip_A)
    print(ip_A, data)

    for i in range(10):
        print(clock.time, cs.table)
        clock.step()
