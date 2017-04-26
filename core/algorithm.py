import random
import networkx
import numpy
import constants


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
def graphHoops(graph, center):
    inter= set()
    hoop= {center}
    while hoop:
        yield hoop# 返回当前圈
        outer= set()
        for node in hoop:# 找出hoop的所有相邻节点
            outer |= graph[node].keys()
        inter, hoop= hoop, outer- hoop- inter # 向外扩张一层


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


#=======================================================================================================================
class SamplePosition:
    def __init__(self, nodes):
        self.nodes= nodes

    def __call__(self, num):
        return random.sample( self.nodes, num ) if num else []


class UniformPosition:
    def __init__(self, graph, *args):
        self.nodes= graph.nodes()

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


#=======================================================================================================================
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


