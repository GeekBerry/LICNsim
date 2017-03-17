#!/usr/bin/python3
#coding=utf-8


import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.animation as animation

#==============================================================================
from common import *
from node import *
from channel import *
class Grid:
    def __init__(self, size):
        self.size= size

        #创建图
        #self.graph= nx.DiGraph( nx.complete_graph(size) ) # FIXME 完全图
        #self.graph= nx.DiGraph( nx.wheel_graph(size) ) # FIXME 车轮图
        #self.graph= nx.DiGraph( nx.cycle_graph(size) ) # FIXME 环形图
        self.graph= nx.DiGraph( nx.grid_2d_graph(size, size) ) #方格子

        #布局
        #self.allpos= nx.spring_layout(self.graph)#FIXME
        self.allpos= {}
        for nodename in self.nodes():
            self.allpos[nodename]= nodename #XXX grid_2d_graph的名字正好与位置相同

        #构造节点
        for nodename in self.nodes():
            node= TestNode( nodename, self.allpos[nodename] )
            log.lable[node]= "Node"+str(nodename)
            self.graph.node[nodename]['ndn']= node

        #构造通道
        for src,dst in self.graph.edges():# 要先建立所有节点再建立Channel
            send_channel= self.graph[src][dst].setdefault( 'ndn', PerfectChannel() )
            recv_channel= self.graph[dst][src].setdefault( 'ndn', PerfectChannel() )
            self[src].api['Face::create']( (src,dst), recv_channel, send_channel )

    #--------------------------------------------------------------------------
    def drawNodes(self, nodenames= None, color= '#FFFFFF'):
        if nodenames is not None  and  len(nodenames) == 0:
            return []# 不绘制
        else:
            collection= nx.draw_networkx_nodes(
                self.graph,
                self.allpos,
                nodelist= nodenames,
                node_size= 2000/self.size, #2000 经验得到的数值
                node_color= color
                )
            return [collection] #必须返回可迭代表


    def drawEdges(self, edgenames= None, color= '#000000'):
        if edgenames is not None  and  len(edgenames) == 0:
            return []# 不绘制
        else:
            collection= nx.draw_networkx_edges(
                self.graph,
                self.allpos,
                edgelist= edgenames,
                edge_color= color
                )
        return [collection] #必须返回可迭代表

    #--------------------------------------------------------------------------
    def nodes(self):
        return self.graph.nodes()

    def __getitem__(self, name):
        return self.graph.node[name]['ndn']


#==============================================================================
import time
import json
from tool import *

def init():
    global collection
    return collection


def testArriveSameTime(i, nodes):
    if i == 0:
        return ( SIZE//2-2, SIZE//2), ( SIZE//2-3,SIZE//2-1)
    else:
        return []

def testArriveOneDiff(i, nodes):
    if i == 0:
        return ( SIZE//2-2, SIZE//2), ( SIZE//2-4,SIZE//2-1)
    else:
        return []
#"""

def step(i):#i: 帧号
    global collection
    global resultfile
    global allrespond
    global info

    #-------------------------------  显示数据  -----------------------------------

    print('='*60)
    print("STEP:", i, '\t',time.clock() )
    """
    for name, elem in info.items():
        print(name, ':')
        print('\t', elem)

    print( "兴趣包转发数量:", len(monitor.data['out_i']) )
    print( "数据包转发数量:", len(monitor.data['out_d']) )
    #"""

    input()

    #------------------------------- 进行转发  ------------------------------------
    monitor.step()# 在 发送兴趣包 和 clock.step()之前

    #发送请求
    picknodes= testArriveOneDiff( i, g.nodes() )
    # picknodes= constPick(  g.nodes(), max(1, int(EXPECT) )  )#随机插入兴趣包
    for nodenames in picknodes: #均匀分布 #XXX APP重复发会被抑制
        g[nodenames].api['APP::ask']( ip.fission() )

    clock.step()
    #------------------------------- 测量数据  ------------------------------------
    info= {}
    info['CS']= len( monitor.data['stores'] )
    info['evict']= monitor.data['evictcount']
    info['ask']= len( monitor.data['ask'] )

    for k,v in monitor.data['respond'].items():
        allrespond.setdefault(k, 0)
        allrespond[k] += v

    # info['respon']= allrespond
    # sorted( allrespond.items(), key=lambda d:d[1], reverse = True)

    step_num, send_num= 0,1
    for k,v in allrespond.items():
        step_num += k*v
        send_num += v
    info['avg_step']= "%.6f"%(step_num / send_num)


    step_num, send_num= 0,1
    for k,v in monitor.data['distance'].items():
        step_num += int(k)*v
        send_num += v
    info['avg_distance']= "%.6f"%(step_num / send_num)

    # info['distance']= monitor.data['distance']

    #------------------------------- 文件操作  ------------------------------------
    resultfile.write( '%d\t%d\t%d\t%s\t%s\n'%( info['CS'], info['evict'], info['ask'], info['avg_distance'], info['avg_step']) )
    #resultfile.write( json.dumps(info)+'\r\n' )
    resultfile.flush()
    #--------------------------------------------------------------------------
    return monitor.draw()


#==============================================================================
from gui import Monitor
from packet import Packet
from packet import Name
ip= Packet( Name([0]),  1, 1 )
dp= Packet( Name([0]), -1, 1 )


log.level= log.LEVEL.NOLOG

SIZE= 21
PROBABILITY= 0.001
NODENUM= SIZE*SIZE
EXPECT= PROBABILITY*NODENUM

CS_LIFE= 10
OnePacketFIFOCS.CS_LIFE_TIME= CS_LIFE
OnePacketLRUCS.CS_LIFE_TIME= CS_LIFE

PITUnit.ENTRY_LIFE_TIME= 200
PITUnit.ENTRY_COOL_TIME= 20

DATANODE= (  (SIZE-1)//2, (SIZE-1)//2  )#中心点有数据

from cs import ContentStore
g= Grid(SIZE)
monitor= Monitor(g, dp.name)

g[DATANODE].install('cs', ContentStore(1) )
g[DATANODE].api['APP::insert'](dp) # 布局数据包

#==============================================================================
fig, ax = plt.subplots()
plt.axis('off')# 关掉轴
plt.subplots_adjust(left=0, bottom=0, right=1, top=1)# 调整屏占比
plt.xlim(-1, SIZE)# 调整x坐标范围, (-1, 0, size-1, size)左右各留一格
plt.ylim(-1, SIZE)# 调整y坐标范围, (-1, 0, size-1, size)左右各留一格


global collection
collection= g.drawNodes(g.nodes()) + g.drawEdges()

global allrespond
allrespond= {}

global resultfile
resultfile= open('NODE%d_UNIFORM%d_LRU_CS%d.txt'%(NODENUM, EXPECT, CS_LIFE), 'w')
resultfile.write("CSnum\tEvict\tAsknum\tavgDst\tavgStep\n")


global info
info= {}


#log.level= log.LEVEL.DEBUG
ani = animation.FuncAnimation(
    fig= fig, #(必要) 绘制的画布
    func= step,# (必要) 每次执行此函数
    fargs= None,# 每次调用func传给func 的参数
    frames= None, #
    interval= 0,
    init_func= init, #初始化画布
    blit= True #True
)


print("SHOW")
plt.show()



