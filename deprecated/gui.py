#!/usr/bin/python3
#coding=utf-8

from common import *
from packet import *








class EdgeTrackApp:#TODO 添加pending记录
    def init(data):
        data['out_i']= []
        data['out_d']= []

    def step(data):
        data['out_i'].clear() #不能直接赋值为空
        data['out_d'].clear() #不能直接赋值为空


    def __init__(self, trackname, data):
        self.trackname= trackname
        self.data= data


    def install(self, announces, api):
        self.api= api
        announces['sendData'].add( self.sendData )
        announces['sendInterest'].add( self.sendInterest )


    def sendData(self, faceid, packet):
        if packet.name == self.trackname\
        and type(faceid) == tuple: #只绘制在图中的边
            self.data['out_d'].append( faceid )#XXX faceid 形式正好和边的名字相同


    def sendInterest(self, faceid, packet):
        if packet.name == self.trackname\
        and type(faceid) == tuple: #只绘制在图中的边
            self.data['out_i'].append( faceid )#XXX faceids 形式正好和边的名字相同

#--------------------------------------------------------------------------
class StoreTrackApp:
    def init(data):
        data['stores']= set()
        data['storecount']= 0
        data['evictcount']= 0

    def step(data):
        data['storecount']= 0
        data['evictcount']= 0


    def __init__(self, trackname, data):
        self.trackname= trackname
        self.data= data            


    def install(self, announces, api):
        self.api= api
        announces['csStore'].add( self.storeData )
        announces['csEvict'].add( self.evictData )


    def storeData(self, packet):
        if packet.name == self.trackname:
            self.data['stores'].add( self.api['Node::getName']() )
            self.data['storecount'] += 1


    def evictData(self, packet):
        if packet.name ==  self.trackname:
            self.data['stores'].discard( self.api['Node::getName']() )
            self.data['evictcount'] += 1

#--------------------------------------------------------------------------
class PendTrackApp:
    def init(data):
        data['pends']= set()
        data['satisfy']= []
        data['unsatisfy']= []

    def step(data):
        data['satisfy'].clear() #不能直接赋值为空
        data['unsatisfy'].clear() #不能直接赋值为空




    def __init__(self, trackname, data):
        self.trackname= trackname
        self.data= data            


    def install(self, announces, api):
        self.api= api
        announces['inInterest'].add( self.inInterest )
        announces['sendData'].add( self.sendData )
        announces['unsatisfy'].add( self.unsatisfy )


    def inInterest(self, faceid, packet):
        if packet.name == self.trackname:
            self.data['pends'].add( self.api['Node::getName']() )


    def sendData(self, faceid, packet):
        if packet.name == self.trackname:
            self.data['pends'].discard( self.api['Node::getName']() )
            #self.data['satisfy'].append( self.api['Node::getName']() )


    def unsatisfy(self, name, entry):
        if name == self.trackname:
            self.data['pends'].discard( self.api['Node::getName']() )
            #self.data['unsatisfy'].append( self.api['Node::getName']() )

#--------------------------------------------------------------------------
class IOAPP:
    def init(data):
        data['respond']= {}# {往返时间: 节点数量, ...} 响应频率统计
        data['ask']= []
        data['nack']= []
        data['nackcount']= 0
        data['askcount']= 0
        data['respondcount']= 0


    def step(data):
        data['respond'].clear() #不能直接赋值为空
        data['ask'].clear() #不能直接赋值为空
        data['nack'].clear() 


    def __init__(self, data):   
        self.data= data
        self.sender= Announce()
        self.sendtime= None
        self.sendname= Name()


    def install(self, announces, api):
        self.api= api
        api['Face::create']('APP', self.sender, self.receive)
        api['APP::ask']= self.send #由APPFace发送兴趣包
        api['APP::insert']= api['CS::inData'] #向结点的CS插入数据包
        

    def send(self, packet):
        if packet.typeid == Packet.TYPEID.INTEREST  \
        and self.sendtime is None:
            self.sendname= packet.name
            self.sendtime= clock.time()
            self.sender(packet)
            self.data['askcount'] += 1
            self.data['ask'].append( self.api['Node::getName']() )


    def receive(self, packet):
        if packet.typeid == Packet.TYPEID.DATA  \
        and packet.name == self.sendname  \
        and self.sendtime is not None:
            self.data['respond'].setdefault( clock.time()-self.sendtime, 0 )
            self.data['respond'][clock.time()-self.sendtime] += 1
            self.data['respondcount'] += 1
            self.sendtime= None


    def unsatisfy(self, name, entry):
        if 'APP' in entry.in_i  and  name == self.sendname:
            self.sendtime= None
            self.data['nack'].append( self.api['Node::getName']() )
            self.data['nackcount'] += 1



