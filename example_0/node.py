# coding=utf-8

from base.node import NodeBase
from base.unit.content_store_unit import ContentStoreUnit
from base.unit.face_unit import FaceUnit, RepeatChecker, LoopChecker
from base.unit.io_info_unit import IOInfoUnit
from base.unit.replace_unit import ReplaceUnit
from example_0.app_unit import *
from example_0.forward_unit import *
from example_0.generate_unit import *


class ServerNode(NodeBase):
    def __init__(self, node_id):
        NodeBase.__init__(self, node_id)

        self.install('replace', ReplaceUnit() )
        self.install('cs',      ContentStoreUnit(capacity=64_000))

        self.install('info',    IOInfoUnit(max_size= 100, life_time= 16_000))  # IOInfoUnit 必须在 ForwarderUnit 之前安装
        self.install('fwd',     ServerForwarderUnit() )

        self.install('faces',   FaceUnit( LoopChecker(10_0000), RepeatChecker() )  )
        self.install('app',     AppUnitBase() )

        self.install( 'generate', ServerGenerateUnit() )


class RouterNode(NodeBase):
    def __init__(self, node_id):
        NodeBase.__init__(self, node_id)

        self.install('replace', ReplaceUnit() )
        self.install('cs',      ContentStoreUnit(capacity=64_000))

        self.install('info',    IOInfoUnit(max_size= 100, life_time= 16_000))  # IOInfoUnit 必须在 ForwarderUnit 之前安装
        self.install('fwd',     RouterForwarderUnit() )

        self.install('faces',   FaceUnit( LoopChecker(10_0000), RepeatChecker() )  )


class ClientNode(NodeBase):
    def __init__(self, node_id):
        NodeBase.__init__(self, node_id)

        self.install('info',    IOInfoUnit(max_size= 100, life_time= 16_000))
        self.install('fwd',     ClientForwarderUnit() )

        self.install('faces',   FaceUnit( LoopChecker(10_000), RepeatChecker() )  )
        self.install('app',     ClientAppUnit(keep_time=16_000, repeate_time=4_000))

        self.install( 'generate', ClientGenerateUnit(delta=12_000) )
