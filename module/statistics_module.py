from collections import defaultdict
from pandas import DataFrame
import matplotlib.pyplot as plt

from core import TupleClass

from module import ModuleBase

NamePlotEntry = TupleClass('pos', 'title', 'field')
NAME_PLOT_ENTRYS = [
    NamePlotEntry((2, 2, 1), 'Ask Number', 'ask'),
    NamePlotEntry((2, 2, 2), 'Send Packets Number', 'sends'),
    NamePlotEntry((2, 2, 3), 'Content Store Number', 'cs_num'),
    NamePlotEntry((2, 2, 4), 'Hit Ratio', 'hit_ratio'),
]

NodePlotEntry = TupleClass('pos', 'title', 'field')
NODE_PLOT_ENTRYS = [
    NodePlotEntry((2, 2, 1), 'Receive Number', 'receives'),
    NodePlotEntry((2, 2, 2), 'Send Packets Number', 'sends'),
    NodePlotEntry((2, 2, 3), 'EvictNumber', 'evict'),
    NodePlotEntry((2, 2, 4), 'Hit Ratio', 'hit_ratio'),
]


class StatisticsModule(ModuleBase):  # 依赖于DBModule及其内部数据结构
    def setup(self, sim):
        self.api = sim.api
        sim.plotNames = self.plotNames
        sim.plotNodes = self.plotNodes
        sim.showPlot = self.show

    def selectWhere(self, *fields, **where) -> dict:
        if not fields:
            fields = self.api['DBModule.getFields']()

        table = defaultdict(list)  # {field:[value, ...], ...}
        for record in self.api['DBModule.query'](**where):
            for field in fields:
                table[field].append(record[field])
        return table

    def frameName(self, name):
        table = self.selectWhere(name=name)
        frame = DataFrame(table)
        frame = frame.groupby('time').sum()
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['cs_num'] = (frame['store'] - frame['evict']).cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()
        return frame

    def plotNames(self, *names):
        frame_table = {name: self.frameName(name) for name in names}

        plt.figure(str(names))
        for entry in NAME_PLOT_ENTRYS:  # 分别绘制不同域的子图
            plt.subplot(*entry.pos)  # 获取子图
            plt.title(entry.title)  # 设置图说明

            for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
                plt.plot(frame.index, frame[entry.field], label=str(name))

            plt.grid(True)  # 添加网格
            plt.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    # -------------------------------------------------------------------------
    def frameNode(self, node_id):
        table = self.selectWhere(node_id=node_id)
        frame = DataFrame(table)
        frame = frame.groupby('time').sum()
        frame['receives'] = frame['in_interest'] + frame['in_data']
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()
        return frame

    def plotNodes(self, *node_ids):
        frame_table = {node_id: self.frameNode(node_id) for node_id in node_ids}
        plt.figure(str(node_ids))
        for entry in NODE_PLOT_ENTRYS:  # 分别绘制不同域的子图
            plt.subplot(*entry.pos)  # 获取子图
            plt.title(entry.title)  # 设置图说明

            for name, frame in frame_table.items():  # 逐条绘制 node 比较曲线
                plt.plot(frame.index, frame[entry.field], label=str(name))

            plt.grid(True)  # 添加网格
            plt.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    def show(self):
        plt.show()
