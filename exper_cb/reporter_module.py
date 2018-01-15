from core import clock, Timer
from module import ModuleBase


class ReporterModule(ModuleBase):
    REPORT_FIELD= ['Time', 'CSNum', 'Store', 'Evict', 'AskNum', 'StepDist', 'AllDist']

    def __init__(self, db_table, delta, file_name=None):
        self.db_table= db_table
        self.delta = delta
        self.file_name= file_name

        self.timer= Timer(self.report)
        self.last_report_time= clock.time()
        self.report_data = dict.fromkeys(self.REPORT_FIELD, None)
        self.global_data = {'cs_num': 0, 'pend_num': 0, 'ask_count': 0, 'dist_count': 0, }

    def setup(self, sim):
        self.file= open(self.file_name, 'w')  # FIXME with as
        self.writeHead()
        self.timer.timing(self.delta)

    def report(self):  # 每个delta进行一次统计
        self.generate(self.last_report_time, clock.time() )
        self.fill()
        self.writeLine()

        self.last_report_time= clock.time()
        self.timer.timing(self.delta)

    def generate(self, start_t, end_t):
        records = self.db_table.query(time=lambda t: start_t <= t < end_t)

        self.step_data = {'store_num': 0, 'evict_num': 0, 'ask_num': 0, 'respond_num': 0,
                          'dist_count': 0, 'send_i_num': 0, 'send_d_num': 0}
        for record in records:
            for field in self.step_data.keys():
                self.step_data[field] += record[field]

        self.global_data['time'] = end_t
        self.global_data['cs_num'] += self.step_data['store_num'] - self.step_data['evict_num']
        self.global_data['pend_num'] += self.step_data['ask_num'] - self.step_data['respond_num']
        self.global_data['ask_count'] += self.step_data['ask_num']
        self.global_data['dist_count'] += self.step_data['dist_count']

    def fill(self):
        self.report_data['Time']= self.global_data['time']
        self.report_data['CSNum'] = self.global_data['cs_num']
        self.report_data['Store'] = self.step_data['store_num']
        self.report_data['Evict'] = self.step_data['evict_num']
        self.report_data['AskNum'] = self.step_data['ask_num']

        try:
            self.report_data['StepDist'] = self.step_data['dist_count'] / self.step_data['ask_num']
        except ZeroDivisionError:
            self.report_data['StepDist'] = None

        try:
            self.report_data['AllDist'] = self.global_data['dist_count'] / self.global_data['ask_count']
        except ZeroDivisionError:
            self.report_data['AllDist'] = None

    def writeHead(self):
        head_str= '\t'.join( self.REPORT_FIELD )

        print(head_str)

        if self.file:
            self.file.write(head_str)
            self.file.write('\n')

    def writeLine(self):
        list_values= [ str(self.report_data[field]) for field in self.REPORT_FIELD ]
        line_str= '\t'.join(list_values)

        print(line_str)
        if self.file:
            self.file.write(line_str)
            self.file.write('\n')

