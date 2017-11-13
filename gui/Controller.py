from PyQt5.QtWidgets import QWidget

from core import INF, Packet
from gui import *


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
    class ContentStoreController(Controller):
        def __init__(self, parent, cs_unit):
            super().__init__(parent)
            if hasattr(cs_unit, 'capacity'):
                self.pair_dict['capacity'] = BindSpinBox(self, (0, 10000), cs_unit, 'capacity',)

            if hasattr(cs_unit, 'size'):
                self.pair_dict['size'] = BindLabel(self, cs_unit, 'size')

            if hasattr(cs_unit, 'table'):
                self.pair_dict['table'] = BindTable(self, Packet.HEAD_FIELDS,
                                                    map(Packet.head, cs_unit.table.values()), )

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

    class FaceController(Controller):
        class EntryController(Controller):
            def __init__(self, parent, entry):
                super().__init__(parent)
                self.pair_dict['receivable'] = BindCheckBox(self, entry, 'receivable')
                self.pair_dict['sendable'] = BindCheckBox(self, entry, 'sendable')

        def __init__(self, parent, face_unit):
            super().__init__(parent)
            for face_id, entry in face_unit.table.items():
                self.pair_dict[face_id] = self.EntryController(self, entry)

    def __init__(self, parent, icn_node):
        super().__init__(parent)

        for key, unit in icn_node.units.items():
            if key == 'cs':  # XXX 依照什么进行类型判断？ key 还是 unit 的类型
                self.pair_dict[key] = self.ContentStoreController(self, unit)

            if key == 'replace':
                self.pair_dict[key] = self.ReplaceController(self, unit)

            if key == 'face':
                self.pair_dict[key] = self.FaceController(self, unit)


# ======================================================================================================================
class EdgeController(Controller):
    def __init__(self, parent, channel):
        super().__init__(parent)

        if hasattr(channel, 'rate'):
            self.pair_dict['rate'] = BindSpinBox(self, (0, INF), channel, 'rate')

        if hasattr(channel, 'delay'):
            self.pair_dict['delay'] = BindSpinBox(self, (0, INF), channel, 'delay')

        if hasattr(channel, 'loss'):
            self.pair_dict['loss'] = BindDoubleSpinBox(self, (0.0, 1.0), channel, 'loss')

        if hasattr(channel, 'queue'):
            self.pair_dict['queue'] = BindTable(self, Packet.HEAD_FIELDS, map(Packet.head, channel.queue))
