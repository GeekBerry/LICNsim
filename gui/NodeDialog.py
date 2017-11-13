from PyQt5.QtWidgets import QDialog

from gui import UIFrom
from gui.ui.node_dialog import Ui_node_dialog
from gui.Controller import NodeController


@UIFrom(Ui_node_dialog)
class NodeDialog(QDialog):
    def __init__(self, parent, announces, api, node_id):
        self.node_id= node_id
        self.announces= announces

        announces['playSteps'].append(self.playSteps)

        self.setWindowTitle(f'Node({self.node_id})')
        self.ui.tree.setHeads('Attr', 'Detail')

        icn_node= api['Sim.getNode'](self.node_id)
        self.node_ctrl= NodeController(self, icn_node)
        self.node_ctrl.setTree(self.ui.tree)

        self.ui.tree.expandAll()

    def playSteps(self, steps):
        self.node_ctrl.refresh()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.announces['NodeDialogClose'](self.node_id)

