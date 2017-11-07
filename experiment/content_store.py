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
    def match(self, packet):  # TODO 多项匹配, 条件匹配
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
