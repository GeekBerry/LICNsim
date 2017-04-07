#!/usr/bin/python3
#coding=utf-8

import constants
from core.logger import *

# log= Logger( Logger.LEVEL.TRACK )
# label= LabelTable() #全局标签
log= Logger( Logger.LEVEL.NOLOG )
label= NoLabelTable()

#=======================================================================================================================
import numpy
import random

# class Impulse:
#     def __init__(self, delta, function):
#         self.delta= delta
#         self.function= function
#
#     def __call__(self, t):
#         if t % self.delta == 0:
#             return self.function(t)
#         else: return 0

class FixedAsk:
    def __init__(self, lam):
        self.lam= lam

    def __call__(self, t):
        return self.lam

class PossionAsk:
    def __init__(self, lam):
        self.lam= lam

    def __call__(self, t):
        return numpy.random.poisson(self.lam)

class ExponentAsk:
    def __init__(self, lam):
        self.lam= lam

    def __call__(self, t):
        return 1 if random.random() < numpy.exp(-t*self.lam) else 0

#=======================================================================================================================
import networkx

def graphHoops(graph, center):
    inter= set()
    hoop= {center}
    while hoop:
        yield hoop# 返回当前圈
        outer= set()
        for node in hoop:# 找出hoop的所有相邻节点
            outer |= graph[node].keys()
        inter, hoop= hoop, outer- hoop- inter # 向外扩张一层

# def graphNearest(graph, center, stores):
#     """
#     返回graph中距离center最近且在store_set中的节点
#     :param graph:networkx.DiGraph
#     :param center:nodename
#     :param stores:set(nodename, ...)
#     :return:nodename
#     """
#     for hoop in graphHoops(graph, center):# 遍历层
#         for node in hoop:# 遍历圈中节点
#             if node in stores:
#                 return node
#     return None

def graphNearestPath(graph, center, content_nodes):
    """
    获取graph图中, center点到 content_nodes 集合最近路径, 不存在返回None
    :param graph:networkx.DiGraph
    :param center:nodename
    :param content_nodes:set(nodename, ...)
    :return:[nodename, ...] OR None

    graph:
      3--4--6
     /    \
    1--2--{5}

    graphNearestPath(graph, 1, {5})过程:
        inter   current outer   cur_paths            next_paths
    1>  {}      {1}     {2,3}   [ [1] ]             [ [1,2], [1,3] ]
    2>  {1}     {2,3}   {5,4}   [ [1,2], [1,3] ]    [ [1,2,5], [1,3,4] ]
    3>  {2,3}   {5,4}   {6}     [ [1,2,5]return ...
    return [1,2,5]
    """
    inter, current, outer= set(), {center}, set()
    cur_paths, next_paths= [ [center] ], []

    while len(cur_paths)>0:
        for path in cur_paths:  # 层遍历
            tie_node= path[-1]
            if tie_node in content_nodes:  # 该路径末尾节点在目标集合中
                return path

            for node in graph.neighbors(tie_node):
                if (node not in current) and (node not in inter):
                    outer.add(node)
                    next_paths.append( path+[node] )

        cur_paths, next_paths= next_paths, []
        inter, current= current, outer

    return None

def graphNodeAvgDistance(graph, center)->float:
    distance, sigma= 0, 0
    for hoop in graphHoops(graph, center):
        sigma+= len(hoop)*distance
        distance+= 1
    return sigma/len(graph)

def graphApproximateDiameter(graph, sample_num= 10):  # 得到graph近似直径
    nodes= random.sample( graph.nodes(), sample_num )  # sample_num: 取样测试偏心率的点数量 如果sample_num>len(graph), 会出现个采样错误
    ecce_dict= networkx.eccentricity(graph, nodes)  # 计算测试点偏心率
    avg_ecce= numpy.mean(  list( ecce_dict.values() )  )
    return int(avg_ecce*1.5)  # 近似直径 FIXME 圆面网络是3/2==1.5 但是得出的值总会偏大

#-----------------------------------------------------------------------------------------------------------------------
class UniformPosition:
    def __init__(self, graph, *args):
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
            distance= constants.INF
            while distance >= self.length:
                distance = numpy.random.zipf(self.alpha)

            node= random.choice( self.hoops[distance] )
            nodes.add(node)

        return nodes

