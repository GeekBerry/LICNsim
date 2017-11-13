# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'node_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_node_dialog(object):
    def setupUi(self, node_dialog):
        node_dialog.setObjectName("node_dialog")
        node_dialog.resize(600, 600)
        self.gridLayout = QtWidgets.QGridLayout(node_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.tree = TreeWidget(node_dialog)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree.setAlternatingRowColors(True)
        self.tree.setObjectName("tree")
        self.tree.headerItem().setText(0, "1")
        self.tree.header().setCascadingSectionResizes(True)
        self.gridLayout.addWidget(self.tree, 0, 0, 1, 1)

        self.retranslateUi(node_dialog)
        QtCore.QMetaObject.connectSlotsByName(node_dialog)

    def retranslateUi(self, node_dialog):
        _translate = QtCore.QCoreApplication.translate
        node_dialog.setWindowTitle(_translate("node_dialog", "Dialog"))


from gui import TreeWidget
