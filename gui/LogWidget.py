from PyQt5.QtWidgets import QWidget, QAbstractItemView

from core import clock, tops
from gui import UIFrom
from gui.ui.log_widget import Ui_log_widget

from algorithm.recur_parser import SymbolTable, Stream, sym, re
from debug import showCall


class QueryParser(SymbolTable):
    def __init__(self):
        Ends = sym(re.compile('\s*'), name='Ends')
        Int = sym(re.compile('-?\d+'), name='Int')
        Str = sym(re.compile(r"\'([^\'])*\'"), name='Str')
        Tuple = sym(re.compile(r'(\([^\)]*\))'), name='Tuple')
        Field = sym(['index', 'time', 'node_id', 'action', 'face_id', 'name', 'type','size', 'nonce'], name='Field')

        self['Time'] = 'T'
        self['Expre'] = self['Time'], Ends, ['+', '-'], Ends, Int  # 只接受时间的加减形式
        Var = self['Expre'] | self['Time'] | Str | Int
        self['InEntry'] = Field, Ends, 'in', Ends, Tuple
        self['EqEntry'] = Field, Ends, '==', Ends, Var
        self['CmpEntry'] = sym(Var, Ends, ['<=', '<'], name='LeftCmp') * (0, 1), \
                           Ends, Field, Ends, \
                           sym(['<=', '<'], Ends, Var, name='RightCmp') * (0, 1)
        Entry = self['EqEntry'] | self['CmpEntry'] | self['InEntry']
        self['Start'] = sym(Ends, Entry, Ends, sym(',') | None)*(0,...)

    def Time(self, match):
        return 'clock.time()'

    def Expre(self, match):
        return ''.join(match)

    def InEntry(self, match):
        return f'{match[0]}= lambda arg: arg in {match[4]}'

    def EqEntry(self, match):
        return f'{match[0]}={match[4]}'

    def CmpEntry(self, match):
        left = ''.join(match[0][0]) if match[0] else ''
        right = ''.join(match[4][0]) if match[4] else ''
        return f'{match[2]}= lambda arg: {left}arg{right}' if left or right else None

    def Start(self, match):
        return ','.join([each[1] for each in match])


@UIFrom(Ui_log_widget)
class LogWidget(QWidget):
    MAX_SHOW_RECORD_NUM= 100

    def __init__(self, parent, announces, api):
        self.ui.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.ui.button.pressed.connect(self.refresh)
        self.ui.edit.editingFinished.connect(self.refresh)
        self.ui.check.stateChanged.connect(self.playSteps)

        self.announces= announces
        self.api= api
        announces['playSteps'].append(self.playSteps)
        self.head_fields= api['DBMoudle.getFields']
        self.db_query = api['DBMoudle.query']

        self.__last_query_key = None  # (time, query_str)

    def playSteps(self, *args):
        if self.ui.check.checkState():
            self.refresh()

    def refresh(self):
        text = self.ui.edit.text()  # TODO 加一个文本解释器
        if self.__last_query_key == (clock.time(), text):
            return  # 检查查询时间和条件，避免重复查询

        query_str = self._parser(text)
        if query_str is None:
            return None

        records = self._query(query_str)
        if records is None:
            return  # 没有 LogMoudle ？？？

        self._draw(records)
        self.__last_query_key = (clock.time(), text)

    def _parser(self, text):
        # 查询操作
        stream= Stream(text)
        query_str = stream.parser( QueryParser()['Start'] )

        if not stream.eof():
            self.announces['logQueryMessage']('Parser Failed')
            return None
        else:
            return query_str

    def _query(self, condition_str):
        try:
            exec(f'records= self.db_query({condition_str})')
        except Exception as err:
            self.announces['logQueryMessage'](err.args[0])
            return None
        else:
            self.announces['logQueryMessage']('Done')
            return locals()['records']

    def _draw(self, records):
        # 显示表
        self.ui.table.setHeads( *self.head_fields() )
        if records is not None:
            records= tops(records, self.MAX_SHOW_RECORD_NUM)  # 先生成列表，才能统计长度
            self.ui.table.setRowCount(len(records))
            for row, record in enumerate(records):
                self.ui.table.setRow(row, *record.values())

