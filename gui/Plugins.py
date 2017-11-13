from PyQt5.QtCore import QObject
from debug import showCall


class MainWindowPlugin(QObject):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window)
        self.announces = announces
        self.api = api


# ======================================================================================================================
from core import clock, Bind
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QToolBar, QToolBox, QSpinBox, QLabel


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
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/gui/images/start.png"), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/gui/images/pause.png"), QIcon.Normal, QIcon.On)
        action_play.setIcon(icon)
        action_play.toggled.connect(self._playSlot)
        self.tool_bar.addAction(action_play)  # FIXME

        # 安装单步按钮
        action_step = QAction('步进', self.tool_bar)
        icon = QIcon()
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/gui/images/step.png"), QIcon.Normal, QIcon.Off)
        action_step.setIcon(icon)
        action_step.triggered.connect(self.playStep)
        self.tool_bar.addAction(action_step)  # FIXME

        # 安装步数显示器
        self.steps_spin = QSpinBox(self.tool_bar)
        self.steps_spin.setRange(1, 1_000)
        self.steps_spin.setValue(self.DEFAULT_STEP_SIZE)
        self.steps_spin.setSingleStep(100)
        self.tool_bar.addWidget(self.steps_spin)

        # TODO 进度条
        self.lable= QLabel(f'current_time: {clock.time()}')
        main_window.statusBar().addPermanentWidget(self.lable)  # addWidget 或者 addPermanentWidget

    def playStep(self, is_triggered=False):
        # TODO 锁住仪表盘
        steps = self.steps_spin.value()

        for i in range(0, steps):
            clock.step()
        self.lable.setText(f'current_time: {clock.time()}')
        self.announces['playSteps'](steps)

    # @showCall
    def playSteps(self):
        self.playStep()
        self.step_timer.start()

    def _playSlot(self, is_play):
        if is_play:
            self.playSteps()
        else:
            self.step_timer.stop()


# ======================================================================================================================
from gui.Painters import *


class PainterPlugin(MainWindowPlugin):
    PAINTERS= (
        ('性能图', "C:/Users/bupt632/Desktop/LICNsim/gui/images/node.png", PropertyPainter),
        ('缓存图', "C:/Users/bupt632/Desktop/LICNsim/gui/images/store.png", NameStorePainter),
        ('命中率图', "C:/Users/bupt632/Desktop/LICNsim/gui/images/hit.png", HitRatioPainter),
    )

    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)

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

            painter= PainterType(announces, api)
            action.triggered.connect(Bind(self.activePainter, painter))

    def activePainter(self, painter, is_triggered):
        self.announces['selectPainter'](painter)


# ======================================================================================================================
# from gui.RealTimeView import FlowRTV
#
# REAL_TIME_VIEW_INFOS = [
#     {
#         'type': FlowRTV,
#         'title': '传输量曲线',
#     },
# ]
#
#
# class RealTimeViewBox(QToolBox):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.currentChanged.connect(self._currentChangedSlot)
#
#         for info in REAL_TIME_VIEW_INFOS:
#             self.addItem(info['type'](self), info['title'])
#
#     def install(self, announces, api):
#         for index in range(0, self.count()):
#             self.widget(index).install(announces, api)
#
#     def _currentChangedSlot(self, index):
#         self.widget(index).refresh()  # TODO 不要直接调用 refresh


# ======================================================================================================================
# from PyQt5.QtWidgets import QDockWidget
# from gui.NameInfoWidget import NameInfoWidget
# from gui.LogWidget import LogWidget


# class DocksPlugin(MainWindowPlugin):
#     DOCKS= (
#         ('Name表', Qt.BottomDockWidgetArea, NameInfoWidget),
#         # ('实时视图', Qt.BottomDockWidgetArea, RealTimeViewBox),
#         # ('日志', Qt.BottomDockWidgetArea, LogWidget),
#     )
#
#     def __init__(self, main_window, announces, api):
#         super().__init__(main_window, announces, api)
#         self.widgets = []
#         for text, area, DockType in self.DOCKS:
#             widget= DockType(main_window)
#             widget.install(announces, api)
#             self.widgets.append(widget)
#
#             dock= QDockWidget(text, self.parent())
#             dock.setWidget(widget)
#             main_window.addDockWidget(area, dock)


# ======================================================================================================================
from gui.NodeDialog import NodeDialog
from gui.EdgeDialog import EdgeDialog


class InfoDialogPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        self.node_dialog_table= {}  # { node_id:dialog, ... } 记录打开着的 NodeDialog
        self.edge_dialog_table= {}  # { (src_id, dst_id):dialog, ... } 记录打开着的 EdgeDialog

        self.announces['NodeDoubleClick'].append(self.showNodeDialog)
        self.announces['NodeDialogClose'].append(self.closeNodeDialog)
        self.announces['EdgeDoubleClick'].append(self.showEdgeDialog)
        self.announces['EdgeDialogClose'].append(self.closeEdgeDialog)

    def showNodeDialog(self, node_id):
        dialog= self.node_dialog_table.get(node_id)
        if dialog is None:
            dialog= NodeDialog(self.parent(), self.announces, self.api, node_id)
            self.node_dialog_table[node_id]= dialog
        dialog.show()

    def closeNodeDialog(self, node_id):
        del self.node_dialog_table[node_id]

    def showEdgeDialog(self, src_id, dst_id):
        dialog= self.edge_dialog_table.get( (src_id, dst_id,) )
        if dialog is None:
            dialog= EdgeDialog(self.parent(), self.announces, self.api, src_id, dst_id)
            self.edge_dialog_table[ (src_id, dst_id,) ]= dialog
        dialog.show()

    def closeEdgeDialog(self, src_id, dst_id):
        del self.edge_dialog_table[ (src_id, dst_id,) ]


# ======================================================================================================================
from gui.NameInfoWidget import NameInfoWidget
from PyQt5.QtWidgets import QDockWidget


class NameInfoPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        name_info_widget= NameInfoWidget(main_window, announces, api)
        dock = QDockWidget('NameInfo表', main_window)
        dock.setWidget(name_info_widget)
        main_window.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.lable= QLabel(f'selected_name: "{Name()}"')
        main_window.statusBar().addPermanentWidget(self.lable)  # addWidget 或者 addPermanentWidget
        announces['selectedName'].append(self.selectedName)

    def selectedName(self, name):
        self.lable.setText(f'selected_name: "{name}"')


# ======================================================================================================================
from gui.LogWidget import LogWidget


class LogPlugin(MainWindowPlugin):
    def __init__(self, main_window, announces, api):
        super().__init__(main_window, announces, api)
        log_widget= LogWidget(main_window, announces, api)
        dock = QDockWidget('Log表', main_window)
        dock.setWidget(log_widget)
        main_window.addDockWidget(Qt.BottomDockWidgetArea, dock)

        self.lable= QLabel(f'log_query_msg: Done')
        main_window.statusBar().addWidget(self.lable)  # 或者 addPermanentWidget
        announces['logQueryMessage'].append(self.logQueryMessage)

    def logQueryMessage(self, msg):
        self.lable.setText(f'log_query_msg: {msg}')
