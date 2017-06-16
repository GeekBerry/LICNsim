# !/usr/bin/python3
# coding=utf-8

import copy
import random


class Packet:
    INTEREST, DATA= 0, 1 # 数据包, 兴趣包
    TYPE_STRING= ['Interest', 'Data']

    def __init__(self, name, type, size= None, data=''):
        self.name= name  # 包名
        self.type= type  # 包类型
        self.nonce= random.randint(0, 1<<32)  # 随机数 范围[0,2^32) 4个字节
        self.size= size  # 包大小
        self.data= data  # 包数据

    def __len__(self):
        if self.size is not None:
            return self.size
        else:
            return len(self.data)

    def __eq__(self, other):
        return self.head() == other.head()

    def __hash__(self):
        return hash( self.head() )

    def head(self):  # 文件摘要, 能区别两个包
        return PacketHead(self.name, self.type, self.nonce)

    def fission(self):  # 分裂成另一个包, 除了nonce域外全都一样
        return Packet(self.name, self.type, self.size, copy.deepcopy(self.data))

    def __str__(self):
        return f'Packet({self.name}, {Packet.TYPE_STRING[self.type]}, {len(self)}, {hex(self.nonce)})'

    def __repr__(self):
        return str(self)


# ======================================================================================================================
class PacketHead(tuple):
    NAME_FIELD, TYPE_FIELD, NONCE_FIELD= 0, 1, 2

    def __new__(cls, name, type, nonce):
        return tuple.__new__(cls, (name, type, nonce) )

    @property
    def name(self):
        return self[PacketHead.NAME_FIELD]

    @property
    def type(self):
        return self[PacketHead.TYPE_FIELD]

    @property
    def nonce(self):
        return self[PacketHead.NONCE_FIELD]

    def __str__(self):
        return f'({self.name}, {Packet.TYPE_STRING[self.type]}, {hex(self.nonce)})'


if __name__ == '__main__':
    a= PacketHead('w', 0, 100)
    print(a)



















