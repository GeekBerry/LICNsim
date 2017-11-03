from core import Packet, Unit


class ExampleForwardUnit(Unit):  # 洪泛
    def install(self, announces, api):
        super().install(announces, api)
        # 监听的Announce
        announces['inPacket'].append(self.inPacket)
        # 调用的 API
        self.getPendIds= self.api['Info.getPendIds']
        self.sends = self.api['Face.sends']
        self.getOutFaceIds= self.api['Face.getOutFaceIds']
        self.matchCS= self.api['CS.match']
        self.storeCS= self.api['CS.store']

    def inPacket(self, face_id, packet):
        if packet.type == Packet.INTEREST:
            self.inInterest(face_id, packet)
        elif packet.type == Packet.DATA:
            self.inData(face_id, packet)
        else:
            pass

    def inInterest(self, face_id, packet):
        data= self.matchCS(packet)

        if data is not None:  # hit
            pend_ids = self.getPendIds(data)
            assert face_id in pend_ids
            self.sends(pend_ids, data)
        else:  # miss
            out_ids= self.getOutFaceIds()  # 所有可以发送 face_id
            out_ids.discard(face_id)
            self.sends(out_ids, packet)  # 洪泛

    def inData(self, face_id, data):
        # 所有数据包一律储存
        self.storeCS(data)  # 必须先调用 storeCS 以便对数据进行处理

        # 向 pending 接口发送回应
        pend_ids = self.getPendIds(data)
        pend_ids.discard(face_id)
        self.sends(pend_ids, data)





