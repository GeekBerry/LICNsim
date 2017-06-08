from PyQt5.QtCore import QRectF, Qt, QObject, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import (QGraphicsView, QAction, QToolBar, QDockWidget, QFileDialog, QWidget, QDial, QCalendarWidget,
                             QVBoxLayout, QScrollArea, QFrame, QToolBox)


from debug import showCall


# ======================================================================================================================
class MainWindowPlugin(QObject):
    def setup(self, main_window):pass


# ======================================================================================================================
from visualizer.painters import *
from core import Bind


PAINTER_INFOS= [  # TODO 写道配置文件中去
    {
        'PainterType':NodePropertyPainter,
        'action_name':'显示节点性能图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/node.png",
    },
    {
        'PainterType':NameStorePainter,
        'action_name':'显示缓存分布图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/store.png",
    },
    {
        'PainterType':HitRatioPainter,
        'action_name':'显示命中率图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/hit.png",
    },
    {
        'PainterType':EdgesPropertyPainter,
        'action_name':'显示边性能图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/edge.png",
    },
    {
        'PainterType':RatePainter,
        'action_name':'显示占用率图',
        'pixmap_name':"C:/Users/bupt632/Desktop/LICNsim/visualizer/images/bytes.png",
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
        main_window.api['Player::step']= self._step
        self.announces= main_window.announces

        tool_bar = QToolBar(main_window)
        tool_bar.setWindowTitle('Play工具栏')
        main_window.addToolBar(Qt.TopToolBarArea, tool_bar)

        # 安装播放按钮
        action_play = QAction('播放/暂停', main_window)
        action_play.setCheckable(True)
        icon = QIcon()
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/visualizer/images/start.png"), QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/visualizer/images/pause.png"), QIcon.Normal, QIcon.On)
        action_play.setIcon(icon)
        action_play.toggled.connect(self._playSlot)
        tool_bar.addAction(action_play)  # FIXME

        # 安装单步按钮
        action_step = QAction('步进', main_window)
        icon = QIcon()
        icon.addPixmap(QPixmap("C:/Users/bupt632/Desktop/LICNsim/visualizer/images/step.png"), QIcon.Normal, QIcon.Off)
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
    # {
    #     'WidgetType':PacketHeadTreeWidget,
    #     'title':'PacketHead树',
    # }
]


class ButtomWidgetPlugin(MainWindowPlugin):
    def setup(self, main_window):
        graph= main_window.graph
        monitor= main_window.monitor
        announces= main_window.announces
        api= main_window.api

        for info in BUTTOM_WIDGETS_INFOS:
            content_dock = QDockWidget(main_window)
            content_dock.setWindowTitle(info['title'])

            widget= info['WidgetType'](content_dock)
            # widget.graph= graph
            widget.monitor= monitor
            widget.install(announces, api)

            content_dock.setWidget(widget)
            main_window.addDockWidget(Qt.BottomDockWidgetArea, content_dock)

            widget.refresh()

# ======================================================================================================================
from visualizer.real_time_views import *

REAL_TIME_VIEW_INFOS= [
    {
        'WidgetType':HitRatioRTV,
        'title':'命中率变化曲线',
    },
    {
        'WidgetType':FlowRTV,
        'title':'传输量曲线',
    },
]


class RealTimeViewPlugin(MainWindowPlugin):  # DEBUG
    def setup(self, main_window):
        graph= main_window.graph
        monitor= main_window.monitor
        announces= main_window.announces
        api= main_window.api

        dock = QDockWidget(main_window)
        dock.setWindowTitle('实时信息栏')

        box= QToolBox(dock)
        for entry in REAL_TIME_VIEW_INFOS:
            widget= entry['WidgetType'](box)
            widget.monitor= monitor
            widget.graph= graph
            widget.install(announces, api)
            box.addItem(widget, entry['title'])
        box.currentChanged.connect( lambda index:box.widget(index).refresh() )

        dock.setWidget(box)
        main_window.addDockWidget(Qt.RightDockWidgetArea, dock)

# ======================================================================================================================
from visualizer.node_info_dialog import NodeInfoDialog
from visualizer.edge_info_dialog import EdgeInfoDialog


class InfoDialogPlugin(MainWindowPlugin):
    def __init__(self, parent= None):
        super().__init__(parent)
        self.node_dialog_table= {}
        self.edge_dialog_table= {}

    def setup(self, main_window):
        self.main_window= main_window
        self.graph= main_window.graph
        self.monitor= main_window.monitor
        self.logger= main_window.logger
        self.announces= main_window.announces
        self.api= main_window.api

        self.announces['NodeDoubleClick'].append( self.showNodeInfoDialog )
        self.announces['NodeDialogClose'].append( self.closedNodeInfoDialog )

        self.announces['EdgeDoubleClick'].append( self.showEdgeInfoDialog )
        self.announces['EdgeDialogClose'].append( self.closedEdgeInfoDialog )

    def showNodeInfoDialog(self, node_name):
        dialog= self.node_dialog_table.get(node_name, None)
        if dialog is None:
            dialog= NodeInfoDialog(self.main_window, self.graph, node_name, self.logger)
            dialog.install(self.announces, self.api)
            self.node_dialog_table[node_name]= dialog

        dialog.setVisible(True)
        dialog.refresh()

    @showCall
    def closedNodeInfoDialog(self, node_name):
        del self.node_dialog_table[node_name]

    def showEdgeInfoDialog(self, src, dst):
        dialog= self.edge_dialog_table.get((src, dst), None)
        if dialog is None:
            dialog= EdgeInfoDialog(self.main_window, self.graph, src, dst, self.logger)
            dialog.install(self.announces, self.api)
            self.edge_dialog_table[(src, dst)]= dialog

        dialog.setVisible(True)
        dialog.refresh()

    def closedEdgeInfoDialog(self, src, dst):
        del self.edge_dialog_table[(src, dst)]



