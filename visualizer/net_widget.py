
from PyQt5.QtWidgets import QGraphicsView, QAction, QToolBar, QDockWidget, QFileDialog, QWidget, QFrame, QGridLayout

from debug import showCall


class NetWidget(QWidget):
    @showCall
    def __init__(self, parent):
        super().__init__(parent)
        from visualizer.ui.ui_net_view import Ui_FormNetView
        self.ui= Ui_FormNetView()
        self.ui.setupUi(self)

    def init(self, scene):
        self.ui.net_view.setScene(scene)

    def install(self, announces, api):
        self.ui.net_view.install(announces, api)
        self.ui.net_view.setLabelNode= self.ui.label_node.setText
        self.ui.net_view.setLabelEdge= self.ui.label_edge.setText
