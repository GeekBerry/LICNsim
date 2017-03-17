#!/usr/bin/python3
#coding=utf-8
import random

class Name(list):
    def isPrefix(self, other):
        if len(self) > len(other):
            return False 
        else:# TODO 更高效的比较方法
            return self == other[0: len(self) ]

    def __hash__(self):
        """使其可以做dict的主键"""
        return hash( id(self) )# TODO hash( tuple(self) )那个比较好

    def __add__(self, other):
        return Name( super().__add__(other) )

    def __and__(self, other):
        """
        abc & ab & ad == a
        """
        prefix=[]

        length= range(  0,  min( len(self), len(other) )  )
        for i in length:
            if self[i] == other[i]:
                prefix.append(self[i])
            else:
                break

        return Name(prefix)


    def __sub__(self, other):
        """
        'abc' - 'ab' == 'c'
        'abc' - 'ax' == 'abc'
        'abc' - 'abc' == ''
        'abc' - 'abcde' == None
        """
        if len(self) >= len(other):
            if other.isPrefix(self):
                return self[ len(other):]
            else:
                return self
        else:
            return None
    
    def __str__(self):# FIXME DEBUG
        return '/'.join(self)


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

#=======================================================================================================================
class Packet:
    class TYPE:
        DATA, EMPTY, INTEREST= -1, 0, 1 # 数据包, 无效包, 兴趣包

    def __init__(self, name, type, size= 1):
        self.name= name #包名
        self.type= type # 包类型
        self.nonce= random.randint(0, 1<<32) # 随机数 范围[0,2^32) 4个字节
        self.size= size # 包大小

    def __hash__(self):
        return hash( id(self) )# hash( self.name self.type self.nonce )

    def __len__(self):
        return self.size

    def __eq__(self, other):
        return  isinstance(other, Packet)  \
                and self.type == other.type \
                and self.name == other.name  \
                and self.nonce == other.nonce

    def fission(self):#分裂成另一个包, 除了nonce域外全都一样
        return Packet(self.name, self.type, self.size)

    def __repr__(self):
        return "Packet("+str(self.name)+","+str(self.type) + "," + str(self.nonce) + ')'




