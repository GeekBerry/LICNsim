from visualizer.untitled import *
from PyQt5.QtWidgets import QApplication, QWidget
import sys

class DesignerQWidget(QWidget):
    def __init__(self, UiFormClass):
        super().__init__()
        self.form= UiFormClass()
        self.form.setupUi(self)


class TestUI(DesignerQWidget):
    def __init__(self):
        super().__init__(Ui_Form)
        self.ui.pushButton.clicked.connect()


from visualizer.networkgraphwidget import *
app = QApplication(sys.argv)

mainwindow= NetWorkGraphWidget()

uiform= Ui_Form()
uiform.setupUi(mainwindow)
uiform.graphicsView.setScene(  NetWorkGraphicsScene() )

mainwindow.show()
sys.exit(app.exec_())
