from collections import defaultdict
from core import TimeSet, clock, Bind, Unit


class FaceUnit(Unit):
    class LoopChecker:
        def __init__(self, nonce_life_time):
            self.info_set = TimeSet(nonce_life_time)

        def isLoop(self, packet):
            info_tuple= (packet.name, packet.type, packet.nonce)
            if info_tuple not in self.info_set:
                self.info_set.add( info_tuple )
                return False
            else:
                return True

    class RepeatChecker:
        def __init__(self):
            # XXX 此处不能用 self.info_set= TimeSet(1) 是因为 TimeSet 不能保证在时间片的一开始进行删除检查
            # XXX 而 RepeatChecker 要求时间一变化, 则立刻清除info_set数据
            self.info_set= set()
            self.record_time= None

        def isRepeat(self, face_id, packet):
            if self.record_time != clock.time:
                self.info_set.clear()
                self.record_time= clock.time

            info_tuple= (face_id, packet.name, packet.type)
            if info_tuple not in self.info_set:  # 重复包
                self.info_set.add(info_tuple)
                return False
            else:
                return True

    # -------------------------------------------------------------------------
    class Face:
        def __init__(self):
            self.receivable= False
            self.in_channel = None

            self.sendable= False
            self.out_channel = None

    def __init__(self, nonce_life_time= 100_000):
        self.table= defaultdict(self.Face)

        self.loop_checker= self.LoopChecker(nonce_life_time)
        self.repeat_checker= self.RepeatChecker()

    def install(self, announces, api):
        super().install(announces, api)

        self.api['Face.sends'] = self.sends
        self.api['Face.receive'] = self.receive
        self.api['Face.setInChannel']= self.setInChannel
        self.api['Face.setOutChannel']= self.setOutChannel
        self.api['Face.getInFaceIds']= self.getInFaceIds
        self.api['Face.getOutFaceIds'] = self.getOutFaceIds

    # -------------------------------------------------------------------------
    def setInChannel(self, face_id, channel):
        entry= self.table[face_id]
        assert entry.in_channel is None  # 不允许重复设置
        entry.receivable= True
        entry.in_channel= channel
        entry.in_channel.receiver = Bind(self.receive, face_id)

    def setOutChannel(self, face_id, channel):
        entry= self.table[face_id]
        assert entry.out_channel is None  # 不允许重复设置
        entry.sendable = True
        entry.out_channel= channel

    def getInFaceIds(self):
        face_ids= set()
        for face_id, entry in self.table.items():
            if entry.receivable:
                face_ids.add(face_id)
        return face_ids

    def getOutFaceIds(self):
        face_ids= set()
        for face_id, entry in self.table.items():
            if entry.sendable:
                face_ids.add(face_id)
        return face_ids

    # -------------------------------------------------------------------------
    def sends(self, face_ids, packet):
        for face_id in face_ids:
            clock.timing(0, self._send, face_id, packet)  # 保证 send 行为是在一个时间片末尾执行

    def _send(self, face_id, packet):
        if not self.repeat_checker.isRepeat(face_id, packet):
            if self.table[face_id].sendable:
                self.table[face_id].out_channel.send(packet)
                self.announces['outPacket'](face_id, packet)
        else:
            self.announces['repeatePacket'](face_id, packet)

    def receive(self, face_id, packet):
        if not self.loop_checker.isLoop(packet):
            if self.table[face_id].receivable:
                self.announces['inPacket'](face_id, packet)
        else:
            self.announces['loopPacket'](face_id, packet)



















