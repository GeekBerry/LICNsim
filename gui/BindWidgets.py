from collections import defaultdict

from PyQt5.QtWidgets import QLabel, QSpinBox, QDoubleSpinBox, QAbstractItemView

from gui.common import ComboBox, TableWidget, TreeWidget
from debug import showCall

# 准备删除
# class BComboBox(ComboBox):
#     def __init__(self, parent, obj, attrs):
#         super().__init__(parent)
#
#         self.getter= lambda : attrs['getter'](obj)
#         self.setter= lambda value: attrs['setter'](obj, value)
#         self.addItems(attrs['range'].items())
#
#         self.currentIndexChanged.connect(self.currentIndexChangedSlot)
#
#     def refresh(self):
#         text, data = self.getter()
#         index = self.addItem(text, data)
#         self.setCurrentIndex(index)
#
#     def currentIndexChangedSlot(self, index):
#         if self.setter is not None:
#             data = self.itemData(index)
#             self.setter(data)
#

# class BLabel(QLabel):
#     def __init__(self, parent, obj, attrs):
#         super().__init__(parent)
#
#         self.getter= lambda: str( attrs['getter'](obj) )
#
#     def refresh(self):
#         self.setText(self.getter())
#
#
# class BSpinBox(QSpinBox):
#     def __init__(self, parent, obj, attrs):
#         super().__init__(parent)
#
#         self.getter= lambda : attrs['getter'](obj)
#         self.setter= lambda value: attrs['setter'](obj, value)
#         self.setRange(*attrs['range'])
#
#         self.editingFinished.connect(self.editingFinishedSlot)
#
#     def refresh(self):
#         self.setValue(self.getter())
#
#     def editingFinishedSlot(self):
#         if self.setter is not None:
#             self.setter(self.value())
#
#     def wheelEvent(self, event):
#         pass
#

# class BDoubleSpinBox(QDoubleSpinBox):
#     def __init__(self, parent, obj, attrs):
#         super().__init__(parent)
#         self.setSingleStep(0.01)
#
#         self.getter= lambda : attrs['getter'](obj)
#         self.setter= lambda value: attrs['setter'](obj, value)
#         self.setRange(*attrs['range'])
#
#         self.editingFinished.connect(self.editingFinishedSlot)
#
#     @showCall
#     def refresh(self):
#         self.setValue(self.getter())
#
#     @showCall
#     def editingFinishedSlot(self):
#         if self.setter is not None:
#             self.setter(self.value())
#
#     @showCall
#     def wheelEvent(self, event):
#         pass
#

# class BTable(TableWidget):
#     def __init__(self, parent, obj, attrs):
#         super().__init__(parent)
#         self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
#         self.horizontalHeader().setStretchLastSection(True)
#
#         self.setHeads(*attrs['range'])
#         self.getter= lambda : attrs['getter'](obj)
#
#     def refresh(self):
#         self.clearContents()
#
#         values = list( self.getter() )
#         self.setRowCount( len(values) )
#         for row, value in enumerate(values):
#             self.setRow(row, *value)

#
# class BNameTree(TreeWidget):
#     def __init__(self, parent, obj, attrs):
#         super().__init__(parent)
#         self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
#
#         self.setHeads( *attrs['range'] )
#         self.name_tree= attrs['tree'](obj)
#         self.getter= attrs['getter']
#
#     def refresh(self):
#         self.clearSelection()
#         self.showNameTree(self, self.name_tree)
#
#     def showNameTree(self, tree_item, name_tree):
#         for name_node in name_tree:
#             if name_node.hasValue():
#                 values= self.getter( name_node.getValue() )
#             else:
#                 values= ()
#             tree_item[name_node.key].setValues(*values)
#
#             self.showNameTree(tree_item[name_node.key], name_node)


# ======================================================================================================================
# 准备删除
# class UIAttrsTree(TreeWidget):
#     UI_TYPE_MAP = {
#         'SpinBox':  BSpinBox,
#         'Int':      BSpinBox,
#         'DSpinBox': BDoubleSpinBox,
#         'Float':    BDoubleSpinBox,
#         'Label':    BLabel,
#         'ComboBox': BComboBox,
#         'Table':    BTable,
#         'NameTree': BNameTree,
#     }
#
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.attr_table = defaultdict(list)  # { attr_name:[widget, ...], ... }
#
#     def install(self, announces, api):
#         self.setHeads('Attr', 'Detail')  # XXX 放在 __init__ 中初始化会被覆盖掉
#         announces['playSteps'].append(self.playSteps)
#         self.refresh()
#         self.expandAll()
#
#     def playSteps(self, steps=None):
#         if self.isVisible():
#             self.refresh()
#
#     def addEntry(self, name, obj):
#         self[name].setValues(obj.__class__.__qualname__)
#
#         if hasattr(obj, 'UI_ATTRS') and (name not in self.attr_table):
#             for attr_name, attr in obj.UI_ATTRS.items():
#                 widget= self.UI_TYPE_MAP[ attr['type'] ](self, obj, attr)  # 查表, 生成 widget
#                 self[name][attr_name].setValues(widget)
#                 self.attr_table[name].append(widget)
#
#     def refresh(self):
#         for attr_widgets in self.attr_table.values():
#             for widget in attr_widgets:
#                 widget.refresh()



