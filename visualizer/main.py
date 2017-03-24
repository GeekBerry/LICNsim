import networkx
from visualizer.ui_net import UINet
graph = networkx.random_graphs.barabasi_albert_graph(30, 1)
graph= networkx.DiGraph(graph)

#-----------------------------------------------------------------------------------------------------------------------
import sys
from PyQt5.QtWidgets  import QApplication, QMainWindow
from visualizer.main_window import Ui_main_window

app = QApplication(sys.argv)
main_window = QMainWindow()


ui_main_window= Ui_main_window() # Ui_Form为生成的Form的名字
ui_main_window.setupUi(main_window)

ui_main_window.ui_net_view.setUINet( UINet(graph) ) #放到哪儿去比较好呢?


main_window.show()
sys.exit(app.exec_())
