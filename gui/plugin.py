from PyQt5.QtCore import QObject
from debug import showCall


class MainWindowPlugin(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUI(parent)

    def setupUI(self, main_window):  # UI布局
        pass

    def install(self, announces, api):  # 消息连接
        self.announces= announces
        self.api= api


# ======================================================================================================================
from visualizer.common import SpinBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QToolBar, QProgressBar, QWidget
from core.clock import clock
from core.data_structure import Bind


class PlayerPlugin(MainWindowPlugin):
    FRAME_DELAY= 1000  # 单位(ms)
    DEFAULT_STEP_SIZE= 1000

    def __init__(self, main_window):
        self.steps= self.DEFAULT_STEP_SIZE  # 要放在 self.setupUI 执行之前

        super().__init__(main_window)
        self.step_timer= QTimer(self)
        self.step_timer.timeout.connect(self.playSteps)
        self.step_timer.setInterval(self.FRAME_DELAY)

    def setupUI(self, main_window):
        self.tool_bar= QToolBar(main_window)
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
        action_step.triggered.connect(self._clockInc)
        self.tool_bar.addAction(action_step)  # FIXME

        # 安装步数显示器
        steps_spin_box= SpinBox(obj= self, attr= 'steps')
        steps_spin_box.setRange(0, 10*self.DEFAULT_STEP_SIZE)
        steps_spin_box.setSingleStep(100)
        self.tool_bar.addWidget( steps_spin_box )

        # TODO 进度条

    @showCall
    def _clockInc(self, is_triggered=False):
        # TODO 锁住仪表盘
        for i in range(0, self.steps):
            clock.step()
        self.announces['playSteps'](self.steps)

    @showCall
    def playSteps(self):
        self._clockInc()
        self.step_timer.start()

    @showCall
    def _playSlot(self, is_play):
        if is_play:
            self.playSteps()
        else:
            self.step_timer.stop()


# ======================================================================================================================
from gui.Painters import *

PAINTER_INFOS= [  # TODO 写到配置文件中去
    {
        'type':PropertyPainter,
        'text':'性能图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/node.png",
    },

    {
        'type':NameStatePainter,
        'text':'缓存图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/store.png",
    },
]


class PainterPlugin(MainWindowPlugin):
    def setupUI(self, main_window):
        # 工具条
        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('Painter工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        self.painters= []
        for info in PAINTER_INFOS:
            painter= info['type']()

            action = QAction( info['text'] , main_window)
            icon = QIcon()
            icon.addPixmap(QPixmap(info['pixmap_name']), QIcon.Normal, QIcon.Off)
            action.setIcon(icon)

            tool_bar.addAction(action)
            action.triggered.connect( Bind(self.activePainter, painter) )

            self.painters.append(painter)

    def install(self, announces, api):
        super().install(announces, api)
        for painter in self.painters:
            painter.install(announces, api)

    @showCall
    def activePainter(self, painter, is_triggered):
        self.api['Painter.currentPainter']= lambda: painter
        self.announces['painterUpdated'](painter)


# ======================================================================================================================
from PyQt5.QtWidgets import QDockWidget
from gui.NameTreeWidget import NameTreeWidget


DOCK_WIDGETS_INFOS= [  # TODO 写到配置文件中去
    {
        'type':NameTreeWidget,
        'title':'Name表',
        'area':Qt.BottomDockWidgetArea
    },
    # {
    #     'type':PacketHeadTreeWidget,
    #     'title':'PacketHead树',
    # }
]


class DocksPlugin(MainWindowPlugin):
    def setupUI(self, main_window):
        self.widgets= []
        for info in DOCK_WIDGETS_INFOS:
            dock = QDockWidget(main_window)
            dock.setWindowTitle(info['title'])
            main_window.addDockWidget(info['area'], dock)

            widget= info['type'](dock)
            dock.setWidget(widget)
            self.widgets.append(widget)

    def install(self, announces, api):
        for widget in self.widgets:
            widget.install(announces, api)


# ======================================================================================================================



























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
