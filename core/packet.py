# !/usr/bin/python3
# coding=utf-8

import copy
import random


class Packet:
    INTEREST, DATA= 'Interest', 'Data' # 数据包, 兴趣包

    HEAD_FIELDS= ('Name', 'Type', 'Size', 'Nonce')
    @classmethod
    def head(cls, packet):  # 文件头部, 能区别两个包
        return packet.name, packet.type, packet.size, packet.nonce

    @classmethod
    def fission(cls, packet):  # 分裂成另一个包, 除了nonce域外全都一样
        new_pcaket= copy.deepcopy(packet)
        new_pcaket.nonce = cls.randomNonce()
        return new_pcaket

    @classmethod
    def randomNonce(cls):
        return random.randint(0, 1 << 32)  # 随机数 范围[0,2^32) 4个字节

    def __init__(self, name, type, size:int, **kwargs):
        self.name= name  # 包名
        self.type= type  # 包类型
        self.size= size  # 包大小
        self.nonce= self.randomNonce()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __hash__(self):
        return self.nonce

    def __eq__(self, other):
        return Packet.head(self) == Packet.head(other)

    def __str__(self):
        return f'Packet({self.name}, {self.type}, {self.size}, {hex(self.nonce)})'

    def __repr__(self):
        return str(self)















