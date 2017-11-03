from collections import defaultdict
from core import Packet, Unit


class ExampleInfoUnit(Unit):
    def __init__(self):
        self.pit= defaultdict(set)  # {name:set(face_id), ...}

    def install(self, announces, api):
        super().install(announces, api)
        announces['inPacket'].append(self.inPacket)
        announces['outPacket'].append(self.outPacket)

        self.api['Info.getPendIds']= self.getPindIds

    def inPacket(self, face_id, packet):
        if packet.type == Packet.INTEREST:
            self.pit[packet.name].add(face_id)

    def outPacket(self, face_id, packet):
        if packet.type == Packet.DATA:
            self.pit[packet.name].discard(face_id)

    def getPindIds(self, packet):
        # 必须新构造set, 以使得出现 RuntimeError"Set changed size during iteration"
        return set( self.pit[packet.name] )
















