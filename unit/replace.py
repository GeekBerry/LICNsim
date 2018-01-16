from core import DataBaseTable, Unit, clock


class ReplaceUnit(Unit):
    def __init__(self, field='c_time'):
        self.db_table= DataBaseTable().create('name', c_time= None, a_time= None, a_count=0)
        self.db_table.createIndexs('c_time', 'a_time', 'a_count')
        self._field = field

    def install(self, announces, api):
        super().install(announces, api)
        announces['csStore'].append(self.storeEvent)
        announces['csEvict'].append(self.evictEvent)
        announces['csHit'].append(self.hitEvent)
        announces['csMiss'].append(self.missEvent)
        api['Replace.replaceIter']= self.replaceIter

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, value):
        assert value in self.db_table.getIndicesFields()  # XXX 必须是索引项
        self._field = value

    # -------------------------------------------------------------------------
    def storeEvent(self, packet):
        cur_time= clock.time
        self.db_table[packet.name]= {'c_time':cur_time, 'a_time':cur_time, 'a_count':1}

    def evictEvent(self, packet):
        del self.db_table[packet.name]

    def hitEvent(self, packet):
        self.db_table[packet.name]['a_time']= clock.time
        self.db_table[packet.name]['a_count'] += 1

    def missEvent(self, packet):
        pass

    # -------------------------------------------------------------------------
    def replaceIter(self):
        for record in self.db_table.minIter(self._field):
            yield record['name']


if __name__ == '__main__':
    unit= ReplaceUnit('c_time')

    from core import Packet, Name
    p1 = Packet(Name('A/1'), 1, Packet.DATA)
    p2 = Packet(Name('A/2'), 1, Packet.DATA)
    p3 = Packet(Name('A/3'), 1, Packet.DATA)

    unit.storeEvent(p1)
    clock.step()

    unit.storeEvent(p2)
    clock.step()

    unit.storeEvent(p3)
    clock.step()

    unit.hitEvent(p1)
    unit.hitEvent(p1)
    unit.hitEvent(p2)

    unit.field= 'c_time'
    print('\nFIFO')
    for p in unit.replaceIter():
        print(p)  # 1,2,3

    unit.field= 'a_time'
    print('\nLRU')
    for p in unit.replaceIter():
        print(p)  # 3,1,2

    unit.field= 'a_count'
    print('\nLFU')
    for p in unit.replaceIter():
        print(p)  # 3,2,1






