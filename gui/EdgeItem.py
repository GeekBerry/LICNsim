import numpy

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem

from common import threshold
from core.data_structure import CallTable, Timer
from debug import showCall


def getAngle(p1, p2):
    return numpy.arctan2( p2.y() - p1.y(), p2.x() - p1.x() ) * 180 / numpy.pi


def getRightOffsetVector(angle):  # 得到右侧法向量
    if -180 <= angle < -90:
        return QPointF(1, -1)
    elif -90 <= angle < 0:
        return QPointF(1, 1)
    elif 0 <= angle < 90:
        return QPointF(-1, 1)
    elif 90 <= angle <= 180:
        return QPointF(-1, -1)
    else:
        raise ValueError(f'angle {angle} not in [0, 360)')


class EdgeItem(QGraphicsItem):
    def __init__(self, src_id, dst_id):
        super().__init__()
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.src_id= src_id
        self.dst_id= dst_id
        self.call_backs= CallTable()
        self.text_item= QGraphicsSimpleTextItem('', self)
        self.text_item.setZValue(3)

        self.hide_timer= Timer(self.hideText)

        self.style= {
            'line_color': Qt.black,
            'line_width': 1,
            'line_offset': 8, # 箭头偏离中心线的距离

            'show_arrow': False,
            'arrow_color': Qt.black,
            'min_arrow_width': 1,
            'max_arrow_width': 8, # 等于箭头偏离中心线的距离
            'arrow_width': 1,

            'show_text': False,
            'name_content': f'Edge {self.src_id} -> {self.dst_id}\n',
            'text_content': '',
            'text_color':Qt.black,
        }

    def type(self):
        return QGraphicsItem.UserType + abs(hash(EdgeItem))

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path= QPainterPath()
        path.addPolygon(self.shape_polygon)
        path.closeSubpath()
        return path

    # -------------------------------------------------------------------------
    def adjust(self, src_p:QPointF, dst_p:QPointF):
        self.angle= getAngle(src_p, dst_p)

        self.src_p= src_p
        self.arrow_p= (src_p + 2 * dst_p) / 3  # 箭头开始位置, 前端2/3处
        self.dst_p= dst_p

        W1= self.style['line_offset']
        W2= 2 * self.style['line_offset']
        W3= 3 * self.style['line_offset']

        vec= getRightOffsetVector(self.angle)
        self.arrow_polygon= QPolygonF([src_p + vec*W1, dst_p + vec*W1, self.arrow_p + vec*W2, self.arrow_p + vec*W1])
        self.shape_polygon= QPolygonF([src_p, src_p + vec*W2, dst_p + vec*W2, dst_p])

        self.bounding_rect= QRectF(src_p, dst_p).normalized()  # normalized 正方向
        self.bounding_rect.adjust(-W3, -W3, W3, W3)

        self.text_p= ( (src_p + dst_p) / 2 ) + vec*W1
        self.text_item.setPos(self.text_p)
        self.prepareGeometryChange()

    def setText(self, text):
        self.style['text_content']= text

    # DEBUG
    # def showText(self, steps= None):
    #     self.style['show_text']= True
    #     if steps is None:  # 不定时
    #         self.hide_timer.cancel()
    #     else:
    #         self.hide_timer.timing(steps)

    def showText(self):
        self.style['show_text']= True

    def hideText(self):
        self.style['show_text']= False

    def setColor(self, color):
        self.style['arrow_color']= color

    def setWidth(self, width:float):
        MAX, MIN= self.style['max_arrow_width'], self.style['min_arrow_width']
        self.style['arrow_width']= threshold(0.0, width, 1.0)*(MAX-MIN) + MIN

    # -------------------------------------------------------------------------
    def paint(self, painter, option, widget= None):
        if self.style['show_arrow'] or self.style['show_text']:
            painter.setPen( QPen(self.style['arrow_color'], self.style['arrow_width']) )
            painter.setBrush(self.style['arrow_color'])
            painter.drawPolygon(self.arrow_polygon)
        else:
            painter.setPen( QPen(self.style['line_color'], self.style['line_width']) )
            painter.drawLine(self.src_p, self.dst_p)

        if self.style['show_text'] and self.style['show_arrow']:
            self.text_item.setPen(self.style['text_color'])
            self.text_item.setText( self.style['name_content'] + self.style['text_content'] )
            self.text_item.show()
        else:
            self.text_item.hide()

        # DEBUG
        # painter.setPen( QPen(Qt.red, 1) )
        # painter.drawPolygon(self.arrow_polygon)
        #
        # painter.setPen( QPen(Qt.green, 1) )
        # painter.drawPolygon(self.shape_polygon)
        #
        # painter.setPen( QPen(Qt.black, 1) )
        # painter.drawRect( self.bounding_rect )
        #
        # painter.setPen( QPen(Qt.black, 1) )
        # painter.drawRect( self.text_item.boundingRect() )

    # -------------------------------------------------------------------------
    @showCall
    def mouseDoubleClickEvent(self, event):
        self.call_backs['mouseDoubleClickEvent'](self.src_id, self.dst_id)
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.style['show_arrow']= True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.style['show_arrow']= False
        self.update()
        super().hoverLeaveEvent(event)

