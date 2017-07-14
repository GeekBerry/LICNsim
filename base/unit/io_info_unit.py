from debug import showCall
from common import Unit, INF
from base.core import defaultdict, Packet, NameTable, SizeDictDecorator, TimeDictDecorator, DefaultDictDecorator, clock, Bind


class IOInfoUnit(Unit):
    """
    NameTable:
            faceid1     faceid2     ...
    name1   Cell        Cell        ...  每一行为一个 Entry
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
            self.recv = defaultdict(lambda: -INF)  # {Packet.TYPE:life_time, ...}
            self.send = defaultdict(lambda: -INF)  # {Packet.TYPE:life_time, ...}

        def pendPast(self):  # face同时接收到I和D, 该face不算Pending
            if (self.recv[Packet.DATA] < self.recv[Packet.INTEREST]
            and self.send[Packet.DATA] < self.recv[Packet.INTEREST]):
                return clock.time() - self.recv[Packet.INTEREST]  # 返回等待时长
            else:
                return -1  # 非 pending 口

        def forwardedPast(self):  # 返回转发兴趣包等待回应时长
            if (self.send[Packet.DATA] < self.send[Packet.INTEREST]  # 没有再发出数据包
            and self.recv[Packet.DATA] < self.send[Packet.INTEREST]):  # 没有接收到数据包
                return clock.time() - self.send[Packet.INTEREST]  # 返回经历时长
            else:
                return -1  # 非 forward 口

        def receviePast(self):  # 返回接收数据包经历时长
            if (self.send[Packet.DATA] < self.recv[Packet.DATA]  # XXX 这一条件是否必要
            and self.send[Packet.INTEREST] < self.recv[Packet.DATA]
            and self.recv[Packet.INTEREST] < self.recv[Packet.DATA] ):
                return clock.time() - self.recv[Packet.DATA]
            else:
                return -1  # 非 recevie 口

        def respondPast(self):
            if (self.recv[Packet.DATA] < self.send[Packet.DATA]  # XXX 这一条件是否必要
            and self.send[Packet.INTEREST] < self.send[Packet.DATA]  # 没有再发出兴趣包
            and self.recv[Packet.INTEREST] < self.send[Packet.DATA]):  # 没有再接收兴趣包
                return clock.time() - self.send[Packet.DATA]
            else:
                return -1  # 非 respond 口

        def __repr__(self):  # debug
            return f'(recv:{dict(self.recv)}, send:{dict(self.send)})'

    class Entry(defaultdict):
        def __init__(self):
            super().__init__(IOInfoUnit.Cell)
            self.pendingIds=   Bind(self.idFiltAndSort, IOInfoUnit.Cell.pendPast)
            self.forwardedIds= Bind(self.idFiltAndSort, IOInfoUnit.Cell.forwardedPast)
            self.receviedIds=   Bind(self.idFiltAndSort, IOInfoUnit.Cell.receviePast)
            self.respondIds=   Bind(self.idFiltAndSort, IOInfoUnit.Cell.respondPast)

        def idFiltAndSort(self, func)->list:
            past_dict= {face_id: func(cell) for face_id, cell in self.items()}
            pend_ids= filter(lambda face_id: past_dict[face_id] >= 0, self)
            return sorted(pend_ids, key=past_dict.get, reverse= False)

    # =========================================================================
    def __init__(self, max_size, life_time):
        super().__init__()

        self.table = NameTable()
        self.table = SizeDictDecorator(self.table, max_size)  # 进行尺寸限制装饰
        self.table = TimeDictDecorator(self.table, life_time)  # 进行时间限制装饰
        self.table = DefaultDictDecorator(self.table, self.Entry)  # 进行默认参数装饰

    def install(self, announces, api):
        self.table.setSizeEvictCallback( announces['Info.evict'] )
        self.table.setTimeEvictCallback( announces['Info.evict'] )

        super().install(announces, api)
        announces['inPacket'].append(self.inPacket)
        announces['outPacket'].append(self.outPacket)

        api['Info.namePendIds'] = self.namePendIds
        api['Info.prefixPendIds']= self.prefixPendIds
        api['Info.prefixPendDict']= self.prefixPendDict

        api['Info.nameForwardedIds'] = self.nameForwardedIds
        api['Info.prefixForwardedIds']= self.prefixForwardedIds
        api['Info.prefixForwardedDict']= self.prefixForwardedDict

        api['Info.nameReceviedIds']= self.nameReceviedIds
        api['Info.prefixReceviedDict']= self.prefixReceviedDict

    def inPacket(self, face_id, packet):
        self.table[packet.name][face_id].recv[packet.type] = clock.time()

    def outPacket(self, face_id, packet):
        self.table[packet.name][face_id].send[packet.type] = clock.time()

    # -------------------------------------------------------------------------
    def namePendIds(self, name):
        return self.table[name].pendingIds()

    def prefixPendIds(self, name):
        face_ids= []
        for entry in self.table.forebearValues(name):
            face_ids.extend( entry.pendingIds() )
        return face_ids

    def prefixPendDict(self, name):
        return { prefix:entry.pendingIds()
            for prefix, entry in self.table.forebearItems(name)
        }

    # -------------------------------------------------------------------------
    def nameForwardedIds(self, name):
        return self.table[name].forwardedIds()

    def prefixForwardedIds(self, name):
        face_ids= []
        for entry in self.table.forebearValues(name):
            face_ids.extend( entry.forwardedIds() )
        return face_ids

    def prefixForwardedDict(self, name):
        return { prefix:entry.forwardedIds()
            for prefix, entry in self.table.forebearItems(name)
        }

    # -------------------------------------------------------------------------
    def nameReceviedIds(self, name):
        return self.table[name].receviedIds()

    def prefixReceviedDict(self, name):
        return { prefix:entry.receviedIds()
            for prefix, entry in self.table.forebearItems(name)
        }

IOInfoUnit.UI_ATTRS = {
    'LifeTime': {
        'type': 'Int',
        'range': (1, 9999_9999),
        'getter': lambda info_unit: info_unit.table.life_time,
        'setter': lambda info_unit, value: info_unit.table.setLifeTime(value)
    },

    'MaxSize': {
        'type': 'Int',
        'range': (1, 9999_9999),
        'getter': lambda info_unit: info_unit.table.max_size,
        'setter': lambda info_unit, value: info_unit.table.setMaxSize(value)
    },

    'InfoTable':{
        'type':'NameTree',
        'tree': lambda info_unit: info_unit.table.name_tree,
        'range': ('Name', 'Pending', 'Forwarded', 'Recevied', 'Respond'),
        'getter': lambda entry: ( entry.pendingIds(), entry.forwardedIds(), entry.receviedIds(), entry.respondIds() )
    }
}


# if __name__ == '__main__':
#     from base.core import Name
#
#     ip1 = Packet(Name('A/1'), Packet.INTEREST, 1)
#     ip2 = Packet(Name('A/2'), Packet.INTEREST, 1)
#     ip3 = Packet(Name('A/3'), Packet.INTEREST, 1)
#
#     info_unit = IOInfoUnit(2, 4)
#
#     info_unit.inPacket('f1', ip1)
#     info_unit.inPacket('f1', ip2)
#     clock.step()
#     info_unit.inPacket('f2', ip1)
#     clock.step()
#     info_unit.inPacket('f3', ip1)
#     print(info_unit, '\n')
#
#     clock.step()
#     clock.step()
#     print(info_unit, '\n')
#
#     clock.step()
#     print(info_unit, '\n')
#
#     p= info_unit.getPendingIds(Name('A/1'))
#     print(p)
