from unit import ForwardUnit


class StoreTrackForwardUnit(ForwardUnit):
    def install(self, announces, api):
        super().install(announces, api)

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
                pass # FIXME path 无效, 或者为空

