#!/usr/bin/python3
#coding=utf-8

from core.common import *
from core.data_structure import *

class Face:
    def __init__(self, faceid):
        self.faceid= faceid
        self.downstream= None
        self.upstream= None
        self.can_recv= True
        self.can_send= True

    def download(self, packet): # 接收一个包
        if self.can_recv:
            log.info(label[self], '接收', str(packet) )
            self.downstream(self.faceid, packet)
        else:
            log.debug('can_recv 为 False , 不能接收数据包')

    def upload(self, packet): # 发送一个包
        if self.can_send:
            log.info(label[self], '发送', str(packet))
            self.upstream(packet)
        else:
            log.debug('can_send 为 False , 不能发送数据包')

#=======================================================================================================================
class LoopChecker:
    def __init__(self, nonce_life_time):
        self.info_set= TimeDictDecorator({}, nonce_life_time) #当做set来用

    def isLoop(self, packet):
        info_tuple= (packet.name, packet.type, packet.nonce)

        if info_tuple in self.info_set:# 循环包
            print('LoopChecker', info_tuple, self.info_set.table[info_tuple])#DEBUG
            return True
        else:
            self.info_set[info_tuple]= None #当做set来用
            return False
# if __name__ == '__main__':
#     log.level= 4
#     lc= LoopChecker()
#     p= lc.isLoop(debug_dp)
#     print(p)
#     p= lc.isLoop(debug_dp)
#     print(p)
#
#     for recv in range(0, LoopChecker.NONCE_LIFE_TIME * 2):
#         clock.step()
#
#     p= lc.isLoop(debug_dp)
#     print(p)

class RepeatChecker:# 在一个step内保证不会往一个faceid发送,相同类型(PACKET.TYPE)和名字(Name)的包(Packet)
    def __init__(self):
        self.refresh_time= -INF # 上次更新时间
        self.info_set= set()

    def isRepeat(self, faceid, packet):
        if self.refresh_time < clock.time():# 清空以前结果
            self.info_set.clear()
            self.refresh_time= clock.time()
            clock.timing(1, self.info_set.clear)#定时, 以免不调用__call__时info长期得不到清空, 只要delay大于1即可

        info_tuple= (faceid, packet.name, packet.type)
        if info_tuple in self.info_set:# 重复包
            return True
        else:
            self.info_set.add(info_tuple)
            return False

#-----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet
from core.packet import Name

class FaceUnit(Unit):
    def __init__(self, loop_checker, repeat_checker):
        Unit.__init__(self)
        self.table= Dict() # {faceId:Face, ...}
        self.loop_checker= loop_checker
        self.repeat_checker= repeat_checker

    def install(self, announces, api):
        #监听的 Announce
        #发布的 Announce
        self.publish['inPacket'].append(announces['inPacket'])
        self.publish['outPacket'].append(announces['outPacket'])
        #提供的 API
        api['Face::create']= self.create
        api['Face::destroy']= self.destroy
        api['Face::getCanSendIds']= self.getSendIds
        api['Face::send']= self.send
        #调用的 API

    #--------------------------------------------------------------------------
    def create(self, faceid, src_channel, dst_channel):# API
        """
            Channel                       Face                           FaceUnit
        +-------------+               +----------+                  +----------------+
        | dst_channel | <--upstream---| can_send |<----upload-----  | |repeat check| |<-- send ---
        +-------------+               |          |                  | ============== |>> outPacket
        | src_channel | ---download-->| can_recv |---downstream-->  | | loop check | |>> inPacket
        +-------------+               +----------+                  +----------------+
        :param faceid:Any
        :param src_channel:isinstance(Channel)
        :param dst_channel:isinstance(Channel)
        :return:None
        """
        self.destroy(faceid) #不破不立

        face= self.table.setdefault( faceid, Face(faceid) )
        src_channel.append( face.download )
        face.upstream= dst_channel
        face.downstream= self.receive

        label[ face ]= label[self],'[',str(faceid),']'
        log.info("创建", label[ face ] )

    def destroy(self, faceid):
        face= self.table.pop(faceid)
        if face is not None:
            face.downstream= EMPTY_FUNC# 不会再下发数据包
            del label[face]

    def getSendIds(self):
        send_ids= [ faceid
            for faceid, face in self.table.items()
                if face.can_send
            ]
        return set( send_ids )

    #--------------------------------------------------------------------------
    def receive(self, faceid, packet):
        if self.loop_checker.isLoop(packet):
            log.waring(label[self], '循环包', faceid, packet)
        else:
            self.publish['inPacket'](faceid, packet)

    def send(self, faceids, packet):
        for faceid in faceids:
            if faceid not in self.table:# 排除无效faceid
                log.waring("invFaceid",faceid)
                continue

            if self.repeat_checker.isRepeat(faceid, packet):# 排除重复包
                log.waring(label[self], '重复包', faceid, packet)
                continue

            self.table[faceid].upload(packet)#发送
            self.publish['outPacket'](faceid, packet)

#=======================================================================================================================
# if __name__ == '__main__':
#     print('test Face', __file__)
#     log.level= 4
#     api= CallTable()
#     announces= AnnounceTable()
#
#     face= FaceUnit(LoopChecker(10000), RepeatChecker())
#     face.install(announces, api)
#
#     app= Announce()
#
#     api['Face::create']('F1',app, print )
#
#     #announces['sendData']( {'F1'}, 'Data')
#
#     dp= Packet(Name(['A',1]), Packet.TYPE.DATA)
#     app(dp)
#
#     face.destroy('F1')
#     app(dp)
#
#     appnew= Announce()
#     api['Face::create']('F1',appnew, print )
#     app(dp)
#     appnew(dp)



