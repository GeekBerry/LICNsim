from PyQt5.QtCore import (QRectF, Qt)
from PyQt5.QtGui import (QPainterPath)
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem

from debug import showCall
from core.data_structure import CallTable
from visualizer.common import threshold

class NodeItem(QGraphicsItem):  # 面向图形界面, 负责控制显示效果
    def __init__(self, node_name):
        super().__init__()
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # 面向UINet 负责增添逻辑操作
        self.node_name= node_name
        self.call_backs= CallTable()
        self.text_item= QGraphicsSimpleTextItem('', self)

        # 面向图形界面, 负责控制显示效果
        self.style= {
            'min_size': 20,
            'max_size': 80,

            'color': Qt.white,

            'show_text': False,
            'text_color': Qt.black,
            'name_content': f'Node {node_name}\n',
            'text_content': '',
            }

        self.bounding_rect= QRectF()

    def type(self)->int:
        return QGraphicsItem.UserType + abs(hash(NodeItem))

    def boundingRect(self):
        return self.bounding_rect

    def shape(self):
        path = QPainterPath()
        path.addRect( self.bounding_rect )
        return path

    def paint(self, painter, option, widget= None)->None:
        #绘制节点
        painter.setBrush(self.style['color'])
        painter.drawEllipse(self.bounding_rect) # painter.drawRect(self.bounding_rect) TODO 形状可定制 Pixmap
        # 绘制说明
        if self.style['show_text']:
            self.text_item.setPen( self.style['text_color'])
            self.text_item.setText( self.style['name_content'] + self.style['text_content'] )
            self.text_item.show()
        else:
            self.text_item.hide()

    # ------------------------------------------------------------------------------------------------------------------
    def setText(self, text)->None:
        self.style['text_content']= text

    def showText(self, steps= None):  # TODO steps
        self.style['show_text']= True
        self.update()

    def hideText(self):
        self.style['show_text']= False
        self.update()

    def setSize(self, size:float):
        # 缓存size
        if hasattr(self, 'size_cache') and self.size_cache == size:
            return
        else:
            self.cache_size= size

        MAX, MIN= self.style['max_size'], self.style['min_size']
        size= threshold(0.0, size, 1.0)*(MAX-MIN) + MIN
        self.bounding_rect= QRectF(-size/2, -size/2, size, size)
        self.update()

    def setColor(self, color)->None:
        self.style['color']= color
        self.update()
    #-------------------------------------------------------------------------------------------------------------------
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.call_backs['ItemPositionHasChanged'](self.node_name)
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        self.call_backs['mouseDoubleClickEvent'](self.node_name)
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.showText()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hideText()
        super().hoverLeaveEvent(event)
