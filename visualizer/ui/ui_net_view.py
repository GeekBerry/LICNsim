# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_net_view.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FormNetView(object):
    def setupUi(self, FormNetView):
        FormNetView.setObjectName("FormNetView")
        FormNetView.resize(701, 447)
        self.gridLayout = QtWidgets.QGridLayout(FormNetView)
        self.gridLayout.setObjectName("gridLayout")
        self.label_edge = QtWidgets.QLabel(FormNetView)
        self.label_edge.setObjectName("label_edge")
        self.gridLayout.addWidget(self.label_edge, 0, 4, 1, 1)
        self.label = QtWidgets.QLabel(FormNetView)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(FormNetView)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        self.label_node = QtWidgets.QLabel(FormNetView)
        self.label_node.setObjectName("label_node")
        self.gridLayout.addWidget(self.label_node, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(65, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(65, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 5, 1, 1)
        self.net_view = NetView(FormNetView)
        self.net_view.setObjectName("net_view")
        self.gridLayout.addWidget(self.net_view, 1, 0, 1, 6)

        self.retranslateUi(FormNetView)
        QtCore.QMetaObject.connectSlotsByName(FormNetView)

    def retranslateUi(self, FormNetView):
        _translate = QtCore.QCoreApplication.translate
        FormNetView.setWindowTitle(_translate("FormNetView", "Form"))
        self.label_edge.setText(_translate("FormNetView", "(未知)"))
        self.label.setText(_translate("FormNetView", "节点图类型:"))
        self.label_2.setText(_translate("FormNetView", "边图类型:"))
        self.label_node.setText(_translate("FormNetView", "(未知)"))

from visualizer import NetView
