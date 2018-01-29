from core import Timer, clock
from module import ModuleBase, DBModule


class ExperDBModule(DBModule):
    def setup(self, sim):
        super().setup(sim)
        self.db_table.addFields(distance=0)  # DEBUG
        sim.loadNodeAnnounce('distance', self._distanceEvent)  # DEBUG

    def _distanceEvent(self, node_id, packet, distacne):  # FIXME 只有cb实验中有
        if distacne > 0:  # FIXME 实验中设计的奇怪的距离计算方式，应该放到哪里好？
            distacne -= 1

        record = self.db_table[self.timeIndex(), packet.name, node_id]
        record['distance'] += distacne


class ReporterModule(ModuleBase):
    REPORT_FIELD = ['Time', 'CSNum', 'Store', 'Evict', 'AskNum', 'StepDist', 'AllDist', 'Disperse']

    def __init__(self, center_node, report_name, delta, file_name):
        """
        是要用报告生成模块
        :param center_node:网络中心节点， 通常为数据源节点
        :param report_name:Name 要追踪的名字
        :param file_name:str 记录文件名
        :param delta:int 记录时间间隔
        """
        self.center_node = center_node
        self.report_name = report_name
        self.file_name = file_name
        self.delta = delta

        self.timer = Timer(self.report)
        self.last_report_time = clock.time

        self.frame = {
            'store': 0, 'evict': 0, 'ask': 0, 'respond': 0, 'out_interest': 0, 'out_data': 0, 'distance': 0,
            'cs_num': 0, 'pend_num': 0, 'ask_count': 0, 'dist_count': 0,
            'step_dist': None, 'all_dist': None, 'disperse': None,
        }

    def setup(self, sim):
        self.query = sim.api['DBModule.query']
        self.getDisperse = sim.api['Track.getDisperse']

        self.file = open(self.file_name, 'w')  # FIXME with as
        self.writeHead()
        self.timer.timing(self.delta)

    def report(self):  # 每个delta进行一次统计
        self.generate(self.last_report_time, clock.time)
        self.writeLine()
        self.last_report_time = clock.time
        self.timer.timing(self.delta)

    def generate(self, start_t, end_t):
        records = self.query(time=lambda t: start_t <= t < end_t, name=self.report_name)

        # 单步记录更新
        self.frame.update({'store': 0, 'evict': 0, 'ask': 0, 'respond': 0,
                           'distance': 0, 'out_interest': 0, 'out_data': 0})

        for record in records:
            self.frame['store'] += record['store']
            self.frame['evict'] += record['evict']
            self.frame['ask'] += record['ask']
            self.frame['respond'] += record['respond']
            self.frame['out_interest'] += record['out_interest']
            self.frame['out_data'] += record['out_data']
            self.frame['distance'] += record['distance']

        # 全局记录更新
        self.frame['time'] = end_t
        self.frame['cs_num'] += self.frame['store'] - self.frame['evict']
        self.frame['pend_num'] += self.frame['ask'] - self.frame['respond']
        self.frame['ask_count'] += self.frame['ask']
        self.frame['dist_count'] += self.frame['distance']

        # 非直接记录计算
        try:
            self.frame['step_dist'] = self.frame['distance'] / self.frame['ask']
        except ZeroDivisionError:
            self.frame['step_dist'] = None

        try:
            self.frame['all_dist'] = self.frame['dist_count'] / self.frame['ask_count']
        except ZeroDivisionError:
            self.frame['all_dist'] = None

        self.frame['disperse'] = self.getDisperse(self.center_node, self.report_name)

    def writeHead(self):
        head_str = '\t'.join(self.REPORT_FIELD)

        print(head_str)
        if self.file:
            self.file.write(head_str)
            self.file.write('\n')

    def writeLine(self):
        fields = ('time', 'cs_num', 'store', 'evict', 'ask', 'step_dist', 'all_dist', 'disperse')
        line_str = '\t'.join([str(self.frame[field]) for field in fields])

        print(line_str)
        if self.file:
            self.file.write(line_str)
            self.file.write('\n')
