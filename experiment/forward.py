from unit import ForwardUnitBase


class StoreTrackForwardUnit(ForwardUnitBase):
    def install(self, announces, api):
        super().install(announces, api)
        self.getPendIds= self.api['Info.getPendIds']
        self.sends = self.api['Face.sends']
        self.matchCS= self.api['CS.match']
        self.storeCS= self.api['CS.store']

    def inInterest(self, face_id, packet):
        data = self.matchCS(packet)
        if data is not None:  # hit
            pend_ids = self.getPendIds(data)
            assert face_id in pend_ids
            self.sends(pend_ids, data)
        else:  # miss
            if hasattr(packet, 'path') and len(packet.path) > 0:
                next_id, *packet.path = packet.path
                self.sends([next_id], packet)
            else:
                self.announces['askMiss'](packet)
                pass # XXX path 无效, 或者为空

    def inData(self, face_id, data):
        # 所有数据包一律储存
        self.storeCS(data)  # 必须先调用 storeCS 以便对数据进行处理
        # 向 pending 接口发送回应
        pend_ids = self.getPendIds(data)
        pend_ids.discard(face_id)
        self.sends(pend_ids, data)
