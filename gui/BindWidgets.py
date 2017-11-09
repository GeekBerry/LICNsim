from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QCheckBox, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QAbstractItemView
from common import TableWidget

from debug import showCall


def bindWidgetToAttr(widget, obj, attr):
    if hasattr(obj, attr):
        widget.obj = obj
        widget.attr = attr
        widget.refresh()


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
        self.stateChanged.connect(self.stateChangedSlot)
        bindWidgetToAttr(self, obj, attr)

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
        bindWidgetToAttr(self, obj, attr)

    def refresh(self):
        self.setText( getattr(self.obj, self.attr) )

    def editingFinishedSlot(self):
        setattr(self.obj, self.attr, self.text())


class BindSpinBox(QSpinBox):
    def __init__(self, parent, range, obj, attr):
        super().__init__(parent)
        self.setRange(*range)
        self.editingFinished.connect(self.editingFinishedSlot)
        bindWidgetToAttr(self, obj, attr)

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

    def __init__(self, parent, range, obj, attr):
        super().__init__(parent)
        self.setRange(*range)
        self.editingFinished.connect(self.editingFinishedSlot)

        self.obj = obj
        self.attr = attr
        self.refresh()


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




