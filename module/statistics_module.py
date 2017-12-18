import pandas
import matplotlib.pyplot as plt

from core import clock

from module import ModuleBase


class StatisticsModule(ModuleBase):  # 依赖于DBModule及其内部数据结构
    def setup(self, sim):
        self.api = sim.api

        sim.api['Statistics.accessNamesFigure'] = self.accessNamesFigure
        sim.api['Statistics.drawName'] = self.drawName
        sim.api['Statistics.accessNodesFigure'] = self.accessNodesFigure
        sim.api['Statistics.drawNode'] = self.drawNode
        sim.api['Statistics.show']= self.show

        sim.plotNames = self.plotNames
        sim.plotNodes = self.plotNodes
        sim.showPlot = self.show

    def selectWhere(self, *fields, **where) -> pandas.DataFrame:
        if not fields:
            fields = self.api['DBModule.getFields']()
        assert 'time' in fields

        delta = self.api['DBModule.getDelta']()
        frame = pandas.DataFrame(data={'time': range(0, clock.time, delta)}, columns=fields).set_index('time').fillna(0)

        records = self.api['DBModule.query'](**where)
        # 用 records 数据覆盖 fream
        for record in records:
            time = record['time']
            for field in frame.columns:
                try:
                    frame.loc[time][field] += record[field]
                except KeyError:
                    assert frame.empty
                except TypeError:
                    assert field == 'name'
                except ValueError:
                    assert field == 'node_id'
        return frame

    # -------------------------------------------------------------------------
    def accessNamesFigure(self, title:str):
        figure= plt.figure(title)

        axes= figure.add_subplot(221)  # 获取子图 2*2 的区域中第 1 张
        axes.set_title('Ask Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes= figure.add_subplot(222)  # 获取子图 2*2 的区域中第 2 张
        axes.set_title('Send Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes= figure.add_subplot(223)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Content Store Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes= figure.add_subplot(224)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Hit Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格

        return figure

    def frameName(self, name):
        frame = self.selectWhere(name=name)
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['cs_num'] = (frame['store'] - frame['evict']).cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()
        return frame

    def drawName(self, figure, name):
        frame = self.frameName(name)
        if frame.empty:  # 对空数据不绘制
            return

        figure.axes[0].plot(frame.index, frame['ask'], label=str(name), )
        figure.axes[0].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[1].plot(frame.index, frame['sends'], label=str(name), )
        figure.axes[1].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[2].plot(frame.index, frame['cs_num'], label=str(name), )
        figure.axes[2].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[3].plot(frame.index, frame['hit_ratio'], label=str(name), )
        figure.axes[3].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    def plotNames(self, *names):
        figure= self.accessNamesFigure(f'名字比较图：{names}')
        for name in names:  # 逐条绘制 name 比较曲线
            self.drawName(figure, name)

    # -------------------------------------------------------------------------
    def accessNodesFigure(self, title:str):
        figure= plt.figure(title)
        axes= figure.add_subplot(221)  # 获取子图 2*2 的区域中第 1 张
        axes.set_title('Receive Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes= figure.add_subplot(222)  # 获取子图 2*2 的区域中第 2 张
        axes.set_title('Send Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes= figure.add_subplot(223)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Used Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes= figure.add_subplot(224)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Hit Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格

        return figure

    def frameNode(self, node_id):
        frame = self.selectWhere(node_id=node_id)
        frame['receives'] = frame['in_interest'] + frame['in_data']
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['used_ratio'] = frame['hit'].cumsum() / frame['store'].cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()
        return frame

    def drawNode(self, figure, node_id):
        frame= self.frameNode(node_id)
        if frame.empty:  # 对空数据不绘制
            return

        figure.axes[0].plot(frame.index, frame['receives'], label=str(node_id), )
        figure.axes[0].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[1].plot(frame.index, frame['sends'], label=str(node_id), )
        figure.axes[1].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[2].plot(frame.index, frame['used_ratio'], label=str(node_id), )
        figure.axes[2].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[3].plot(frame.index, frame['hit_ratio'], label=str(node_id), )
        figure.axes[3].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    def plotNodes(self, *node_ids):
        figure= self.accessNamesFigure(f'节点比较图：{node_ids}')
        for node_id in node_ids:  # 逐条绘制 node 比较曲线
            self.drawNode(figure, node_id)

    def show(self):
        plt.show()
