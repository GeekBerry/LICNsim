#!/usr/bin/python3
#coding=utf-8

from PyQt5.QtCore import (QLineF, QPointF, qrand, QRectF, QRect, QPoint, Qt)
from PyQt5.QtGui import (QPainter, QPainterPath, QPen, QPolygonF, QFont, QFontMetrics)
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsView, QGraphicsScene)


import numpy
#-----------------------------------------------------------------------------------------------------------------------
class Edge(QGraphicsItem):
    Type = QGraphicsItem.UserType + 2

    def __init__(self, src_pos, dst_pos):
        super().__init__()
        self.style= {
            'text_hight':10,

            'line_width':1,
            'line_color':Qt.black,

            'text_font': QFont('Courier New', 10, QFont.Black),

            'forward_text': '',
            'forward_color': Qt.black,

            'reverse_text': '',
            'reverse_color': Qt.black
            }

        self.show_detail= False
        self.adjust(src_pos, dst_pos)

        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)


    def type(self):
        return Edge.Type


    def adjust(self, src, dst):
        offset= self.style['line_width'] + self.style['text_hight']
        # 线
        self.line= QLineF(src, dst)
        # 中间点
        self.middle= (src + dst)/2
        # 角度
        if self.line.dx() != 0:
            self.angle = numpy.arctan( self.line.dy()/self.line.dx() ) /(2.0*numpy.pi) * 360
        else:
            self.angle = 90 if self.line.dy()>0 else -90
        # 轮廓
        r_ver= QPointF(1,-1) if self.angle > 0 else QPointF(-1,-1)
        r_ver *= offset
        self.polygon= QPolygonF([ src-r_ver, src+r_ver, dst+r_ver, dst-r_ver ])
        # 边界
        self.bounding_rect= QRectF(self.line.x1(), self.line.y1(), self.line.dx(), self.line.dy() ).normalized()
        self.bounding_rect.adjust(-offset, -offset, offset, offset)
        # 通知几何变换
        self.prepareGeometryChange()

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path= QPainterPath()
        path.addPolygon(self.polygon)
        path.closeSubpath()
        return path

    def paint(self, painter, option, widget):
        if self.show_detail: # 需要几何变换的绘图操作
            painter.translate( self.middle ) # 以线段中点为原点
            painter.rotate( self.angle )    # 以线段为X轴
            self._paintDetail(painter)
            # 一系列绘图
        else:# 画线
            painter.setPen( QPen(self.style['line_color'], self.style['line_width']) )
            painter.drawLine(self.line)


    def _paintDetail(self, painter):
        line_width= self.style['line_width']
        font= self.style['text_font']

        painter.setFont(font)
        fm= QFontMetrics(font)

        # 设置文本和颜色
        up_text, down_text= self.style['reverse_text'], self.style['forward_text']
        up_color, down_color= self.style['reverse_color'], self.style['forward_color']
        if self.line.dx() < 0:
            up_text, down_text= down_text, up_text
            up_color, down_color= down_color, up_color

        if up_text:
            painter.setPen( QPen(up_color, line_width) )
            painter.drawText( -fm.width(up_text)/2, -fm.descent()-line_width, '<'+up_text)
            painter.drawLine(0,0, -int(self.line.length()/2), 0)

        if down_text:
            painter.setPen( QPen(down_color, line_width) )
            painter.drawText( -fm.width(down_text)/2, fm.ascent()+line_width, down_text+'>')
            painter.drawLine(0,0, int(self.line.length()/2), 0)


    def hoverEnterEvent(self, event):
        self.show_detail= True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.show_detail= False
        self.update()
        super().hoverLeaveEvent(event)

#-----------------------------------------------------------------------------------------------------------------------
from core.common import AnnounceTable
class NetEdge: #TODO 与网络关联起来
    def __init__(self, edge, forward:bool):
        self.edge= edge
        self.forward= forward

    def adjust(self, src, dst):
        if self.forward:
            self.edge.adjust(src, dst)
        else:pass # 非正向边不进行调整, 以免重复调用

    def setText(self, text): #TODO ...变得更抽象
        if self.forward:
            self.edge.style['forward_text']= text
        else:
            self.edge.style['reverse_text']= text
        self.edge.update()

    def showDetail(self):
        self.edge.show_detail= True
        self.edge.update()

    def hideDetail(self):
        self.edge.show_detail= False
        self.edge.update()

    #TODO def showSpeed(...)
    #TODO ...

