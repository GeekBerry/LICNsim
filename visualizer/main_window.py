#!/usr/bin/python3
#coding=utf-8

from debug import showCall


from core import clock, AnnounceTable, CallTable
from PyQt5.QtWidgets import QMainWindow, QAction

from visualizer.plugin import *
from visualizer.net_scene import NetScene


# ======================================================================================================================

class MainWindow(QMainWindow):
    docks= {Qt.LeftDockWidgetArea:[], Qt.RightDockWidgetArea:[], Qt.TopDockWidgetArea:[], Qt.BottomDockWidgetArea:[]}

    def __new__(cls, *args, **kwargs):
        main_window= QMainWindow.__new__(cls)
        QMainWindow.__init__(main_window)

        from visualizer.ui.ui_main_window import Ui_main_window
        main_window.ui= Ui_main_window()
        main_window.ui.setupUi(main_window)
        return main_window

    @showCall
    def __init__(self, graph, monitor, logger=None):
        self.install( AnnounceTable(), CallTable() )

        if logger is not None:
            logger.addAnnounceTable('MainWindow', self.announces)

        self.graph= graph
        self.monitor= monitor
        self.logger= logger

        self.monitor.install(self.announces, self.api)

        self.scene= NetScene(self.graph)  # NetScene
        self.scene.install(self.announces, self.api)

        self.ui.net_widget.init(self.scene)  # FIXME
        self.ui.net_widget.install(self.announces, self.api)

        # ---------------------------------------------------------------------
        self.addPlugin(PlayerPlugin)
        self.addPlugin(PainterPlugin)
        self.addPlugin(ButtomWidgetPlugin)
        self.addPlugin(InfoDialogPlugin)
        self.addPlugin(RealTimeViewPlugin)
        self.updateStatusBar()

    def install(self, announces, api):
        announces['playSteps'].append( self.updateStatusBar )
        self.announces= announces
        self.api= api

    @showCall
    def addPlugin(self, PluginFactory):
        PluginFactory(self).setup(self)

    def updateStatusBar(self, *unuse_args):
        self.statusBar().showMessage( f'steps:{clock.time()}' )

    def addDockWidget(self, dock_widget_area, dock_widget, orientation=None):  # 使得同一个方向的Dock合并在一起
        if orientation is None:
            super().addDockWidget(dock_widget_area, dock_widget)
        else:
            super().addDockWidget(dock_widget_area, dock_widget, orientation)

        for area, links in self.docks.items():
            if area == dock_widget_area:
                if links:
                    self.tabifyDockWidget(links[-1], dock_widget)
                links.append(dock_widget)
                break


