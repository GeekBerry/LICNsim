import random
from collections import deque
from core import Timer, clock, AnnounceTable


class Channel:
    """
    Announces:
        send -> transfer -> loss/receive
    """
    receiver= None  # 回调接受者

    class Sender:
        def __init__(self, rate, call_back):
            self.rate = rate
            self.call_back = call_back
            self.timer = Timer(self.finish)  # 当前发送定时器
            self.queue = deque()

        def send(self, packet):
            self.queue.append(packet)
            self.checkSend()

        def checkSend(self):
            if not self.timer and self.queue:
                packet = self.queue.popleft()
                delay= packet.size//self.rate
                clock.timing(delay, self.finish, packet)

        def finish(self, packet):
            self.call_back(packet)
            self.checkSend()

    def __init__(self, src_id, dst_id, rate: int, delay: int, loss: float):
        self.__id= src_id, dst_id
        self.sender= self.Sender(rate, self.transfer)
        self.delay= delay
        self.loss= loss
        self.announces = AnnounceTable()

    @property
    def rate(self):
        return self.sender.rate

    @rate.setter
    def rate(self, value):
        self.sender.rate= value

    @property
    def queue(self):
        return list(self.sender.queue)

    def getId(self):
        return self.__id

    def send(self, packet):
        self.announces['send'](packet)
        self.sender.send(packet)

    def transfer(self, packet):
        self.announces['transfer'](packet)
        clock.timing(self.delay, self.finish, packet)

    def finish(self, packet):
        if random.random() < self.loss:
            self.announces['loss'](packet)
        else:
            self.announces['receive'](packet)
            self.receiver(packet)
