import numpy

from core import Packet, Name, INF
from unit import *
from unit.channel import Channel
from unit.node import NodeBase

ip_A = Packet(Name('A'), Packet.INTEREST, 1)
ip_A1 = Packet(Name('A/1'), Packet.INTEREST, 1)
ip_B = Packet(Name('B'), Packet.INTEREST, 1)
dp_A = Packet(Name('A'), Packet.DATA, 500)
dp_A1 = Packet(Name('A/1'), Packet.DATA, 500)
dp_B = Packet(Name('B'), Packet.DATA, 500)


# ======================================================================================================================
def nodeFactory(
        node_type='router',
        nonce_life_time=100_000,
        cs_capacity=None,
        replace_mode='FIFO',
        evict_mode=None,
        evict_life_time=None,
        ForwardType=FloodForwardUnit,
        forward_rate=1,
        forward_capacity=INF,
):
    def factor():
        node = NodeBase()
        assert node_type in ('server', 'router', 'client')
        node.node_type = node_type

        node.pos = numpy.random.rand(2) * 1000  # 给出一个 (0~1000, 0~1000) 的随机位置信息
        # 安装接口模块和应用层模块
        node.install('face', FaceUnit(nonce_life_time=nonce_life_time))
        node.install('app', GuidedAppUnit())  # 必须安装在FaceUnit后, 才能建立APPChannel
        # 安装CS模块和替换模块
        if cs_capacity is not None:
            node.install('cs', ContentStoreUnit(capacity=cs_capacity))
            node.install('replace', ReplaceUnit(mode=replace_mode))
        # 安装自动驱逐模块
        if evict_mode is not None:
            assert evict_mode in CSEvictUnit.MODE_TYPES
            assert evict_life_time is not None
            node.install('evict', CSEvictUnit(life_time=evict_life_time, mode=evict_mode))
        # 安装信息模块和转发模块
        node.install('info', IOInfoUnit())  # 安装在 ForwardUnit 前, InfoUnit 才能先行处理 inPack 信号

        TODO 把 forward_rate  forward_capacity 弄到 FaceUnit 去
        node.install('forward', ForwardType(rate=forward_rate, capacity=forward_capacity))

        node.store = node.api['CS.store']
        node.ask = node.api['App.ask']
        return node

    return factor


ExampleNode = nodeFactory(
    # node_type='router',
    # nonce_life_time=100_000,
    cs_capacity=10_000,
    replace_mode='FIFO',
    evict_mode='FIFO',
    evict_life_time=100,
    ForwardType=FloodForwardUnit,
    # forward_rate=1,
    # forward_capacity=INF,
)


# -----------------------------------------------------------------------------
def channelFactor(channel_type='wired', rate=INF, delay=0, loss=0.0):
    def factor():
        channel = Channel(rate, delay, loss)

        assert channel_type in ('wired', 'wireless')
        channel.channel_type = channel_type

        return channel

    return factor


OneStepChannel = channelFactor(
    # channel_type='wired',
    rate=INF,
    delay=1,
    loss=0.0
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
        return f'{obj.__qualname__}<{hex(id(obj.__self__))}>'
    elif isinstance(obj, (type, types.FunctionType, types.BuiltinFunctionType)):
        return obj.__qualname__
    else:
        return f'{obj.__class__.__qualname__}<{hex(id(obj))}>'


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
