from core import Name, Packet

ip_A = Packet(Name('A'), Packet.INTEREST, 1)
ip_A1 = Packet(Name('A/1'), Packet.INTEREST, 1)
ip_B = Packet(Name('B'), Packet.INTEREST, 1)
dp_A = Packet(Name('A'), Packet.DATA, 500)
dp_A1 = Packet(Name('A/1'), Packet.DATA, 500)
dp_B = Packet(Name('B'), Packet.DATA, 500)

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
        return f'{obj.__class__}<{hex(id(obj.__self__))}>'
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
