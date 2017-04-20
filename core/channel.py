#!/usr/bin/python3
#coding=utf-8

import random
import itertools
from core.common import Hardware
from core.clock import clock
from core.data_structure import Announce
from core.data_structure import SizeLeakyBucket


class Channel(Hardware, Announce):
    def __init__(self, src, dst, rate:int, buffer_size:int, delay:int, loss:float):
        Hardware.__init__(self, f'Channel({src}->{dst})')
        Announce.__init__(self)

        self.delay= delay
        self.loss= loss
        self._order_iter= itertools.count()  # 标记该Channel处理的包序号
        self._bucket= SizeLeakyBucket(self._begin, rate, buffer_size)

    @property
    def rate(self):
        return self._bucket.rate

    @rate.setter
    def rate(self, value):
        self._bucket.rate= value

    @property
    def buffer_size(self):
        return self._bucket.max_size

    @buffer_size.setter
    def buffer_size(self, value):
        self._bucket.max_size= value

    def __call__(self, packet):
        order= next(self._order_iter)
        if not self._bucket(order, packet, size= len(packet)):  # size= 1: rate, buffer_size的单位为(包); size=len(packet): rate, buffer_size的单位为(bytes)
            self.announces['full'](order, packet)

    def _begin(self, order, packet):
        self.announces['begin'](order, packet)
        clock.timing(self.delay, self._finish, order, packet)

    def _finish(self, order, packet):
        if self.loss and random.random() < self.loss:
            self.announces['loss'](order, packet)
        else:
            self.announces['finish'](order, packet)
            super().__call__(packet)



#=======================================================================================================================
from constants import INF

def PerfectChannel(src, dst):
    return  Channel(src, dst, rate= INF, buffer_size= INF, delay=0, loss= 0.0)

def OneStepChannel(src, dst):
    return  Channel(src, dst, rate= INF, buffer_size= INF, delay=1, loss= 0.0)


if __name__ == '__main__':
    channel= OneStepChannel(None, None)

    channel.buffer_size= 10
    channel.rate= 1

    print(channel._bucket._queue.max_size)
    print(channel._bucket.rate)



