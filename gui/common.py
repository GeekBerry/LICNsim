from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from debug import showCall


def HotColor(value):
    color = QColor()
    color.setHsvF(0.3 * (1 - value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color


def DeepColor(value, color=QColor(Qt.red)):  # h:0.0为红色
    h, s, v, a = color.getHsvF()
    return QColor.fromHsvF(h, value, v, a)


# ================================================================================
class UIFrom:
    def __init__(self, UI_From):
        """
        :param UI_From: 要使用的 UI_From 类名
        """
        self.UI_From = UI_From

    def __call__(self, cls):
        def creater(parent, *args, **kwargs):
            widget = cls.__new__(cls, parent)
            super(cls, widget).__init__(parent)
            widget.ui = self.UI_From()
            widget.ui.setupUi(widget)
            widget.__init__(parent, *args, **kwargs)
            return widget

        return creater


# ================================================================================
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget


class TreeItem(QTreeWidgetItem):
    TEXT, DATA = 0, 1

    def __init__(self, parent, text):
        super().__init__(parent, [text])
        self.table = {}  # {key:TreeItem, ...}

    def __getitem__(self, key):
        if key not in self.table:
            self.table[key]= TreeItem(self, str(key))
        return self.table[key]

    def __delitem__(self, key):
        if key in self.table:
            index = self.indexOfChild(self.table[key])
            item = self.takeChild(index)
            item.clear()
            del self.table[key]

    def setValues(self, *values):
        for col, value in enumerate(values, start=1):  # start=1, 因为第 0 位为item的头部
            if isinstance(value, QWidget):
                self.treeWidget().setItemWidget(self, col, value)
            else:
                self.setData(col, self.TEXT, str(value))  # XXX 等价于 self.setText( col, str(value) ) ???
                self.setData(col, self.DATA, value)

    def getData(self, col):
        return self.data(col, self.DATA)

    def getPath(self):
        path= []
        cur_item= self
        while cur_item:
            path.append( cur_item.text(0) )
            cur_item= cur_item.parent()
        return reversed(path)

    def clear(self):
        for child in self.takeChildren():
            child.clear()
        self.table.clear()


class TreeWidget(QTreeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.setAlternatingRowColors(True)  # 隔行显示颜色
        self.table = {}  # {key:TreeItem, ...}

    def setHeads(self, *values):
        for col, value in enumerate(values):
            self.headerItem().setText(col, str(value))

    def __getitem__(self, key):
        if key not in self.table:
            self.table[key]= TreeItem(self, str(key))
        return self.table[key]

    def __delitem__(self, key):
        if key in self.table:
            index = self.indexOfTopLevelItem(self.table[key])
            item = self.takeTopLevelItem(index)
            item.clear()
            del self.table[key]


# ======================================================================================================================
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class TableWidget(QTableWidget):
    def setHeads(self, *values):
        self.setColumnCount(len(values))
        for col, value in enumerate(values):
            self.setHorizontalHeaderItem(  col, QTableWidgetItem( str(value) )  )

    # def setLines(self, *values):  XXX 这个函数是干嘛的？
    #     self.setRowCount( len(values) )
    #     for row, value in enumerate(values):
    #         self.setVerticalHeaderItem(  row, QTableWidgetItem( str(value) )  )

    def setRow(self, row, *datas):
        for col, data in enumerate(datas):
            self.setCell(row, col, data)

    def setCell(self, row, col, data=None):
        if not 0 <= col < self.columnCount():  # XXX 越界赋值会换行， 有必要在此检查边界以免越界覆盖
            return

        item = QTableWidgetItem()
        if isinstance(data, (int, float)):
            item.setData(0, data)
        else:
            item.setText(str(data))

        item.setData(1, data)
        self.setItem(row, col, item)

    def getCellText(self, row, col):
        return self.item(row, col).text()

    def getCellData(self, row, col):
        return self.item(row, col).data(1)


# ======================================================================================================================
from PyQt5.QtWidgets import QComboBox


class ComboBox(QComboBox):
    def addItem(self, text, data=None):
        index = self.findText(text)
        if index == -1:  # 没有找到, 返回 '-1'
            index = 0
            while index < self.count() and text < self.itemText(index):  # 插入排序
                index += 1
            self.insertItem(index, text, data)
        return index

    def addItems(self, items):
        for text, data in items:
            self.addItem(text, data)

    def wheelEvent(self, event):  # 禁用滚轮
        pass


