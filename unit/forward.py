from core import Packet, Unit, LeakBucket, INF, Bind
from unit import APP_LAYER_FACE_ID


class ForwardUnitBase(Unit):
    def __init__(self, rate=1, capacity=INF):
        self.bucket = LeakBucket(rate, capacity)

    def install(self, announces, api):
        super().install(announces, api)
        api['Forward.getRate']= self.getRate
        announces['inPacket'].append(self.inPacket)
        self.bucket.pop = self.switchPacket
        self.bucket.overflow = announces['overflow']  # 溢出信号

    def getRate(self):
        return self.bucket.rate

    def inPacket(self, face_id, packet):
        args= face_id, packet
        self.bucket.append(args, size=1)

    def switchPacket(self, args):
        face_id, packet= args
        if packet.type is Packet.INTEREST:
            self.inInterest(face_id, packet)
        elif packet.type is Packet.DATA:
            self.inData(face_id, packet)
        else:
            pass

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

    def missEvent(self, face_id, packet):  # 洪泛
        out_ids = self.api['Face.getOutFaceIds']()  # 所有可以发送 face_id
        out_ids.discard(face_id)
        self.api['Face.sends'](out_ids, packet)

    def inData(self, face_id, data):
        pend_ids = self.api['Info.getPendIds'](data)
        pend_ids.discard(face_id)
        if pend_ids:
            self.api['Face.sends'](pend_ids, data)  # 向 pending 接口发送回应
            self.api['CS.store'](data)


class GuidedForwardUnit(ForwardUnitBase):
    def missEvent(self, face_id, packet):
        fwd_id = self.api['Guide.getForwardFace'](packet)
        if fwd_id is not None:
            self.api['Face.sends']([fwd_id], packet)
