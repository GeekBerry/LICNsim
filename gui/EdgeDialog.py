from PyQt5.QtWidgets import QDialog
from gui.ui.edge_dialog import Ui_edge_dialog
from gui.common import UIFrom

from debug import showCall


@UIFrom(Ui_edge_dialog)
class EdgeDialog(QDialog):
    def __init__(self, parent, src_id, dst_id):
        self.src_id= src_id
        self.dst_id= dst_id

        super().__init__(parent)
        from gui.ui.edge_dialog import Ui_edge_dialog
        self.ui= Ui_edge_dialog()
        self.ui.setupUi(self)

        self.setWindowTitle(f'Edge({self.src_id}, {self.dst_id})')

    @showCall
    def install(self, announces, api):
        self.announces= announces
        announces['playSteps'].append(self.playSteps)

        icn_edge= api['ICNNet.getEdge'](self.src_id, self.dst_id)

        self.ui.tree.addEntry('Channel', icn_edge)
        self.ui.tree.install(announces, api)
        # self.refresh()

    def playSteps(self, steps):
        # if self.isVisible():
        #     self.refresh()
        pass
    # def refresh(self):
    #     self.ui.tree.refresh()

    # -------------------------------------------------------------------------
    def closeEvent(self, event):
        super().closeEvent(event)
        self.announces['EdgeDialogClose'](self.src_id, self.dst_id)





