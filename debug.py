import cProfile
import pstats
import time

import networkx

import core.algorithm
import core.common
import core.packet

def timeIt(func):
    def _lambda(*args, **kwargs):
        start_time= time.clock()
        ret= func(*args, **kwargs)
        print(func.__name__, '运行:', (time.clock()- start_time), 's')
        return ret
    return _lambda


show_call_print= True
show_call_deep= 0
show_call_file= open('show_call.txt', 'w')
def showCall(func):
    def lam(*args, **kwargs):
        global show_call_deep, show_call_file

        string= '\t'*show_call_deep + 'START: ' + str(func)
        if show_call_print:
            print(string)
        show_call_file.write(string+'\n')

        show_call_deep += 1
        ret= func(*args, **kwargs)
        show_call_deep -= 1

        string= '\t'*show_call_deep + 'END: ' + str(func)
        if show_call_print:
            print(string)
        show_call_file.write(string+'\n')

        return ret
    return lam


def timeProfile(cmd):
    prof= cProfile.Profile()
    prof.run(cmd)
    pstats.Stats(prof).strip_dirs().sort_stats('cumtime').print_stats('', 50)  # sort_stats:  ncalls, tottime, cumtime


#=======================================================================================================================
debug_ip=  core.packet.Packet( core.packet.Name('/DEBUG_PACKET'),   core.packet.Packet.INTEREST, size=1)
debug_ip1= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/1'), core.packet.Packet.INTEREST, size=1 )
debug_ip2= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/2'), core.packet.Packet.INTEREST, size=1 )
debug_dp=  core.packet.Packet( core.packet.Name('/DEBUG_PACKET'),   core.packet.Packet.DATA, size=1 )
debug_dp1= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/1'), core.packet.Packet.DATA, size=1 )
debug_dp2= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/2'), core.packet.Packet.DATA, size=1 )



class GraphGrid100X100:
    def __init__(self):
        self.diameter= 100
        self.center= (50,50)
        self.graph= networkx.DiGraph( networkx.grid_2d_graph(self.diameter, self.diameter) )


class GraphGrid11X11:
    def __init__(self):
        self.diameter= 11
        self.center= (5,5)
        self.graph= networkx.DiGraph( networkx.grid_2d_graph(self.diameter, self.diameter) )


class GraphBA50:
    def __init__(self):
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.DiGraph( networkx.random_graphs.barabasi_albert_graph(50, 1) )
        self.diameter= core.algorithm.graphApproximateDiameter(self.graph)


class GraphBA10000:
    def __init__(self):
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.DiGraph( networkx.random_graphs.barabasi_albert_graph(10000, 1) )
        self.diameter= core.algorithm.graphApproximateDiameter(self.graph)


class GraphTree3X8:
    def __init__(self):
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.DiGraph( networkx.balanced_tree(r=3, h=8) )
        self.diameter= 8 * 2  # h*2
