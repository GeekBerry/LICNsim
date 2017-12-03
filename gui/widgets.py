from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QCheckBox, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QAbstractItemView, QTreeWidgetItem, QWidget, QTreeWidget, QHeaderView,
                             QTableWidget, QAbstractScrollArea, QTableWidgetItem)

from debug import showCall


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
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
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


class TableWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setAlternatingRowColors(True)  # 隔行显示颜色

    def setHeads(self, *values):  # 设置行表头
        self.setColumnCount(len(values))
        for col, value in enumerate(values):
            self.setHorizontalHeaderItem(  col, QTableWidgetItem( str(value) )  )

    def setLines(self, *values):  # 设置列表头
        self.setRowCount( len(values) )
        for row, value in enumerate(values):
            self.setVerticalHeaderItem(  row, QTableWidgetItem( str(value) )  )

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


# =============================================================================
def _bindWidgetToAttr(widget, obj, attr):
    if hasattr(obj, attr):
        widget.obj = obj
        widget.attr = attr
        widget.refresh()


class BindLabel(QLabel):
    def __init__(self, parent, obj, attr):
        super().__init__(parent)
        _bindWidgetToAttr(self, obj, attr)

    def refresh(self):
        self.setText(str(getattr(self.obj, self.attr)))


class BindCheckBox(QCheckBox):
    def __init__(self, parent, obj, attr):
        super().__init__(parent)
        self.stateChanged.connect(self.stateChangedSlot)
        _bindWidgetToAttr(self, obj, attr)

    def refresh(self):
        if getattr(self.obj, self.attr):
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

    def stateChangedSlot(self, state):
        if state:
            setattr(self.obj, self.attr, Qt.Checked)
        else:
            setattr(self.obj, self.attr, Qt.Unchecked)


class BindLineEdit(QLineEdit):
    def __init__(self, parnet, obj, attr):
        super().__init__(parnet)
        self.editingFinished.connect(self.editingFinishedSlot)
        _bindWidgetToAttr(self, obj, attr)

    def refresh(self):
        self.setText( getattr(self.obj, self.attr) )

    def editingFinishedSlot(self):
        setattr(self.obj, self.attr, self.text())


class BindSpinBox(QSpinBox):
    def __init__(self, parent, obj, attr, range):
        super().__init__(parent)
        self.setRange(*range)
        self.editingFinished.connect(self.editingFinishedSlot)
        _bindWidgetToAttr(self, obj, attr)

    def editingFinishedSlot(self):
        setattr(self.obj, self.attr, self.value())

    def refresh(self):
        self.setValue(getattr(self.obj, self.attr))

    def wheelEvent(self, event):
        pass


class BindDoubleSpinBox(QDoubleSpinBox):
    editingFinishedSlot = BindSpinBox.editingFinishedSlot
    refresh = BindSpinBox.refresh
    wheelEvent = BindSpinBox.wheelEvent

    def __init__(self, parent, obj, attr, range):
        super().__init__(parent)
        self.setRange(*range)
        self.editingFinished.connect(self.editingFinishedSlot)
        _bindWidgetToAttr(self, obj, attr)


class BindComboBox(QComboBox):
    def __init__(self, parent, obj, attr, range):
        """
        :param parent:
        :param obj:
        :param attr:
        :param range: (str, ...)  只接受字符串类型
        """
        super().__init__(parent)
        self.addItems(range)
        self.currentIndexChanged.connect(self.currentIndexChangedSlot)
        _bindWidgetToAttr(self, obj, attr)

    def currentIndexChangedSlot(self, index):
        setattr(self.obj, self.attr, self.itemText(index))

    def refresh(self):
        text = getattr(self.obj, self.attr)
        index = self.findText(text)
        assert index != -1  # 一定要找到
        self.setCurrentIndex(index)

    def wheelEvent(self, event):
        pass


class BindTable(TableWidget):
    def __init__(self, parent, heads, get_rows):
        super().__init__(parent)
        self.getRows = get_rows

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.setHeads(*heads)
        self.refresh()

    def refresh(self):
        self.clearContents()

        rows = self.getRows() # 先生成列表才能统计行数
        self.setRowCount(len(rows))
        for row, values in enumerate(rows):
            self.setRow(row, *values)



