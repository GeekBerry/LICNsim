from debug import showCall

from core import INF
from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QDoubleSpinBox, QAbstractItemView, QComboBox


class BindLabel(QLabel):
    def __init__(self, parent, obj, attr):
        super().__init__(parent)
        self.obj = obj
        self.attr = attr
        self.refresh()

    def refresh(self):
        self.setText(str(getattr(self.obj, self.attr)))


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


from gui.common import TableWidget


class BindTable(TableWidget):
    def __init__(self, parent, heads, row_iter):
        super().__init__(parent)
        self.row_iter = row_iter

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.horizontalHeader().setStretchLastSection(True)
        self.setHeads(*heads)
        self.refresh()

    def refresh(self):
        rows = list(self.row_iter)  # 先生成列表才能统计行数
        self.setRowCount(len(rows))
        for row, values in enumerate(rows):
            self.setRow(row, *values)


# ======================================================================================================================
from core import Packet


class Controller(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.pair_dict = {}  # { str:QWidget 或 Controller, ...}

    def setTree(self, tree_widget):
        """
        将 self.pair_dict 的键值对显示到 tree_widget 上
        如果键值对中的值为 Controller 实例，递归渲染
        :param tree_widget:
        :return: None
        """
        for key, value in self.pair_dict.items():
            if isinstance(value, Controller):
                value.setTree(tree_widget[key])
            else:
                tree_widget[key].setValues(value)

    def refresh(self):
        for widget in self.pair_dict.values():
            if widget.isVisible():
                widget.refresh()


# ----------------------------------------------------------------------------------------------------------------------
class NodeController(Controller):
    def __init__(self, parent, icn_node):
        super().__init__(parent)

        for key, unit in icn_node.units.items():
            if key == 'cs':  # XXX 依照什么进行类型判断？ key 还是 unit 的类型
                self.pair_dict[key] = ContentStoreController(self, unit)

            if key == 'replace':
                self.pair_dict[key] = ReplaceController(self, unit)


class ContentStoreController(Controller):
    def __init__(self, parent, cs_unit):
        super().__init__(parent)
        if hasattr(cs_unit, 'capacity'):
            self.pair_dict['capacity'] = BindSpinBox(self, cs_unit, 'capacity', range=(0, 10000))

        if hasattr(cs_unit, 'size'):
            self.pair_dict['size'] = BindLabel(self, cs_unit, 'size')

        if hasattr(cs_unit, 'table'):
            self.pair_dict['table'] = BindTable(self, Packet.HEAD_FIELDS, map(Packet.head, cs_unit.table.values()), )


class ReplaceController(Controller):
    def __init__(self, parent, replace_unit):
        super().__init__(parent)
        if hasattr(replace_unit, 'mode'):
            self.pair_dict['mode'] = BindComboBox(self, replace_unit, 'mode', ('FIFO', 'LRU', 'LFU'))

        if hasattr(replace_unit, 'db_table'):
            # TODO for core import DataBaseTable; assert isinstance(replace_unit.db_table, DataBaseTable)
            self.pair_dict['table'] = BindTable(self,
                                                replace_unit.db_table.getFields(),
                                                map(lambda record: record.values(), replace_unit.db_table.query())
                                                )


# ======================================================================================================================
class EdgeController(Controller):
    def __init__(self, parent, channel):
        super().__init__(parent)

        if hasattr(channel, 'rate'):
            self.pair_dict['rate'] = BindSpinBox(self, channel, 'rate', range=(0, INF))

        if hasattr(channel, 'delay'):
            self.pair_dict['delay'] = BindSpinBox(self, channel, 'delay', range=(0, INF))

        if hasattr(channel, 'loss'):
            self.pair_dict['loss'] = BindDoubleSpinBox(self, channel, 'loss', range=(0.0, 1.0))

        if hasattr(channel, 'queue'):
            self.pair_dict['queue'] = BindTable(self, Packet.HEAD_FIELDS, map(Packet.head, channel.queue))
