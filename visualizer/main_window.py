# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(1099, 733)
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.ui_net_view = UINetView(self.centralwidget)
        self.ui_net_view.setAccessibleName("")
        self.ui_net_view.setObjectName("ui_net_view")
        self.gridLayout.addWidget(self.ui_net_view, 0, 0, 1, 1)
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1099, 23))
        self.menubar.setObjectName("menubar")
        self.menu_view = QtWidgets.QMenu(self.menubar)
        self.menu_view.setObjectName("menu_view")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(main_window)
        self.toolBar.setObjectName("toolBar")
        main_window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.dock_tool = QtWidgets.QDockWidget(main_window)
        self.dock_tool.setStatusTip("")
        self.dock_tool.setObjectName("dock_tool")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dock_tool.setWidget(self.dockWidgetContents)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dock_tool)
        self.action_tool_dock = QtWidgets.QAction(main_window)
        self.action_tool_dock.setCheckable(False)
        self.action_tool_dock.setChecked(False)
        self.action_tool_dock.setObjectName("action_tool_dock")
        self.menu_view.addAction(self.action_tool_dock)
        self.menubar.addAction(self.menu_view.menuAction())

        self.retranslateUi(main_window)
        self.action_tool_dock.triggered['bool'].connect(self.dock_tool.show)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))
        self.menu_view.setTitle(_translate("main_window", "View"))
        self.toolBar.setWindowTitle(_translate("main_window", "toolBar"))
        self.dock_tool.setWindowTitle(_translate("main_window", "Dock Tool"))
        self.action_tool_dock.setText(_translate("main_window", "Tool Dock"))

from visualizer.ui_net import UINetView
