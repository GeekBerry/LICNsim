# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'flow_RTV.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_flow_RTV(object):
    def setupUi(self, flow_RTV):
        flow_RTV.setObjectName("flow_RTV")
        flow_RTV.resize(274, 706)
        self.gridLayout = QtWidgets.QGridLayout(flow_RTV)
        self.gridLayout.setObjectName("gridLayout")
        self.title = QtWidgets.QLabel(flow_RTV)
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 0, 0, 1, 1)
        self.accum_num = QtWidgets.QLabel(flow_RTV)
        self.accum_num.setObjectName("accum_num")
        self.gridLayout.addWidget(self.accum_num, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(109, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 6, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(flow_RTV)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 7, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(169, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 2, 1, 1)
        self.segm_num = QtWidgets.QLabel(flow_RTV)
        self.segm_num.setObjectName("segm_num")
        self.gridLayout.addWidget(self.segm_num, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(flow_RTV)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(157, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 2, 1, 1)
        self.label = QtWidgets.QLabel(flow_RTV)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.line = QtWidgets.QFrame(flow_RTV)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 4, 0, 1, 3)
        self.label_4 = QtWidgets.QLabel(flow_RTV)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.segm_size = QtWidgets.QLabel(flow_RTV)
        self.segm_size.setObjectName("segm_size")
        self.gridLayout.addWidget(self.segm_size, 6, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(109, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 7, 2, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem4, 8, 0, 1, 3)
        self.accum_size = QtWidgets.QLabel(flow_RTV)
        self.accum_size.setObjectName("accum_size")
        self.gridLayout.addWidget(self.accum_size, 7, 1, 1, 1)
        self.size_canvas = PolyLineCanvas(flow_RTV)
        self.size_canvas.setMinimumSize(QtCore.QSize(256, 256))
        self.size_canvas.setObjectName("size_canvas")
        self.gridLayout.addWidget(self.size_canvas, 5, 0, 1, 3)
        self.num_canvas = PolyLineCanvas(flow_RTV)
        self.num_canvas.setMinimumSize(QtCore.QSize(256, 256))
        self.num_canvas.setObjectName("num_canvas")
        self.gridLayout.addWidget(self.num_canvas, 1, 0, 1, 3)

        self.retranslateUi(flow_RTV)
        QtCore.QMetaObject.connectSlotsByName(flow_RTV)

    def retranslateUi(self, flow_RTV):
        _translate = QtCore.QCoreApplication.translate
        flow_RTV.setWindowTitle(_translate("flow_RTV", "Form"))
        self.title.setText(_translate("flow_RTV", "(未知)"))
        self.accum_num.setText(_translate("flow_RTV", "(未知)"))
        self.label_5.setText(_translate("flow_RTV", "总包流量(字节)"))
        self.segm_num.setText(_translate("flow_RTV", "(未知)"))
        self.label_2.setText(_translate("flow_RTV", "总包数量(个)"))
        self.label.setText(_translate("flow_RTV", "当前包数量(个)"))
        self.label_4.setText(_translate("flow_RTV", "当前包流量(字节)"))
        self.segm_size.setText(_translate("flow_RTV", "(未知)"))
        self.accum_size.setText(_translate("flow_RTV", "(未知)"))

from visualizer import PolyLineCanvas