#--------------------------------------------------------------------------
class GodView:
    def init(data):
        if isinstance(data,dict):
            data['distance']= {}

    def step(data):
        pass


    def __init__(self, grid, data):
        self.ALLNODES= grid.nodes()
        self.data= data
        self.inGraph= lambda node: \
            0<=node[0]<grid.size and node[0]<grid.size\
            and\
            0<=node[1]<grid.size and node[1]<grid.size


    def install(self, announces, api):
        self.api= api
        api['getDistance']= self.getDistance
        #api['getDistance']= lambda:DATANODE
        announces['inInterest'].add( self.inInterest )


    def inInterest(self, faceid, packet):#DEBUG
        if faceid == 'APP':
            srcnode= self.api['Node::getName']() 
            dstnode= self.api['getDistance']()
            dst= manhattanDistance(srcnode, dstnode)

            self.data['distance'].setdefault(str(dst), 0)
            self.data['distance'][str(dst)]+= 1


    def getDistance(self):#->node
        if len( self.data['stores'] ) < len(self.ALLNODES)/5: #XXX 还有比10更好的值吗
            #start= time.clock()
            node= self.getNearestCSNode_forStores()
            #print("forStores", time.clock()-start)
        else:
            #start= time.clock()
            node= self.getNearestCSNode_outerManhattanHoop()
            #print("outerManhattanHoop", time.clock()-start)
        return node
        

    def getNearestCSNode_forStores(self):#->node
        nodename= self.api['Node::getName']()
    
        def getDistanceFromSelf(dstnode):
            return manhattanDistance( nodename, dstnode)
    
        if self.data['stores']:
            return min(self.data['stores'], key= getDistanceFromSelf)
        else:
            return None


    def getNearestCSNode_outerManhattanHoop(self):
        import numpy as np
        center= self.api['Node::getName']()
        hoop= [np.array(center)]

        while hoop:
            validhoop= []
            for node in hoop:
                #if tuple(node) in self.ALLNODES:#在图范围内
                if self.inGraph(node):#在图范围内
                    if tuple(node) in self.data['stores']:
                        return tuple(node)# 找到了
                    else:
                        validhoop.append( node )

            hoop= outerGridHoop(center, validhoop)

        return None




#==============================================================================
class Monitor:
    #--------------------------------------------------------------------------
    def __init__(self, grid, trackname):
        self.grid= grid
        self.trackname= trackname
        self.data= {} # statistic
        
        EdgeTrackApp.init(self.data)
        StoreTrackApp.init(self.data)
        PendTrackApp.init(self.data)
        IOAPP.init(self.data)
        GodView.init(self.data)

        for nodename in grid.nodes():
            grid[nodename].install( 'app_edge_track', EdgeTrackApp(self.trackname, self.data) )
            grid[nodename].install( 'app_store_track', StoreTrackApp(self.trackname, self.data) )
            grid[nodename].install( 'app_pend_track', PendTrackApp(self.trackname, self.data) )
            grid[nodename].install( 'app_io', IOAPP(self.data) )
            grid[nodename].install( 'app_godview', GodView(self.grid, self.data) )#依赖于 app_store_track


    def step(self):        
        EdgeTrackApp.step(self.data)
        StoreTrackApp.step(self.data)
        PendTrackApp.step(self.data)
        IOAPP.step(self.data)
        GodView.step(self.data)
        return self.draw()


    def draw(self):
        collection= self.grid.drawNodes( [(0,0)] )# FIXME 必须要画点什么才行, 画个点试试
        collection+= self.grid.drawNodes( self.data['pends'], color='#007F00')
        collection+= self.grid.drawNodes( self.data['stores'],color='#FF0000')
        collection+= self.grid.drawEdges( self.data['out_d'], color='#FF0000')
        collection+= self.grid.drawEdges( self.data['out_i'], color='#00FF00')
        collection+= self.grid.drawNodes( self.data['ask'],   color='#0000FF')
        return collection






