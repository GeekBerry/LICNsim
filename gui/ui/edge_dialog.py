# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edge_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_edge_dialog(object):
    def setupUi(self, edge_dialog):
        edge_dialog.setObjectName("edge_dialog")
        edge_dialog.resize(504, 287)
        self.gridLayout = QtWidgets.QGridLayout(edge_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.tree = UIAttrsTree(edge_dialog)
        self.tree.setObjectName("tree")
        self.tree.headerItem().setText(0, "1")
        self.gridLayout.addWidget(self.tree, 0, 0, 1, 1)

        self.retranslateUi(edge_dialog)
        QtCore.QMetaObject.connectSlotsByName(edge_dialog)

    def retranslateUi(self, edge_dialog):
        _translate = QtCore.QCoreApplication.translate
        edge_dialog.setWindowTitle(_translate("edge_dialog", "Dialog"))


from gui.BindWidgets import UIAttrsTree
