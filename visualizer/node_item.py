from PyQt5.QtCore import (QRectF, QRect, QPoint, Qt)
from PyQt5.QtGui import (QPainterPath, QFont, QFontMetrics)
from PyQt5.QtWidgets import QGraphicsItem


from core.data_structure import CallTable


class NodeItem(QGraphicsItem):  # 面向图形界面, 负责控制显示效果
    def __init__(self, node_name):
        super().__init__()
        self.setZValue(2)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        # 面向图形界面, 负责控制显示效果
        self.style= {
            'rect': QRectF(),
            'color': Qt.white,

            'show_text':False,
            'name':'',
            'abstract':'',
            'abstract_rect':QRectF(),
            }
        self.setFont( QFont('Courier New', 10, QFont.Normal) )
        # 面向UINet 负责增添逻辑操作
        self.node_name= node_name
        self.call_backs= CallTable()

    def type(self)->int:
        return QGraphicsItem.UserType + abs(hash(NodeItem))

    def boundingRect(self):
        return self.style['rect'] | self.style['abstract_rect']

    def shape(self):
        path = QPainterPath()
        path.addRect( self.style['rect'] )
        return path

    def paint(self, painter, option, widget= None)->None:
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

    #-------------------------------------------------------------------------------------------------------------------
    def setFont(self, font)->None:
        self.font= font
        self.metrics= QFontMetrics(font)

    def setIsShowText(self, is_show_text:bool)->None:
        self.style['show_text']= is_show_text
        self.update()

    def setName(self, name)->None:
        self.style['name']= name
        self.update()

    def setAbstract(self, abstract)->None:
        self.style['abstract']= abstract
        # 计算文字矩形
        rect= self.metrics.boundingRect( QRect(), Qt.AlignTop|Qt.AlignLeft, abstract )
        rect.moveCenter(   QPoint(  0, -( rect.height()+self.style['rect'].height() )/2  )   )  # 将rect中点放到上方
        self.style['abstract_rect']= QRectF(rect)
        self.update()

    def setSize(self, size)->None:
        self.style['rect']= QRectF(-size/2, -size/2, size, size)
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
        self.setIsShowText(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setIsShowText(False)
        super().hoverLeaveEvent(event)
