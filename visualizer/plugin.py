from PyQt5.QtCore import QRectF, Qt, QObject, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QAction, QToolBar, QDockWidget


from debug import showCall


# ======================================================================================================================
class MainWindowPlugin(QObject):
    def setup(self, main_window):pass


# ======================================================================================================================
from visualizer.planters import *
from core import Bind


PAINTER_INFOS= [  # TODO 写道配置文件中去
    {
        'PainterType':NodePropertyPainter,
        'action_name':'显示节点性能图',
        'pixmap_name':":/icon/visualizer/images/node.png",
    },
    {
        'PainterType':NameStorePainter,
        'action_name':'显示缓存分布图',
        'pixmap_name':":/icon/visualizer/images/store.png",
    },
    {
        'PainterType':HitRatioPainter,
        'action_name':'显示命中率图',
        'pixmap_name':":/icon/visualizer/images/hit.png",
    },
    {
        'PainterType':EdgesPropertyPainter,
        'action_name':'显示边性能图',
        'pixmap_name':":/icon/visualizer/images/edge.png",
    },
    {
        'PainterType':RatePainter,
        'action_name':'显示占用率图',
        'pixmap_name':":/icon/visualizer/images/bytes.png",
    },
]


class PainterPlugin(MainWindowPlugin):
    def setup(self, main_window):
        graph= main_window.graph
        monitor= main_window.monitor
        announces= main_window.announces
        api= main_window.api

        # 工具条
        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('Painter工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        for index, painter_info in enumerate(PAINTER_INFOS):
            # 创建Painter
            painter= painter_info['PainterType']()
            painter.graph= graph
            painter.monitor= monitor
            painter.install(announces, api)
            # 创建Action
            action = QAction( painter_info['action_name'] , main_window)
            if painter_info['pixmap_name']:
                icon = QIcon()
                icon.addPixmap(QPixmap(painter_info['pixmap_name']), QIcon.Normal, QIcon.Off)
                action.setIcon(icon)
            tool_bar.addAction(action)
            # 连接Action与Painter
            action.triggered.connect( Bind(api['NetView::triggerPainter'], painter) )

# ======================================================================================================================
from visualizer.common import SpinBox


class PlayerPlugin(MainWindowPlugin):
    FRAME_DELAY= 1000  # 单位(ms)
    DEFAULT_STEP_SIZE= 1000

    def __init__(self, parent):
        super().__init__(parent)
        self.step_size= self.DEFAULT_STEP_SIZE

        self.step_timer= QTimer(self)
        self.step_timer.timeout.connect(self.playSteps)
        self.step_timer.setInterval(self.FRAME_DELAY)

    @showCall
    def setup(self, main_window):
        self.announces= main_window.announces

        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('Play工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        # 安装播放按钮
        action_play = QAction('播放/暂停', main_window)
        action_play.setCheckable(True)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icon/visualizer/images/start.png"), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap(":/icon/visualizer/images/pause.png"), QIcon.Normal, QIcon.On)
        action_play.setIcon(icon)
        action_play.toggled.connect(self._playSlot)
        tool_bar.addAction(action_play)  # FIXME

        # 安装单步按钮
        action_step = QAction('步进', main_window)
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icon/visualizer/images/step.png"), QIcon.Normal, QIcon.Off)
        action_step.setIcon(icon)
        action_step.triggered.connect(self._step)
        tool_bar.addAction(action_step)  # FIXME

        # 安装步数显示器
        steps_spin_box= SpinBox(self, 'step_size')
        steps_spin_box.setRange(0, 10*self.DEFAULT_STEP_SIZE)
        steps_spin_box.setSingleStep(100)
        tool_bar.addWidget( steps_spin_box )

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
from visualizer.cs_table_widget import CSTableWidget
from visualizer.packet_head_tree import PacketHeadTreeWidget


BUTTOM_WIDGETS_INFOS= [  # TODO 写道配置文件中去
    {
        'WidgetType':CSTableWidget,
        'title':'ContentsName表',
    },
    {
        'WidgetType':PacketHeadTreeWidget,
        'title':'PacketHead树',
    }
]

class ButtomWidgetPlugin(MainWindowPlugin):
    def setup(self, main_window):
        graph= main_window.graph
        monitor= main_window.monitor
        announces= main_window.announces
        api= main_window.api

        for info in BUTTOM_WIDGETS_INFOS:
            widget= info['WidgetType'](main_window)
            # widget.graph= graph
            widget.monitor= monitor
            widget.install(announces, api)

            content_dock = QDockWidget(main_window)
            content_dock.setWindowTitle(info['title'])
            content_dock.setWidget(widget)
            main_window.addDockWidget(Qt.BottomDockWidgetArea, content_dock)






