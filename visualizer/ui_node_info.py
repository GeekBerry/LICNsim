# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_node_info.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NodeInfo(object):
    def setupUi(self, NodeInfo):
        NodeInfo.setObjectName("NodeInfo")
        NodeInfo.resize(917, 642)
        self.gridLayout = QtWidgets.QGridLayout(NodeInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(NodeInfo)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_cs = QtWidgets.QWidget()
        self.tab_cs.setObjectName("tab_cs")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_cs)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.table_cs = QtWidgets.QTableWidget(self.tab_cs)
        self.table_cs.setObjectName("table_cs")
        self.table_cs.setColumnCount(0)
        self.table_cs.setRowCount(0)
        self.gridLayout_3.addWidget(self.table_cs, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_cs, "")
        self.tab_infotable = QtWidgets.QWidget()
        self.tab_infotable.setObjectName("tab_infotable")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_infotable)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tree_info = QtWidgets.QTreeWidget(self.tab_infotable)
        self.tree_info.setObjectName("tree_info")
        self.tree_info.headerItem().setText(0, "1")
        self.gridLayout_2.addWidget(self.tree_info, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_infotable, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(NodeInfo)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(NodeInfo)

    def retranslateUi(self, NodeInfo):
        _translate = QtCore.QCoreApplication.translate
        NodeInfo.setWindowTitle(_translate("NodeInfo", "Dialog"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_cs), _translate("NodeInfo", "ContentStore"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_infotable), _translate("NodeInfo", "InfoTable"))

