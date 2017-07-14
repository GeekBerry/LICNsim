from PyQt5.QtWidgets import QDialog
from gui.ui.node_dialog import Ui_node_dialog
from gui.common import UIFrom

from debug import showCall


@UIFrom(Ui_node_dialog)
class NodeDialog(QDialog):
    def __init__(self, parent, node_id):
        self.node_id= node_id
        self.setWindowTitle(f'Node({self.node_id})')

    def install(self, announces, api):
        self.announces= announces
        announces['playSteps'].append(self.playSteps)

        icn_node= api['ICNNet.getNode'](self.node_id)

        self.ui.tree.addEntry('Node', icn_node)
        for unit_name, unit in icn_node.units.items():
            self.ui.tree.addEntry(unit_name, unit)
        self.ui.tree.install(announces, api)

    def playSteps(self, steps):
        pass

    @showCall
    def closeEvent(self, event):
        super().closeEvent(event)
        self.announces['NodeDialogClose'](self.node_id)




