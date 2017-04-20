#!/usr/bin/python3
#coding=utf-8


from debug import showCall

from core.packet import Packet, Name, PacketHead
from visualizer.common import HeadTreeItem, TreeItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView


class PacketHeadTreeWidget(QTreeWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    @showCall
    def init(self, monitor):
        self.monitor= monitor
        self.setHeaderItem(HeadTreeItem(self, 'Key'))
        self._show()

    def install(self, announces, api):
        announces['playSteps'].append(self.refresh)
        self.api= api

    def refresh(self, steps):
        self._show()
        self.setColumnWidth(0, 200)
        self.expandToDepth(0)

    @showCall
    def _show(self):
        for p_name, packet_types in self.monitor.packets.items():
            for p_type, packet_nonces in packet_types.items():
                for p_nonce in packet_nonces:
                    self.headerItem()[p_name][ Packet.TYPE_STRING[p_type] ][ hex(p_nonce) ].setTexts()

    @showCall
    def selectionChanged(self, selected, deselected):
        for item in self.selectedItems():
            path= self.getPath(item)
            if len(path) == 3:  # 3: len(PacketHead._fields)
                packet_head= PacketHead( Name(path[0]), Packet.TYPE_STRING.index(path[1]), int(path[2], base=16))
                self.api['View::setShowTransfer'](packet_head)

    def getPath(self, item):
        path= []
        while item:
            path.append( item.text(0) )
            item= item.parent()
        path.reverse()
        return path
