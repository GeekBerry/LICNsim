#!/usr/bin/python3
#coding=utf-8

from core.common import *
from core.data_structure import *
#-----------------------------------------------------------------------------------------------------------------------
class InfoUnit(Unit):
    """
    table={
        name1: Info{
            faceid1: Entry{
                send:{TYPE: Time, TYPE2: Time...}
                recv:{TYPE: Time, TYPE2: Time...}
                },
            ...
        },
        ...
    }
    """
    class Entry:
        def __init__(self):
            self.recv= defaultdict(lambda:-INF) # {Packet.TYPE:life_time, ...}
            self.send= defaultdict(lambda:-INF) # {Packet.TYPE:life_time, ...}

        def __repr__(self):
            return str( self.__dict__ )

    class Info:
        def __new__(cls):
            return defaultdict( InfoUnit.Entry )


    def __init__(self, max_size, life_time):
        super().__init__()

        # 进行默认参数装饰
        self.table= defaultdict( InfoUnit.Info )
        # 进行尺寸限制装饰
        self.table= SizeDictDecorator(self.table, max_size)
        # 进行时间限制装饰
        self.table= TimeDictDecorator(self.table, life_time)
        self.table.before_delete_callback= self.infoEvictCallBack


    def install(self, announces, api):
        """
        :param announces:
            evictInfo(TODO)
        :param api:
        :return:
        """
        #监听的 Announce
        announces['inPacket'].append(self.inPacket)
        announces['outPacket'].append(self.outPacket)
        self.publish= announces
        api['Info::getInfo']= self.getInfo

    def inPacket(self, faceid, packet):
        self.table[packet.name][faceid].recv[packet.type]= clock.time()

    def outPacket(self, faceid, packet):
        self.table[packet.name][faceid].send[packet.type]= clock.time()

    def getInfo(self, packet):
        return self.table[packet.name]

    def infoEvictCallBack(self, name, packet):
        self.publish['evictInfo']( name, packet )


# if __name__ == '__main__':
#     i= InfoUnit(2, 1)
#     i.table['A'][1001].recv['I']= 10
#     i.table['B'][1001].send['D']= 20
#     p= i.table['B'][1002].recv['I']
#     print(p)
#     print(i.table)
#     clock.step()
#     clock.step()
#     clock.step()
#     clock.step()
#     clock.step()
#     print(i.table)


