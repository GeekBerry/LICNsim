from collections import defaultdict
from core import Packet, Unit, clock


class IOInfoUnit(Unit):
    def __init__(self):
        self.pit = defaultdict(set)  # {name:set(face_id,...), ...}

    def install(self, announces, api):
        super().install(announces, api)
        announces['inPacket'].append(self.inPacket)
        announces['outPacket'].append(self.outPacket)
        self.api['Info.getPendIds'] = self.getPindIds

    def uninstall(self, announces, api):
        del api['Info.getPendIds']
        announces['outPacket'].discard(self.outPacket)
        announces['inPacket'].discard(self.inPacket)
        super().uninstall(announces, api)

    def inPacket(self, face_id, packet):
        if packet.type is Packet.INTEREST:
            self.pit[packet.name].add(face_id)

    def outPacket(self, face_id, packet):
        if packet.type is Packet.DATA:
            self.pit[packet.name].discard(face_id)
            if not self.pit[packet.name]:
                del self.pit[packet.name]

    def getPindIds(self, packet) -> set:
        if packet.name in self.pit:
            # 必须新构造set, 以免Forwarder查表过程中对表进行操作，出现 RuntimeError"Set changed size during iteration"
            return set(self.pit[packet.name])
        else:
            return set()