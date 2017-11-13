from PyQt5.QtWidgets import QDialog

from gui import UIFrom
from gui.ui.edge_dialog import Ui_edge_dialog
from gui.Controller import EdgeController


@UIFrom(Ui_edge_dialog)
class EdgeDialog(QDialog):
    def __init__(self, parent, announces, api, src_id, dst_id):
        self.announces= announces
        self.src_id= src_id
        self.dst_id= dst_id

        announces['playSteps'].append(self.playSteps)

        self.setWindowTitle(f'Edge({self.src_id}, {self.dst_id})')
        self.ui.tree.setHeads('Attr', 'Detail')

        icn_edge= api['Sim.getEdge'](self.src_id, self.dst_id)
        self.edge_ctrl= EdgeController(self, icn_edge)
        self.edge_ctrl.setTree(self.ui.tree)

        self.ui.tree.expandAll()

    def playSteps(self, steps):
        self.edge_ctrl.refresh()

    # -------------------------------------------------------------------------
    def closeEvent(self, event):
        super().closeEvent(event)
        self.announces['EdgeDialogClose'](self.src_id, self.dst_id)

