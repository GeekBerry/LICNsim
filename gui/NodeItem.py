from PyQt5.QtCore import QRectF, Qt, QPointF
from PyQt5.QtGui import QPainterPath, QPixmap
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem

from core import threshold, EMPTY_FUNC
from debug import showCall


class NodeItem(QGraphicsItem):  # 面向图形界面, 负责控制显示效果
    MIN_SIZE, MAX_SIZE = 20, 80

    press_callback= EMPTY_FUNC
    release_callback= EMPTY_FUNC
    double_click_callback= EMPTY_FUNC
    move_callback= EMPTY_FUNC

    def __init__(self, node_id):
        super().__init__()

        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable)  # 可以移动
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # 面向UINet 负责增添逻辑操作
        self.node_id = node_id
        self.hover = False
        self.cached_size = None
        self.bounding_rect = QRectF()  # XXX 在重绘时会被更新，重绘前可能会节点可能会被覆盖显示

        # self.call_backs = CallTable()
        self.text_item = QGraphicsSimpleTextItem(self)
        self.text_item.setZValue(3)

        # 面向图形界面, 负责控制显示效果
        self.style = {
            'name': f'Node {node_id}',
            'color': Qt.white,
            'shape': 'Pie',  # ('Pie', 'Rect', QPixmap)
            'size': 0.5,  # 0~1 的中间值

            'text': '',
            'text_color': Qt.black,
            'show_text': False,
        }

    def type(self) -> int:
        return QGraphicsItem.UserType + abs(hash(NodeItem))

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path = QPainterPath()
        path.addRect(self.bounding_rect)
        return path

    def paint(self, painter, option, widget=None) -> None:
        # 绘制尺寸
        size = threshold(0.0, self.style['size'], 1.0)
        size = size * (self.MAX_SIZE - self.MIN_SIZE) + self.MIN_SIZE
        if size != self.cached_size:
            self.bounding_rect = QRectF(-size / 2, -size / 2, size, size)
            self.cached_size = size
        # 绘制图标或颜色和形状
        if isinstance( self.style['shape'], QPixmap):
            pixmap= self.style['shape']
            painter.drawPixmap(  self.bounding_rect, pixmap, QRectF( pixmap.rect() )  )
        elif self.style['shape'] == 'Pie':
            painter.setBrush(self.style['color'])
            painter.drawEllipse(self.bounding_rect)  # or drawRect
        elif self.style['shape'] == 'Rect':
            painter.setBrush(self.style['color'])
            painter.drawRect(self.bounding_rect)  # or drawRect
        else:
            raise ValueError('未知shape类型', self.style['shape'])
        # 绘制说明
        text = f"{self.style['name']}\n"
        if self.style['show_text'] or self.hover:
            text += str(self.style['text'])

        self.text_item.setPen(self.style['text_color'])
        self.text_item.setText(text)
        self.text_item.show()

    # ------------------------------------------------------------------------------------------------------------------
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.style['pos']= self.pos()  # 更新位置变化
            self.move_callback(self.node_id)
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        self.press_callback(self.node_id)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.release_callback(self.node_id)
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.double_click_callback(self.node_id)
        return super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.hover= True
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hover = False
        return super().hoverLeaveEvent(event)

    # ------------------------------------------------------------------------------------------------------------------
    def setStyle(self, style) -> None:
        for key in self.style:
            if key in style:
                self.style[key] = style[key]
        self.update()

    def checkPos(self, x, y):
        pos= QPointF(x,y)
        if self.pos() != pos:
            self.setPos(pos)