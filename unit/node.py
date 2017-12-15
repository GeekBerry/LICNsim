import numpy
from core import Hardware
from unit import *


class NodeBase(Hardware):
    def __init__(self):
        super().__init__()
        self.node_type = 'router'
        self.pos = (0, 0)


def nodeFactory(
        node_type='router',
        nonce_life_time=100_000,
        cs_capacity=None,
        replace_mode='FIFO',
        evict_mode=None,
        evict_life_time=None,
        ForwardType=ForwardUnitBase,
        forward_rate=1,
        forward_capacity=INF,
):
    def factor():
        node = NodeBase()
        assert node_type in ('server', 'router', 'client')
        node.node_type = node_type

        node.pos = numpy.random.rand(2) * 1000  # 给出一个 (0~1000, 0~1000) 的随机位置信息
        # 安装接口模块和应用层模块
        node.install('face', FaceUnit(nonce_life_time=nonce_life_time))
        node.install('app', AppUnit())  # 必须安装在FaceUnit后, 才能建立APPChannel
        # 安装CS模块和替换模块
        if cs_capacity is not None:
            node.install('cs', ContentStoreUnit(capacity=cs_capacity))
            node.install('replace', ReplaceUnit(mode=replace_mode))
        # 安装自动驱逐模块
        if evict_mode is not None:
            assert evict_mode in CSEvictUnit.MODE_TYPES
            assert evict_life_time is not None
            node.install('evict', CSEvictUnit(life_time=evict_life_time, mode=evict_mode))
        # 安装信息模块和转发模块
        node.install('info', IOInfoUnit())  # 安装在 ForwardUnit 前, InfoUnit 才能先行处理 inPack 信号
        node.install('forward', ForwardType(rate=forward_rate, capacity=forward_capacity))

        node.store = node.api['CS.store']
        node.ask = node.api['App.ask']
        return node

    return factor
