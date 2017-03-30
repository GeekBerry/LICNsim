import networkx
from visualizer.ui_net import Screen
from core.common import AnnounceTable, CallTable
from core.common import log, UniformPosition, FixedAsk, Impulse
from example_CB.experiment_node import SimulatCSUnit
from example_CB.experiment_net import Simulation, Filer

log.level= 0

SIZE= 101
graph = networkx.grid_2d_graph(SIZE,SIZE)
graph= networkx.DiGraph(graph)


# TODO 能切换graph

#-----------------------------------------------------------------------------------------------------------------------
import sys
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication, QMainWindow
from visualizer.main_window import Ui_main_window

app = QApplication(sys.argv)
main_window = QMainWindow()

ui_main_window= Ui_main_window()  # Ui_Form 为生成的 Form 的名字
ui_main_window.setupUi(main_window)


announces= AnnounceTable()
api= CallTable()
# QT
ui_main_window.ui_net_view.install(announces, api)  # UINetView
# ICN
sim= Simulation(graph, num_func= Impulse(4*SIZE, FixedAsk()), pos_func= UniformPosition(graph))
sim.install(announces, api)
sim.setCSMode(SimulatCSUnit.MODE.FIFO)
sim.setCSTime(100*SIZE)
sim.setSourceNode((SIZE//2,SIZE//2))  # 要在设置mode之后

filer= Filer('visualizer.txt', sim.name, 1, print_screen= True)
filer.install(announces, api)
# UI
screen= Screen(graph)

for (x,y), node in screen.ui_net.items():
    node.setPos( QPointF(x*200, y*200) )
screen.adaptive()

screen.install(announces, api)



main_window.show()

if __name__ == '__main__' and 1:
    from core.common import timeProfile
    timeProfile('app.exec_()')
    sys.exit()
else:
    sys.exit(app.exec_())




