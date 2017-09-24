from common import Hardware
from module import *

import networkx


class Simulator(Hardware):
    def __init__(self):
        super().__init__('')
        self.install('topology', TopologyModule())
        self.install('icn_net', ICNNetModule())
        self.install('hub', HubModule())
        self.install('database', DataBaseModule())
        self.install('monitor', MonitorModule())  # 与 database 不同, 用 monitor 执行实时的, 不需储存的监控行为
        self.install('gui', GUIModule())

        self.graph= None

    def addNode(self, NodeFactory)->int:
        return self.api['ICNNet.createNode'](NodeFactory)

    def addEdge(self, src_id, dst_id, ChannelFactory):
        return self.api['ICNNet.addEdge'](src_id, dst_id, ChannelFactory)



from base.node import NodeBase
from base.unit.content_store_unit import ContentStoreUnit
from base.unit.face_unit import FaceUnit, RepeatChecker, LoopChecker
from base.unit.io_info_unit import IOInfoUnit
from base.unit.replace_unit import ReplaceUnit

class Node(NodeBase):
    def __init__(self, node_id):
        super().__init__(node_id)

        self.install('cs',      ContentStoreUnit(capacity=64_000))
        self.install('replace', ReplaceUnit() )
        self.install('info',    IOInfoUnit(max_size= 100, life_time= 16_000))  # IOInfoUnit 必须在 ForwarderUnit 之前安装
        self.install('faces',   FaceUnit( LoopChecker(10_0000), RepeatChecker() )  )

from base.channel import PerfectChannel

if __name__ == '__main__':
    sim= Simulator()
    node1= sim.addNode(Node)
    node2= sim.addNode(Node)
    p= sim.addEdge(node1, node2, PerfectChannel)
    print(node1, node2, p)

