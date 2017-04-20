# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_main_window.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.setObjectName("main_window")
        main_window.resize(1075, 733)
        self.central_widget = QtWidgets.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.gridLayout = QtWidgets.QGridLayout(self.central_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_net_node = QtWidgets.QLabel(self.central_widget)
        self.label_net_node.setObjectName("label_net_node")
        self.gridLayout.addWidget(self.label_net_node, 0, 0, 1, 1)
        self.label_net_edge = QtWidgets.QLabel(self.central_widget)
        self.label_net_edge.setObjectName("label_net_edge")
        self.gridLayout.addWidget(self.label_net_edge, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.view_net = NetView(self.central_widget)
        self.view_net.setAccessibleName("")
        self.view_net.setObjectName("view_net")
        self.gridLayout.addWidget(self.view_net, 1, 0, 1, 3)
        main_window.setCentralWidget(self.central_widget)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.toolbar_play = QtWidgets.QToolBar(main_window)
        self.toolbar_play.setObjectName("toolbar_play")
        main_window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar_play)
        self.dock_name_store = QtWidgets.QDockWidget(main_window)
        self.dock_name_store.setObjectName("dock_name_store")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.table_contents = CSTableWidget(self.dockWidgetContents_2)
        self.table_contents.setObjectName("table_contents")
        self.table_contents.setColumnCount(0)
        self.table_contents.setRowCount(0)
        self.gridLayout_3.addWidget(self.table_contents, 0, 0, 1, 1)
        self.dock_name_store.setWidget(self.dockWidgetContents_2)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dock_name_store)
        self.toolbar_view = QtWidgets.QToolBar(main_window)
        self.toolbar_view.setObjectName("toolbar_view")
        main_window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar_view)
        self.dock_packet_head = QtWidgets.QDockWidget(main_window)
        self.dock_packet_head.setObjectName("dock_packet_head")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tree_packet_head = PacketHeadTreeWidget(self.dockWidgetContents)
        self.tree_packet_head.setObjectName("tree_packet_head")
        self.tree_packet_head.headerItem().setText(0, "1")
        self.gridLayout_2.addWidget(self.tree_packet_head, 0, 0, 1, 1)
        self.dock_packet_head.setWidget(self.dockWidgetContents)
        main_window.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dock_packet_head)
        self.action_step = QtWidgets.QAction(main_window)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/visualizer/images/step.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_step.setIcon(icon)
        self.action_step.setObjectName("action_step")
        self.action_node = QtWidgets.QAction(main_window)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/node.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_node.setIcon(icon1)
        self.action_node.setObjectName("action_node")
        self.action_rate = QtWidgets.QAction(main_window)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icon/visualizer/images/bytes.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_rate.setIcon(icon2)
        self.action_rate.setObjectName("action_rate")
        self.action_stores = QtWidgets.QAction(main_window)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icon/visualizer/images/store.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_stores.setIcon(icon3)
        self.action_stores.setObjectName("action_stores")
        self.action_hits = QtWidgets.QAction(main_window)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icon/visualizer/images/hit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_hits.setIcon(icon4)
        self.action_hits.setObjectName("action_hits")
        self.action_transfer = QtWidgets.QAction(main_window)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icon/visualizer/images/transfer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_transfer.setIcon(icon5)
        self.action_transfer.setObjectName("action_transfer")
        self.toolbar_play.addAction(self.action_step)
        self.toolbar_view.addAction(self.action_hits)
        self.toolbar_view.addAction(self.action_stores)
        self.toolbar_view.addAction(self.action_rate)
        self.toolbar_view.addAction(self.action_transfer)

        self.retranslateUi(main_window)
        self.action_step.triggered.connect(main_window.playSteps)
        self.action_stores.triggered.connect(main_window.viewName)
        self.action_hits.triggered.connect(main_window.viewHits)
        self.action_rate.triggered.connect(main_window.viewRate)
        self.action_transfer.triggered.connect(main_window.viewTransfer)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "LICNsim"))
        self.label_net_node.setText(_translate("main_window", "label_net"))
        self.label_net_edge.setText(_translate("main_window", "TextLabel"))
        self.toolbar_play.setWindowTitle(_translate("main_window", "播放工具栏"))
        self.dock_name_store.setWindowTitle(_translate("main_window", "NameStore表"))
        self.toolbar_view.setWindowTitle(_translate("main_window", "显示工具栏"))
        self.dock_packet_head.setWindowTitle(_translate("main_window", "Packet传输表"))
        self.action_step.setText(_translate("main_window", "下一步"))
        self.action_node.setText(_translate("main_window", "Node"))
        self.action_rate.setText(_translate("main_window", "信道速率"))
        self.action_rate.setToolTip(_translate("main_window", "信道速率"))
        self.action_stores.setText(_translate("main_window", "CS信息"))
        self.action_hits.setText(_translate("main_window", "命中率"))
        self.action_transfer.setText(_translate("main_window", "传输图"))
        self.action_transfer.setToolTip(_translate("main_window", "Transfer"))

from visualizer import CSTableWidget, NetView, PacketHeadTreeWidget
import res_rc