#-----------------------------------------------------------------------------------------------------------------------
class GridPosLogic:
        CENTER, OUTSIDE, UP, DOWN, LEFT, RIGHT, LEFTUP, RIGHTDOWN, RIGHTUP, LEFTDOWN= range(0, 10)
        def __init__(self, cx, cy):
            self.sx, self.sy = 1, 1
            self.cx, self.cy= cx, cy
            self.ex, self.ey= 2*self.cx - 1, 2*self.cy - 1

            self.hsx, self.hsy= (self.sx+self.cx)//2, (self.sy+self.cy)//2
            self.hex, self.hey= (self.cx+self.ex)//2, (self.cy+self.ey)//2

        def reset(self):
            self.vector= [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        def insert(self, point):
            x,y = point[0], point[1]

            if self.inCenter(x,y):
                self.vector[self.CENTER]+=1
            else: self.vector[self.OUTSIDE]+=1

            if self.inUp(x,y):
                self.vector[self.UP]+=1
            else: self.vector[self.DOWN]+=1

            if self.inLeft(x,y):
                self.vector[self.LEFT]+=1
            else: self.vector[self.RIGHT]+=1

            if self.inLeftUp(x,y):
                self.vector[self.LEFTUP]+=1
            else: self.vector[self.RIGHTDOWN]+=1

            if self.inRightUp(x,y):
                self.vector[self.RIGHTUP]+=1
            else: self.vector[self.LEFTDOWN]+=1

        def inCenter(self, x,y):
            return self.hsx<=x<self.hex and self.hsy<=y<self.hey

        def inUp(self, x,y):
            return self.sy<=y<self.cy

        def inLeft(self, x,y):
            return self.sx<=x<self.cx

        def inLeftUp(self, x,y):
            return x+y <= self.ex

        def inRightUp(self, x,y):
            return y<=x

class GridPosLogicSmallGrid:
    def __init__(self, cx, cy):
        self.sx, self.sy= 1, 1
        self.ex, self.ey= 2*cx - 1, 2*cy - 1

    def reset(self):
        self.vector= [0]*100

    def insert(self, point):
        x, y = point[0], point[1]

        px= x*10 // (self.ex+1)
        py= y*10 // (self.ey+1)

        self.vector[ px*10 + py ]+=1


#=======================================================================================================================
import time
def timeIt(func):
    def _lambda(*args, **kwargs):
        start_time= time.clock()
        ret= func(*args, **kwargs)
        print(func.__name__, '运行:', (time.clock()- start_time), 's')
        return ret
    return _lambda

show_call_deep= 0
def showCall(func):
    def lam(*args, **kwargs):
        global show_call_deep
        print('\t'*show_call_deep, 'START: ',func)
        show_call_deep += 1
        ret= func(*args, **kwargs)
        show_call_deep -= 1
        print('\t'*show_call_deep, 'END: ',func)
        return ret
    return lam

import cProfile
import pstats
def timeProfile(cmd):
    prof= cProfile.Profile()
    prof.run(cmd)
    pstats.Stats(prof).strip_dirs().sort_stats('tottime').print_stats('', 20)# sort_stats:  ncalls, tottime, cumtime

#-----------------------------------------------------------------------------------------------------------------------
import os
import sys
import ctypes
class CppDll:
    """
    main= CppDll('main')
    d= {1:100}
    p= main.foo(d)
    print(p)
    """
    PYTHON_DIR= '\\'.join(sys.executable.split('\\')[0:-1])
    GCC= 'E:/program/Dev-Cpp/MinGW64/bin/gcc'
    INCLUDE= f' -I{PYTHON_DIR}/INCLUDE -DBUILDING_DLL=1'
    LIBS= f' -L{PYTHON_DIR}/LIBS'
    LIB= f' -static-libgcc {PYTHON_DIR}/LIBS/python36.lib'

    def __init__(self, file_name):
        if not os.path.exists(f'{file_name}.cpp'):
            raise OSError(f'找不到文件 {file_name}.cpp')

        if not os.path.exists(f'{file_name}.dll')\
        or os.stat( f'{file_name}.cpp' ).st_mtime > os.stat( f'{file_name}.dll' ).st_mtime: # gcc修改时间 > dll修改时间
            os.system(f'{self.GCC} -c {file_name}.cpp -o {file_name}.o {self.INCLUDE} -std=gnu++11')
            os.system(f'{self.GCC} -shared {file_name}.o -o {file_name}.dll {self.LIBS} {self.LIB}')
        self.cdll = ctypes.CDLL( f'{os.getcwd()}/{file_name}.dll' )  # os.getcwd() ???

    def __getattr__(self, item):  # FIXME??? 是否需要对类型强制要求
        # cpp文件中函数对应形式为 PyObject* xxx(PyObject* pointer)
        func= self.cdll[item]
        func.argtypes= (ctypes.py_object,)
        func.restype= ctypes.py_object
        return func

#-----------------------------------------------------------------------------------------------------------------------
def getSysKwargs()->dict:
    return dict([ part.split('=') for part in sys.argv[1:] ])

def setSysKwargs(**kwargs)->str:
    string= ''
    for k,v in kwargs.items():
        string += f'{k}={v} '
    return string

def python(filename, **kwargs):
    os.system(f'python {filename} {setSysKwargs(**kwargs)}')
#=======================================================================================================================
from core.data_structure import AnnounceTable
class Unit:
    def __init__(self):

        self.publish= AnnounceTable()
        label[self.publish]= label[self],".pub"

    def install(self, announces, api):
        # 监听的 Announce
        # 发布的 Announce
        # 提供的 API
        # 调用的 API
        pass





