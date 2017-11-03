from core import Packet
from unit import ExampleAppUnit


class StoreTrackAppUnit(ExampleAppUnit):
    def install(self, announces, api):
        super().install(announces, api)

    def ask(self, packet):
        if self.makePacketPath(packet):
            super().ask(packet)

    def makePacketPath(self, packet):
        path = self.api['getStorePath']()
        if path:  # is not None  and  len(path)>0
            node_id, *path = path
            setattr(packet, 'path', path)
            self.announces['askDistance'](packet, len(path))
            return True
        else:  # 否则证明网络中无CS
            self.announces['askFailed'](packet)
            return False
