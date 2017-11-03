from core import Packet, Unit


class ExampleAppUnit(Unit):
    APP_LAYER_FACE_ID = 'application'
    receiver = None  # 回调接受者

    def install(self, announces, api):
        super().install(announces, api)

        # AppUnit.receiver(packet) => Face.receive(APP_LAYER_FACE_ID, packet)
        api['Face.setInChannel'](self.APP_LAYER_FACE_ID,  self)

        # Face.send(APP_LAYER_FACE_ID, packet) => AppUnit.send(packet)
        api['Face.setOutChannel'](self.APP_LAYER_FACE_ID, self)

        api['App.ask'] = self.ask
        api['App.respond'] = self.send

    def ask(self, packet):
        assert packet.type == Packet.INTEREST
        assert self.receiver is not None
        self.announces['ask'](packet)
        self.receiver(packet)

    def send(self, packet):
        self.announces['respond'](packet)


