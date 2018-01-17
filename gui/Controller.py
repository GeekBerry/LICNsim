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
            if widget.isVisible() and hasattr(widget, 'refresh'):  # 可见, 且是 BindWidget
                widget.refresh()


# ----------------------------------------------------------------------------------------------------------------------
class NodeController(Controller):
    class IOInfoContorller(Controller):
        def __init__(self, parent, io_info_unit):
            super().__init__(parent)
            self.io_info_unit = io_info_unit
            self.pair_dict['pit'] = BindTable(self, ('Name', 'FaceIds'), self.getPITRows)

        def getPITRows(self):
            return list(self.io_info_unit.pit.items())

    class ContentStoreController(Controller):
        def __init__(self, parent, cs_unit):
            super().__init__(parent)
            self.cs_unit = cs_unit

            self.pair_dict['capacity'] = BindSpinBox(self, cs_unit, 'capacity', (0, INF))
            self.pair_dict['size'] = BindLabel(self, cs_unit, 'size')
            self.pair_dict['table'] = BindTable(self, Packet.HEAD_FIELDS, self.getCSTableRows)

        def getCSTableRows(self):
            return [packet.head() for packet in self.cs_unit.table.values()]

    class EvictController(Controller):
        def __init__(self, parent, evict_unit):
            super().__init__(parent)
            self.pair_dict['mode'] = BindComboBox(self, evict_unit, '_mode', evict_unit.MODE_TYPES)
            self.pair_dict['life_time'] = BindSpinBox(self, evict_unit, 'life_time', (0, INF))

    class ReplaceController(Controller):
        def __init__(self, parent, replace_unit):
            super().__init__(parent)
            self.replace_unit = replace_unit

            self.pair_dict['mode'] = BindComboBox(self, replace_unit, '_mode', replace_unit.MODE_FIELD_MAP.keys())
            self.pair_dict['table'] = BindTable(self, replace_unit.db_table.getFields(), self.getReplaceTableRows)

        def getReplaceTableRows(self):
            return [record.values() for record in self.replace_unit.db_table.query()]

    class FaceController(Controller):
        class EntryController(Controller):
            def __init__(self, parent, entry):
                super().__init__(parent)
                self.pair_dict['receivable'] = BindCheckBox(self, entry, 'receivable')
                self.pair_dict['sendable'] = BindCheckBox(self, entry, 'sendable')

        def __init__(self, parent, face_unit):
            super().__init__(parent)
            self.face_unit = face_unit

            self.pair_dict['capacity'] = BindSpinBox(self, face_unit.bucket, 'capacity', (0, INF))
            self.pair_dict['size'] = BindLabel(self, face_unit.bucket, 'size')
            self.pair_dict['rate'] = BindSpinBox(self, face_unit.bucket, 'rate', (0, INF))
            self.pair_dict['rest'] = BindLabel(self, face_unit.bucket, 'rest')
            self.pair_dict['queue'] = BindTable(self, ('FaceId', 'Packet'), self.getBucketRows)

            for face_id, entry in face_unit.table.items():
                self.pair_dict[f'Face {face_id}'] = self.EntryController(self, entry)

        def getBucketRows(self):
            return list(self.face_unit.bucket)

    def __init__(self, parent, icn_node):
        super().__init__(parent)
        self.pair_dict['node type'] = QLabel(icn_node.__class__.__name__)

        # XXX 以什么作unit判断依据? key 还是 unit 的类型?
        unit = icn_node.units.get('info')
        if unit is not None:
            self.pair_dict['IOInfoUnit'] = self.IOInfoContorller(self, unit)

        unit = icn_node.units.get('cs')
        if unit is not None:
            self.pair_dict['ContentStoreUnit'] = self.ContentStoreController(self, unit)

        unit = icn_node.units.get('evict')
        if unit is not None:
            self.pair_dict['CSEvictUnit'] = self.EvictController(self, unit)

        unit = icn_node.units.get('replace')
        if unit is not None:
            self.pair_dict['ReplaceUnit'] = self.ReplaceController(self, unit)

        unit = icn_node.units.get('face')
        if unit is not None:
            self.pair_dict['FaceUnit'] = self.FaceController(self, unit)


# ======================================================================================================================
class EdgeController(Controller):
    def __init__(self, parent, icn_edge):
        super().__init__(parent)
        self.icn_edge = icn_edge

        self.pair_dict['rate'] = BindSpinBox(self, icn_edge, 'rate', (0, INF))
        self.pair_dict['delay'] = BindSpinBox(self, icn_edge, 'delay', (0, INF))
        self.pair_dict['loss'] = BindDoubleSpinBox(self, icn_edge, 'loss', (0.0, 1.0))
        self.pair_dict['queue'] = BindTable(self, Packet.HEAD_FIELDS, self.getQueueRows)

    def getQueueRows(self):
        return [packet.head() for packet in self.icn_edge.queue()]
