#!/usr/bin/python3
#coding=utf-8

from PyQt5.QtCore import (QLineF, QPointF, qrand, QRectF, QRect, QPoint, Qt, pyqtSlot)
from PyQt5.QtGui import (QPainter, QPainterPath, QPen, QColor, QPolygonF, QFont, QFontMetrics)
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsView, QGraphicsScene)


import numpy
#-----------------------------------------------------------------------------------------------------------------------
class EdgeItem(QGraphicsItem):
    Type = QGraphicsItem.UserType + 2
    TEXT_HEIGHT= 10
    MAX_LINE_WIDTH= 10

    def __init__(self, src_pos, dst_pos):
        super().__init__()
        self.style= {
            'line_width':2,
            'line_color':Qt.black,

            'show_forward': False,
            'forward_text': '',
            'forward_color': Qt.black,

            'show_reverse': False,
            'reverse_text': '',
            'reverse_color': Qt.black
            }# 完全依照此渲染

        self.adjust(src_pos, dst_pos)
        self.setFont( QFont('Courier New', 10, QFont.Black) )

        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)

    def type(self):
        return EdgeItem.Type

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path= QPainterPath()
        path.addPolygon(self.polygon)
        path.closeSubpath()
        return path

    def setFont(self, font):
        self.font= font
        self.metrics= QFontMetrics(font)

    def adjust(self, src, dst):
        offset= self.MAX_LINE_WIDTH + self.TEXT_HEIGHT
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
        self.bounding_rect= QRectF( self.line.x1(), self.line.y1(), self.line.dx(), self.line.dy() ).normalized()
        self.bounding_rect.adjust(-offset, -offset, offset, offset)
        # 通知几何变换
        self.prepareGeometryChange()

    def paint(self, painter, option, widget= None):
        painter.setPen( QPen(self.style['line_color'], self.style['line_width']) )
        painter.drawLine(self.line)

        if self.style['show_forward'] or self.style['show_reverse']:  # 需要几何变换的绘图操作
            painter.translate(self.middle)  # 以线段中点为原点
            painter.rotate(self.angle)    # 以线段为X轴

            painter.setFont(self.font)
            if self.style['show_forward']:
                self._paintForward(painter)
            if self.style['show_reverse']:
                self._paintReverse(painter)
            # 一系列绘图 ...

    def _paintForward(self, painter):
        text, color= self.style['forward_text'], self.style['forward_color']
        if self.line.dx() >= 0:
            self._paintDownText(painter, text, color)
        else:
            self._paintUpText(painter, text, color)

    def _paintReverse(self, painter):
        text, color= self.style['reverse_text'], self.style['reverse_color']
        if self.line.dx() >= 0:
            self._paintUpText(painter, text, color)
        else:
            self._paintDownText(painter, text, color)

    def _paintUpText(self, painter, text, color):
        line_width= self.style['line_width']
        painter.setPen( QPen(color, line_width) )
        painter.drawText( -self.metrics.width(text)/2, -self.metrics.descent()-line_width, '<'+text)
        painter.drawLine(0,0, -int(self.line.length()/2), 0)

    def _paintDownText(self, painter, text, color):
        line_width= self.style['line_width']
        painter.setPen( QPen(color, line_width) )
        painter.drawText( -self.metrics.width(text)/2, self.metrics.ascent()+line_width, text+'>')
        painter.drawLine(0,0, int(self.line.length()/2), 0)

    # def hoverEnterEvent(self, event):
    #     super().hoverEnterEvent(event)
    #
    # def hoverLeaveEvent(self, event):
    #     super().hoverLeaveEvent(event)

