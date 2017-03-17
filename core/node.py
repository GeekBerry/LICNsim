#!/usr/bin/python3
#coding=utf-8

from core.common import *
from core.data_structure import *
from core.packet import Packet

#=======================================================================================================================
class NodeBase:
    def __init__(self):
        self.api= CallTable()
        label[ self.api ]= label[self],'.api'
        self.announces= AnnounceTable()
        label[ self.announces ]= label[self],'.anno'

    def install(self, name, unit):
        unit.install( self.announces, self.api )
        setattr(self, name, unit)
        label[ unit ]= label[self],'.',name

#-----------------------------------------------------------------------------------------------------------------------
class ForwarderUnitBase(Unit):
    def install(self, announces, api):
        announces['inPacket'].append(self._inPacket)
        self.api= api

    def _inPacket(self, faceid, packet):
        pass


class AppUnitBase(Unit):
    def __init__(self):
        super().__init__()
        self.app_channel= Announce() #用于发送兴趣包的通道

    def install(self, announces, api):
        #发布的 Announce
        self.publish['ask'].append( announces['ask'] )#arg( Packet )
        self.publish['respond'].append( announces['respond'] ) #arg( Packet )
        #调用的API
        api['Face::create']('APP', self.app_channel, self._respond)
        self.api= api
        #提供的API
        api['APP::ask']= self._ask


    def _ask(self, packet):
        self.publish['ask'](packet)
        self.app_channel(packet)# 发送packet

    def _respond(self, packet):
        self.publish['respond'](packet)


class LogUnit(Unit):
    def install(self, announces, api):
        for name in announces:
            announces[name].insert(0, Bind(self.logout, name) )

    def logout(self, name, *args):
        print('[',clock.time(),']', label[self], name, *args)
#=======================================================================================================================





