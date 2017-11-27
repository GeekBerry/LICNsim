import random
from config import POS_SCALE
from core import Hardware
from unit import *


class NodeBase(Hardware):
    def __init__(self, node_id:int, name=None, pos=None):
        """
        :param node_id: int 唯一标识符，类似MAC地址作用
        :param name: str 节点显示名字
        :param pos: 位置 (x,y) 其中 x 和 y 数量级在 [-1.0,1.0] 为合适
        """
        if name is None:
            name= f'{self.__class__.__name__}({node_id})'

        if pos is None:
            pos= random.randint(-POS_SCALE,POS_SCALE), random.randint(-POS_SCALE,POS_SCALE)

        super().__init__()
        self.__node_id= node_id
        self.name= name
        self.pos = pos

    @property
    def node_id(self):
        return self.__node_id


class ExampleNode(NodeBase):
    def __init__(self, node_id=None):
        super().__init__(node_id)

        self.install('cs', ContentStore())
        self.install('replace', ReplaceUnit('FIFO'))
        self.install('face', FaceUnit())
        self.install('app', ExampleAppUnit())
        self.install('info', InfoUnit())  # 必须安装在ForwardUnit前, info先行处理inPack信号
        self.install('forward', ForwardUnit())

        self.api['Node.getId']= lambda :self.node_id

        self.store = self.api['CS.store']
        self.ask = self.api['App.ask']
        self.setInChannel = self.api['Face.setInChannel']
        self.setOutChannel = self.api['Face.setOutChannel']