#-----------------------------------------------------------------------------------------------------------------------
from core.common import Timer
from core.packet import Packet
class UINetEdge:
    def __init__(self, edge, is_forward:bool):
        self.edge= edge
        self.is_forward= is_forward
        self.hide_timer= Timer(self.hideDetail)

    #-------------------------------------------------------------------------------------------------------------------
    def _setColor(self, color):
        if self.is_forward:
            self.edge.style['forward_color']= color
        else:
            self.edge.style['reverse_color']= color

    def _setText(self, text):
        if self.is_forward:
            self.edge.style['forward_text']= text
        else:
            self.edge.style['reverse_text']= text

    #-------------------------------------------------------------------------------------------------------------------
    def adjust(self, src, dst):
        if self.is_forward:
            self.edge.adjust(src, dst)
        else:pass # 非正向边不进行调整, 以免重复调用

    def showDetail(self):
        if self.is_forward:
            self.edge.style['show_forward']= True
        else:
            self.edge.style['show_reverse']= True
        self.edge.update()

    def hideDetail(self):
        if self.is_forward:
            self.edge.style['show_forward']= False
        else:
            self.edge.style['show_reverse']= False
        self.edge.update()

    #-------------------------------------------------------------------------------------------------------------------
    def showPacket(self, packet):
        # 设置颜色
        if packet.type == Packet.TYPE.INTEREST:
            self._setColor(Qt.green)
        elif packet.type == Packet.TYPE.DATA:
            self._setColor(Qt.red)
        else:
            self._setColor(Qt.black)
        # 设置文本
        self._setText( repr(packet.name) )
        self.showDetail()

        self.hide_timer.timing(1)

    #TODO def showSpeed(...)

#=======================================================================================================================
from core.common import AnnounceTable
class NodeItem(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self):
        super().__init__()
        self.publish= AnnounceTable()
        self.style= {
            'rect': QRectF(),
            'color': Qt.white,

            'show_text':False,
            'name':'',
            'abstract':'',
            'abstract_rect':QRectF(),
            }
        self.show_detail= False

        self.setFont( QFont('Courier New', 10, QFont.Normal) )

        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def type(self):
        return NodeItem.Type

    def boundingRect(self):
        return self.style['rect'] | self.style['abstract_rect']

    def shape(self):
        path = QPainterPath()
        path.addRect( self.style['rect'] )
        return path

    def setFont(self, font):
        self.font= font
        self.metrics= QFontMetrics(font)

    def setAbstract(self, abstract):
        self.style['abstract']= abstract
        # 计算文字矩形
        rect= self.metrics.boundingRect( QRect(), Qt.AlignTop|Qt.AlignLeft, abstract )
        rect.moveCenter(   QPoint(  0, -( rect.height()+self.style['rect'].height() )/2  )   )  # 将rect中点放到上方
        self.style['abstract_rect']= QRectF(rect)

    def paint(self, painter, option, widget= None):
        #绘制节点
        painter.setBrush(self.style['color'])
        rect= self.style['rect']

        painter.drawEllipse(rect) # painter.drawRect(rect) TODO 形状可定制 Pixmap
        # 绘制说明
        if self.style['show_text']:
            painter.setPen(Qt.black)
            painter.setFont(self.font)
            # 绘制name
            painter.drawText( self.style['rect'], Qt.AlignCenter, self.style['name'])
            # 绘制abstract
            painter.drawText( self.style['abstract_rect'], Qt.AlignTop|Qt.AlignLeft, self.style['abstract'])

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.publish['ItemPositionHasChanged']()
        return super().itemChange(change, value)

    # def mousePressEvent(self, event):
    #     self.update()
    #     super().mousePressEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     self.update()
    #     super().mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        self.style['show_text']= True
        self.publish['hoverEnterEvent']()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.style['show_text']= False
        self.publish['hoverLeaveEvent']()
        super().hoverLeaveEvent(event)

#-----------------------------------------------------------------------------------------------------------------------
class UINetNode:  # TODO 面向NET
    def __init__(self, node):
        self.node= node

    def setName(self, name):
        self.node.style['name']= name

    def setAbstract(self, abstract):
        self.node.setAbstract(abstract)
        self.node.update()

    def setSize(self, size):
        self.node.style['rect']= QRectF(-size/2, -size/2, size, size)
        self.node.update()

    def setColor(self, color):
        self.node.style['color']= color
        self.node.update()

    def pos(self):
        return self.node.pos()

    def setPos(self, point):
        self.node.setPos(point)

