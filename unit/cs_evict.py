import numpy
from core import Timer, Unit, INF

class CSEvictUnit(Unit):
    """
    用于监听和实现CSUnit自动驱逐功能，用于虚拟一个包在节点中被替换的工作
    """
    MODE_TYPES = ['CONST', 'FIFO', 'LRU', 'GEOMETRIC']

    def __init__(self, life_time=INF, mode='CONST'):
        self.table = {}  # {Name:Timer, ...}
        self.life_time = life_time
        self.mode = mode

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value: str):
        assert value in self.MODE_TYPES
        self._mode = value

    def install(self, announces, api):
        super().install(announces, api)
        announces['csStore'].append(self.store)
        announces['csEvict'].append(self.evict)
        announces['csHit'].append(self.hit)
        self.csDiscard = api['CS.discard']

    def store(self, packet):
        timer = self.table.setdefault(packet.name, Timer(self.csDiscard))

        if self.mode in ('FIFO', 'LRU'):
            timer.timing(self.life_time, packet.name)
        elif self.mode == 'GEOMETRIC':
            life_time = numpy.random.geometric(1 / self.life_time)  # 几何分布
            timer.timing(life_time, packet.name)

    def hit(self, packet):
        assert packet.name in self.table
        if self.mode == 'LRU':
            self.table[packet.name].timing(self.life_time, packet.name)

    def evict(self, packet):
        del self.table[packet.name]


if __name__ == '__main__':
    from core import clock, AnnounceTable, CallTable
    from unit import ContentStoreUnit
    from debug import *

    anno, api = AnnounceTable(), CallTable()

    cs = ContentStoreUnit()
    cs.install(anno, api)

    evict = CSEvictUnit(6, 'FIFO')
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
