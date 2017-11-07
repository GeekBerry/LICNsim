from collections import defaultdict
from core import Hardware
from unit import *


class ExampleNode(Hardware):
    def __init__(self, node_id=None):
        super().__init__(node_id)

        self.anno_map= defaultdict(set)

        self.install('cs', ContentStore())
        self.install('replace', ReplaceUnit('FIFO'))
        self.install('face', FaceUnit())
        self.install('app', ExampleAppUnit())
        self.install('info', InfoUnit())  # 必须安装在ForwardUnit前, info先行处理inPack信号
        self.install('forward', ForwardUnit())

        self.api['Node.getId']= self.getId

        self.store = self.api['CS.store']
        self.ask = self.api['App.ask']
        self.setInChannel = self.api['Face.setInChannel']
        self.setOutChannel = self.api['Face.setOutChannel']





