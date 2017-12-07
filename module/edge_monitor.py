from collections import defaultdict

from core import clock
from module import ModuleBase


class EdgeMonitor(ModuleBase):
    class Record:
        def __init__(self):
            self.send_rate = 0
            self.send_size = 0

        def sendOccupy(self):
            try:
                occupy = self.send_size / (self.send_rate * clock.time())  # XXX 不能应对rate变化的情况
            except ZeroDivisionError:
                return 0.0
            else:
                return min(occupy, 1.0)  # 由于send_size统计全部已发送尺寸, 因此计算出occupy有可能大于1.0

    def __init__(self):
        self.edge_table = defaultdict(self.Record)

    def setup(self, sim):
        sim.loadEdgeAnnounce('send', self._sendEvent)
        sim.api['EdgeMonitor.table'] = lambda: self.edge_table
        self.getEdgeRate= lambda edge_id: sim.edge(edge_id).rate

    def _sendEvent(self, edge_id, packet):
        record = self.edge_table[edge_id]
        record.send_rate = self.getEdgeRate(edge_id)  # 有必要每次做更新吗
        record.send_size += packet.size