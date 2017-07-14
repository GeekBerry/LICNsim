from PyQt5.QtWidgets import QMainWindow
from gui.common import UIFrom
from gui.Plugins import PlayerPlugin, DocksPlugin, PainterPlugin, InfoDialogPlugin
from gui.NetScene import NetScene

from gui.ui.main_window import Ui_main_window

from debug import showCall

@UIFrom(Ui_main_window)
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        self.scene= NetScene()  # DEBUG
        self.ui.net_view.setScene(self.scene)  # DEBUG

    def install(self, announces, api):
        self.announces= announces
        self.api= api

        self.scene.install(announces, api)  # DEBUG
        PainterPlugin(self).install(announces, api)
        PlayerPlugin(self).install(announces, api)
        DocksPlugin(self).install(announces, api)
        InfoDialogPlugin(self).install(announces, api)


# if __name__ == '__main__':
#     import sys
#     from PyQt5.QtWidgets import QApplication, QMainWindow
#     from visualizer.ui.ui_main_window import Ui_main_window
#     from core.data_structure import AnnounceTable, CallTable
#
#     app = QApplication(sys.argv)  # 必须放在MainWindow前
#
#     main_window= MainWindow()
#     main_window.install( AnnounceTable(), CallTable() )
#     main_window.show()
#
#     sys.exit(app.exec_())
#

