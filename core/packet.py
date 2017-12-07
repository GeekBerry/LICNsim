# !/usr/bin/python3
# coding=utf-8

import copy
import random


class Packet:
    INTEREST, DATA= 'Interest', 'Data' # 数据包, 兴趣包
    HEAD_FIELDS= ('Name', 'Type', 'Size', 'Nonce')

    @staticmethod
    def randomNonce():
        return random.randint(0, 1 << 32)  # 随机数 范围[0,2^32) 4个字节

    def __init__(self, name, type, size:int, **kwargs):
        self.name= name  # 包名
        self.type= type  # 包类型
        self.size= size  # 包大小
        self.nonce= self.randomNonce()
        # for k, v in kwargs.items():
        #     setattr(self, k, v)

    def head(self):  # 文件头部, 能区别两个包
        return self.name, self.type, self.size, self.nonce

    def fission(self):  # 分裂成另一个包, 除了nonce域外全都一样
        return Packet(self.name, self.type, self.size)

    def __hash__(self):
        return self.nonce

    def __eq__(self, other):
        return self.head() == other.head()

    def __str__(self):
        return f'Packet({self.name}, {self.type}, {self.size}, {hex(self.nonce)})'

    def __repr__(self):
        return str(self)















