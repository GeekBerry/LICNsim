from core import Hardware
from unit import *
from experiment import *

from unit.content_store import ContentStore
from experiment.content_store import LCDContentStore, LCPContentStore


class RouteNode(Hardware):
    def __init__(self, node_id, cs_unit, evict_unit):
        super().__init__(node_id)

        self.install('cs', cs_unit)
        # self.install('replace', ReplaceUnit('FIFO'))
        self.install('evict', evict_unit)

        self.install('face', FaceUnit())
        self.install('app', StoreTrackAppUnit())
        self.install('info', InfoUnit())  # 必须安装在ForwardUnit前, info先行处理inPack信号
        self.install('forward', StoreTrackForwardUnit())

        self.api['Node.getId']= self.getId

        self.insert = self.api['CS.insert']
        self.ask = self.api['App.ask']
        self.setInChannel = self.api['Face.setInChannel']
        self.setOutChannel = self.api['Face.setOutChannel']
        self.setEvictMode= self.api['Evict.setMode']


# def NodeFactor(cs_life_time, cs_mode):
#     def factor(node_id):
#         node= RouteNode(node_id, cs_life_time, cs_mode)
#         return node
#     return factor


class OuterNode(Hardware):
    def __init__(self, node_id, cs_unit, evict_unit):
        super().__init__(node_id)

        self.install('cs', cs_unit)
        # self.install('replace', ReplaceUnit('FIFO'))
        self.install('evict', evict_unit)

        self.install('face', FaceUnit())
        self.install('app', StoreTrackAppUnit())
        self.install('info', InfoUnit())  # 必须安装在ForwardUnit前, info先行处理inPack信号
        self.install('forward', StoreTrackForwardUnit())

        self.api['Node.getId']= self.getId

        self.insert = self.api['CS.insert']
        self.ask = self.api['App.ask']
        self.setInChannel = self.api['Face.setInChannel']
        self.setOutChannel = self.api['Face.setOutChannel']
        self.setEvictMode= self.api['Evict.setMode']


def NodeFactor(**kwargs):
    def factor(node_id):
        if kwargs['cs_type'] == 'LCE':
            cs_unit= ContentStore()
        elif kwargs['cs_type'] == 'LCD':
            cs_unit= LCDContentStore()
        elif kwargs['cs_type'] == 'LCP':
            cs_unit= LCPContentStore( kwargs['p'] )
        else:
            raise ValueError()

        node= RouteNode(node_id, cs_unit, CSEvictUnit(kwargs['cs_time'], kwargs['evict_mode']) )
        return node
    return factor