#=======================================================================================================================
from core.common import Bind
class UINet:
    EDGE_LEN= 80  # 默认边长度
    NODE_SIZE= 40  # 默认Node大小
    def __init__(self, graph):
        self.graph= graph

        AREA_SIZE= self.EDGE_LEN * len(graph)**0.5  # 来自方形网平均宽度
        # 构建Node
        for nodename in self.graph:
            node= NodeItem()
            node.setPos( qrand()%AREA_SIZE, qrand()%AREA_SIZE )
            node.publish['ItemPositionHasChanged'].append( Bind(self._nodeMoved, nodename) )
            node.publish['hoverEnterEvent'].append( Bind(self._nodeHoverEnter, nodename) )
            node.publish['hoverLeaveEvent'].append( Bind(self._nodeHoverLeave, nodename) )
            self.graph.node[nodename]['ui']= UINetNode(node)
            self.graph.node[nodename]['ui'].setSize(self.NODE_SIZE)
        # 构建Edge
        for src,dst in self.graph.edges():
            if 'ui' in self.graph[dst][src]:  # 反向已有, 不重复建立
                continue
            edge= EdgeItem(self.graph.node[src]['ui'].pos(), self.graph.node[dst]['ui'].pos())
            self.graph[src][dst]['ui']= UINetEdge(edge, True)  # True 正向
            self.graph[dst][src]['ui']= UINetEdge(edge, False)  # False 反向
        #---------------------------------------------------------------------------------------------------------------
        # DEBUG NodeItem
        for nodename in self.graph:
            self.graph.node[nodename]['ui'].setName( str(nodename) )
            self.graph.node[nodename]['ui'].setAbstract( '0123456789\n0123456789' )
        # # DEBUG EdgeItem
        # for src,dst in self.graph.edges():
        #     self.graph[src][dst]['ui'].setText("%s,%s" % (src, dst))
        #     self.graph[dst][src]['ui'].setText("%s,%s" % (dst, src))
    #-------------------------------------------------------------------------------------------------------------------
    def items(self):
        for nodename in self.graph:
            yield nodename, self.graph.node[nodename]['ui']

    def nodes(self):
        for nodename in self.graph:
            yield self.graph.node[nodename]['ui']

    def node(self, nodename):
        return self.graph.node[nodename]['ui']

    def edges(self):
        for src,dst in self.graph.edges():
            yield self.graph[dst][src]['ui']

    def edge(self, src, dst):
        return self.graph[src][dst]['ui']
    #-------------------------------------------------------------------------------------------------------------------
    def graphLayout(self, times):
        if len(self.graph) > 100: # 节点数量太多, 不进行布局
            return

        ratio= self.EDGE_LEN * self.EDGE_LEN # XXX ratio为此值时, 点之间距离大致为length
        for i in range(0, times):
            for nodename in self.graph:
                self._calculateForces(nodename, ratio)

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
            self.graph[src][dst]['ui'].adjust(src_pos, dst_pos)
            self.graph[dst][src]['ui'].adjust(dst_pos, src_pos)

    def _nodeHoverEnter(self, src):
        # for dst in self.graph[src]:
        #     self.graph[src][dst]['ui'].showDetail()
        #     self.graph[dst][src]['ui'].showDetail()
        pass

    def _nodeHoverLeave(self, src):
        # for dst in self.graph[src]:
        #     self.graph[src][dst]['ui'].hideDetail()
        #     self.graph[dst][src]['ui'].hideDetail()
        pass

#=======================================================================================================================
from core.packet import Name  # FIXME
from core.common import debug
from core.common import clock

