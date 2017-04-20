from PyQt5.QtCore import QRectF, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsView


# TODO 如何解决UINet, ICNNet和DB常作为参数的问题
# TODO 类似于Filer的图形界面数据更新器, 思考:不显示的是否要后台更新
# FIXME 概率性的崩溃


from constants import INF
from core.clock import clock
from debug import showCall
from core.data_structure import SheetTable, defaultdict
from visualizer.ui_net import UINetHelper
from visualizer.common import DeepColor, HotColor, threshold

#=======================================================================================================================
class NetView(QGraphicsView):  # TODO 重构, 缓存
    DELTA= 40000  # FIXME  delta如何确定
    def __init__(self, parent= None):
        super().__init__(parent)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)  # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.node_mode= 'topology'
        self.edge_mode= 'empty'

    @showCall
    def init(self, graph, scene, monitor):
        self.graph= graph
        self.setScene(scene)
        self.monitor= monitor

        self.name_store_painter= NameStorePainter(graph, monitor)
        self.hit_ratio_painter= HitRatioPainter(graph, monitor)
        self.transfer_painter= TransferPainter(graph, monitor)
        self.rate_painter= RatePainter(graph, monitor)
        self.refresh()

    def install(self, announces, api):
        # 监听的 announce
        announces['playSteps'].append(self.refresh)
        # 发布的 announce
        # 提供的 API
        api['View::setShowName']= self.setShowName
        api['View::setShowTransfer']= self.setShowTransfer
        # 调用的 API
        self.setLabelNodeText= api['Main::setLabelNetNode']
        self.setLabelNodeText('拓扑图')  # 显示标签
        self.setLabelEdgeText= api['Main::setLabelNetEdge']
        self.setLabelEdgeText('拓扑图')

    def setShowName(self, packet_name):
        self.name_store_painter.show_name= packet_name
        self.showName()

    def setShowTransfer(self, packet_head):
        self.transfer_painter.show_packet_head= packet_head
        self.showTransfer()
    #-------------------------------------------------------------------------------------------------------------------
    @showCall
    def refresh(self, *args):
        if self.node_mode == 'name_store':
            self.name_store_painter.paint()
        elif self.node_mode == 'hit_ratio':
            self.hit_ratio_painter.paint()

        if self.edge_mode == 'transfer':
            self.showTransfer()
        elif self.edge_mode == 'rate':
            self.showRate()

    @showCall
    def showName(self):
        self.node_mode= 'name_store'
        self.setLabelNodeText(f'"{self.name_store_painter.show_name}" CS缓存图')  # 显示标签
        self.refresh()
        self.setBackGround()

    @showCall
    def showHitRatio(self):
        self.node_mode= 'hit_ratio'
        self.setLabelNodeText('缓存命中图')
        self.refresh()
        self.setBackGround()

    @showCall
    def showTransfer(self):
        self.edge_mode= 'transfer'
        self.setLabelEdgeText('传输图')
        self.transfer_painter.paint()

    def showRate(self):
        self.edge_mode= 'rate'
        self.setLabelEdgeText('占用率图')
        self.rate_painter.paint()

    #-------------------------------------------------------------------------------------------------------------------
    def setBackGround(self):
        if self.node_mode == 'name_store':
            self.setBackgroundBrush(QBrush(QColor(255,250,250)))
        elif self.node_mode == 'hit_ratio':
            self.setBackgroundBrush(QBrush(QColor(250,255,250)))
        else:
            self.setBackgroundBrush( QBrush(QColor(255,255,255)) )

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_P:
            self.scene().graphLayout()
        elif key == Qt.Key_Space:
            self.transfer_painter.step()
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
        if event.angleDelta().y() < 0: # 简化版
            self.scaleView(0.7)
        else:
            self.scaleView( 1/0.7 )

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if 0.01< factor < 10:
            self.scale(scaleFactor, scaleFactor)

# ======================================================================================================================
class Painter:
    def __init__(self, graph, monitor):
        self.show_time= -1 # 比0小即可
        self.graph= graph
        self.monitor= monitor

    def paint(self):
        pass

# ----------------------------------------------------------------------------------------------------------------------
class NameStorePainter(Painter):
    def __init__(self, graph, monitor):
        super().__init__(graph, monitor)
        self.show_name= None

    def paint(self):
        paint_dict= self.calculate()
        for node_name, value in paint_dict.items():
            ui_node= UINetHelper.node(self.graph, node_name)
            ui_node.setText(' ')
            if value is True:
                ui_node.setColor(Qt.red)
            else:
                ui_node.setColor(Qt.white)

    def calculate(self):
        contents= self.monitor.contents.get(self.show_name, [])  # TODO match 或 前缀查找等

        store_dict= dict.fromkeys(self.graph)
        for node_name in store_dict:
            if node_name in contents:
                store_dict[node_name]= True
            else:
                store_dict[node_name]= False
        return store_dict

