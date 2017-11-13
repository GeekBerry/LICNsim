import sys

from PyQt5.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from gui.Plugins import PlayerPlugin, PainterPlugin, InfoDialogPlugin, NameInfoPlugin, LogPlugin
from module import MoudleBase


class GUIModule(MoudleBase):
    def __init__(self):
        self.app = QApplication(sys.argv)  # 必须放在 MainWindow 构造前

    def setup(self, sim):
        super().setup(sim)
        sim.show= self.show  # XXX 是否是奇技淫巧

        self.main_window= MainWindow(None, sim.announces, sim.api)
        self.main_window.addPlugin('NameInfoPlugin', NameInfoPlugin)
        self.main_window.addPlugin('LogPlugin', LogPlugin)
        self.main_window.addPlugin('PainterPlugin', PainterPlugin)
        self.main_window.addPlugin('PlayerPlugin', PlayerPlugin)
        self.main_window.addPlugin('InfoDialogPlugin', InfoDialogPlugin)
        self.main_window.show()

    def show(self):
        self.sim.announces['playSteps'](0)  # 在此发布 playSteps，以初始化各个窗口部件
        self.app.exec_()
