from base.channel import *


class ChannelType1(Channel):
    def __init__(self, src_id, dst_id):
        super().__init__(src_id, dst_id, rate=10, delay=0, loss=0.0)

