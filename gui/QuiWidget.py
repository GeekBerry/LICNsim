class UIFrom:  # 装饰器
    def __init__(self, UI_From):
        """
        :param UI_From: 要使用的UI_From类名
        """
        self.UI_From= UI_From

    def __call__(self, cls):
        def creater(*args, **kwargs):
            widget= cls(*args, **kwargs)
            widget.ui= self.UI_From()
            widget.ui.setupUi(widget)
            return widget
        return creater



# ======================================================================================================================
from PyQt5.QtWidgets import QMainWindow
from gui.ui.main_window import Ui_main_window

from gui.plugin import PlayerPlugin, DocksPlugin


@UIFrom(Ui_main_window)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(None)

    def install(self, announces, api):
        self.announces= announces
        self.api= api

        PlayerPlugin(self).install(announces, api)
        # DocksPlugin(self).install(announces, api)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from visualizer.ui.ui_main_window import Ui_main_window
    from core.data_structure import AnnounceTable, CallTable

    app = QApplication(sys.argv)  # 必须放在MainWindow前

    main_window= MainWindow()
    main_window.install( AnnounceTable(), CallTable() )
    main_window.show()

    sys.exit(app.exec_())
