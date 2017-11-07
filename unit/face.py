from core import TimeDictDecorator, clock, Bind, Unit


class FaceUnit(Unit):
    class LoopChecker:
        def __init__(self, nonce_life_time):
            self.info_set = TimeDictDecorator({}, nonce_life_time)  # 当做set来用

        def isLoop(self, packet):
            info_tuple= (packet.name, packet.type, packet.nonce)
            if info_tuple not in self.info_set:
                self.info_set.setdefault( info_tuple )
                return False
            else:
                return True

    class RepeatChecker:
        def __init__(self):
            self.info_set= set()
            self.record_time= None

        def isRepeat(self, face_id, packet):
            if self.record_time != clock.time():
                self.info_set.clear()
                self.record_time= clock.time()

            info_tuple= (face_id, packet.name, packet.type)
            if info_tuple not in self.info_set:  # 重复包
                self.info_set.add(info_tuple)
                return False
            else:
                return True

    # -------------------------------------------------------------------------
    def __init__(self, nonce_life_time= 100_000):
        self.in_channels= {}
        self.out_channels= {}
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
        assert face_id not in self.in_channels
        self.in_channels[face_id]= channel
        channel.receiver= Bind(self.receive, face_id)

    def setOutChannel(self, face_id, channel):
        assert face_id not in self.out_channels
        self.out_channels[face_id]= channel

    def getInFaceIds(self):
        return set( self.in_channels.keys() )

    def getOutFaceIds(self):
        return set( self.out_channels.keys() )

    # -------------------------------------------------------------------------
    def sends(self, face_ids, packet):
        for face_id in face_ids:
            self.send(face_id, packet)

    def send(self, face_id, packet):
        if not self.repeat_checker.isRepeat(face_id, packet):
            self.announces['outPacket'](face_id, packet)
            self.out_channels[face_id].send(packet)
        else:
            self.announces['repeatePacket'](face_id, packet)

    def receive(self, face_id, packet):
        if not self.loop_checker.isLoop(packet):
            self.announces['inPacket'](face_id, packet)
        else:
            self.announces['loopPacket'](face_id, packet)



















