import numpy
from itertools import count
from common import Unit, logging
from base.core import Timer, Name, Packet, clock


class ServerGenerateUnit(Unit):
    DATA_SIZE= 64

    def __init__(self):
        self.timer= Timer(self.reStore)

    def install(self, announces, api):
        super().install(announces, api)
        api['Generate.store']= self.store

    def store(self, prefix:Name, delta:int):
        self.prefix= prefix
        self.index_iter= count()
        self.delta= delta
        self.timer.timing(0)

    def reStore(self):
        index= next(self.index_iter)
        name= Name.fromArgs(*self.prefix, index)
        packet= Packet( name, Packet.DATA, self.DATA_SIZE, c_time= clock.time() )
        self.api['APP.store'](packet),
        self.timer.timing(self.delta)


class ClientGenerateUnit(Unit):
    INTEREST_SIZE= 1

    def __init__(self, delta):
        self.delta= delta
        self.prefix= None
        self.start_time= None
        self.recevie_dict= {}  # {name:time, ...}
        self.reask_timer= Timer(self.heartbeat)
        self.stop_timer= Timer(self.stop)

    def install(self, announces, api):
        super().install(announces, api)
        api['Generate.ask']= self.ask
        api['Generate.stop']= self.stop
        announces['respond'].append(self.respond)

    def ask(self, prefix, time_length):
        if self.stop_timer:
            self.stop_timer.timing(0)  # 立即执行

        self.start_time= clock.time()
        self.recevie_dict.clear()
        self.prefix= prefix
        self.reask_timer.timing(0)
        self.stop_timer.timing(time_length)

    def heartbeat(self):
        assert self.prefix is not None
        packet= Packet(self.prefix, Packet.INTEREST, self.INTEREST_SIZE)
        self.api['APP.ask'](packet)
        self.reask_timer.timing(self.delta)

        logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} ask {packet}")

    def stop(self):
        packet= Packet(self.prefix, Packet.DATA, 1, is_cancel=True)
        self.api['APP.store'](packet)
        self.reask_timer.cancel()

        logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} {dict(self.recevie_dict)}")
        self.prefix= None
        # logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} stop {packet}")

    def respond(self, packet):
        if (not self.reask_timer) or ( not self.prefix.isPrefix(packet.name) ):
            logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} unexcept {packet}")
            return

        if packet.type == Packet.INTEREST:
            logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} timeOut {packet}")
            return

        if hasattr(packet, 'is_cancel'):
            # logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} Finished {packet}")
            return

        if packet.type == Packet.DATA:
            self.recevie_dict[packet.name]= clock.time()
            # logging.info(f"{clock.time()} Node{self.api['Hardware.getId']()} Respond {packet} ")
            return

    # def xxx(self):
    #     prefix= numpy.random.zipf(2,1)
    #
    #     self.ask()

