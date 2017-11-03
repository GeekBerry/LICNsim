from PyQt5.QtCore import QObject
from debug import showCall


class MainWindowPlugin(QObject):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.setupUI(main_window)

    def setupUI(self, main_window):  # UI布局
        pass

    def install(self, announces, api):  # 消息连接
        self.announces = announces
        self.api = api


# ======================================================================================================================
from core import clock, Bind
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QToolBar, QToolBox, QSpinBox


class PlayerPlugin(MainWindowPlugin):
    FRAME_DELAY = 1000  # 单位(ms)
    DEFAULT_STEP_SIZE = 1

    def __init__(self, main_window):
        super().__init__(main_window)
        self.step_timer = QTimer(self)
        self.step_timer.timeout.connect(self.playSteps)
        self.step_timer.setInterval(self.FRAME_DELAY)

    def setupUI(self, main_window):
        self.tool_bar = QToolBar(main_window)
        self.tool_bar.setWindowTitle('Play工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        # 添加播放按钮
        action_play = QAction('播放/暂停', self.tool_bar)
        action_play.setCheckable(True)

        icon = QIcon()
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/visualizer/images/start.png"), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/visualizer/images/pause.png"), QIcon.Normal, QIcon.On)
        action_play.setIcon(icon)
        action_play.toggled.connect(self._playSlot)
        self.tool_bar.addAction(action_play)  # FIXME

        # 安装单步按钮
        action_step = QAction('步进', self.tool_bar)
        icon = QIcon()
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/visualizer/images/step.png"), QIcon.Normal, QIcon.Off)
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

    # @showCall
    def playStep(self, is_triggered=False):
        # TODO 锁住仪表盘
        steps = self.steps_spin.value()

        for i in range(0, steps):
            clock.step()
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
        ('性能图', "C:/Users/bupt632/Desktop/LICNsim/visualizer/images/node.png", PropertyPainter),
        ('缓存图', "C:/Users/bupt632/Desktop/LICNsim/visualizer/images/store.png", NameStorePainter),
        # ('命中率图', "C:/Users/bupt632/Desktop/LICNsim/visualizer/images/hit.png", NodeHitPainter),
    )

    def setupUI(self, main_window):
        # 工具条
        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('Painter工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        self.painters = {}
        for text, pixmap_name, PainterType in self.PAINTERS:
            self.painters[text]= PainterType()

            action = QAction(text, main_window)
            icon = QIcon()
            icon.addPixmap(QPixmap(pixmap_name), QIcon.Normal, QIcon.Off)
            action.setIcon(icon)
            tool_bar.addAction(action)
            action.triggered.connect(Bind(self.activePainter, text))

    def install(self, announces, api):
        super().install(announces, api)
        for painter in self.painters.values():
            painter.install(announces, api)

    def activePainter(self, text, is_triggered):
        self.announces['selectPainter']( self.painters[text] )


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
from PyQt5.QtWidgets import QDockWidget
from gui.NameTreeWidget import NameTreeWidget
from gui.LogWidget import LogWidget


class DocksPlugin(MainWindowPlugin):
    DOCKS= (
        ('Name表', Qt.BottomDockWidgetArea, NameTreeWidget),
        # ('实时视图', Qt.BottomDockWidgetArea, RealTimeViewBox),
        # ('日志', Qt.BottomDockWidgetArea, LogWidget),
    )

    def setupUI(self, main_window):
        self.widgets = []
        for text, area, DockType in self.DOCKS:
            widget= DockType(main_window)
            self.widgets.append(widget)

            dock= QDockWidget(text, self.parent())
            dock.setWidget(widget)
            main_window.addDockWidget(area, dock)

    def install(self, announces, api):
        for widget in self.widgets:
            widget.install(announces, api)

# ======================================================================================================================
from gui.NodeDialog import NodeDialog
from gui.EdgeDialog import EdgeDialog


class InfoDialogPlugin(MainWindowPlugin):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.node_dialog_table= {}  # { node_id:dialog, ... } 记录打开着的 NodeDialog
        self.edge_dialog_table= {}  # { (src_id, dst_id):dialog, ... } 记录打开着的 EdgeDialog

    def install(self, announces, api):
        super().install(announces, api)
        self.announces['NodeDoubleClick'].append(self.showNodeDialog)
        self.announces['NodeDialogClose'].append(self.closeNodeDialog)
        self.announces['EdgeDoubleClick'].append(self.showEdgeDialog)
        self.announces['EdgeDialogClose'].append(self.closeEdgeDialog)

    def showNodeDialog(self, node_id):
        dialog= self.node_dialog_table.get(node_id)
        if dialog is None:
            dialog= NodeDialog(self.parent(), node_id)
            dialog.install(self.announces, self.api)
            self.node_dialog_table[node_id]= dialog
        dialog.show()

    def closeNodeDialog(self, node_id):
        del self.node_dialog_table[node_id]

    def showEdgeDialog(self, src_id, dst_id):
        dialog= self.edge_dialog_table.get( (src_id, dst_id,) )
        if dialog is None:
            dialog= EdgeDialog(self.parent(), src_id, dst_id)
            dialog.install(self.announces, self.api)
            self.edge_dialog_table[ (src_id, dst_id,) ]= dialog
        dialog.show()

    def closeEdgeDialog(self, src_id, dst_id):
        del self.edge_dialog_table[ (src_id, dst_id,) ]





















# TODO 解析该格式; 是否有必要???
# style= {
#     'type': QToolBar,
#     'window_title':'Play工具栏',
#     'actions':{
#         'play_action':{
#             'type':QAction,
#             'text':'播放/暂停',
#             'icon':{
#                 'type':QIcon,
#                 'pixmap':{
#                     (QIcon.Normal, QIcon.Off): 'C:/Users/bupt632/Desktop/LICNsim/visualizer/images/start.png',
#                     (QIcon.Normal, QIcon.On): 'C:/Users/bupt632/Desktop/LICNsim/visualizer/images/pause.png'
#                 },
#             },  # icon
#             'check_able':True,
#         },  # action
#
#         'step_action':{
#             'type':QAction,
#             'text':'步进',
#             'icon':{
#                 'type':QIcon,
#                 'pixmap':{
#                     (QIcon.Normal, QIcon.Off): 'C:/Users/bupt632/Desktop/LICNsim/visualizer/images/step.png',
#                 }
#             },  # icon
#         },  # action
#
#         'steps_box':{
#             'type':SpinBox,
#             'range':(0, 10000),
#             'single_step': 100,
#         }
#     },
# }  # style
