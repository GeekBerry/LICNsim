#usr/bin/python3
#coding=utf-8

from PyQt5.QtCore import (Qt, QLine, QPoint, QRectF, QSize)
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsScene, QGraphicsView)
from PyQt5.QtGui import (QPainter, QPen, QWheelEvent ,QGuiApplication)


class Line(QGraphicsItem):# DEBUG
    def __init__(self):
        super().__init__()
        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def paint(self, painter, option, widget):
        painter.setPen( QPen(Qt.green, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin) )
        painter.drawLine(  QLine( QPoint(0,0), QPoint(0,100) )  )
        #painter.drawLine(  QLineF( QPointF(100,0), QPointF(100,100) )  )

        painter.setPen( QPen(Qt.red, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin) )
        painter.drawLine(  QLine( QPoint(0,0), QPoint(100,0) )  )
        #painter.drawLine(  QLineF( QPointF(0,100), QPointF(100,100) )  )

    def boundingRect(self):
        return QRectF( QPoint(0,0), QPoint(1,1) )



class NetWorkGraphicsScene(QGraphicsScene):#场景
    SIZE= QSize(100,100) # TODO
    def __init__(self):
        super().__init__()
        self.setSceneRect( -self.SIZE.width()//2, -self.SIZE.height()//2, self.SIZE.width(), self.SIZE.height() )
        self.setup()

    def setup(self):
        self.addItem( Line() )



class NetWorkGraphWidget(QGraphicsView):
    SCALE_MIN_RATE=     0.1
    SCALE_MAX_RATE=     10.0
    SCALE_STEP_RATE=    1.414

    def __init__(self, *args):
        super().__init__(*args)
        self.setCacheMode(QGraphicsView.CacheBackground) #设置缓存模式 CacheNone, CacheBackground
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate) # BoundingRectViewportUpdate
        self.setRenderHint(QPainter.Antialiasing) # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse) # 设置矩阵变化中心 NoAnchor, AnchorViewCenter, AnchorUnderMouse
        #self.setResizeAnchor(QGraphicsView.NoAnchor) # NoAnchor, AnchorViewCenter, AnchorUnderMouse
        self.setDragMode(QGraphicsView.ScrollHandDrag) #设置拖拽 NoDrag, ScrollHandDrag, RubberBandDrag

    def wheelEvent(self, event):# 滚轮实现放缩
        scale_rate= self.transform().m11()# "m11()"时x方向上的放缩倍率
        if event.angleDelta().y() > 0 :
            if scale_rate < self.SCALE_MAX_RATE: # 变大
                self.scale( self.SCALE_STEP_RATE, self.SCALE_STEP_RATE)
        else:
            if self.SCALE_MIN_RATE < scale_rate: # 变小
                self.scale( 1/self.SCALE_STEP_RATE, 1/self.SCALE_STEP_RATE )
