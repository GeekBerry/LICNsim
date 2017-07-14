import random
from common import INF
from core import Packet, Name, setLimitedSub, clock
from unit.content_store_unit import anyMatchSelector
from unit.forward_unit import ForwarderUnitBase
from debug import showCall


class ForwarderUnit(ForwarderUnitBase):
    def inData(self, face_id, packet):
        if hasattr(packet, 'is_cancel'):
            self.inCancelData(face_id, packet)
        else:
            self.inRealData(face_id, packet)

    def inRealData(self, face_id, packet):
        raise NotImplementedError

    def inCancelData(self, faceid, packet):
        raise NotImplementedError


# -----------------------------------------------------------------------------
class ServerForwarderUnit(ForwarderUnit):
    def inRealData(self, face_id, packet):
        if face_id == 'APP':  # 只接受来自应用层的Data
            self.api['CS.store'](packet)  # DEBUG 只是做显示用
            face_ids= self.api['Info.prefixPendIds'](packet.name)
            self.api['Face.send'](face_ids, packet)  # 对所有前缀项进行回应

    def inCancelData(self, faceid, packet):
        pass


class RouterForwarderUnit(ForwarderUnit):
    PICK_NUM= INF

    def inInterest(self, face_id, packet):
        face_ids= self.pickForwardIds(face_id, packet)
        if face_ids:
            face_ids= random.sample( face_ids, min(len(face_ids), self.PICK_NUM) )
            self.api['Face.send']( face_ids, packet )

    def pickForwardIds(self, face_id, packet):
        face_ids= set( self.api['Face.netIds']() )

        face_ids.discard( face_id )  # 接入口一定删除

        # pending_ids= self.api['Info.namePendIds'](packet.name)
        # setLimitedSub(face_ids, pending_ids, self.PICK_NUM)  # 剔除部分 pending 口
        #
        # forwarded_ids= self.api['Info.nameForwardedIds'](packet.name)  # 以转发时间间隔由短向长排序
        # setLimitedSub(face_ids, forwarded_ids, self.PICK_NUM)  # 剔除部分 forwarded 口

        return face_ids

    # -------------------------------------------------------------------------
    def inRealData(self, face_id, packet):
        self.api['CS.store'](packet)  # DEBUG 只是做显示用
        face_ids= self.api['Info.prefixPendIds'](packet.name)
        if face_ids:
            self.api['Face.send'](face_ids, packet)  # 对所有前缀项进行回应
        else:  # TODO 没有 pending 接口, 应该发送 cancel_data
            recevied_dict= self.api['Info.prefixReceviedDict'](packet.name)
            for name in recevied_dict:
                cancel_packet= Packet(name, Packet.DATA, 0, is_cancel=True)  # 利用同名消除 Pending
                self.api['Face.send']([face_id], cancel_packet)

        # 发送 cancel 消息包
        forwarded_dict= self.api['Info.prefixForwardedDict'](packet.name)
        for name, forwarded_ids in forwarded_dict.items():
            forwarded_ids= set(forwarded_ids)
            if face_id in forwarded_ids:  # 要求 face_id 必须被转发过兴趣包
                forwarded_ids.discard(face_id)
                cancel_packet= Packet(name, Packet.DATA, 0, is_cancel=True)  # 利用同名消除 Pending
                self.api['Face.send'](forwarded_ids, cancel_packet)
            # else: face_id 不是有效数据源, 不应该触发 cancel_data 转发

    def inCancelData(self, faceid, packet):
        if not self.api['Info.namePendIds'](packet.name):  # (精确匹配名字) 没有pending口
            forwarded_ids= self.api['Info.prefixForwardedIds'](packet.name)
            self.api['Face.send'](forwarded_ids, packet)  # 转发 cancel


class ClientForwarderUnit(ForwarderUnit):
    def inInterest(self, face_id, packet):
        if face_id == 'APP':
            face_ids= self.api['Face.netIds']()
            self.api['Face.send']( face_ids, packet )  # 向所有 NetFace 发送

    def inRealData(self, face_id, packet):
        self.api['CS.store'](packet)  # DEBUG 只是做显示用
        face_ids= self.api['Info.prefixPendIds'](packet.name)
        if 'APP' in face_ids:  # XXX 只转发给 APP
            self.api['APP.respond'](packet)

    def inCancelData(self, faceid, packet):
        if faceid == 'APP':  # 只接受 APP 的 cancel
            self.api['APP.respond'](packet)

            forwarded_ids= self.api['Info.prefixForwardedIds'](packet.name)
            self.api['Face.send'](forwarded_ids, packet)  # 转发 cancel


