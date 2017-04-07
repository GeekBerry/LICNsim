from PyQt5.QtCore import (QRectF, Qt, pyqtSlot, pyqtSignal)
from PyQt5.QtGui import (QPainter, QColor)
from PyQt5.QtWidgets import QGraphicsView


# TODO 如何解决UINet, ICNNet和DB常作为参数的问题
# TODO 类似于Filer的图形界面数据更新器, 思考:不显示的是否要后台更新
# FIXME 概率性的崩溃


from core.clock import clock
from core.common import AnnounceTable, showCall
from core.data_structure import SheetTable


def HotColor(value):
    color= QColor()
    color.setHsvF(0.3*(1-value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color

def DeepColor(value, h= 0.0):  # h:0.0为红色
    color= QColor()
    color.setHsvF(h, value, 1.0)
    return color

#=======================================================================================================================
class NetView(QGraphicsView):
    MODE_NONE, MODE_CS, MODE_HIT= 0, 1, 2
    setLabelText= pyqtSignal(str)  # 显示标签信号

    def __init__(self, parent= None):
        super().__init__(parent)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        self.setRenderHint(QPainter.Antialiasing)  # 设置线段抗锯齿
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.publish= AnnounceTable()
        self.mode= self.MODE_NONE
        self.show_name= None  # 当前显示的PacketName
        self.label_text= '拓扑图'

    def install(self, announces, api):
        # 监听的 announce
        announces['playSteps'].append(self.refresh)
        # 发布的 announce
        # 提供的 API
        api['View::viewStores']= self.viewStores
        # 调用的 API
        # self.api= api

    def setNet(self, icn_net, ui_net, db):
        self.icn_net= icn_net
        self.ui_net= ui_net
        self.db= db

        self.setScene(ui_net)
        self.refresh()

    #-------------------------------------------------------------------------------------------------------------------
    @pyqtSlot()
    def viewStores(self, packet_name= None):
        if packet_name:  # 显示名字有更新
            self.show_name= packet_name
        self.mode= self.MODE_CS
        self.refresh()

    @pyqtSlot()
    def viewHits(self):
        self.mode= self.MODE_HIT
        self.refresh()

    #-------------------------------------------------------------------------------------------------------------------
    def refresh(self, *args):
        if self.mode == self.MODE_CS:
            self._paintStore()
        elif self.mode == self.MODE_HIT:
            self._paintHitRatio()

        self.ui_net.update()
        self.setLabelText.emit(self.label_text)  # 显示标签

    def _paintHitRatio(self):
        DELTA= 4000  # FIXME 4000 delta如何确定
        # 表名
        self.label_text= '缓存命中图'
        # 统计记录
        time= clock.time()
        records= self.db.node_t(time= lambda t: time-DELTA < t <= time)
        hit_miss_dict= SheetTable(hit=int, miss=int)
        for node_record in records:
            entry= hit_miss_dict[ node_record['node_name'] ]
            entry.hit += node_record['hit']
            entry.miss += node_record['miss']
        # 计算命中率
        for node_name, entry in hit_miss_dict.items():
            if entry.hit:
                ratio= entry.hit / (entry.miss + entry.hit)
                self.ui_net.node(node_name).setColor( HotColor(ratio) )
            else:
                self.ui_net.node(node_name).setColor( Qt.lightGray )

    def _paintStore(self):
        self.label_text= f'"{self.show_name}" CS缓存图'
        # clear
        for ui_node in self.ui_net.nodes():
            ui_node.setColor(Qt.white)

        if self.show_name:
            for node_name in self.db.contents[self.show_name]:
                self.ui_net.node(node_name).setColor(Qt.red)

    #-------------------------------------------------------------------------------------------------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_P:
            self.ui_net.graphLayout(1)
        elif key == Qt.Key_Space:
            self.playStep()
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


#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys, networkx
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import qsrand, QTime
    from core.data_structure import CallTable
    from core.common import log
    from visualizer.ui_net import UINet
    log.level= log.LEVEL.WARING

    # graph= networkx.grid_2d_graph(10, 10)
    # graph= networkx.balanced_tree(2, 4)
    # graph= networkx.watts_strogatz_graph(20, 4, 0.3)
    graph = networkx.random_graphs.barabasi_albert_graph(30, 1)
    graph= networkx.DiGraph(graph)

    app = QApplication(sys.argv)
    qsrand(  QTime(0,0,0).secsTo( QTime.currentTime() )  )


    announces= AnnounceTable()
    api= CallTable()

    view = NetView()
    view.install(announces, api)

    ui_net= UINet(graph)  # 要在UINetView后建立
    view.setNet(None, ui_net, None)


    view.setGeometry(100, 100, 800, 500)
    view.show()
    sys.exit(app.exec_())

    # from core.common import timeProfile
    # timeProfile('app.exec_()')




