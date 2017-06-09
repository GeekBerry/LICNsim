from debug import showCall

from PyQt5.QtCore import QObject


class MainWindowPlugin(QObject):
    pass


# ======================================================================================================================
from visualizer.common import SpinBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QToolBar, QProgressBar, QWidget

from core.clock import clock


class PlayerPlugin(MainWindowPlugin):
    FRAME_DELAY= 1000  # 单位(ms)
    DEFAULT_STEP_SIZE= 1000

    def __init__(self, main_window):
        super().__init__(main_window)

        self.step_size= self.DEFAULT_STEP_SIZE

        self.step_timer= QTimer(self)
        self.step_timer.timeout.connect(self.playSteps)
        self.step_timer.setInterval(self.FRAME_DELAY)

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
        action_step.triggered.connect(self._step)
        self.tool_bar.addAction(action_step)  # FIXME

        # 安装步数显示器
        steps_spin_box= SpinBox(obj= self, attr= 'step_size')
        steps_spin_box.setRange(0, 10*self.DEFAULT_STEP_SIZE)
        steps_spin_box.setSingleStep(100)
        self.tool_bar.addWidget( steps_spin_box )

        # TODO 进度条

    @showCall
    def install(self, announces, api):
        self.announces= announces
        api['Player::step']= self._step

    @showCall
    def _step(self, value=False):
        # TODO 锁住仪表盘
        for i in range(0, self.step_size):
            clock.step()
        self.announces['playSteps'](self.step_size)

    @showCall
    def playSteps(self):
        self._step()
        self.step_timer.start()

    @showCall
    def _playSlot(self, is_play):
        if is_play:
            self.playSteps()
        else:
            self.step_timer.stop()


# ======================================================================================================================
from PyQt5.QtWidgets import QDockWidget
from visualizer.cs_table_widget import CSTableWidget


DOCK_WIDGETS_INFOS= [  # TODO 写道配置文件中去
    {
        'WidgetType':CSTableWidget,
        'title':'ContentsName表',
        'area':Qt.BottomDockWidgetArea
    },
    # {
    #     'WidgetType':PacketHeadTreeWidget,
    #     'title':'PacketHead树',
    # }
]

class DocksPlugin(MainWindowPlugin):
    def __init__(self, main_window):
        super().__init__(main_window)

        self.widgets= []
        for info in DOCK_WIDGETS_INFOS:
            dock = QDockWidget(main_window)
            dock.setWindowTitle(info['title'])
            main_window.addDockWidget(info['area'], dock)

            widget= info['WidgetType'](dock)
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
