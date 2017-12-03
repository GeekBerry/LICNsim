import random
from collections import deque
from core import Timer, clock, AnnounceTable, top, DEBUG_FUNC, LeakBucket, INF


class ChannelBase:
    receiver = DEBUG_FUNC  # 链接接受者

    def send(self, packet):
        raise NotImplementedError()


class Channel(ChannelBase):
    """
    Announces:
        send -> transfer -> loss/receive
    """
    def __init__(self, rate: int, delay: int, loss: float):
        self.bucket= LeakBucket(rate, INF)
        self.bucket.pop = self.transfer

        self.delay = delay
        self.loss = loss
        self.announces = AnnounceTable()

    @property
    def rate(self):
        return self.bucket.rate

    @rate.setter
    def rate(self, value):
        self.bucket.rate = value

    def queue(self):
        return iter(self.bucket)

    def send(self, packet):
        self.announces['send'](packet)
        self.bucket.append(packet, size=packet.size)

    def transfer(self, packet):
        self.announces['transfer'](packet)
        clock.timing(self.delay, self.finish, packet)

    def finish(self, packet):
        if random.random() < self.loss:
            self.announces['loss'](packet)
        else:
            self.announces['arrive'](packet)
            self.receiver(packet)
