from PyQt5.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QPolygonF, QFont, QFontMetrics
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem, QGraphicsTextItem

import numpy
from core.data_structure import CallTable, Timer
from debug import showCall
from core.packet import Packet

import random

class EdgeItem(QGraphicsItem):  # 面向图形界面, 负责控制显示效果
    P_0, P_1_3, P_2_3, P_1= 0, 1, 2, 3
    MAX_LINE_WIDTH= 10

    def __init__(self, edge_name:tuple):
        super().__init__()
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        # self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(True)
        # 面向图形界面, 负责控制显示效果
        self.style= {
            'line_color':Qt.black,
            'line_width': 1,

            'show_forward': False,
            'forward_color': Qt.black,
            'forward_width': 1,  # 建议为1~8

            'show_reverse': False,
            'reverse_color': Qt.black,
            'reverse_width': 1,  # 建议为1~8
            }  # 完全依照此渲染
        # 面向UINet 负责增添逻辑操作
        self.edge_name= edge_name
        self.call_backs= CallTable()

        self.hover= False
        self.forward_text= QGraphicsSimpleTextItem('', self)
        self.reverse_text= QGraphicsSimpleTextItem('', self)

    def type(self):
        return QGraphicsItem.UserType + abs(hash(EdgeItem))

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path= QPainterPath()
        path.addPolygon(self.polygon)
        path.closeSubpath()
        return path

    # -------------------------------------------------------------------------
    def adjust(self, src, dst):
        self.points=[src, (2 * src + dst) / 3, (src + 2 * dst) / 3, dst]  # [0, 1/3, 2/3, 1]
        # 角度
        if src.x() == dst.x():
            self.angle = 90 if dst.y() > src.y() else -90
        else:
            self.angle = 360 * numpy.arctan(  ( dst.y()-src.y() )/( dst.x()-src.x() )  ) /(2.0*numpy.pi)
        # 绘制折线
        W= self.MAX_LINE_WIDTH
        V= QPointF(1,-1) if self.angle > 0 else QPointF(-1,-1)
        self.polygon= QPolygonF([ src-W*V, src+W*V, dst+W*V, dst-W*V ])  # 轮廓
        self.forward_polygon= QPolygonF([src - 4*V, dst - 4*V, self.points[self.P_2_3] - 16*V, self.points[self.P_2_3] - 4*V])  # 去向
        self.reverse_polygon= QPolygonF([dst + 4*V, src + 4*V, self.points[self.P_1_3] + 16*V, self.points[self.P_1_3] + 4*V])  # 回向
        # 边界
        self.bounding_rect= QRectF( src, dst ).normalized()  # normalized 正方向
        self.bounding_rect.adjust(-2*W, -2*W, 2*W, 2*W)
        # 字符
        self.adjustForwardText()
        self.adjustReverseText()
        # 通知几何变换
        self.prepareGeometryChange()

    def adjustForwardText(self):
        rect= self.forward_text.boundingRect()
        if self.angle > 0:
            self.forward_text.setPos(self.points[self.P_1_3] - 4*QPointF(1,-1))
            self.forward_text.moveBy(-rect.width(), 0)
        else:
            self.forward_text.setPos(self.points[self.P_1_3] - 4*QPointF(-1,-1))

    def adjustReverseText(self):
        rect= self.reverse_text.boundingRect()
        if self.angle > 0:
            self.reverse_text.setPos(self.points[self.P_2_3] + 4*QPointF(1,-1))
            self.reverse_text.moveBy(0.0, -rect.height())
        else:
            self.reverse_text.setPos(self.points[self.P_2_3] + 4*QPointF(-1,-1))
            self.reverse_text.moveBy(-rect.width(), -rect.height())
    # -------------------------------------------------------------------------
    def paint(self, painter, option, widget= None):
        if self.style['show_forward'] or self.style['show_reverse'] or self.hover:
            if self.style['show_forward'] or self.hover:
                painter.setPen( QPen(self.style['forward_color'], self.style['forward_width']) )
                painter.setBrush(self.style['forward_color'])
                painter.drawPolygon(self.forward_polygon)

            if self.style['show_forward'] and self.hover:
                self.forward_text.setPen(self.style['forward_color'])
                self.forward_text.show()
            else:
                self.forward_text.hide()

            if self.style['show_reverse'] or self.hover:
                painter.setPen( QPen(self.style['reverse_color'], self.style['reverse_width']) )
                painter.setBrush(self.style['reverse_color'])
                painter.drawPolygon(self.reverse_polygon)

            if self.style['show_reverse'] and self.hover:
                self.reverse_text.setPen(self.style['reverse_color'])
                self.reverse_text.show()
            else:
                self.reverse_text.hide()
        else:
            painter.setPen( QPen(self.style['line_color'], self.style['line_width']) )
            painter.drawLine(self.points[self.P_0], self.points[self.P_1])

    # ------------------------------------------------------------------------------------------------------------------
    def setForwardText(self, text):
        self.forward_text.setText(text)
        self.adjustForwardText()

    def setReverseText(self, text):
        self.reverse_text.setText(text)
        self.adjustReverseText()

    # -------------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        self.call_backs['mouseDoubleClickEvent'](self.edge_name)
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.hover= True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hover= False
        self.update()
        super().hoverLeaveEvent(event)


class ForwardEdgeItem:
    def __init__(self, edge_item):
        self.edge_item= edge_item
        self.hide_timer= Timer(self.hide)

    def getArrow(self)->tuple:
        return self.edge_item.edge_name

    def setColor(self, color):
        self.edge_item.style['forward_color']= color
        self.edge_item.update()

    def setText(self, text):
        self.edge_item.setForwardText(text)
        self.edge_item.update()

    def adjust(self, src, dst):
        self.edge_item.adjust(src, dst)

    def show(self, steps= None):
        self.edge_item.style['show_forward']= True
        self.edge_item.update()

        if steps is None:  # 不定时
            self.hide_timer.cancel()
        else:
            self.hide_timer.timing(steps)

    def hide(self):
        self.edge_item.style['show_forward']= False
        self.edge_item.update()


class ReverseEdgeItem:
    def __init__(self, edge_item):
        self.edge_item= edge_item
        self.hide_timer= Timer(self.hide)

    def getArrow(self)->tuple:
        return self.edge_item.edge_name[::-1]

    def setColor(self, color):
        self.edge_item.style['reverse_color']= color
        self.edge_item.update()

    def setText(self, text):
        self.edge_item.setReverseText(text)
        self.edge_item.update()

    def adjust(self, src, dst):
        # 反向边不进行 adjust, 以免重复调用
        pass

    def show(self, steps= None):
        self.edge_item.style['show_reverse']= True
        self.edge_item.update()
        if steps is None:
            self.hide_timer.cancel()
        else:
            self.hide_timer.timing(steps)

    def hide(self):
        self.edge_item.style['show_reverse']= False
        self.edge_item.update()


def getEdgePair(edge_item)->tuple:
    return ForwardEdgeItem(edge_item), ReverseEdgeItem(edge_item)
