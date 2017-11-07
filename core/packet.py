# !/usr/bin/python3
# coding=utf-8

import copy
import random


class Packet:
    INTEREST, DATA= 0, 1 # 数据包, 兴趣包
    TYPE_STRING= ['Interest', 'Data']

    HEAD_FIELDS= ('Name', 'Type', 'Size', 'Nonce')
    @classmethod
    def head(cls, packet):  # 文件头部, 能区别两个包
        return packet.name, Packet.TYPE_STRING[packet.type], packet.size, packet.nonce

    def __init__(self, name, type, size:int, **kwargs):
        self.name= name  # 包名
        self.type= type  # 包类型
        self.size= size  # 包大小
        self.renonce()

        for k, v in kwargs.items():
            setattr(self, k, v)

    # def typeStr(self): 准备废除
    #     return Packet.TYPE_STRING[self.type]

    def fission(self):  # 分裂成另一个包, 除了nonce域外全都一样
        new_pcaket= copy.deepcopy(self)
        new_pcaket.renonce()
        return new_pcaket

    def renonce(self):
        self.nonce= random.randint(0, 1<<32)  # 随机数 范围[0,2^32) 4个字节

    def __str__(self):
        return f'Packet({self.name}, {Packet.TYPE_STRING[self.type]}, {self.size}, {hex(self.nonce)})'

    def __repr__(self):
        return str(self)


# ======================================================================================================================
# class PacketHead(tuple):
#     NAME_FIELD, TYPE_FIELD, NONCE_FIELD= 0, 1, 2
#
#     def __new__(cls, name, type, nonce):
#         return tuple.__new__(cls, (name, type, nonce) )
#
#     @property
#     def name(self):
#         return self[PacketHead.NAME_FIELD]
#
#     @property
#     def type(self):
#         return self[PacketHead.TYPE_FIELD]
#
#     @property
#     def nonce(self):
#         return self[PacketHead.NONCE_FIELD]
#
#     def __str__(self):
#         return f'({self.name}, {Packet.TYPE_STRING[self.type]}, {hex(self.nonce)})'
#
#     def __repr__(self):
#         return f'PacketHead{self}'














