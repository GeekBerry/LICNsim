from core import DataBaseTable, Unit, clock


class ReplaceUnit(Unit):
    MODE_FIELD_MAP = {'FIFO': 'c_time', 'LRU': 'a_time', 'LFU': 'hit_count'}

    def __init__(self, mode='FIFO'):
        self.db_table= DataBaseTable().create('name', c_time= None, a_time= None, hit_count=0)
        self.db_table.createIndexs('c_time', 'a_time', 'hit_count')
        self._mode = mode

    def install(self, announces, api):
        super().install(announces, api)
        announces['csStore'].append(self.store)
        announces['csEvict'].append(self.evict)
        announces['csHit'].append(self.hit)
        announces['csMiss'].append(self.miss)
        api['Replace.replaceIter']= self.replaceIter
        api['Replace.setMode']= lambda value: setattr(self, 'mode', value)

    def store(self, packet):
        cur_time= clock.time()
        self.db_table[packet.name]= {'c_time':cur_time, 'a_time':cur_time, 'hit_count':1}

    def hit(self, packet):
        self.db_table[packet.name]['a_time']= clock.time()
        self.db_table[packet.name]['hit_count'] += 1

    def miss(self, packet):
        pass

    def evict(self, packet):
        del self.db_table[packet.name]

    # -------------------------------------------------------------------------
    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        assert value in self.MODE_FIELD_MAP.keys()
        self._mode= value

    def replaceIter(self):
        field= self.MODE_FIELD_MAP[self._mode]
        for record in self.db_table.minIter(field):
            yield record['name']


if __name__ == '__main__':
    unit= ReplaceUnit('FIFO')

    from core import Packet, Name
    p1 = Packet(Name('A/1'), 1, Packet.DATA)
    p2 = Packet(Name('A/2'), 1, Packet.DATA)

    unit.store(p1)
    clock.step()

    unit.store(p2)
    clock.step()

    unit.hit(p1)

    # FIFO
    for p in unit.replaceIter():
        print(p)

    # LRU
    unit.mode= 'LRU'
    for p in unit.replaceIter():
        print(p)

    # LFU
    unit.mode= 'LFU'
    for p in unit.replaceIter():
        print(p)






