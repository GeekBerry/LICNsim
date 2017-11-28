import random
from unit import ContentStore


class LCPContentStore(ContentStore):
    def __init__(self, probability):
        super().__init__()
        self.probability = probability

    def store(self, data):
        if random.random() < self.probability:
            super().store(data)
        else:
            self.announces['csStoreReject'](data)


class LCDContentStore(ContentStore):
    """
    Leave Copy Down 实现思路
    在数据包被 match 时,为数据包添加'store'域;
    在数据包被储存时如果有'store', 说明数据包第一次被储存, 删除'store'标记后储存,否则不予储存
    """
    def match(self, packet):
        data = super().match(packet)
        if data is not None:
            setattr(data, 'store', True)
        return data

    def store(self, data):
        if hasattr(data, 'store'):
            delattr(data, 'store')
            super().store(data)
        else:
            self.announces['csStoreReject'](data)
