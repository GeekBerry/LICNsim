from core import Packet, Unit, INF


class ForwardUnitBase(Unit):
    """
                        / hitEvent
            / inInterest
    inPacket            \ missEvent
            \ inData
    """

    def __init__(self, rate=1, capacity=INF):
        # self.bucket = LeakBucket(rate, capacity)
        pass

    def install(self, announces, api):
        super().install(announces, api)
        announces['inPacket'].append(self.inPacket)

    def inPacket(self, face_id, packet):
        if packet.type is Packet.INTEREST:
            self.inInterest(face_id, packet)
        elif packet.type is Packet.DATA:
            self.inData(face_id, packet)
        else:
            pass  # 类型不明

    def inInterest(self, face_id, packet):
        data = self.api['CS.match'](packet)
        if data is not None:
            self.hitEvent(face_id, data)
        else:
            self.missEvent(face_id, packet)

    def hitEvent(self, face_id, data):
        pend_ids = self.api['Info.getPendIds'](data)
        pend_ids.add(face_id)
        self.api['Face.sends'](pend_ids, data)

    @NotImplementedError
    def missEvent(self, face_id, packet):
        pass

    def inData(self, face_id, data):
        pend_ids = self.api['Info.getPendIds'](data)
        pend_ids.discard(face_id)
        if pend_ids:
            self.api['Face.sends'](pend_ids, data)  # 向 pending 接口发送回应
            self.api['CS.store'](data)


class FloodForwardUnit(ForwardUnitBase):
    def missEvent(self, face_id, packet):
        out_ids = self.api['Face.getOutFaceIds']()  # 所有可以发送 face_id
        out_ids.discard(face_id)
        self.api['Face.sends'](out_ids, packet)


class ShortestForwardUnit(ForwardUnitBase):
    def missEvent(self, face_id, packet):
        fwd_id = self.api['Track.getForwardFace'](packet.name)
        if fwd_id is not None:
            self.api['Face.sends']([fwd_id], packet)


class GuidedForwardUnit(ForwardUnitBase):
    def missEvent(self, face_id, packet):
        try:
            fwd_id = packet.path.pop(0)
        except IndexError:  # 没找到目标点，但 path 为空
            pass  # 直接丢弃
        else:
            self.api['Face.sends']([fwd_id], packet)