# ----------------------------------------------------------------------------------------------------------------------
class HitRatioPainter(Painter):
    def __init__(self, graph, monitor):
        super().__init__(graph, monitor)
        self.delta= 4000  # FIXME

    def paint(self):
        paint_dict= self.calculate()
        for node_name, ratio in paint_dict.items():
            ui_node= UINetHelper.node(self.graph, node_name)
            if ratio is None:
                ui_node.setColor(Qt.lightGray)
                ui_node.setText('无访问记录')
            else:
                UINetHelper.node(self.graph, node_name).setColor(HotColor(ratio))  # DeepColor or HotColor
                UINetHelper.node(self.graph, node_name).setText(f'命中率 {"%0.2f"%(ratio*100)}%')

    def calculate(self):
        time= clock.time()
        records= self.monitor.node_t(time= lambda t: time - self.delta < t <= time)
        hit_miss_dict= SheetTable(hit=int, miss=int)
        for node_record in records:
            entry= hit_miss_dict[ node_record['node_name'] ]
            entry.hit += node_record['hit']
            entry.miss += node_record['miss']
        # 计算命中率
        ratio_dict= dict.fromkeys(self.graph)
        for node_name, entry in hit_miss_dict.items():
            if entry.hit or entry.miss:
                ratio_dict[node_name]= entry.hit / (entry.miss + entry.hit)
        return ratio_dict

# ----------------------------------------------------------------------------------------------------------------------
class TransferPainter(Painter):
    def __init__(self, graph, monitor):
        super().__init__(graph, monitor)
        self.show_packet_head= None
        self.animation= None

    @showCall
    def step(self):
        if self.animation is not None:
            if not self.animation:
                self.animation.start()
            else:
                self.animation.step()

    @showCall
    def paint(self):  # TODO 动画与绘图分离
        self.animation= Animation( self.graph, self.calculate() )
        self.animation.start()
        while self.animation:
            self.animation.step()

    def calculate(self):
        records= self.monitor.transfer_t(packet_head=self.show_packet_head)
        script= Animation.Script()
        for record in records:
            script[ record['begin'] ].show_edge.append( record )
            script[ record['end'] ].hide_edge.append( record )
        return script

# ----------------------------------------------------------------------------------------------------------------------
class RatePainter(Painter):
    def __init__(self, graph, monitor):
        super().__init__(graph, monitor)
        self.delta= 1000  # FIXME

    def paint(self):
        paint_dict= self.calculate()
        for (src, dst), ratio in paint_dict.items():
            ui_edge= UINetHelper.edge(self.graph, src, dst)
            ui_edge.setColor( HotColor(ratio) )
            ui_edge.setText(f'占用率 {"%0.2f"%(ratio*100)}%')
            ui_edge.show()

    def calculate(self):
        t0, t1= clock.time()-self.delta, clock.time()
        records= self.monitor.transfer_t(begin= lambda t: t < t1, end= lambda t: t0 < t )
        # 统计忙碌时长
        rate_dict= dict.fromkeys( self.graph.edges(), 0 )
        for record in records:
            rate_dict[ (record['src'],record['dst']) ] += min(t1, record['end']) - max(t0, record['begin'])
        # 计算占比
        for key in rate_dict:
            rate_dict[key] /= self.delta

        return rate_dict


# ----------------------------------------------------------------------------------------------------------------------
from constants import TransferState
from core.packet import Packet

class Animation:
    @staticmethod
    def Script():
        return SheetTable(show_edge=list, hide_edge=list)

    @showCall
    def __init__(self, graph, script):
        self.graph= graph
        self.script= script
        self.time_list= sorted(  list( script.keys() )  )
        self.index= None

    def __bool__(self):
        return (self.index is not None) and (self.index < len(self.time_list))

    @showCall
    def start(self):
        self.index= 0
        self.clearScreen()

    @showCall
    def step(self):
        if self:
            t= self.time_list[self.index]
            for record in self.script[t].show_edge:
                self.showRecord(record)
            for record in self.script[t].hide_edge:
                self.hideRecord(record)

            self.index+=1

    def showRecord(self, record):
        ui_edge= UINetHelper.edge(self.graph, record['src'], record['dst'])
        ui_edge.setColor(Qt.green)
        ui_edge.setText( toText(record) )
        ui_edge.show()

    def hideRecord(self, record):
        ui_edge= UINetHelper.edge(self.graph, record['src'], record['dst'])
        ui_edge.setText('')

        if record['state'] == TransferState.ARRIVED:
            ui_edge.setColor(Qt.darkGreen)
        elif record['state'] == TransferState.LOSS:
            ui_edge.setColor(Qt.darkRed)
        elif record['state'] == TransferState.SENDING:
            ui_edge.setColor(Qt.darkBlue)
        else:
            ui_edge.hide()

    @showCall
    def clearScreen(self):
        for ui_edge in UINetHelper.edges(self.graph):
            ui_edge.setColor(Qt.black)
            ui_edge.setText('')
            ui_edge.hide()

def toText(record):
    state_str= TransferState.TYPE_STRING[ record['state'] ]
    name_str= record['packet_head'].name
    type_str= Packet.typeStr( record['packet_head'].type )
    nonce_str= '%8X'%(record['packet_head'].nonce)
    begin_str= record['begin']
    end_str= record['end']
    return f'{state_str}\nName:{name_str}\nType:{type_str}\nNonce:{nonce_str}\nBegin:{begin_str}\nEnd:{end_str}'
