# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log_widget.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_log_table(object):
    def setupUi(self, log_table):
        log_table.setObjectName("log_table")
        log_table.resize(631, 143)
        self.gridLayout_6 = QtWidgets.QGridLayout(log_table)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.line = QtWidgets.QFrame(log_table)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_6.addWidget(self.line, 0, 5, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(log_table)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.time_start_box = QtWidgets.QSpinBox(log_table)
        self.time_start_box.setKeyboardTracking(False)
        self.time_start_box.setMaximum(999999999)
        self.time_start_box.setSingleStep(100)
        self.time_start_box.setObjectName("time_start_box")
        self.gridLayout_2.addWidget(self.time_start_box, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(log_table)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.time_end_box = QtWidgets.QSpinBox(log_table)
        self.time_end_box.setKeyboardTracking(False)
        self.time_end_box.setMaximum(999999999)
        self.time_end_box.setSingleStep(100)
        self.time_end_box.setProperty("value", 1000)
        self.time_end_box.setObjectName("time_end_box")
        self.gridLayout_2.addWidget(self.time_end_box, 1, 1, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_2 = QtWidgets.QLabel(log_table)
        self.label_2.setObjectName("label_2")
        self.gridLayout_5.addWidget(self.label_2, 0, 0, 1, 1)
        self.packet_combo = ComboBox(log_table)
        self.packet_combo.setObjectName("packet_combo")
        self.gridLayout_5.addWidget(self.packet_combo, 1, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 4, 1, 1)
        self.table = LogTableWidget(log_table)
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.table.setAlternatingRowColors(True)
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setCascadingSectionResizes(True)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setCascadingSectionResizes(False)
        self.table.verticalHeader().setHighlightSections(True)
        self.table.verticalHeader().setSortIndicatorShown(False)
        self.table.verticalHeader().setStretchLastSection(False)
        self.gridLayout_6.addWidget(self.table, 1, 0, 1, 7)
        self.line_2 = QtWidgets.QFrame(log_table)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_6.addWidget(self.line_2, 0, 1, 1, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_5 = QtWidgets.QLabel(log_table)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.id_combo = ComboBox(log_table)
        self.id_combo.setObjectName("id_combo")
        self.gridLayout_3.addWidget(self.id_combo, 1, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_3, 0, 2, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(log_table)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.num_label = QtWidgets.QLabel(log_table)
        self.num_label.setObjectName("num_label")
        self.gridLayout.addWidget(self.num_label, 0, 1, 1, 2)
        self.refresh_button = QtWidgets.QPushButton(log_table)
        self.refresh_button.setObjectName("refresh_button")
        self.gridLayout.addWidget(self.refresh_button, 1, 0, 1, 2)
        self.refresh_check = QtWidgets.QCheckBox(log_table)
        self.refresh_check.setObjectName("refresh_check")
        self.gridLayout.addWidget(self.refresh_check, 1, 2, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout, 0, 6, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_6 = QtWidgets.QLabel(log_table)
        self.label_6.setObjectName("label_6")
        self.gridLayout_4.addWidget(self.label_6, 0, 0, 1, 1)
        self.operate_combo = ComboBox(log_table)
        self.operate_combo.setObjectName("operate_combo")
        self.gridLayout_4.addWidget(self.operate_combo, 1, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_4, 0, 3, 1, 1)

        self.retranslateUi(log_table)
        QtCore.QMetaObject.connectSlotsByName(log_table)

    def retranslateUi(self, log_table):
        _translate = QtCore.QCoreApplication.translate
        log_table.setWindowTitle(_translate("log_table", "Form"))
        self.label_3.setText(_translate("log_table", "起始时间:"))
        self.label_4.setText(_translate("log_table", "终止时间:"))
        self.label_2.setText(_translate("log_table", "包头部(PacketHead)"))
        self.table.setSortingEnabled(True)
        self.label_5.setText(_translate("log_table", "发起者(Id)"))
        self.label.setText(_translate("log_table", "结果数量:"))
        self.num_label.setText(_translate("log_table", "(未知)"))
        self.refresh_button.setText(_translate("log_table", "刷新"))
        self.refresh_check.setText(_translate("log_table", "实时刷新"))
        self.label_6.setText(_translate("log_table", "操作名(Operate)"))

from gui.LogWidget import LogTableWidget
from gui.common import ComboBox