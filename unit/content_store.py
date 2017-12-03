from core import Unit, NameTable, Packet


class ContentStore(Unit):
    def __init__(self, capacity=10000):
        self._capacity = capacity
        self.size = 0  # 已经占用的尺寸 0<= size <= _capacity
        self.table = NameTable()

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        assert 0 < value
        self.limit(value)
        self._capacity= value

    def install(self, announces, api):
        super().install(announces, api)
        api['CS.size'] = lambda: self.size
        api['CS.store'] = self.store
        api['CS.insert'] = self.insert
        api['CS.match'] = self.match
        api['CS.discard'] = self.discard
        self.replace_iter = api['Replace.replaceIter']

    def store(self, data):
        """
        :param data: 数据包
        :return:
        """

        if data.size > self._capacity:
            return False  # 包过大, 不能插入

        if data.name in self.table:
            return False  # 重名包, 不再插入或覆盖  TODO 交给用户选择覆盖还是丢弃

        self.limit(self._capacity - data.size)  # 腾出足够空间
        data= data.fission()  # XXX 是否需要构造一个新的包
        self.insert(data)  # 插入

    def match(self, packet):  # TODO 多项匹配, 条件匹配
        """
        :param packet: 兴趣包
        :return: Packet 数据包
        """
        data = self.table.get(packet.name)  # 完全匹配法
        if data is not None:
            # data = data.fission()  XXX 是否需要构造一个新的包
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
        assert self.size <= self._capacity

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






















