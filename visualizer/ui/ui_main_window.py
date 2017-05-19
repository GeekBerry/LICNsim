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
        self.view_net = NetView(self.central_widget)
        self.view_net.setAccessibleName("")
        self.view_net.setObjectName("view_net")
        self.gridLayout.addWidget(self.view_net, 1, 0, 1, 6)
        spacerItem = QtWidgets.QSpacerItem(367, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.label_net_node = QtWidgets.QLabel(self.central_widget)
        self.label_net_node.setObjectName("label_net_node")
        self.gridLayout.addWidget(self.label_net_node, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.central_widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.central_widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        self.label_net_edge = QtWidgets.QLabel(self.central_widget)
        self.label_net_edge.setObjectName("label_net_edge")
        self.gridLayout.addWidget(self.label_net_edge, 0, 4, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 5, 1, 1)
        main_window.setCentralWidget(self.central_widget)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(main_window)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1075, 23))
        self.menuBar.setObjectName("menuBar")
        main_window.setMenuBar(self.menuBar)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "LICNsim"))
        self.label_net_node.setText(_translate("main_window", "label_net_node"))
        self.label.setText(_translate("main_window", "节点图类型:"))
        self.label_2.setText(_translate("main_window", "边图类型:"))
        self.label_net_edge.setText(_translate("main_window", "label_net_edge"))

from visualizer import NetView
import res_rc
