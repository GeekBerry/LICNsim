# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_log_widget(object):
    def setupUi(self, log_widget):
        log_widget.setObjectName("log_widget")
        log_widget.resize(538, 262)
        log_widget.setAutoFillBackground(True)
        self.gridLayout = QtWidgets.QGridLayout(log_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.edit = QtWidgets.QLineEdit(log_widget)
        self.edit.setObjectName("edit")
        self.horizontalLayout.addWidget(self.edit)
        self.button = QtWidgets.QPushButton(log_widget)
        self.button.setObjectName("button")
        self.horizontalLayout.addWidget(self.button)
        self.check = QtWidgets.QCheckBox(log_widget)
        self.check.setChecked(True)
        self.check.setTristate(False)
        self.check.setObjectName("check")
        self.horizontalLayout.addWidget(self.check)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.table = TableWidget(log_widget)
        self.table.setMaximumSize(QtCore.QSize(16777215, 200))
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.gridLayout.addWidget(self.table, 2, 0, 1, 1)

        self.retranslateUi(log_widget)
        QtCore.QMetaObject.connectSlotsByName(log_widget)

    def retranslateUi(self, log_widget):
        _translate = QtCore.QCoreApplication.translate
        log_widget.setWindowTitle(_translate("log_widget", "Form"))
        self.button.setText(_translate("log_widget", "查询"))
        self.check.setText(_translate("log_widget", "实时刷新"))

from gui import TableWidget
