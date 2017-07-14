from base.core import DataBaseTable
from core import clock
from common import Unit

from debug import showCall


class ReplaceUnitBase(Unit):
    def __init__(self, replace_iter):
        self.replace_iter= replace_iter

    def install(self, announces, api):
        super().install(announces, api)
        announces['csStore'].append(self.store)
        announces['csEvict'].append(self.evict)
        announces['csHit'].append(self.hit)
        announces['csMiss'].append(self.miss)

        api['Replace.setReplaceIter']= self.setReplaceIter
        api['Replace.replaces']= lambda :self.replace_iter(self)  # 绑定self 到 replaceIter 中
        api['Replace.isCover']= self.isCover

    # -------------------------------------------------------------------------
    @showCall
    def setReplaceIter(self, replace_iter):
        self.replace_iter= replace_iter

    def store(self, packet):pass

    def hit(self, packet):pass

    def miss(self, packet):pass

    def evict(self, packet):pass

    def isCover(self, old_packet, new_packet):
        raise NotImplementedError


# ======================================================================================================================
class ReplaceUnit(ReplaceUnitBase):
    @staticmethod
    def replaceFIFO(replace_unit):
        for record in replace_unit.db_table.minIter('c_time'):
            yield record['name']

    @staticmethod
    def replaceLRU(replace_unit):
        for record in replace_unit.db_table.minIter('a_time'):
            yield record['name']

    # -------------------------------------------------------------------------
    def __init__(self, replace_iter= None):
        if replace_iter is None:
            replace_iter= ReplaceUnit.replaceFIFO
        super().__init__(replace_iter)

        self.db_table= DataBaseTable().create('name', c_time=None, a_time=None)
        self.db_table.createIndexs('c_time', 'a_time')

    def install(self, announces, api):
        super().install(announces, api)
        api['Replace.setIsCover']= lambda is_cover_decider: self.__setattr__('isCover', is_cover_decider)

    def store(self, packet):
        cur_time= clock.time()
        self.db_table[packet.name]= {'c_time':cur_time, 'a_time':cur_time}

    def hit(self, packet):
        self.db_table[packet.name]['a_time']= clock.time()

    def evict(self, packet):
        del self.db_table[packet.name]

    def isCover(self, old_packet, new_packet):
        return False


ReplaceUnit.UI_ATTRS= {
    'Func':{
        'type':'ComboBox',
        'range': {
            ReplaceUnit.replaceFIFO.__name__: ReplaceUnit.replaceFIFO,
            ReplaceUnit.replaceLRU.__name__: ReplaceUnit.replaceLRU
        },
        'getter': lambda replace_unit: (replace_unit.replace_iter.__name__, replace_unit.replace_iter),
        'setter': ReplaceUnit.setReplaceIter
    },

    'Table':{
        'type':'Table',
        'range': ('Name', 'CreateTime', 'AccessTime'),
        'getter': lambda replace_unit: map( lambda record:(record['name'], record['c_time'], record['a_time']), replace_unit.db_table.query() )
    }
}


# ======================================================================================================================
class ExampleExtendReplaceUnit(ReplaceUnit):  # 此例子展示了如何在 DataBaseTable 框架下扩展 ReplaceUnit, 新增 LFU 替换策略
    @staticmethod
    def replaceLFU(replace_unit):
        for record in replace_unit.db_table.minIter('a_count'):
            yield record['name']

    def __init__(self):
        super().__init__()
        self.db_table.addFields(a_count=0)
        self.db_table.createIndexs('a_count')  # 不建立索引无法使用 minIter

    def hit(self, packet):
        super().hit(packet)
        self.db_table[packet.name]['a_count']+= 1  # 命中一次, 判定为使用一次; 也可对 miss 进行统计


# ----------------------------------------------------------------------------------------------------------------------
import random

def replaceRealRandomExample(replace_unit):
    assert isinstance(replace_unit, ExampleRandomReplaceUnit)
    names= list(replace_unit.name_set)
    random.shuffle(names)
    return iter(names)


class ExampleRandomReplaceUnit(ReplaceUnitBase):  # 此例展示了放弃 ReplaceUnit, 如何实现全新替换单元;  当然也可将扩展集成到 ReplaceUnit 子类中
    @staticmethod
    def replaceRandom(replace_unit):
        for name in replace_unit.name_set:  # XXX 依靠的是 set hash 存放的随机性
            yield name

    def __init__(self):
        super().__init__(replaceRealRandomExample)
        self.name_set= set()

    def store(self, packet):
        self.name_set.add(packet.name)

    def evict(self, packet):
        self.name_set.discard(packet.name)

    def isCover(self, old_packet, new_packet):
        return new_packet.size > old_packet.size  # 择大储存




