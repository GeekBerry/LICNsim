from core import Unit, NameTable


class ContentStore(Unit):
    def __init__(self, capacity=10000):
        self.capacity = capacity
        self.size = 0  # 已经占用的尺寸 0<= size <= capacity
        self.table = NameTable()

    def install(self, announces, api):
        super().install(announces, api)
        api['CS.size'] = lambda: self.size
        api['CS.store'] = self.store
        api['CS.insert'] = self.insert
        api['CS.match'] = self.match
        api['CS.discard'] = self.discard
        self.replace_iter = api['Replace.replaceIter']

    def store(self, packet):
        """
        :param packet: 数据包
        :return:
        """
        assert packet.size <= self.capacity
        if packet.name not in self.table:
            self.limit(self.capacity - packet.size)  # 腾出足够空间
            self.insert(packet)  # 插入
        else:  # 重复
            pass

    def match(self, packet):  # TODO 多项匹配, 条件匹配
        """
        :param packet: 兴趣包
        :return: Packet 数据包
        """
        data = self.table.get(packet.name)  # 完全匹配法
        if data is not None:
            data = data.fission()  # 构造一个新的包
            self.announces['csHit'](data)
            return data
        else:
            self.announces['csMiss'](packet)
            return None

    # -------------------------------------------------------------------------
    def insert(self, packet):
        self.table[packet.name] = packet
        self.size += packet.size
        self.announces['csStore'](packet)
        assert self.size <= self.capacity

    def discard(self, name):
        try:
            packet = self.table.pop(name)
        except KeyError:
            return
        else:
            self.size -= packet.size
            self.announces['csEvict'](packet)

    def limit(self, max_size):
        if self.size <= max_size:
            return

        name_iter = self.replace_iter()
        while self.size > max_size:
            self.discard(next(name_iter))






















