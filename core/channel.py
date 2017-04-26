#!/usr/bin/python3
#coding=utf-8

# from debug import showCall
import random
import itertools

from constants import INF
from core import Hardware, clock, Announce, SizeLeakyBucket

class Channel(Hardware, Announce):
    def __init__(self, src, dst, rate:int, buffer_size:int, delay:int, loss:float):
        Hardware.__init__(self, f'Channel({src}->{dst})')
        Announce.__init__(self)

        self.delay= delay
        self.loss= loss
        self._order_iter= itertools.count()  # 标记该Channel处理的包序号
        self._bucket= SizeLeakyBucket(rate, buffer_size)

        self._bucket.callbacks['queue']= self.announces['queue']
        self._bucket.callbacks['full']= self.announces['full']
        self._bucket.callbacks['begin']= self.announces['begin']
        self._bucket.callbacks['end']= self._transfer

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
        self._bucket.append(len(packet), order, packet)
        # size= 1: rate, buffer_size的单位为(包); size=len(packet): rate, buffer_size的单位为(bytes)

    def _transfer(self, order, packet):
        self.announces['end'](order, packet)
        clock.timing(self.delay, self._finish, order, packet)

    def _finish(self, order, packet):
        if random.random() < self.loss:
            self.announces['loss'](order, packet)
        else:
            self.announces['arrived'](order, packet)
            Announce.__call__(self, packet)


#=======================================================================================================================
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



