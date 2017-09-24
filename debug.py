
# import time
# def timeIt(func):
#     def _lambda(*args, **kwargs):
#         start_time= time.clock()
#         ret= func(*args, **kwargs)
#         print(func.__name__, '运行:', (time.clock()- start_time), 's')
#         return ret
#     return _lambda

import itertools
import traceback
# ======================================================================================================================
import types


def objName(obj):  # TODO 整理重写
    if type(obj) == types.MethodType:
        addr= hex(id(obj.__self__))
        return f'{obj.__qualname__}<{addr}>'
    elif type(obj) == types.FunctionType:
        return obj.__qualname__
    elif isinstance(obj, type):
        return obj.__qualname__
    elif type(obj) == types.BuiltinFunctionType:
        return obj.__qualname__
    else:
        addr= hex(id(obj))
        return f'{obj.__class__.__qualname__}<{addr}>'


show_call_print= True
show_line_iter= itertools.count()
show_call_deep= 0
# show_call_file= open('show_call.txt', 'w')

def showCall(func):
    def lam(*args, **kwargs):
        global show_call_deep
        # global show_call_file

        string= str(next(show_line_iter))+':\t' + '\t'*show_call_deep + 'START: ' + objName(func)
        if show_call_print:
            print(string)
        # show_call_file.write(string+'\n')

        show_call_deep += 1

        try:
            ret= func(*args, **kwargs)
        except Exception as exc:
            traceback.print_exc()
            exit(1)
            ret= None

        show_call_deep -= 1

        string= str(next(show_line_iter))+':\t' + '\t'*show_call_deep + 'END: ' + objName(func)
        if show_call_print:
            print(string)
        # show_call_file.write(string+'\n')

        return ret
    return lam


# ======================================================================================================================
import cProfile
import pstats


def timeProfile(cmd):
    prof= cProfile.Profile()
    prof.run(cmd)
    pstats.Stats(prof).strip_dirs().sort_stats('tottime').print_stats('', 50)  # sort_stats:  ncalls, tottime, cumtime


# ======================================================================================================================
def exeScript(sim, script):
    from base.core import clock, tupleClass
    Instr= tupleClass('delay', 'action', 'node_id', 'packet')

    ACTION_MAP= {
        'ask':  lambda node_id, packet: sim.api['ICNNet.getNode'](node_id).api['APP.ask']( packet.fission() ),
        'store': lambda node_id, packet: sim.api['ICNNet.getNode'](node_id).api['APP.store'](packet),
    }

    for each in script:
        instr= Instr(*each)
        clock.timing( instr.delay, ACTION_MAP[instr.action], instr.node_id, instr.packet )


# ======================================================================================================================
def print_clock():
    from base.core import clock
    for t in sorted(clock._todo.keys()):
        print('Time', t)
        for handle in clock._todo[t]:
            if handle:
                print(f'\t{handle.func}\t{handle.args}\t{handle.kwargs}\n')
