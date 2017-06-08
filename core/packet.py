# !/usr/bin/python3
# coding=utf-8

import copy
import random




# TODO 重写
# class Name(list):
#     def __init__(self, arg= None):
#         if isinstance(arg, str):
#             # re.match(r'(/\w+)+|/', string)  TODO
#             super().__init__( arg.split('/')[1:] )
#         else:
#             super().__init__(arg)
#
#     def isPrefix(self, other):
#         if len(self) > len(other):
#             return False
#         else:  # TODO 更高效的比较方法
#             return self == other[0: len(self)]
#
#     def __hash__(self):
#         """使其可以做dict的主键"""
#         return hash( tuple(self) )  # TODO 如何提高效率
#
#     def __add__(self, other):
#         return Name( super().__add__(other) )
#
#     def __and__(self, other):
#         """
#         abc & ab & ad == a
#         """
#         prefix=[]
#
#         length= range(  0,  min( len(self), len(other) )  )
#         for i in length:
#             if self[i] == other[i]:
#                 prefix.append(self[i])
#             else:
#                 break
#
#         return Name(prefix)
#
#
#     def __sub__(self, other):
#         """
#         'abc' - 'ab' == 'c'
#         'abc' - 'ax' == 'abc'
#         'abc' - 'abc' == ''
#         'abc' - 'abcde' == None
#         """
#         if len(self) >= len(other):
#             if other.isPrefix(self):
#                 return self[ len(other):]
#             else:
#                 return self
#         else:
#             return None
#
#     def __str__(self):  # FIXME DEBUG
#         return '/'+'/'.join([ str(each) for each in self])
# if __name__ == '__main__':
#     print("测试代码")
#
#     n1= Name(['bupt','mp4'])
#     n2= Name(['bupt','mp4','1'])
#
#     print( n1 & n2 ) # /bupt/mp4
#     print( n1 + n2 ) # /bupt/mp4/bupt/mp4/1
#     print( n2 - n1 ) # ['1']
#     print( n1.isPrefix(n2) ) # True
# =======================================================================================================================


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


from core.name import Name

class PacketHead:
    def __init__(self, name=Name('/'), type=None, nonce=0):
        self.name= name
        self.type= type
        self.nonce= nonce

    def __hash__(self):
        return hash( (self.name, self.type, self.nonce,) )

    def __eq__(self, other):
        return (self.name, self.type, self.nonce) == (other.name, other.type, other.nonce)

    def __str__(self):
        return f'({self.name}, {Packet.TYPE_STRING[self.type]}, {hex(self.nonce)})'



