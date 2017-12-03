from core import Hardware
from unit import *


class NodeBase(Hardware):
    def __init__(self):
        """
        :param pos: 位置 (x,y)
        """
        super().__init__()
        # self.pos = (0,0)


class ExampleNode(NodeBase):
    def __init__(self):
        super().__init__()
        self.install('face', FaceUnit(nonce_life_time=100_000))
        self.install('app', AppUnit())  # 必须安装在FaceUnit后, 才能建立APPChannel

        self.install('cs', ContentStore(capacity=10000))
        self.install('replace', ReplaceUnit(mode='FIFO'))
        self.install('evict', CSEvictUnit(life_time=20, mode='FIFO'))

        self.install('info', InfoUnit())  # 安装在 ForwardUnit 前, InfoUnit 才能先行处理 inPack 信号
        self.install('forward', GuidedForwardUnit())

        self.store = self.api['CS.store']
        self.ask = self.api['App.ask']



class ClientNodeBase(ExampleNode):
    pass


class RouterNodeBase(ExampleNode):
    pass


class ServerNodeBase(ExampleNode):
    pass