#=======================================================================================================================
class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self):
        super().__init__()
        self.publish= AnnounceTable()
        self.style= {
            'rect': QRectF(),
            'color': Qt.white,

            'name': '',
            'font': QFont('Courier New', 10, QFont.Black),

            'abstract_font': QFont('Courier New', 10, QFont.Normal),
            'abstract':'',
            'abstract_rect':QRectF(),
            }
        self.show_detail= False

        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def type(self):
        return Node.Type

    def boundingRect(self):
        return self.style['rect'] | self.style['abstract_rect']

    def shape(self):
        path = QPainterPath()
        path.addRect( self.style['rect'] )
        return path

    def setAbstract(self, abstract):
        self.style['abstract']= abstract
        # 计算文字矩形
        fm= QFontMetrics( self.style['abstract_font'] )
        rect= fm.boundingRect(  QRect(), Qt.AlignTop|Qt.AlignLeft, abstract )
        rect.moveCenter( QPoint(0, -( rect.height()+self.style['rect'].height() )/2) )# 将rect中点放到上方
        self.style['abstract_rect']= QRectF(rect)

    def paint(self, painter, option, widget):
        #绘制节点
        painter.setBrush(self.style['color'])
        rect= self.style['rect']

        painter.drawEllipse(rect) # painter.drawRect(rect) TODO 形状可定制 Pixmap

        painter.setFont( self.style['font'] )
        painter.drawText( self.style['rect'], Qt.AlignCenter, self.style['name'])

        # 绘制说明
        if self.show_detail:
            painter.setPen(Qt.black)
            painter.setFont( self.style['abstract_font'] )
            painter.drawText( self.style['abstract_rect'], Qt.AlignTop|Qt.AlignLeft, self.style['abstract'])

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.publish['ItemPositionHasChanged']()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.update()
        super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self.show_detail= True
        self.publish['hoverEnterEvent']()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.show_detail= False
        self.publish['hoverLeaveEvent']()
        super().hoverLeaveEvent(event)

#-----------------------------------------------------------------------------------------------------------------------

class NetNode:# TODO 面向NET
    def __init__(self, node):
        self.node= node

    def setName(self, name):
        self.node.style['name']= name

    def setAbstract(self, abstract):
        self.node.setAbstract(abstract)

    def setSize(self, size):
        self.node.style['rect']= QRectF(-size/2, -size/2, size, size)

    def setColor(self, color):
        self.node.style['color']= color

    def pos(self):
        return self.node.pos()

    def setPos(self, point):
        self.node.setPos(point)

#=======================================================================================================================
from core.common import Bind
class UINet:
    EDGE_LEN= 80 # 默认边长度
    NODE_SIZE= 40 # 默认Node大小
    def __init__(self, graph):
        self.graph= graph
        self.scene= QGraphicsScene()

        AREA_SIZE= self.EDGE_LEN * len(graph)**0.5 #来自方形网平均宽度

        # 构建Node
        for nodename in self.graph:
            node= Node()
            node.setPos( qrand()%AREA_SIZE, qrand()%AREA_SIZE )
            node.publish['ItemPositionHasChanged'].append( Bind(self._nodeMoved, nodename) )
            node.publish['hoverEnterEvent'].append( Bind(self._nodeHoverEnter, nodename) )
            node.publish['hoverLeaveEvent'].append( Bind(self._nodeHoverLeave, nodename) )

            self.graph.node[nodename]['ui']= NetNode(node)
            self.graph.node[nodename]['ui'].setSize( self.NODE_SIZE )

        # 构建Edge
        for src,dst in self.graph.edges():
            if 'ui' in self.graph[dst][src]:# 反向已有, 不重复建立
                continue

            edge= Edge( self.graph.node[src]['ui'].pos(), self.graph.node[dst]['ui'].pos() )

            self.graph[src][dst]['ui']= NetEdge(edge, True) # True 正向
            self.graph[dst][src]['ui']= NetEdge(edge, False) # False 反向

        #---------------------------------------------------------------------------------------------------------------
        # DEBUG Node
        for nodename in self.graph:
            self.graph.node[nodename]['ui'].setName( str(nodename) )
            self.graph.node[nodename]['ui'].setAbstract( '0123456789\n0123456789' )
        # DEBUG Edge
        for src,dst in self.graph.edges():
            self.graph[src][dst]['ui'].setText("%s,%s" % (src, dst))
            self.graph[dst][src]['ui'].setText("%s,%s" % (dst, src))
        # DEBUG 布局
        # self._graphLayout(self.EDGE_LEN, 50) # 只能排在'构建Node'和'构建Edge'之后调用

        self.addToScene()

    def nodes(self):
        for nodename in self.graph:
            yield self.graph.node[nodename]['ui']

    def node(self, nodename):
        return self.graph.node[nodename]['ui']

    #-------------------------------------------------------------------------------------------------------------------
    def addToScene(self):
        for nodename in self.graph:
            net_node= self.graph.node[nodename]['ui']
            self.scene.addItem( net_node.node )

        for src,dst in self.graph.edges():
            net_edge= self.graph[dst][src]['ui']
            self.scene.addItem( net_edge.edge ) # addItem不怕重复添加

        self.scene.setSceneRect( self.scene.itemsBoundingRect() )
        self.scene.update()


    def removeFromScene(self):
        for nodename in self.graph:
            net_node= self.graph.node[nodename]['ui']
            self.scene.removeItem( net_node.node )

        for src,dst in self.graph.edges():
            net_edge= self.graph[dst][src]['ui']
            scene.removeItem( net_edge.edge ) # removeItem 不怕删除不存在item

        self.scene.setSceneRect( self.scene.itemsBoundingRect() )
        self.scene.update()

    #-------------------------------------------------------------------------------------------------------------------
    def graphLayout(self, length, times):
        if len(self.graph) > 100: # 节点数量太多, 不进行布局
            return

        ratio= length*length # XXX ratio为此值时, 点之间距离大致为length
        for i in range(0, times):
            for nodename in self.graph:
                self._calculateForces(nodename, ratio)

        rect= self.scene.itemsBoundingRect()
        self.scene.setSceneRect(rect)#TODO 如何减少调用次数???

    def _calculateForces(self, nodename, ratio): # 计算一个节点受力
        force= QPointF(0.0, 0.0)
        weight= len(self.graph[nodename])

        node_pos= self.graph.node[nodename]['ui'].pos()
        for othername in self.graph.nodes():
            other_pos= self.graph.node[othername]['ui'].pos()
            vec= other_pos - node_pos
            vls= vec.x()*vec.x() + vec.y()*vec.y()

            if 0 < vls < (2*self.EDGE_LEN) * (2*self.EDGE_LEN): # vec.length() 小于 2*self.EDGE_LEN 才计算斥力; 2来自于经验
                force -= (vec/vls) * ratio# 空间中节点间为排斥力

            if othername in self.graph[nodename]:
                force += vec/weight # 连接的节点间为吸引力

        self.graph.node[nodename]['ui'].setPos( node_pos + force*0.4 ) #force系数不能为1, 否则无法收敛; 0.4来自于经验,不会变化太快

    #-------------------------------------------------------------------------------------------------------------------
    def _nodeMoved(self, src):
        src_pos= self.graph.node[src]['ui'].pos()
        for dst in self.graph[src]:
            dst_pos= self.graph.node[dst]['ui'].pos()
            self.graph[src][dst]['ui'].adjust( src_pos, dst_pos )
            self.graph[dst][src]['ui'].adjust( dst_pos, src_pos )

    def _nodeHoverEnter(self, src):
        for dst in self.graph[src]:
            self.graph[src][dst]['ui'].showDetail()
            self.graph[dst][src]['ui'].showDetail()

    def _nodeHoverLeave(self, src):
        for dst in self.graph[src]:
            self.graph[src][dst]['ui'].hideDetail()
            self.graph[dst][src]['ui'].hideDetail()

