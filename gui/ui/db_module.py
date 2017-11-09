# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'db_module.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_db_module(object):
    def setupUi(self, db_module):
        db_module.setObjectName("db_module")
        db_module.resize(538, 197)
        db_module.setAutoFillBackground(True)
        self.gridLayout = QtWidgets.QGridLayout(db_module)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.edit = QtWidgets.QLineEdit(db_module)
        self.edit.setObjectName("edit")
        self.horizontalLayout.addWidget(self.edit)
        self.label = QtWidgets.QLabel(db_module)
        self.label.setMinimumSize(QtCore.QSize(61, 16))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.check = QtWidgets.QCheckBox(db_module)
        self.check.setObjectName("check")
        self.horizontalLayout.addWidget(self.check)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.table = TableWidget(db_module)
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.gridLayout.addWidget(self.table, 1, 0, 1, 1)

        self.retranslateUi(db_module)
        QtCore.QMetaObject.connectSlotsByName(db_module)

    def retranslateUi(self, db_module):
        _translate = QtCore.QCoreApplication.translate
        db_module.setWindowTitle(_translate("db_module", "Form"))
        self.label.setText(_translate("db_module", "完成"))
        self.check.setText(_translate("db_module", "实时刷新"))

from gui.common import TableWidget
