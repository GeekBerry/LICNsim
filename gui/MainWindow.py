from PyQt5.QtWidgets import QMainWindow, QDockWidget
from PyQt5.QtCore import Qt

from gui.common import UIFrom
from gui.NetScene import NetScene
from gui.ui.main_window import Ui_main_window

from debug import showCall


@UIFrom(Ui_main_window)
class MainWindow(QMainWindow):
    def __init__(self, parent, announces, api):
        self.announces= announces
        self.api= api

        self.scene = NetScene(self, announces, api)
        self.ui.net_view.setScene(self.scene)

        self.plugins= {}  # 保存 plugin ，使得 plugin 生命期同 self 一样长

    def addPlugin(self, text, PluginFactor):
        self.plugins[text]= PluginFactor(self, self.announces, self.api)

    def addDockPlugin(self, text, PluginFactor, area=Qt.BottomDockWidgetArea):
        plugin= PluginFactor(self, self.announces, self.api)
        dock= QDockWidget(text, self)
        dock.setWidget(plugin)
        self.addDockWidget(area, dock)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from core import AnnounceTable, CallTable

    app = QApplication(sys.argv)  # 必须放在MainWindow前

    main_window = MainWindow(None, AnnounceTable(), CallTable())
    main_window.show()

    sys.exit(app.exec_())
