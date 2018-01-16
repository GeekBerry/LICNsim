from collections import defaultdict
from core import TimeSet, clock, Bind, Unit, INF, LeakBucket


class FaceUnit(Unit):
    """
                          +--------+
    receive --(append)--> | bucket | --(pop)--> inPacket
                          +--------+
                         /          \
                      rate        capacity
    """

    class LoopChecker:
        def __init__(self, nonce_life_time):
            self.info_set = TimeSet(nonce_life_time)

        def isLoop(self, packet):
            info_tuple = (packet.name, packet.type, packet.nonce)
            if info_tuple not in self.info_set:
                self.info_set.add(info_tuple)
                return False
            else:
                return True

    class RepeatChecker:
        def __init__(self):
            # XXX 此处不能用 self.info_set= TimeSet(1) 是因为 TimeSet 不能保证在时间片的一开始进行删除检查
            # XXX 而 RepeatChecker 要求时间一变化, 则立刻清除info_set数据
            self.info_set = set()
            self.record_time = None

        def isRepeat(self, face_id, packet):
            if self.record_time != clock.time:
                self.info_set.clear()
                self.record_time = clock.time

            info_tuple = (face_id, packet.name, packet.type)
            if info_tuple not in self.info_set:  # 重复包
                self.info_set.add(info_tuple)
                return False
            else:
                return True

    class Face:
        def __init__(self):
            self.receivable = False
            self.in_channel = None

            self.sendable = False
            self.out_channel = None

    # -------------------------------------------------------------------------
    def __init__(self, rate=1, capacity=INF, life_time=100_000):
        self.table = defaultdict(self.Face)

        self.loop_checker = self.LoopChecker(life_time)
        self.repeat_checker = self.RepeatChecker()

        self.bucket = LeakBucket(rate, capacity)
        self.bucket.pop = self._inPacket
        self.bucket.overflow = self.overflow

    def install(self, announces, api):
        super().install(announces, api)

        api['Face.sends'] = self.sends
        api['Face.receive'] = self.receive
        api['Face.setInChannel'] = self.setInChannel
        api['Face.setOutChannel'] = self.setOutChannel
        api['Face.getInFaceIds'] = self.getInFaceIds
        api['Face.getOutFaceIds'] = self.getOutFaceIds
        api['Face.getRate'] = lambda: self.bucket.rate

    # -------------------------------------------------------------------------
    def setInChannel(self, face_id, channel):
        entry = self.table[face_id]
        assert entry.in_channel is None  # 必须为空，不允许重复设置
        entry.receivable = True
        entry.in_channel = channel
        entry.in_channel.receiver = Bind(self.receive, face_id)

    def setOutChannel(self, face_id, channel):
        entry = self.table[face_id]
        assert entry.out_channel is None  # 不允许重复设置
        entry.sendable = True
        entry.out_channel = channel

    def getInFaceIds(self):
        face_ids = set()
        for face_id, entry in self.table.items():
            if entry.receivable:
                face_ids.add(face_id)
        return face_ids

    def getOutFaceIds(self):
        face_ids = set()
        for face_id, entry in self.table.items():
            if entry.sendable:
                face_ids.add(face_id)
        return face_ids

    # -------------------------------------------------------------------------
    def sends(self, face_ids, packet):
        for face_id in face_ids:
            if not self.table[face_id].sendable:
                pass  # 接口不允许发送
            elif self.repeat_checker.isRepeat(face_id, packet):
                self.announces['repeatePacket'](face_id, packet)
            else:
                clock.timing(0, self._outPacket, face_id, packet)  # 利用定时器保证 send 行为是在一个时间片末尾执行

    def _outPacket(self, face_id, packet):
        self.table[face_id].out_channel.send(packet)  # 发往接出信道
        self.announces['outPacket'](face_id, packet)

    def receive(self, face_id, packet):
        if not self.table[face_id].receivable:
            pass  # 接口不允许接收
        elif self.loop_checker.isLoop(packet):
            self.announces['loopPacket'](face_id, packet)
        else:
            value = face_id, packet
            self.bucket.append(value, size=1)  # 添加到接收队列, size= 1(个包), 最终触发 _inPacket

    def _inPacket(self, value):
        face_id, packet = value
        self.announces['inPacket'](face_id, packet)

    # -------------------------------------------------------------------------
    def overflow(self, args):
        face_id, packet = args
        self.announces['overflow'](face_id, packet)
