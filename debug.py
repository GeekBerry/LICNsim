import cProfile
import pstats
import time


def timeIt(func):
    def _lambda(*args, **kwargs):
        start_time= time.clock()
        ret= func(*args, **kwargs)
        print(func.__name__, '运行:', (time.clock()- start_time), 's')
        return ret
    return _lambda


import itertools
show_call_print= False
show_line_iter= itertools.count()
show_call_deep= 0
# show_call_file= open('show_call.txt', 'w')
def showCall(func):
    def lam(*args, **kwargs):
        global show_call_deep
        # global show_call_file

        string= str(next(show_line_iter))+':\t' + '\t'*show_call_deep + 'START: ' + str(func)
        if show_call_print:
            print(string)
        # show_call_file.write(string+'\n')

        show_call_deep += 1
        ret= func(*args, **kwargs)
        show_call_deep -= 1

        string= str(next(show_line_iter))+':\t' + '\t'*show_call_deep + 'END: ' + str(func)
        if show_call_print:
            print(string)
        # show_call_file.write(string+'\n')

        return ret
    return lam


def timeProfile(cmd):
    prof= cProfile.Profile()
    prof.run(cmd)
    pstats.Stats(prof).strip_dirs().sort_stats('tottime').print_stats('', 50)  # sort_stats:  ncalls, tottime, cumtime


