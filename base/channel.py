#!/usr/bin/python3
# coding=utf-8

import random
from collections import deque

from base.core import Timer
from core import clock
from base.core import top, CallTable, AnnounceTable
from common import INF


class Channel:
    """
    CallBacks:
        'idle'(): 信道空闲信号
        'arrived'(Packet): 包到达回调

    Announces:
        sendStart --(size//rate)--> sendBreak 或 sendEnd
        transferStart --(delay)--> transferEnd 或 transferLoss

        'sendStart'(Packet): 开始发送
        'sendBreak'(Packet): 中断发送
        'sendEnd'(Packet): 发送结束
        'transferStart'(packet): 开始传输
        'transferEnd'(packet): 结束传输
        'transferLoss'(Packet): 丢包
    """
    class Sender:
        def __init__(self, rate, call_back):
            self._rate= rate
            self._call_back= call_back
            self._start_time= 0
            self._send_size= 0  # 要发送的尺寸
            self._timer= Timer(self._finish)

        def isBusy(self)->bool:
            return bool(self._timer)

        def getRate(self):
            return self._rate

        def setRate(self, rate):  # 每次修改速率, 相当于另起一次发送, 发送剩下的 size
            rest_size= self._send_size - self._rate * (clock.time() - self._start_time)
            self._rate= rate
            self.send( max(0, rest_size) )

        def send(self, size):
            self._send_size= size
            self._start_time= clock.time()
            self._timer.timing( self._send_size//self._rate )

        def _finish(self):
            self.clear()
            self._call_back()

        def clear(self):
            self._send_size= 0
            self._timer.cancel()

    class Transmitter:
        ADD_TIME, DATA_FIELD= 0, 1  # queue 中记录tuple的下标

        def __init__(self, delay, call_back):
            self._delay= delay
            self._call_back= call_back
            self.queue= deque()  # deque( (ADD_TIME:int, DATA_FIELD:Any), ... )
            self._timer= Timer(self.checkPop)

        def getDelay(self):
            return self._delay

        def setDelay(self, delay):  # 重新计算哪一些需要pop
            self._delay= delay
            self.checkPop()

        def pushBack(self, data):
            self.queue.append( (clock.time(), data,) )  # (ADD_TIME:clock.time(), DATA_FIELD:data)
            if not self._timer:
                self.checkPop()

        def checkPop(self):
            self._timer.cancel()
            while self.queue:
                min_pop_time= top(self.queue)[self.ADD_TIME] + self._delay
                if min_pop_time <= clock.time():  # 注意是 '<=', 这样才能实现delay=0 时的逻辑; add_t= 3, delay= 0 -> pop_time==3 -> clock==3 then pop
                    data= self.queue.popleft()[self.DATA_FIELD]
                    clock.timing(0, self._call_back, data)  # XXX 不要用 self._call_back(data); 必须用 clock.timing(delay=0, ) 否则会造成递归调用
                else:
                    self._timer.timing( min_pop_time - clock.time() )
                    break

    def __init__(self, src_id, dst_id, rate:int, delay:int, loss:float):
        self.sender= self.Sender(rate, self.sendEnd)
        self.transmitter= self.Transmitter(delay, self.transferEnd)
        self.loss= loss

        self._sending_packet= None
        self.callbacks= CallTable()
        self.announces= AnnounceTable()

    @property
    def rate(self):
        return self.sender.getRate()

    @rate.setter
    def rate(self, value):
        self.sender.setRate(value)

    @property
    def delay(self):
        return self.transmitter.getDelay()

    @delay.setter
    def delay(self, value):
        self.transmitter.setDelay(value)

    def isBusy(self)->bool:
        return self.sender.isBusy()

    def send(self, packet):
        self.sendStart(packet)

    def sendStart(self, packet):
        if self.sender.isBusy():
            self.sendBreak()
        self._sending_packet= packet
        self.announces['sendStart'](self._sending_packet)
        self.sender.send( self._sending_packet.size )

    def sendBreak(self):
        self.sender.clear()
        assert self._sending_packet is not None
        self.announces['sendBreak'](self._sending_packet)
        self._sending_packet= None

    def sendEnd(self):
        self.announces['sendEnd'](self._sending_packet)
        self.transferStart(self._sending_packet)
        self._sending_packet= None
        self.callbacks['idle']()

    def transferStart(self, packet):
        self.announces['transferStart'](packet)
        self.transmitter.pushBack(packet)

    def transferEnd(self, packet):
        if random.random() < self.loss:
            self.announces['transferLoss'](packet)
        else:
            self.announces['transferEnd'](packet)
            self.callbacks['arrived'](packet)


# ----------------------------------------------------------------------------------------------------------------------
Channel.UI_ATTRS= {
    'Rate':{
        'type':'Int',
        'range':(0, 99999999),
        'getter': lambda obj: obj.rate,
        'setter': lambda obj, value: setattr(obj, 'rate', value)
    },

    'Delay':{
        'type':'Int',
        'range':(0, 99999999),
        'getter': lambda obj: obj.delay,
        'setter': lambda obj, value: setattr(obj, 'delay', value)
    },

    'Loss':{
        'type':'Float',
        'range':(0.0, 1.0),
        'getter': lambda obj: obj.loss,
        'setter': lambda obj, value: setattr(obj, 'loss', value)
    },

    'Sending':{
        'type':'Label',
        'getter': lambda channel: channel._sending_packet
    },

    'Queue':{
        'type':'Table',
        'range': ('AddTime', 'Data'),
        'getter': lambda channel: channel.transmitter.queue
    }
}


# ======================================================================================================================
class PerfectChannel(Channel):
    def __init__(self, src_id, dst_id):
        super().__init__(src_id, dst_id, rate= INF, delay=0, loss=0.0)


class OneStepChannel(Channel):
    def __init__(self, src_id, dst_id):
        super().__init__(src_id, dst_id, rate= INF, delay=1, loss=0.0)



