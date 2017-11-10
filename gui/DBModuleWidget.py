from PyQt5.QtWidgets import QWidget, QAbstractItemView
from PyQt5.QtCore import Qt

from gui import bindWidgetToAttr
from gui.common import UIFrom
from gui.ui.db_module import Ui_db_module

from debug import showCall


@UIFrom(Ui_db_module)
class DBModuleWidget(QWidget):
    def __init__(self, parent, announces, api):
        self.ui.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.ui.edit.editingFinished.connect(self.refresh)

        self.ui.table.setHeads( *api['DBMoudle.getFields'] () )
        self.db_query = api['DBMoudle.query']
        announces['playSteps'].append(self.playSteps)

    def playSteps(self, steps):
        if self.ui.check.checkState():
            self.refresh()

    @showCall
    def _query(self):
        condition_str= self.ui.edit.text()
        try:
            exec(f'records= self.db_query({condition_str})')
        except Exception as err:
            print(err.args)
            self.ui.label.setText( err.args[0] )
            return None
        else:
            self.ui.label.setText('Finished')
            return locals()['records']

    def refresh(self):
        records= self._query()

        if records is not None:
            records= list(records)  # 先生成列表，才能统计长度
            self.ui.table.setRowCount(len(records))
            for row, record in enumerate(records):
                self.ui.table.setRow(row, *record.values())
        else:
            pass




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
