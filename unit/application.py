from core import Packet, Unit
from unit.channel import ChannelBase

APP_LAYER_FACE_ID = 'app_layer'


class AppChannel(ChannelBase):
    def ask(self, packet):  # 由应用层调用向网络层发数据
        self.receiver(packet)  # 向下交付

    def send(self, packet):  # 由网络层调用向应用层发数据
        self.respond(packet)  # 向上交付

    @NotImplementedError
    def respond(self, packet):
        pass


class AppUnit(Unit, AppChannel):  # 一个网络层指向网络层自己的 ChannelBase
    def install(self, announces, api):
        super().install(announces, api)

        # AppChannel.receiver(packet) => Face.receive(APP_LAYER_FACE_ID, packet)
        api['Face.setInChannel'](APP_LAYER_FACE_ID, self)

        # Face.send(APP_LAYER_FACE_ID, packet) => AppChannel.send(packet)
        api['Face.setOutChannel'](APP_LAYER_FACE_ID, self)

        api['App.ask'] = self.ask
        api['App.respond'] = self.respond

    def ask(self, packet):  # 应用层网络层发数据
        assert packet.type is Packet.INTEREST
        self.announces['ask'](packet)
        super().ask(packet)

    def respond(self, packet):  # 网络层向应用层发数据
        self.announces['respond'](packet)


class GuidedAppUnit(AppUnit):
    def ask(self, packet):
        packet.path = self.api['Track.getForwardPath'](packet.name)

        if packet.path is None:
            return  # 没有目标数据源，直接丢弃

        # FIXME 实验中设计的奇怪的距离计算方式，应该放到哪里好？
        if len(packet.path) > 0:
            distance = len(packet.path) - 1
        else:
            distance = 0

        self.announces['distance'](packet, distance)
        super().ask(packet)
