#!/usr/bin/python3
#coding=utf-8

from core.common import *

class PerfectChannel(Announce):
    # def __init__(self):
    #     self.rate= 0xFFFFFFFF #XXX 一个很大的数字
    #     self.delay= 0
    #     self.loss= 0

    def __call__(self, packet):
        clock.timing(0, Bind(super().__call__, packet))


class OneStepChannel(Announce):
    def __call__(self, packet):
        clock.timing(1, Bind(super().__call__, packet))


class NoQueueChannel(Announce):
    def __init__(self):
        super().__init__()
        self.rate= 1    #int 单位byte/step
        self.delay= 0   #int 单位step
        self.loss= 0    #int 单位loss%

    def __call__(self, packet):#发送 packet, 实现在队列时间管理
        trans_time= len(packet)/self.rate
        clock.timing(trans_time, Bind(self.__emit, packet))

    def __emit(self, packet):
        if random.randint(0,100) >= self.loss: # 没有丢包
            clock.timing(self.delay, Bind(super().__call__, packet)) # Announce.__call__ 使其终端真正接收数据
        else:
            log.info(packet, '在途中丢失，丢包率是', self.loss)


class Channel(Announce):
    def __init__(self):
        super().__init__()
        self.rate= 1    #int 单位byte/step
        self.delay= 0   #int 单位step
        self.loss= 0    #int 单位loss%
        self.__finish= 0#float 当前处理结束时间

    def __call__(self, packet):#发送 packet, 实现在队列时间管理
        start_time= max( clock.time(), self.__finish )
        trans_time= len(packet)/self.rate
        self.__finish= start_time + trans_time
        clock.timing(self.__finish - clock.time(), Bind(self.__emit, packet))

    def __emit(self, packet):
        if random.randint(0,100) >= self.loss: # 没有丢包
            clock.timing(self.delay, Bind(super().__call__, packet)) # Announce.__call__ 使其终端真正接收数据
        else:
            log.info(packet, '在途中丢失，丢包率是', self.loss)


"""
class Channel(Announce):# 链路层 + 物理层
    def __init__(self):
        self._capacity= 0xFFFF
        self.rate= 1    #int 单位byte/step
        self.delay= 0   #int 单位step
        self.loss= 0    #int 单位loss%
        self.buffer= LeakyBucket(self._capacity, self.rate, self.__emit)

    def __call__(self, packet):#发送 packet, 实现在队列时间管理
        if not self.buffer.push( packet, len(packet) ):
            log.waring('缓存溢出丢包', str(packet) )

    def __emit(self, packet):
        if random.randint(0,100) >= self.loss: # 没有丢包
            clock.timing(self.delay, Announce.__call__, self, packet) # Announce.__call__ 使其终端真正接收数据
        else:
            log.info(packet, '在途中丢失，丢包率是', self.loss)
"""

