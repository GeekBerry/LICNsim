from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView

from debug import showCall


class NetView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)  # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    # ---------------------------- 实现拖动屏幕 ----------------------------------
    def mousePressEvent(self, event):
        self.mouse_press_pos= event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:  # 鼠标右键拖动背景
            delta= self.mouse_press_pos - event.pos()
            h_value= self.horizontalScrollBar().value()
            v_value= self.verticalScrollBar().value()
            self.horizontalScrollBar().setValue( delta.x() + h_value )
            self.verticalScrollBar().setValue( delta.y() + v_value )
            self.mouse_press_pos= event.pos()
        super().mouseMoveEvent(event)

    # ---------------------------- 实现滚轮放缩 ----------------------------------
    def wheelEvent(self, event):
        # self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))
        if event.angleDelta().y() < 0:  # 简化版
            self.scaleView(0.7)
        else:
            self.scaleView( 1/0.7 )

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if 0.01< factor < 10:
            self.scale(scaleFactor, scaleFactor)
