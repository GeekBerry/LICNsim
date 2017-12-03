import numpy, random
from core import Timer
from module import MoudleBase


class FixedAsk:
    def __init__(self, lam):
        self.lam= lam

    def __call__(self):
        return self.lam


class PossionAsk:
    def __init__(self, lam):
        self.lam = lam

    def __call__(self):
        return numpy.random.poisson(self.lam)


class FileAsk:
    def __init__(self, file_name):
        file = open(file_name, 'r')
        string = file.read()
        self.seq = [int(float(each)) for each in string.split('\t')]
        self.index= 0

    def __call__(self):
        num = 0
        if 0<= self.index < len(self.seq):
            num= self.seq[self.index]
            self.index += 1

        return num


# ----------------------------------------------------------------------------------------------------------------------
class UniformDistribute:
    def __init__(self, node_ids):
        self.node_ids = list(node_ids)

    def __call__(self, num):
        assert num < len(self.node_ids)
        return random.sample(self.node_ids, num)


class AskMoudle(MoudleBase):
    def __init__(self, packet, num_asker, pos_asker, delta=1, delay=0):
        self.timer = Timer(self._ask)
        self.timer.timing(delay)

        self.packet= packet
        self.num_asker = num_asker
        self.pos_asker = pos_asker
        self.delta = delta

    def _ask(self):
        num = self.num_asker()
        node_ids= self.pos_asker(num)
        for node_id in node_ids:
            self.sim.node(node_id).ask( self.packet.fission() )

        self.timer.timing(self.delta)


