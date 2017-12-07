import networkx
from PyQt5.QtCore import Qt, QObject, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QToolBar, QSpinBox, QLabel, QButtonGroup, QRadioButton, QDockWidget

from config import *
from core import clock, Bind, top

from debug import showCall


class MainWindowPlugin(QObject):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window)
        self.announces = announces
        self.api = api


# ======================================================================================================================
class PlayerPlugin(MainWindowPlugin):
    FRAME_DELAY = 1000  # 单位(ms)
    DEFAULT_STEP_SIZE = 1

    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        self.step_timer = QTimer(self)
        self.step_timer.timeout.connect(self.playSteps)
        self.step_timer.setInterval(self.FRAME_DELAY)

        self.tool_bar = QToolBar(main_window)
        self.tool_bar.setWindowTitle('Play工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        # 添加播放按钮
        action_play = QAction('播放/暂停', self.tool_bar)
        action_play.setCheckable(True)

        icon = QIcon()
        icon.addPixmap(QPixmap(PLAY_ACTION_IMAGE), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap(PAUSE_ACTION_IMAGE), QIcon.Normal, QIcon.On)
        action_play.setIcon(icon)
        action_play.toggled.connect(self._playSlot)
        self.tool_bar.addAction(action_play)

        # 安装单步按钮
        action_step = QAction('步进', self.tool_bar)
        icon = QIcon()
        icon.addPixmap(QPixmap(STEP_ACTION_IMAGE), QIcon.Normal, QIcon.Off)
        action_step.setIcon(icon)
        action_step.triggered.connect(self.playStep)
        self.tool_bar.addAction(action_step)

        # 安装步数显示器
        self.steps_spin = QSpinBox(self.tool_bar)
        self.steps_spin.setRange(1, 1_000)
        self.steps_spin.setValue(self.DEFAULT_STEP_SIZE)
        self.steps_spin.setSingleStep(100)
        self.tool_bar.addWidget(self.steps_spin)

        # TODO 进度条
        self.lable = QLabel(f'current_time: {clock.time()}')
        main_window.statusBar().addPermanentWidget(self.lable)  # addWidget 或者 addPermanentWidget

    def playStep(self, is_triggered=False):
        # TODO 锁住仪表盘
        steps = self.steps_spin.value()

        for i in range(0, steps):
            clock.step()
        self.lable.setText(f'current_time: {clock.time()}')
        self.announces['playSteps'](steps)

    def playSteps(self):
        self.playStep()
        self.step_timer.start()

    def _playSlot(self, is_play):
        if is_play:
            self.playSteps()
        else:
            self.step_timer.stop()


# ======================================================================================================================
from gui.Painters import PropertyPainter, NameStorePainter, HitRatioPainter, OccupyPainter


class PainterPlugin(MainWindowPlugin):
    PAINTERS = (
        ('性能图', PROPERTY_ACTION_IMAGE, PropertyPainter),
        ('缓存图', STORE_ACTION_IMAGE, NameStorePainter),
        ('命中率图', HIT_ACTION_IMAGE, HitRatioPainter),
        ('占用率图', OCCUPY_ACTION_IMAGE, OccupyPainter)
    )

    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        announces['playSteps'].append(self.playSteps)
        self.painters = {}  # {text: painter, ...}
        self.current_painter = None

        # 工具条
        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('Painter工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        for text, pixmap_name, PainterType in self.PAINTERS:
            action = QAction(text, main_window)
            icon = QIcon()
            icon.addPixmap(QPixmap(pixmap_name), QIcon.Normal, QIcon.Off)
            action.setIcon(icon)
            tool_bar.addAction(action)

            self.painters[text] = PainterType(announces, api)
            action.triggered.connect(Bind(self.activePainter, text))

    def playSteps(self, steps):
        if self.current_painter is None:  # 设置默认 Painter
            self.activePainter(top(self.painters))
        self.current_painter.refresh()

    def activePainter(self, text, is_triggered=None):
        if self.current_painter is not None:
            self.current_painter.putDown()

        self.current_painter = self.painters.get(text)

        if self.current_painter is not None:
            self.current_painter.pickUp()


# ======================================================================================================================
from gui.NodeDialog import NodeDialog
from gui.EdgeDialog import EdgeDialog


class InfoDialogPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        self.node_dialog_table = {}  # { node_id:dialog, ... } 记录打开着的 NodeDialog
        self.edge_dialog_table = {}  # { edge_id:dialog, ... } 记录打开着的 EdgeDialog

        self.announces['doubleClickNode'].append(self.showNodeDialog)
        self.announces['closeNodeDialog'].append(self.closeNodeDialog)
        self.announces['doubleClickEdge'].append(self.showEdgeDialog)
        self.announces['closeEdgeDialog'].append(self.closeEdgeDialog)

    def showNodeDialog(self, node_id):
        dialog = self.node_dialog_table.get(node_id)
        if dialog is None:
            dialog = NodeDialog(self.parent(), self.announces, self.api, node_id)
            self.node_dialog_table[node_id] = dialog
        dialog.show()

    def closeNodeDialog(self, node_id):
        del self.node_dialog_table[node_id]
        self.announces['playSteps'](0)

    def showEdgeDialog(self, edge_id):
        dialog = self.edge_dialog_table.get(edge_id)
        if dialog is None:
            dialog = EdgeDialog(self.parent(), self.announces, self.api, edge_id)
            self.edge_dialog_table[edge_id] = dialog
        dialog.show()

    def closeEdgeDialog(self, edge_id):
        del self.edge_dialog_table[edge_id]
        self.announces['playSteps'](0)


# ======================================================================================================================
from gui.NameInfoWidget import NameInfoWidget


class NameInfoPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        name_info_widget = NameInfoWidget(main_window, announces, api)
        dock = QDockWidget('NameInfo表', main_window)
        dock.setWidget(name_info_widget)
        main_window.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.lable = QLabel(f'selected_name: ""')
        main_window.statusBar().addPermanentWidget(self.lable)  # addWidget 或者 addPermanentWidget
        announces['selectedName'].append(self._selectedName)

    def _selectedName(self, name):
        self.lable.setText(f'selected_name: "{name}"')


# ======================================================================================================================
from gui.LogWidget import LogWidget


class LogPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        log_widget = LogWidget(main_window, announces, api)
        dock = QDockWidget('Log表', main_window)
        dock.setWidget(log_widget)
        main_window.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.lable = QLabel(f'log_query_msg: Done')
        main_window.statusBar().addWidget(self.lable)  # 或者 addPermanentWidget
        announces['logQueryMessage'].append(self.logQueryMessage)

    def logQueryMessage(self, msg):
        self.lable.setText(f'log_query_msg: {msg}')


# ======================================================================================================================
class LayoutPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        self.topology_ratio = QRadioButton('拓扑布局', main_window)
        self.physical_ratio = QRadioButton('物理布局', main_window)

        self.group_box = QButtonGroup(main_window)
        self.group_box.addButton(self.topology_ratio)
        self.group_box.addButton(self.physical_ratio)
        self.group_box.buttonClicked.connect(self.buttonClickedSlot)

        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('位置工具栏')
        tool_bar.addWidget(self.topology_ratio)
        tool_bar.addWidget(self.physical_ratio)
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        self.topology_layout = None
        self.last_clicked_ratio = None
        self.pixmap = QPixmap(BACKGROUND_MAP_IMAGE)
        announces['playSteps'].append(self.playSteps)
        announces['sceneNodeMoved'].append(self.sceneNodeMoved)

    def playSteps(self, steps):
        if self.group_box.checkedButton() is None:  # 设置默认模式
            self.topology_layout = self._getTopologyLayout()
            self.topology_ratio.click()  # 导致 self.buttonClickedSlot(self.topology_ratio)
        elif self.group_box.checkedButton() is self.physical_ratio:  # 物理位置图
            self.buttonClickedSlot(self.physical_ratio)  # 重新加载位置图, 以更新位置信息

    def buttonClickedSlot(self, ratio):
        if (ratio is self.topology_ratio) and (ratio is self.last_clicked_ratio):
            self.topology_layout = self._getTopologyLayout()  # 多次点击, 重新计算位置

        self.api['Scene.setBackgroundPixmap'](self.getBackgroundPixmap())
        self.api['Scene.setLayout'](self.getLayout())
        self.last_clicked_ratio = ratio

    def sceneNodeMoved(self, node_id, pos):
        if self.group_box.checkedButton() is self.topology_ratio:
            self.topology_layout[node_id] = pos  # 拓扑图模式下修改缓存的位置信息
        elif self.group_box.checkedButton() is self.physical_ratio:
            icn_node = self.api['Sim.node'](node_id)
            icn_node.pos = pos  # 物理图模式下修改节点实际位置
            self.announces['playSteps'](0)
        else:  # 没有模式被设置
            pass

    # -------------------------------------------------------------------------
    def getLayout(self):
        if self.group_box.checkedButton() is self.topology_ratio:
            return self.topology_layout
        elif self.group_box.checkedButton() is self.physical_ratio:
            return self._getPhysicalLayout()
        else:  # 没有模式被设置
            pass

    def getBackgroundPixmap(self):
        if self.group_box.checkedButton() is self.topology_ratio:
            return None
        elif self.group_box.checkedButton() is self.physical_ratio:
            return self.pixmap
        else:  # 没有模式被设置
            pass

    # -------------------------------------------------------------------------
    def _getPhysicalLayout(self) -> dict:
        graph = self.api['Sim.graph']()
        layout = {}
        for node_id in graph:
            icn_node = self.api['Sim.node'](node_id)
            layout[node_id] = getattr(icn_node, 'pos', (0,0))
        return layout

    def _getTopologyLayout(self) -> dict:
        graph = self.api['Sim.graph']()
        layout = networkx.spring_layout(graph, scale=500, iterations=50)  # scale 单位pix
        # FIXME spring_layout 中, 利用已有pos迭代, 会出现扭曲 pos= self.topology_layout
        return layout
