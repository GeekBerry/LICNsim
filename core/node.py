#!/usr/bin/python3
#coding=utf-8

from core.common import *
from core.data_structure import *
from core.packet import Packet

#=======================================================================================================================
class NodeBase:
    def __init__(self):
        self.api= CallTable()
        label[self.api]= label[self], '.api'
        self.announces= AnnounceTable()
        label[self.announces]= label[self], '.anno'

    def install(self, name, unit):
        unit.install(self.announces, self.api)
        setattr(self, name, unit)
        label[unit]= label[self], '.', name

#-----------------------------------------------------------------------------------------------------------------------
class ForwarderUnitBase(Unit):
    def install(self, announces, api):
        announces['inPacket'].append(self._inPacket)
        self.api= api  # FIXME 是否要全部引用

    def _inPacket(self, face_id, packet):
        pass


class AppUnitBase(Unit):
    def __init__(self):
        super().__init__()
        self.app_channel= Announce() #用于发送兴趣包的通道

    def install(self, announces, api):
        # 监听的 Announce
        # 发布的 Announce
        self.publish['ask']= announces['ask']
        self.publish['respond']= announces['respond']
        # 提供的 API
        api['APP::ask']= self._ask
        # 调用的 API
        api['Face::create']('APP', self.app_channel, self._respond)  # 调用Face的api建立连接
        self.api= api  # FIXME 是否要全部引用

    def _ask(self, packet):
        self.publish['ask'](packet)
        self.app_channel(packet)  # 发送packet

    def _respond(self, packet):
        self.publish['respond'](packet)


class LogUnit(Unit):
    def install(self, announces, api):
        for name in announces:
            announces[name].insert( 0, Bind(self.logout, name) )

    def logout(self, name, *args):
        print('[', clock.time(), ']', label[self], name, *args)
#=======================================================================================================================





