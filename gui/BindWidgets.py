from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QAbstractItemView
from common import TableWidget

from debug import showCall


class BindLabel(QLabel):
    def __init__(self, parent, obj, attr):
        super().__init__(parent)
        self.obj = obj
        self.attr = attr
        self.refresh()

    def refresh(self):
        self.setText(str(getattr(self.obj, self.attr)))


class BindCheckBox(QCheckBox):
    def __init__(self, parent, obj, attr):
        super().__init__(parent)
        self.obj = obj
        self.attr = attr
        self.refresh()
        self.stateChanged.connect(self.stateChangedSlot)

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


class BindSpinBox(QSpinBox):
    def __init__(self, parent, obj, attr, range):
        super().__init__(parent)
        self.obj = obj
        self.attr = attr

        self.setRange(*range)
        self.refresh()
        self.editingFinished.connect(self.editingFinishedSlot)

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
        self.obj = obj
        self.attr = attr

        self.setRange(*range)
        self.refresh()
        self.editingFinished.connect(self.editingFinishedSlot)


class BindComboBox(QComboBox):
    def __init__(self, parent, obj, attr, range):
        """
        :param parent:
        :param obj:
        :param attr:
        :param range: (str, ...)  只接受字符串类型
        """
        super().__init__(parent)
        self.obj = obj
        self.attr = attr
        self.addItems(range)
        self.currentIndexChanged.connect(self.currentIndexChangedSlot)
        self.refresh()

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
    def __init__(self, parent, heads, row_iter):
        super().__init__(parent)
        self.row_iter = row_iter

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.horizontalHeader().setStretchLastSection(True)
        self.setHeads(*heads)
        self.refresh()

    @showCall
    def refresh(self):
        rows = list(self.row_iter)  # 先生成列表才能统计行数
        self.setRowCount(len(rows))
        for row, values in enumerate(rows):
            self.setRow(row, *values)


