#!/usr/bin/python3
#coding=utf-8


from core.logger import *
from core.clock import clock, Timer

IS_DEBUG= 1
if IS_DEBUG:
    import time
    def timeIt(func):
        def _lambda(*args, **kwargs):
            start_time= time.clock()
            ret= func(*args, **kwargs)
            print(func.__name__, '运行:', (time.clock()- start_time), 's')
            return ret
        return _lambda

    def showCall(func, *args, **kwargs):
        def lam(*args, **kwargs):
            print('<', func.__name__, '>')
            ret= func(*args, **kwargs)
            print('</', func.__name__, '>')
            return ret
        return lam

    import cProfile
    import pstats
    def timeProfile(cmd):
        prof= cProfile.Profile()
        prof.run(cmd)
        pstats.Stats(prof).sort_stats('tottime').print_stats('', 20)# sort_stats:  ncalls, tottime, cumtime
        # .strip_dirs()

    log= Logger( Logger.LEVEL.TRACK )
    label= LabelTable() #全局标签

    from core.packet import Packet
    from core.packet import Name
    debug_ip= Packet(Name(['DEBUG_PACKET']), Packet.TYPE.INTEREST)
    debug_ip1= Packet(Name(['DEBUG_PACKET', 1]), Packet.TYPE.INTEREST)
    debug_ip2= Packet(Name(['DEBUG_PACKET', 2]), Packet.TYPE.INTEREST)
    debug_dp= Packet(Name(['DEBUG_PACKET']), Packet.TYPE.DATA)
    debug_dp1= Packet(Name(['DEBUG_PACKET', 1]), Packet.TYPE.DATA)
    debug_dp2= Packet(Name(['DEBUG_PACKET', 2]), Packet.TYPE.DATA)

else:
    log= Logger( Logger.LEVEL.NOLOG )
    label= NoLabelTable()


# 全局变量
INF= 0x7FFFFFFF  #无穷大 此处用4byte整形最大正数

#=======================================================================================================================
import numpy
import random

class Impulse:
    def __init__(self, delta, function):
        self.delta= delta
        self.function= function

    def __call__(self, t):
        if t % self.delta == 0:
            return self.function(t)
        else:return 0

def fixedAsk(t):
    return 1

def possionAsk(t):
    return numpy.random.poisson(1)

class exponentAsk:
    def __init__(self, lam):
        self.lam= lam

    def __call__(self, t):
        return 1 if random.random() < numpy.exp(-t*self.lam) else 0

#=======================================================================================================================
def graphHoops(graph, center):
    inter= set()
    hoop= {center}
    while hoop:
        yield hoop# 返回当前圈
        outer= set()
        for node in hoop:# 找出hoop的所有相邻节点
            outer |= graph[node].keys()
        inter, hoop= hoop, outer- hoop- inter # 向外扩张一层


def graphNearest(graph, center, stores):
    """
    返回graph中距离center最近且在store_set中的节点
    :param graph:networkx.DiGraph
    :param center:nodename
    :param stores:set(nodename, ...)
    :return:nodename
    """
    for hoop in graphHoops(graph, center):# 遍历层
        for node in hoop:# 遍历圈中节点
            if node in stores:
                return node
    return None


def graphNearestPath(graph, center, content_nodes):
    """
    获取graph图中, center点到 content_nodes 集合最近路径, 不存在返回None
    :param graph:networkx.DiGraph
    :param center:nodename
    :param content_nodes:set(nodename, ...)
    :return:[nodename, ...]

    graph:
      3--4--6
     /    \
    1--2---5

    graphNearestPath(graph, 1, {5})过程:
        inter   current outer   cur_path            next_path
    1>  {}      {1}     {2,3}   [ [1] ]             [ [1,2], [1,3] ]
    2>  {1}     {2,3}   {5,4}   [ [1,2], [1,3] ]    [ [1,2,5], [1,3,4] ]
    3>  {2,3}   {5,4}   {6}     [ [1,2,5]return ...
    return [1,2,5]
    """
    inter, current, outer= set(), {center}, set()
    cur_path, next_path= [ [center] ], []

    while len(cur_path)>0:
        for path in cur_path:# 层遍历
            if path[-1] in content_nodes:
                return path

            for node in graph[ path[-1] ].keys():
                if node not in current  and  node not in inter:
                    outer.add(node)
                    next_path.append( path+[node] )

        cur_path, next_path= next_path, []
        inter, current= current, outer

    return None

#-----------------------------------------------------------------------------------------------------------------------
class UniformPosition:
    def __init__(self, graph):
        self.nodes= [ node for node in graph.nodes() ]

    def __call__(self, num):
        return random.sample( self.nodes, num ) if num else []


class ZipfPosition:
    def __init__(self, graph, center, alpha):
        self.hoops= [ list(hoop) for hoop in graphHoops(graph, center) ]
        self.length= len( self.hoops )-1
        self.alpha= alpha # 指数值

    def __call__(self, num): # FIXME 函数运行时间不定
        nodes= set()
        while len(nodes) < num:
            distance= INF
            while distance >= self.length:
                distance = numpy.random.zipf(self.alpha)

            node= random.choice( self.hoops[distance] )
            nodes.add(node)

        return nodes

#=======================================================================================================================
EMPTY_FUNC= lambda *args: None

class Function:
    def __init__(self, func, *args, **kwargs):
        self.func= func
        self.args= args
        self.kwargs= kwargs

    def __call__(self):
        log.track(self.func, self.args, self.kwargs)
        return self.func(*self.args, **self.kwargs)

class Bind(Function):
    def __call__(self, *args, **kwargs):
        return self.func(*self.args, *args, **kwargs) #FIXME self.kwargs

#-----------------------------------------------------------------------------------------------------------------------
class CallTable(dict):
    class CallBack:#用于CallTable[name]还不存在时,返回一个绑定指向列表的量
        def __init__(self):
            self.func= None

        def __eq__(self, other):
            return self.func is other

        def __call__(self, *args):
            if self.func is not None:
                return self.func(*args)
            else:
                log.error(str(args), "未找到对应函数,无法执行")
                raise RuntimeError('未找到对应函数',self.func,'无法执行')

    def __getitem__(self, name):
        return self.setdefault( name, CallTable.CallBack() )

    def __setitem__(self, name, func):
        callback= self.setdefault( name, CallTable.CallBack() )
        callback.func= func

class Announce(list):#-> void, raise KeyError
    def __call__(self, *args, **kwargs):
        for callback in self:
            callback(*args, **kwargs)

        if len(self) == 0:
            log.info(label[self], args, "没人订阅")

    def __hash__(self):
        return hash( id(self) )

class AnnounceTable(dict):
    def __getitem__(self, name):
        announce= self.get(name)
        if announce is None:
            announce= self[name]= Announce()
            label[announce]= label[self],'[',name,']'
        return announce

#=======================================================================================================================
class Unit:
    def __init__(self):
        self.publish= AnnounceTable()
        label[self.publish]= label[self],".pub"

    def install(self, announces, api):
        #监听的 Announce
        #发布的 Announce
        #提供的 API
        #调用的 API
        pass





















