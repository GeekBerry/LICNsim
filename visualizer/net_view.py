from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsView


from visualizer.painters import *

from core.packet import Packet
from core.clock import clock
from core.data_structure import SheetTable
from debug import showCall
from visualizer.common import HotColor, TransferRecordToText
from visualizer.ui_net import UINetHelper


# ======================================================================================================================
class NetView(QGraphicsView):  # TODO 重构, 缓存
    def __init__(self, parent= None):
        super().__init__(parent)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)  # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.setLabelNode= None
        self.setLabelEdge= None
        self.node_painter= None
        self.edge_painter= None

    def install(self, announces, api):
        self.announces= announces
        self.api= api

        announces['playSteps'].append(self.refresh)
        api['NetView::triggerPainter']= self.triggerPainter
        api['NetView::refreshPainter']= self.refreshPainter

    @showCall
    def triggerPainter(self, painter, *args):  # 设置,刷新和显示painter
        if isinstance(painter, NodePainter):
            self.node_painter= painter
            self.node_painter.refresh()
            # 设置背景颜色
            bg_color= self.node_painter.style.get('back_ground_color', Qt.white)
            self.setBackgroundBrush(bg_color)
            # 设置标题
            title= self.node_painter.style.get('title', '(未知)')
            self.setLabelNode(title)
        elif isinstance(painter, EdgePainter):
            self.edge_painter= painter
            self.edge_painter.refresh()
            # 设置标题
            title= self.edge_painter.style.get('title', '(未知)')
            self.setLabelEdge(title)
        else:
            return

    @showCall
    def refreshPainter(self, painter):  # 如果painter为当前使用的painter, 立刻刷新
        if painter is self.node_painter:
            self.node_painter.refresh()
            # 设置标题
            title= self.node_painter.style.get('title', '(未知)')
            self.setLabelNode(title)
        elif painter is self.edge_painter:
            self.edge_painter.refresh()
            # 设置标题
            title= self.edge_painter.style.get('title', '(未知)')
            self.setLabelEdge(title)
        else:
            pass

    @showCall
    def refresh(self, *args):  # FIXME
        if self.node_painter:
            self.node_painter.refresh()

        if self.edge_painter:
            self.edge_painter.refresh()

    # ------------------------------------------------------------------------------------------------------------------
    # def keyPressEvent(self, event):
    #     key = event.key()
        # if key == Qt.Key_P:
        #     self.scene().graphLayout()
        # elif key == Qt.Key_Enter:
        #     self.api['Player::step']()
        # else: super().keyPressEvent(event)

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

    @showCall
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




# ----------------------------------------------------------------------------------------------------------------------
# class Animation:
#     @staticmethod
#     def Script():
#         return SheetTable(show_edge=list, hide_edge=list)
#
#     @showCall
#     def __init__(self, graph, script):
#         self.graph= graph
#         self.script= script
#         self.time_list= sorted(  list( script.keys() )  )
#         self.index= None
#
#     def __bool__(self):
#         return (self.index is not None) and (self.index < len(self.time_list))
#
#     @showCall
#     def start(self):
#         self.index= 0
#         self.clearScreen()
#
#     @showCall
#     def step(self):
#         if self:
#             t= self.time_list[self.index]
#             for record in self.script[t].show_edge:
#                 self.showRecord(record)
#             for record in self.script[t].hide_edge:
#                 self.hideRecord(record)
#
#             self.index+=1
#
#     def showRecord(self, record):
#         ui_edge= UINetHelper.edge(self.graph, record['src'], record['dst'])
#         ui_edge.setColor(Qt.green)
#         ui_edge.setText(TransferRecordToText(record))
#         ui_edge.showText()
#
#     def hideRecord(self, record):
#         ui_edge= UINetHelper.edge(self.graph, record['src'], record['dst'])
#         ui_edge.setText('')
#
#         if record['state'] == TransferState.ARRIVED:
#             ui_edge.setColor(Qt.darkGreen)
#         elif record['state'] == TransferState.LOSS:
#             ui_edge.setColor(Qt.darkRed)
#         elif record['state'] == TransferState.SENDING:
#             ui_edge.setColor(Qt.darkBlue)
#         else:
#             ui_edge.hide()
#
#     @showCall
#     def clearScreen(self):
#         for ui_edge in UINetHelper.edges(self.graph):
#             ui_edge.setColor(Qt.black)
#             ui_edge.setText('')
#             ui_edge.hide()

