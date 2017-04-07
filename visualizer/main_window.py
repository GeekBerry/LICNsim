from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow

from core.clock import clock
from core.common import showCall

from visualizer.ui_node_info import Ui_NodeInfo
from visualizer.node_info_dialog import NodeInfoDialog

class MainWindow(QMainWindow):
    def __init__(self, *args):
        super().__init__(*args)

    def setNet(self, icn_net, ui_net, db):
        self.icn_net= icn_net
        self.ui_net= ui_net
        self.db= db

    @showCall
    def install(self, announces, api):
        self.publish= announces
        self.api= api
        api['Main::showNodeInfo']= self.newNodeInfoDialog

    @pyqtSlot()
    def playSteps(self):
        steps= 400  # TODO 获取steps
        for i in range(0, steps):
            clock.step()
        self.publish['playSteps'](steps)  # 一定要先step, 再publish

    @showCall
    def newNodeInfoDialog(self, node_name):
        dialog= NodeInfoDialog(self)  # 如果不以self为parent, 窗口会一闪而过
        ui_node_info= Ui_NodeInfo()
        ui_node_info.setupUi(dialog)
        dialog.setWindowTitle( f'Node{node_name}信息' )
        dialog.show()
