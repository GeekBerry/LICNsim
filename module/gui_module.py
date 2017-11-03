import sys

from PyQt5.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from module import MoudleBase


class GUIModule(MoudleBase):
    def __init__(self):
        self.app = QApplication(sys.argv)  # 必须放在MainWindow前
        self.main_window= MainWindow(None)

    def setup(self, sim):
        super().setup(sim)
        self.main_window.install(sim.announces, sim.api)
        self.main_window.show()
        setattr(sim, 'show', self.show)

    def show(self):
        self.sim.announces['playSteps'](0)  # XXX 放在窗口显示后, 用于初始化各个部件
        self.app.exec_()