#=======================================================================================================================
class UINetView(QGraphicsView):
    EDGE_LEN= 80 # 默认边长度
    NODE_SIZE= 40 # 默认Node大小ppp
    def __init__(self, parent= None):
        super().__init__( parent )

        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing) # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def setUINet(self, ui_net):
        self.setScene( ui_net.scene )
        self.ui_net= ui_net

    #-------------------------------------------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Up:pass
        elif key == Qt.Key_Down:pass
        elif key == Qt.Key_Left:pass
        elif key == Qt.Key_Right:pass
        elif key == Qt.Key_Plus: self.scaleView(1.2)
        elif key == Qt.Key_Minus: self.scaleView(1/1.2)
        elif key == Qt.Key_P:
            self.ui_net.graphLayout(self.EDGE_LEN, 1)
        else: super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.mouse_start_pos= event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton: #Qt.LeftButton:# 鼠标右键拖动背景
            delta= self.mouse_start_pos - event.pos()
            h_value= self.horizontalScrollBar().value()
            v_value= self.verticalScrollBar().value()
            self.horizontalScrollBar().setValue( delta.x() + h_value )
            self.verticalScrollBar().setValue( delta.y() + v_value )
            self.mouse_start_pos= event.pos()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        # self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))
        if event.angleDelta().y() < 0: # 简化版
            self.scaleView(0.7)
        else:
            self.scaleView( 1/0.7 )

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if 0.07< factor < 100:
            self.scale(scaleFactor, scaleFactor)

#=======================================================================================================================
if __name__ == '__main__':
    import sys, networkx
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import qsrand, QTime
    from core.common import log
    log.level= log.LEVEL.WARING

    # graph= networkx.grid_2d_graph(10, 10)
    # graph= networkx.balanced_tree(2, 4)
    # graph= networkx.watts_strogatz_graph(20, 4, 0.3)
    graph = networkx.random_graphs.barabasi_albert_graph(30, 1)
    graph= networkx.DiGraph(graph)

    app = QApplication(sys.argv)
    qsrand(  QTime(0,0,0).secsTo( QTime.currentTime() )  )

    widget = UINetView()
    net= UINet(graph)

    widget.setGeometry(100, 100, 800, 500)
    widget.setUINet( net )
    widget.show()
    sys.exit(app.exec_())

    # from core.common import timeProfile
    # timeProfile('app.exec_()')



