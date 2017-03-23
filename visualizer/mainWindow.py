# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(812, 719)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 812, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setCursor(QtGui.QCursor(QtCore.Qt.UpArrowCursor))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.head_tool_bar = QtWidgets.QToolBar(MainWindow)
        self.head_tool_bar.setObjectName("head_tool_bar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.head_tool_bar)
        MainWindow.insertToolBarBreak(self.head_tool_bar)
        self.dockWidget_5 = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_5.setObjectName("dockWidget_5")
        self.dockWidgetContents_5 = QtWidgets.QWidget()
        self.dockWidgetContents_5.setObjectName("dockWidgetContents_5")
        self.dockWidget_5.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_5)
        self.action_save = QtWidgets.QAction(MainWindow)
        self.action_save.setCheckable(False)
        self.action_save.setObjectName("action_save")
        self.head_tool_bar.addAction(self.action_save)
        self.head_tool_bar.addSeparator()

        self.retranslateUi(MainWindow)
        self.action_save.triggered.connect(self.dockWidget_5.hide)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.head_tool_bar.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.action_save.setText(_translate("MainWindow", "save"))
        self.action_save.setToolTip(_translate("MainWindow", "保存"))


if __name__ == "__main__":
    from PyQt5.QtWidgets  import QApplication, QWidget, QMainWindow
    import sys

    app = QApplication(sys.argv)
    widget = QMainWindow()
    Ui_MainWindow().setupUi(widget) # Ui_Form为生成的Form的名字
    widget.show()
    sys.exit(app.exec_())
