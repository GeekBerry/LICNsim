from core import Packet, Unit
from unit.channel import ChannelBase

APP_LAYER_FACE_ID = 'app_layer'


class AppUnit(Unit):  # 一个网络层指向网络层自己的 ChannelBase
    """
    ------------------+-----------------------+---------------------------
        Application   |       Channel         |            Face
    ------------------+-----------------------+---------------------------
      AppUnit.ask    -|> APPChannel.receiver -|> Face['app_layer'].receive
    AppUnit.respond  <|-   AppChannel.send   <|-  Face['app_layer'].send
    ------------------+-----------------------+---------------------------
    """

    def __init__(self):
        self.app_channel = ChannelBase()
        self.app_channel.send = self.respond

    def install(self, announces, api):
        super().install(announces, api)

        # app_channel.receiver(packet) => Face.receive(APP_LAYER_FACE_ID, packet)
        api['Face.setInChannel'](APP_LAYER_FACE_ID, self.app_channel)

        # Face.send(APP_LAYER_FACE_ID, packet) => AppChannel.send(packet)
        api['Face.setOutChannel'](APP_LAYER_FACE_ID, self.app_channel)

        api['App.ask'] = self.ask
        api['App.respond'] = self.respond

    def ask(self, packet):  # 由应用层调用向网络层发数据
        assert packet.type is Packet.INTEREST
        self.announces['ask'](packet)
        self.app_channel.receiver(packet)  # 向下交付

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
