# python3.6
# coding=utf-8

# ======================================================================================================================
from debug import showCall
from base.core import top


def exactMatchSelector(packet, data_iter):
    # XXX data_packets 是先根序遍历的, 如果第一个名字不匹配, 后续更不可能匹配, 所以在此中断
    data = top(data_iter)
    if (data is not None) and (packet.name == data.name):
        return data
    else:
        return None

def anyMatchSelector(packet, data_iter):
    for data in data_iter:
        return data
    return None


# ======================================================================================================================
from common import Unit
from base.core import NameTable, clock


class ContentStoreUnit(Unit):
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0  # 已经占用的尺寸 0<= size <= capacity
        self.table = NameTable()

    # -------------------------------------------------------------------------
    def install(self, announces, api):
        super().install(announces, api)
        api['CS.store'] = self.store
        api['CS.match'] = self.match

    def setCapacity(self, value):
        assert value >= 0
        self.limit(value)
        self.capacity = value

    # -------------------------------------------------------------------------
    def store(self, packet):
        if packet.size > self.capacity:
            # raise Exception('包尺寸大于CS容量')
            return False

        if self.isCoverOrStore(packet):
            self.discard(packet.name)
            self.limit(self.capacity - packet.size)  # 腾出足够空间
            self.insert(packet)  # 插入

        return True

    def match(self, packet, selector=exactMatchSelector):  # TODO 多项匹配, 条件匹配
        """
        :param packet: 兴趣包
        :param selector: callable( iter(Packet) ) -> Packet or None
        :return: Packet 数据包
        """
        data_iter = self.table.descendantValues(packet.name)
        data = selector(packet, data_iter)

        if data is not None:
            data= data.fission()  # 构造一个新的包
            self.announces['csHit'](data)
            return data
        else:
            self.announces['csMiss'](packet)
            return None

    # -------------------------------------------------------------------------
    def isCoverOrStore(self, packet):
        old_data = self.table.get(packet.name)
        if old_data is None:
            return True  # isStore
        else:
            return self.api['Replace.isCover'](old_data, packet)

    def limit(self, max_size):
        name_iter = self.api['Replace.replaces']()
        while self.size > max_size:
            self.discard(next(name_iter))

    # -------------------------------------------------------------------------
    def insert(self, packet):
        self.table[packet.name]= packet
        self.size += packet.size
        self.announces['csStore'](packet)

    def discard(self, name):
        try:
            packet = self.table.pop(name)
        except KeyError:
            return
        else:
            self.size -= packet.size
            self.announces['csEvict'](packet)

    def print(self):
        print('\n', self.size, '/', self.capacity)
        print(self.table)


# 对于布局文件参数的设置
def unfoldContentStore(cs_unit):
    for name, packet in cs_unit.table.items():
        yield name, packet.typeStr(), hex(packet.nonce), packet.size


ContentStoreUnit.UI_ATTRS= {
    'Capacity':{
        'type':'Int',
        'range':(0, 99999999),
        'getter': lambda obj: obj.capacity,
        'setter': lambda obj, value: ContentStoreUnit.setCapacity(obj, value)
    },

    'Size':{
        'type':'Label',
        'getter': lambda obj: obj.size,
    },

    'Table':{
        'type':'Table',
        'range': ('Name', 'Packet', 'Nonce', 'Size'),
        'getter': unfoldContentStore,
    }
}


# ======================================================================================================================
# TODO 重新实现或者遗弃
# import constants
# from core.data_structure import TimeDictDecorator
# class SimulatCSUnit(ContentStoreUnit):
#     """
#     模拟一个繁忙的CS, 即数据包插入后一段时间就会被'替换'
#     有两种替换模式(FIFO, LRU),默认为不替换(MANUAL)
#     """
#     class MODE:
#         MANUAL, FIFO, LRU= 0, 1, 2
#
#     def __init__(self, capacity, life_time):
#         super().__init__(capacity)
#         self.table= TimeDictDecorator(self.table, life_time)  # 对时间进行限制
#         self.table.evict_callback= self._evict
#
#     def install(self, announces, api):
#         super().install(announces, api)
#         api['CS.setMode']= self.setMode
#         api['CS.setLifeTime']= self.setLifeTime
#
#     def setMode(self, mode):
#         if mode == self.MODE.MANUAL: self.table.life_time= constants.INF
#         elif mode == self.MODE.FIFO: self.table.get_refresh= False
#         elif mode == self.MODE.LRU:  pass
#         else: pass
#
#     def setLifeTime(self, life_time):
#         self.table.life_time= life_time


# if __name__ == '__main__':
#     from core.clock import clock
#     cs= SimulatCSUnit(10, life_time= 2)
#
#     cs.mode= SimulatCSUnit.MODE.FIFO
#
#     cs.store(debug_dp)
#     cs.store(debug_dp1)
#     clock.step()
#     print(cs.table)
#
#     cs.match(debug_dp)
#     clock.step()
#     print(cs.table)
#
#     clock.step()
#     print(cs.table)
#
#     clock.step()
#     print(cs.table)
