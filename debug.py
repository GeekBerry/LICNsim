from core import Packet, Name

ip_A = Packet(Name('A'), Packet.INTEREST, 1)
ip_A1 = Packet(Name('A/1'), Packet.INTEREST, 1)
ip_B = Packet(Name('B'), Packet.INTEREST, 1)
dp_A = Packet(Name('A'), Packet.DATA, 500)
dp_A1 = Packet(Name('A/1'), Packet.DATA, 500)
dp_B = Packet(Name('B'), Packet.DATA, 500)

from unit.channel import *

OneStepChannel = channelFactor(rate=INF, delay=1, loss=0.0)

from unit.node import nodeFactory
from unit.forward import GuidedForwardUnit

ExampleNode = nodeFactory(
    cs_capacity=10_000,
    replace_mode='FIFO',
    evict_mode='FIFO',
    evict_life_time=100,
    ForwardType= GuidedForwardUnit
)
# ======================================================================================================================
import cProfile, pstats


def prcfile(code):
    cProfile.run(code, 'cProfile.result')
    p = pstats.Stats('cProfile.result')
    p.strip_dirs().sort_stats('tottime').print_stats(20)  # cumulative, tottime, cumtime


# ======================================================================================================================
import itertools
import traceback
import types


def objName(obj):  # TODO 整理重写
    if type(obj) == types.MethodType:
        addr = hex(id(obj.__self__))
        return f'{obj.__qualname__}<{addr}>'
    elif type(obj) == types.FunctionType:
        return obj.__qualname__
    elif isinstance(obj, type):
        return obj.__qualname__
    elif type(obj) == types.BuiltinFunctionType:
        return obj.__qualname__
    else:
        addr = hex(id(obj))
        return f'{obj.__class__.__qualname__}<{addr}>'


show_call_print = True
show_line_iter = itertools.count()
show_call_deep = 0


# show_call_file= open('show_call.txt', 'w')


def showCall(func):
    def lam(*args, **kwargs):
        global show_call_deep
        # global show_call_file

        string = str(next(show_line_iter)) + ':\t' + '\t' * show_call_deep + 'START: ' + objName(func)
        if show_call_print:
            print(string)
        # show_call_file.write(string+'\n')

        show_call_deep += 1

        try:
            ret = func(*args, **kwargs)
        except Exception as exc:
            traceback.print_exc()
            exit(1)
            ret = None

        show_call_deep -= 1

        string = str(next(show_line_iter)) + ':\t' + '\t' * show_call_deep + 'END: ' + objName(func)
        if show_call_print:
            print(string)
        # show_call_file.write(string+'\n')

        return ret

    return lam
