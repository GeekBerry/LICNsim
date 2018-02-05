import numpy
from core import Hardware, INF
from unit import *


class NodeBase(Hardware):
    def __init__(self):
        super().__init__()
        self.node_type = 'router'
        self.pos = numpy.random.rand(2) * 1000  # 给出一个 (0~1000, 0~1000) 的随机位置信息


def nodeFactory(
        node_type='router',  # enum('server', 'router', 'client')

        recv_rate=1,
        recv_capacity=INF,
        nonce_life_time=100_000,

        cs_capacity=None,
        cs_probability= 1.0,
        replace_mode=None,
        evict_mode=None,  # enum('CONST', 'FIFO', 'LRU', 'GEOMETRIC')
        evict_life_time=None,

        AppType=AppUnit,
        InfoType=IOInfoUnit,
        ForwardType=FloodForwardUnit,
        ContentStoreType= ContentStoreUnit,
):
    MODE_FIELD_MAP = {'FIFO': 'c_time', 'LRU': 'a_time', 'LFU': 'hit_count'}

    def factor():
        node = NodeBase()

        assert node_type in ('server', 'router', 'client')
        node.node_type = node_type

        node.pos = numpy.random.rand(2) * 1000  # 给出一个 (0~1000, 0~1000) 的随机位置信息

        # 配置接口模块
        node.install('face', FaceUnit(rate=recv_rate, capacity=recv_capacity, life_time=nonce_life_time))

        # 配置CS模块
        if cs_capacity is not None:
            node.install('cs', ContentStoreType(capacity=cs_capacity, probability=cs_probability))

        # 配置替换模块
        if replace_mode is not None:
            field = MODE_FIELD_MAP[replace_mode]
            node.install('replace', ReplaceUnit(field))

        # 安装自动驱逐模块
        if evict_mode is not None:
            assert evict_mode in CSEvictUnit.MODE_TYPES
            node.install('evict', CSEvictUnit(mode=evict_mode, life_time=evict_life_time))

        # 安装 应用层模块，信息模块, 转发模块
        node.install('app', AppType())  # 必须安装在FaceUnit后, 才能建立APPChannel
        node.install('info', InfoType())  # 安装在 ForwardUnit 前, InfoUnit 才能先行处理 inPack 信号
        node.install('forward', ForwardType())

        # 添加便捷调用函数
        node.store = node.api['CS.store']
        node.ask = node.api['App.ask']

        return node

    return factor
