import sys

from PyQt5.QtWidgets import QApplication
from gui.MainWindow import MainWindow
from gui.Plugins import PlayerPlugin, PainterPlugin, InfoDialogPlugin, NameInfoPlugin, LogPlugin, LayoutPlugin
from module import MoudleBase


class GUIModule(MoudleBase):
    def __init__(self):
        self.app = QApplication(sys.argv)

    def setup(self, sim):
        self.announces= sim.announces
        self.api= sim.api
        self.start()
        sim.show= self.show

    def start(self):
        self.main_window= MainWindow(None, self.announces, self.api)
        self.main_window.addPlugin('PainterPlugin', PainterPlugin)
        self.main_window.addPlugin('LayoutPlugin', LayoutPlugin)
        self.main_window.addPlugin('PlayerPlugin', PlayerPlugin)
        self.main_window.addPlugin('NameInfoPlugin', NameInfoPlugin)
        self.main_window.addPlugin('LogPlugin', LogPlugin)
        self.main_window.addPlugin('InfoDialogPlugin', InfoDialogPlugin)
        self.main_window.show()

    def show(self):
        self.announces['playSteps'](0)  # 在此发布 playSteps，以初始化各个窗口部件
        self.app.exec_()
