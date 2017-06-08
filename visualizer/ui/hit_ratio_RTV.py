# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hit_ratio_RTV.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_hit_ratio_RTV(object):
    def setupUi(self, hit_ratio_RTV):
        hit_ratio_RTV.setObjectName("hit_ratio_RTV")
        hit_ratio_RTV.resize(274, 377)
        self.gridLayout = QtWidgets.QGridLayout(hit_ratio_RTV)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 3)
        self.label = QtWidgets.QLabel(hit_ratio_RTV)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.title = QtWidgets.QLabel(hit_ratio_RTV)
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 0, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(145, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 2, 1, 1)
        self.avg_ratio = QtWidgets.QLabel(hit_ratio_RTV)
        self.avg_ratio.setObjectName("avg_ratio")
        self.gridLayout.addWidget(self.avg_ratio, 3, 1, 1, 1)
        self.canvas = PolyLineCanvas(hit_ratio_RTV)
        self.canvas.setMinimumSize(QtCore.QSize(256, 256))
        self.canvas.setObjectName("canvas")
        self.gridLayout.addWidget(self.canvas, 1, 0, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(hit_ratio_RTV)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.cur_ratio = QtWidgets.QLabel(hit_ratio_RTV)
        self.cur_ratio.setObjectName("cur_ratio")
        self.gridLayout.addWidget(self.cur_ratio, 2, 1, 1, 1)

        self.retranslateUi(hit_ratio_RTV)
        QtCore.QMetaObject.connectSlotsByName(hit_ratio_RTV)

    def retranslateUi(self, hit_ratio_RTV):
        _translate = QtCore.QCoreApplication.translate
        hit_ratio_RTV.setWindowTitle(_translate("hit_ratio_RTV", "Form"))
        self.label.setText(_translate("hit_ratio_RTV", "平均命中率(%)"))
        self.title.setText(_translate("hit_ratio_RTV", "(未知)"))
        self.avg_ratio.setText(_translate("hit_ratio_RTV", "(未知)"))
        self.label_2.setText(_translate("hit_ratio_RTV", "当前命中率(%)"))
        self.cur_ratio.setText(_translate("hit_ratio_RTV", "(未知)"))

from visualizer import PolyLineCanvas
