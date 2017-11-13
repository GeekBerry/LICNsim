# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'flow_rtv.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_flow_rtv(object):
    def setupUi(self, flow_rtv):
        flow_rtv.setObjectName("flow_rtv")
        flow_rtv.resize(409, 425)
        flow_rtv.setMinimumSize(QtCore.QSize(255, 0))
        self.gridLayout_2 = QtWidgets.QGridLayout(flow_rtv)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(flow_rtv)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.name_label = QtWidgets.QLabel(flow_rtv)
        self.name_label.setObjectName("name_label")
        self.horizontalLayout.addWidget(self.name_label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.canvas = PolyLineCanvas(flow_rtv)
        self.canvas.setMinimumSize(QtCore.QSize(255, 255))
        self.canvas.setObjectName("canvas")
        self.gridLayout_2.addWidget(self.canvas, 2, 0, 1, 2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(flow_rtv)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.scale_label = QtWidgets.QLabel(flow_rtv)
        self.scale_label.setObjectName("scale_label")
        self.gridLayout.addWidget(self.scale_label, 0, 1, 1, 1)
        self.scale_slider = QtWidgets.QSlider(flow_rtv)
        self.scale_slider.setMinimum(0)
        self.scale_slider.setMaximum(3)
        self.scale_slider.setSingleStep(1)
        self.scale_slider.setPageStep(1)
        self.scale_slider.setProperty("value", 0)
        self.scale_slider.setSliderPosition(0)
        self.scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.scale_slider.setInvertedAppearance(False)
        self.scale_slider.setInvertedControls(False)
        self.scale_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.scale_slider.setObjectName("scale_slider")
        self.gridLayout.addWidget(self.scale_slider, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(flow_rtv)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)
        self.mode_combo = ComboBox(flow_rtv)
        self.mode_combo.setObjectName("mode_combo")
        self.gridLayout.addWidget(self.mode_combo, 1, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 2)
        self.note_label = QtWidgets.QLabel(flow_rtv)
        self.note_label.setObjectName("note_label")
        self.gridLayout_2.addWidget(self.note_label, 1, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 4, 0, 1, 2)

        self.retranslateUi(flow_rtv)
        QtCore.QMetaObject.connectSlotsByName(flow_rtv)

    def retranslateUi(self, flow_rtv):
        _translate = QtCore.QCoreApplication.translate
        flow_rtv.setWindowTitle(_translate("flow_rtv", "Form"))
        self.label.setText(_translate("flow_rtv", "前缀(Prefix):"))
        self.name_label.setText(_translate("flow_rtv", "(未知)"))
        self.label_3.setText(_translate("flow_rtv", "分度值:"))
        self.scale_label.setText(_translate("flow_rtv", "(未知)"))
        self.label_2.setText(_translate("flow_rtv", "模式:"))
        self.note_label.setText(_translate("flow_rtv", "(未知)"))

from gui.MatplotlibCanvas import PolyLineCanvas
from gui import ComboBox