def HotColor(value):
    color= QColor()
    color.setHsvF(0.3*(1-value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color

class Screen:  # 渲染内容是否要完全依赖DB
    def __init__(self, graph):
        self.scene= QGraphicsScene()
        self.ui_net= UINet(graph)
        self.addUINet(self.ui_net)

    def install(self, announces, api):
        # 监听的 announce
        announces['layout'].append(self.graphLayout)
        announces['step'].append(self.step)
        announces['transfer'].append(self._transfer)
        # 调用的 API
        api['View::setScene'](self.scene)
        self.db= api['DB::self']()

    #-------------------------------------------------------------------------------------------------------------------
    def step(self, steps):
        name= Name([''])  # FIXME 额... 要等于sim中
        # print(self.db.__dict__)

        # clear
        for ui_node in self.ui_net.nodes():
            ui_node.setColor(Qt.white)

        self.showStore(name)
        self.scene.update()

    def showStore(self, packet_name):
        content_nodes= self.db.content_table[packet_name].content
        for node_name in content_nodes:
            self.ui_net.node(node_name).setColor(Qt.red)

    def _transfer(self, src, dst, packet):
        self.ui_net.edge(src, dst).showPacket( packet )

    #-------------------------------------------------------------------------------------------------------------------
    def graphLayout(self):
        self.ui_net.graphLayout(times= 1)  # 迭代一次
        self.adaptive()
        self.scene.update()

    def addUINet(self, ui_net):
        for ui_net_node in ui_net.nodes():
            self.scene.addItem(ui_net_node.node)
        for ui_net_edge in ui_net.edges():
            self.scene.addItem(ui_net_edge.edge)  # addItem不怕重复添加
        self.adaptive()
        self.scene.update()

    def removeUINet(self, ui_net):
        for ui_net_node in ui_net.nodes():
            self.scene.removeItem(ui_net_node.node)
        for ui_net_edge in ui_net.edges():
            self.scene.removeItem(ui_net_edge)  # removeItem 不怕重复删除
        self.adaptive()
        self.scene.update()

    def adaptive(self):
        self.scene.setSceneRect( self.scene.itemsBoundingRect() )

#=======================================================================================================================
class UINetView(QGraphicsView):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)  # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.publish= AnnounceTable()

    @pyqtSlot(bool)
    def buttonSlot(self, bool):
        print('buttonSlot', bool)

    def install(self, announces, api):
        # 发布的 announce
        self.publish['step']= announces['step']
        self.publish['layout']= announces['layout']
        # 提供的 API
        api['View::setScene']= self.setScene
        # 调用的 API
        self.api= api
    #-------------------------------------------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_P:
            self.publish['layout']()
        elif key == Qt.Key_Space:
            self.publish['step'](400)
        else: super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self.mouse_press_pos= event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MiddleButton:  # 鼠标中键拖动背景
            delta= self.mouse_press_pos - event.pos()
            h_value= self.horizontalScrollBar().value()
            v_value= self.verticalScrollBar().value()
            self.horizontalScrollBar().setValue( delta.x() + h_value )
            self.verticalScrollBar().setValue( delta.y() + v_value )
            self.mouse_press_pos= event.pos()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        # self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))
        if event.angleDelta().y() < 0: # 简化版
            self.scaleView(0.7)
        else:
            self.scaleView( 1/0.7 )

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if 0.01< factor < 10:
            self.scale(scaleFactor, scaleFactor)

#=======================================================================================================================
if __name__ == '__main__':
    import sys, networkx
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import qsrand, QTime
    from core.common import log, AnnounceTable, CallTable
    log.level= log.LEVEL.WARING

    # graph= networkx.grid_2d_graph(10, 10)
    # graph= networkx.balanced_tree(2, 4)
    # graph= networkx.watts_strogatz_graph(20, 4, 0.3)
    graph = networkx.random_graphs.barabasi_albert_graph(30, 1)
    graph= networkx.DiGraph(graph)

    app = QApplication(sys.argv)
    qsrand(  QTime(0,0,0).secsTo( QTime.currentTime() )  )

    announces= AnnounceTable()
    api= CallTable()

    view = UINetView()
    view.install(announces, api)

    screen= Screen(graph)
    screen.install(announces, api)

    view.setGeometry(100, 100, 800, 500)
    view.show()
    sys.exit(app.exec_())

    # from core.common import timeProfile
    # timeProfile('app.exec_()')



