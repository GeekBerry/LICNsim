import numpy
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem

from core import CallTable, Timer, threshold
from debug import showCall


def getAngle(p1, p2):
    return numpy.arctan2(p2.y() - p1.y(), p2.x() - p1.x()) * 180 / numpy.pi


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
    LINE_WIDTH = 1
    OFFSET = 8  # 方向线偏离中心线的距离
    MIN_ARROW_WIDTH, MAX_ARROW_WIDTH = 1, 8

    def __init__(self, edge_id):
        super().__init__()
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.edge_id = edge_id
        self.call_backs = CallTable()
        self.text_item = QGraphicsSimpleTextItem('', self)
        self.text_item.setZValue(4)

        self.style = {
            'name': f'Edge{edge_id}',
            'color': Qt.black,
            'width': 0.5,  # 0~1 的中间值
            'show_arrow': False,

            'text': '',
            'text_color': Qt.black,
            'show_text': False,
        }
        self.hover= False

    def type(self):
        return QGraphicsItem.UserType + abs(hash(EdgeItem))

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path = QPainterPath()
        path.addPolygon(self.shape_polygon)
        path.closeSubpath()
        return path

    # -------------------------------------------------------------------------
    def adjust(self, src_p: QPointF, dst_p: QPointF):
        self.angle = getAngle(src_p, dst_p)

        self.src_p = src_p
        self.arrow_p = (src_p + 2 * dst_p) / 3  # 箭头开始位置, 前端2/3处
        self.dst_p = dst_p

        W1 = 1 * self.OFFSET
        W2 = 2 * self.OFFSET
        W3 = 3 * self.OFFSET

        vec = getRightOffsetVector(self.angle)
        self.arrow_polygon = QPolygonF([
            src_p + vec * W1,
            dst_p + vec * W1,
            self.arrow_p + vec * W2,
            self.arrow_p + vec * W1])

        self.shape_polygon = QPolygonF([
            src_p,
            src_p + vec * W2,
            dst_p + vec * W2,
            dst_p])

        self.bounding_rect = QRectF(src_p, dst_p).normalized()  # normalized 正方向
        self.bounding_rect.adjust(-W3, -W3, W3, W3)

        self.text_p = ((src_p + dst_p) / 2) + vec * W1
        self.text_item.setPos(self.text_p)
        self.prepareGeometryChange()

    # -------------------------------------------------------------------------
    def paint(self, painter, option, widget=None):
        if self.style['show_arrow'] or self.hover:
            width = threshold(0.0, self.style['width'], 1.0)
            width = width * (self.MAX_ARROW_WIDTH - self.MIN_ARROW_WIDTH) + self.MIN_ARROW_WIDTH

            painter.setPen(QPen(self.style['color'], width))
            painter.setBrush(self.style['color'])
            painter.drawPolygon(self.arrow_polygon)
        else:
            # TODO 定制线类型 虚线或实线
            painter.setPen(QPen(Qt.black, self.LINE_WIDTH))
            painter.drawLine(self.src_p, self.dst_p)

        if (self.style['show_arrow'] and self.style['show_text']) or self.hover:
            self.text_item.setPen(self.style['text_color'])
            self.text_item.setText(f"{self.style['name']}\n{self.style['text']}")
            self.text_item.show()
        else:
            self.text_item.hide()

    # -------------------------------------------------------------------------
    def mouseDoubleClickEvent(self, event):
        self.call_backs['mouseDoubleClickEvent'](self.edge_id)
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.hover= True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hover= False
        self.update()
        super().hoverLeaveEvent(event)

    # -------------------------------------------------------------------------
    def setStyle(self, style) -> None:
        for key in self.style:
            try:
                self.style[key] = style[key]
            except KeyError:
                pass
        self.update()