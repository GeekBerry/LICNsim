import networkx
from visualizer.ui_net import UINet

from core.data_structure import AnnounceTable, CallTable
from core.common import log, UniformPosition, FixedAsk, ZipfPosition
from core.icn_net import ICNNet, AskGenerator
from core.channel import OneStepChannel
from example_CB.experiment_node import SimulatCSUnit, ExperimentNode
from example_CB.experiment_net import ExperimentMonitorDB
import constants

log.level= 1

SIZE= 11
graph = networkx.grid_2d_graph(SIZE,SIZE)
graph= networkx.DiGraph(graph)
center= (5,5)

# TODO 能切换graph

#-----------------------------------------------------------------------------------------------------------------------
import sys
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication
from visualizer.ui_main_window import Ui_main_window
from visualizer.main_window import MainWindow

app = QApplication(sys.argv)
main_window = MainWindow()

ui_main_window= Ui_main_window()  # Ui_Form 为生成的 Form 的名字
ui_main_window.setupUi(main_window)

# 额外工作
# ui_main_window.menu_view.addAction(ui_main_window.dock.toggleViewAction())


announces= AnnounceTable()
api= CallTable()

main_window.install(announces, api)
# QT
ui_main_window.ui_net_view.install(announces, api)  # NetView
ui_main_window.dock_table.install(announces, api)

#=======================================================================================================================
# ICNNET
icn_net= ICNNet(graph, ExperimentNode, OneStepChannel)
icn_net.install(announces, api)
# 数据库
db= ExperimentMonitorDB(graph)
db.install(announces, api)
# 初始化缓存
for node in icn_net.nodes():
    node.api['CS::setMode'](SimulatCSUnit.MODE.FIFO)
for node in icn_net.nodes():
    node.api['CS::setLifeTime'](100*SIZE)
icn_net.node(center).api['CS::setMode'](SimulatCSUnit.MODE.MANUAL)  # 要在设置全局mode之后
icn_net.node(center).api['CS::store'](constants.debug_dp)  # 要在CS类型配置之后,才会被正确驱逐
# 请求发生器
ask_gen= AskGenerator(icn_net, FixedAsk(1), UniformPosition(graph), constants.debug_ip, delta=4*SIZE)
ask_gen.start()
# UI
ui_net= UINet(graph)  # 要在UINetView后建立
ui_net.install(announces, api)

main_window.setNet(icn_net, ui_net, db)
ui_main_window.ui_net_view.setNet(icn_net, ui_net, db)
ui_main_window.dock_table.setNet(db)

for (x,y), node in ui_net.items():
    node.setPos( QPointF(x*200, y*200) )
ui_net.adaptive()

main_window.show()

if __name__ == '__main__':
    from core.common import timeProfile
    timeProfile('app.exec_()')
    sys.exit()
    # sys.exit(app.exec_())




