import sys

from PyQt5.QtWidgets import QApplication

from MainWindow import MainWindow
from common import Unit
from debug import showCall


class GUIModule(Unit):
    def __init__(self):
        self.app = QApplication(sys.argv)  # 必须放在MainWindow前
        self.main_window= MainWindow(None)

    def install(self, announces, api):
        super().install(announces, api)
        self.main_window.install(self.announces, self.api )
        api['Gui.start']= self.start

    @showCall
    def start(self):
        self.main_window.show()
        self.announces['playSteps'](0)  # 放在窗口显示后, 用于初始化各个部件
        return self.app.exec_()


