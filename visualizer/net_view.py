from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsView


from visualizer.planters import *

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

        self.node_painter= None
        self.edge_painter= None

    def install(self, announces, api):
        self.announces= announces
        self.api= api

        announces['playSteps'].append(self.refresh)
        api['NetView::setBackGroundBrush']= self.setBackgroundBrush
        api['NetView::triggerPainter']= self.triggerPainter

    @showCall
    def triggerPainter(self, painter, boolen= False):
        if isinstance(painter, NodePainter):
            self.api['MainWindow::setLabelNetNode']( painter.title )
            self.setBackgroundBrush( painter.back_ground_color )
            self.node_painter= painter
        elif isinstance(painter, EdgePainter):
            self.api['MainWindow::setLabelNetEdge']( painter.title )
            self.edge_painter= painter
        else:
            pass

        painter.update()
        painter.paint()

    @showCall
    def refresh(self, *args):  # FIXME
        if self.node_painter:
            self.node_painter.update()
            self.node_painter.paint()

        if self.edge_painter:
            self.edge_painter.update()
            self.edge_painter.paint()

    # ------------------------------------------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_P:
            self.scene().graphLayout()
        else: super().keyPressEvent(event)

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


# # ======================================================================================================================
# class Painter:
#     def __init__(self, graph, monitor):
#         self.graph= graph
#         self.monitor= monitor
#
#     def paint(self):
#         pass
#
# # ----------------------------------------------------------------------------------------------------------------------
# from core.icn_net import ICNNetHelper
#
#
# class NodesPainter(Painter):
#     def paint(self):
#         for nodename, ui_node in UINetHelper.nodeItems(self.graph):
#             ui_node.setColor(Qt.white)
#             ui_node.setText('')
#             ui_node.hideText()
#
#             icn_node= ICNNetHelper.node(self.graph, nodename)
#             unit= icn_node.units.get('buffer')
#             if unit:
#                 size= unit.rate/100  # FIXME
#                 ui_node.setSize(size)
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# class NameStorePainter(Painter):
#     def __init__(self, graph, monitor):
#         super().__init__(graph, monitor)
#         self.show_name= None
#
#     def paint(self):
#         paint_dict= self.calculate()
#         for node_name, value in paint_dict.items():
#             ui_node= UINetHelper.node(self.graph, node_name)
#             ui_node.setText(' ')
#             if value is True:
#                 ui_node.setColor(Qt.red)
#             else:
#                 ui_node.setColor(Qt.white)
#
#     def calculate(self):
#         contents= self.monitor.contents.get(self.show_name, [])  # TODO match 或 前缀查找等
#
#         store_dict= dict.fromkeys(self.graph)
#         for node_name in store_dict:
#             if node_name in contents:
#                 store_dict[node_name]= True
#             else:
#                 store_dict[node_name]= False
#         return store_dict
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# class HitRatioPainter(Painter):
#     def __init__(self, graph, monitor):
#         super().__init__(graph, monitor)
#
#         self.last_record_time= -1  # '-1': 比0小即可
#         self.hit_miss_table= SheetTable(hit=int, miss=int)
#
#     def paint(self):
#         paint_dict= self.calculate()
#         for node_name, ratio in paint_dict.items():
#             ui_node= UINetHelper.node(self.graph, node_name)
#             if ratio is None:
#                 ui_node.setColor(Qt.lightGray)
#                 ui_node.setText('无访问记录')
#             else:
#                 UINetHelper.node(self.graph, node_name).setColor(HotColor(ratio))  # DeepColor or HotColor
#                 UINetHelper.node(self.graph, node_name).setText(f'命中率 {"%0.2f"%(ratio*100)}%')
#
#     def calculate(self):
#         records= self.monitor.node_t(time= lambda t: self.last_record_time < t <= clock.time())
#         for node_record in records:
#             entry= self.hit_miss_table[ node_record['node_name']]
#             entry.hit += node_record['hit']
#             entry.miss += node_record['miss']
#         self.last_record_time= clock.time()
#
#         # 计算命中率
#         ratio_dict= dict.fromkeys(self.graph)
#         for node_name, entry in self.hit_miss_table.items():
#             if entry.hit or entry.miss:
#                 ratio_dict[node_name]= entry.hit / (entry.miss + entry.hit)
#         return ratio_dict
#
# # ----------------------------------------------------------------------------------------------------------------------
# from core.channel import Channel
#
#
# class EdgesPainter(Painter):
#     def paint(self):
#         for (src, dst), ui_edge in UINetHelper.edgeItems(self.graph):
#             ui_edge.setColor(Qt.black)
#             ui_edge.setText('')
#             ui_edge.hideText()
#
#             icn_edge= ICNNetHelper.edge(self.graph, src, dst)
#             if isinstance(icn_edge, Channel):
#                 width= icn_edge.rate/10  # FIXME
#                 ui_edge.setWidth(width)
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# from constants import TransferState
#
#
# class TransferPainter(Painter):
#     COLOR_MAP= {
#             TransferState.ARRIVED:  Qt.green,
#             TransferState.SENDING:  QColor(255,160,45),
#             TransferState.LOSS:     Qt.red,
#         }
#
#     def __init__(self, graph, monitor):
#         super().__init__(graph, monitor)
#         self.show_packet_head= None
#
#     @showCall
#     def paint(self):
#         paint_dict= self.calculate()
#         for (src, dst), record in paint_dict.items():
#             ui_edge= UINetHelper.edge(self.graph, src, dst)
#
#             if record  and  (record['state'] in self.COLOR_MAP):
#                 ui_edge.setColor( self.COLOR_MAP[record['state']] )
#                 ui_edge.setText(TransferRecordToText(record))
#                 ui_edge.showText()
#             else:
#                 ui_edge.setColor(Qt.black)
#                 ui_edge.setText('')
#                 ui_edge.hideText()
#
#     def calculate(self):
#         records= self.monitor.transfer_t(packet_head=self.show_packet_head)
#         transfer_dict= dict.fromkeys(self.graph.edges(), {})
#         for record in records:
#             transfer_dict[ (record['src'], record['dst'],) ]= record
#         return transfer_dict
#
#
# # ----------------------------------------------------------------------------------------------------------------------
# class RatePainter(Painter):
#     def __init__(self, graph, monitor):
#         super().__init__(graph, monitor)
#         self.delta= 1000  # FIXME
#
#     def paint(self):
#         paint_dict= self.calculate()
#         for (src, dst), ratio in paint_dict.items():
#             ui_edge= UINetHelper.edge(self.graph, src, dst)
#             ui_edge.setColor( HotColor(ratio) )
#             ui_edge.setText(f'占用率 {"%0.2f"%(ratio*100)}%')
#             ui_edge.showText()
#
#     def calculate(self):
#         t0, t1= clock.time()-self.delta, clock.time()
#         records= self.monitor.transfer_t(begin= lambda t: t < t1, end= lambda t: t0 < t )
#         # 统计忙碌时长
#         rate_dict= dict.fromkeys( self.graph.edges(), 0 )
#         for record in records:
#             rate_dict[ (record['src'],record['dst']) ] += min(t1, record['end']) - max(t0, record['begin'])
#         # 计算占比
#         for key in rate_dict:
#             rate_dict[key] /= self.delta
#
#         return rate_dict
#

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

