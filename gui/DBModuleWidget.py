from PyQt5.QtWidgets import QWidget, QAbstractItemView

from PyQt5.QtCore import Qt

from gui import bindWidgetToAttr
from gui.common import UIFrom
from gui.ui.db_module import Ui_db_module



@UIFrom(Ui_db_module)
class DBModuleWidget(QWidget):
    def __init__(self, parent, announces, api):
        self.real_time_refresh = False
        self.query_condition= ''

        self.ui.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.ui.edit.editingFinished.connect(self.refresh)


        # announces['playSteps'].append(self.playSteps)
        pass

    def refresh(self):
        print('refresh')

    # def playSteps(self, steps):
    #     print(self.real_time_refresh)
    #     print(repr(self.query_condition))


    # def playSteps(self, steps):  # DEBUG
    #     s= 'time= clock.time()-1'
    #
    #     e= f'records= self.db_table.query({s})'
    #     try:
    #         exec(e)
    #     except Exception as err:
    #         print(err.args[0], ':', err.args[1][3])
    #         raise err
    #     print(locals()['records'])
    #     pass
