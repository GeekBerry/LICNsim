from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

from gui.common import UIFrom
from gui.Plugins import PlayerPlugin, PainterPlugin, DocksPlugin, InfoDialogPlugin
from gui.NetScene import NetScene

from gui.ui.main_window import Ui_main_window
from gui.NameTreeWidget import NameTreeWidget

from debug import showCall


@UIFrom(Ui_main_window)
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        self.scene = NetScene()  # DEBUG
        self.ui.net_view.setScene(self.scene)  # DEBUG

    def install(self, announces, api):
        self.announces = announces
        self.api = api

        self.scene.install(announces, api)
        self.addPlugin(PainterPlugin)
        self.addPlugin(PlayerPlugin)
        self.addPlugin(InfoDialogPlugin)
        self.addDockPlugin('Name表', NameTreeWidget)

    def addPlugin(self, PluginType,):
        plugin= PluginType(self)
        plugin.install(self.announces, self.api)

    def addDockPlugin(self, title, WidgetType, area=Qt.BottomDockWidgetArea):
        widget= WidgetType(self)
        widget.install(self.announces, self.api)

        dock= QDockWidget(title, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from core import AnnounceTable, CallTable

    app = QApplication(sys.argv)  # 必须放在MainWindow前

    main_window = MainWindow()
    main_window.install(AnnounceTable(), CallTable())
    main_window.show()

    sys.exit(app.exec_())
