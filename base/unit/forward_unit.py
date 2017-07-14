from base.core import Packet
from common import Unit


class ForwarderUnitBase(Unit):
    def install(self, announces, api):
        super().install(announces, api)
        # 监听的Announce
        announces['inPacket'].append(self.inPacket)
        # 调用的 API

    def inPacket(self, face_id, packet):
        if packet.type == Packet.INTEREST:
            self.inInterest(face_id, packet)
        elif packet.type == Packet.DATA:
            self.inData(face_id, packet)
        else:pass

    def inInterest(self, face_id, packet):
        pass

    def inData(self, face_id, packet):
        pass


