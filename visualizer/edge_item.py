from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt)
from PyQt5.QtGui import (QPainterPath, QPen, QPolygonF, QFont, QFontMetrics)
from PyQt5.QtWidgets import QGraphicsItem

import numpy
from core.data_structure import CallTable, Timer
from core.common import showCall
from core.packet import Packet

class EdgeItem(QGraphicsItem):  # 面向图形界面, 负责控制显示效果
    TEXT_HEIGHT= 10
    MAX_LINE_WIDTH= 10

    def __init__(self, edge_name:tuple):
        super().__init__()
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)
        # 面向图形界面, 负责控制显示效果
        self.style= {
            'line_width':2,
            'line_color':Qt.black,

            'show_forward': False,
            'forward_text': '',
            'forward_color': Qt.black,

            'show_reverse': False,
            'reverse_text': '',
            'reverse_color': Qt.black
            }  # 完全依照此渲染
        self.setFont( QFont('Courier New', 10, QFont.Black) )
        # 面向UINet 负责增添逻辑操作
        self.edge_name= edge_name
        self.call_backs= CallTable()

    def type(self):
        return QGraphicsItem.UserType + abs(hash(EdgeItem))

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path= QPainterPath()
        path.addPolygon(self.polygon)
        path.closeSubpath()
        return path

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
    #-------------------------------------------------------------------------------------------------------------------
    def setFont(self, font):
        self.font= font
        self.metrics= QFontMetrics(font)

    def mouseDoubleClickEvent(self, event):
        self.call_backs['mouseDoubleClickEvent'](self.edge_name)
        super().mouseDoubleClickEvent(event)

    # def hoverEnterEvent(self, event):
    #     self.style['show_forward']= True
    #     self.style['show_reverse']= True
    #     super().hoverEnterEvent(event)
    #
    # def hoverLeaveEvent(self, event):
    #     self.style['show_forward']= False
    #     self.style['show_reverse']= False
    #     super().hoverLeaveEvent(event)

class ForwardEdgeItem:
    def __init__(self, edge_item):
        self.edge_item= edge_item
        self.hide_timer= Timer(self.setIsShowText, False)

    def getArrow(self)->tuple:
        return self.edge_item.edge_name

    def setColor(self, color):
        self.edge_item.style['forward_color']= color

    def setText(self, text):
        self.edge_item.style['forward_text']= text

    def adjust(self, src, dst):
        self.edge_item.adjust(src, dst)

    def setIsShowText(self, is_show_text:bool)->None:
        self.edge_item.style['show_forward']= is_show_text
        self.edge_item.update()

    def showPacket(self, packet):
        # 设置颜色
        if packet.type == Packet.TYPE.INTEREST:
            self.setColor(Qt.green)
        elif packet.type == Packet.TYPE.DATA:
            self.setColor(Qt.red)
        else:
            self.setColor(Qt.black)
        # 设置文本
        self.setText(repr(packet.name))
        self.showDetail()

        self.hide_timer.timing(1)

class ReverseEdgeItem:
    def __init__(self, edge_item):
        self.edge_item= edge_item
        self.hide_timer= Timer(self.setIsShowText, False)

    def getArrow(self)->tuple:
        return self.edge_item.edge_name[::-1]

    def setColor(self, color):
        self.edge_item.style['reverse_color']= color

    def setText(self, text):
        self.edge_item.style['reverse_text']= text

    def adjust(self, src, dst):
        # 反向边不进行 adjust, 以免重复调用
        pass

    def setIsShowText(self, is_show_text:bool)->None:
        self.edge_item.style['show_reverse']= is_show_text
        self.edge_item.update()

    def showPacket(self, packet):
        # 设置颜色
        if packet.type == Packet.TYPE.INTEREST:
            self.setColor(Qt.green)
        elif packet.type == Packet.TYPE.DATA:
            self.setColor(Qt.red)
        else:
            self.setColor(Qt.black)
        # 设置文本
        self.setText(repr(packet.name))
        self.showDetail()

        self.hide_timer.timing(1)

def getEdgePair(edge_item)->tuple:
    return ForwardEdgeItem(edge_item), ReverseEdgeItem(edge_item)
