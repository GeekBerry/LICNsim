import pandas
import matplotlib.pyplot as plt

from core import clock

from module import ModuleBase


class StatisticsModule(ModuleBase):  # 依赖于DBModule及其内部数据结构
    def setup(self, sim):
        sim.api['Statistics.plotNames'] = self.plotNames
        sim.api['Statistics.show']= self.show

        sim.plotNames = self.plotNames
        sim.plotNodes = self.plotNodes
        sim.showPlot = self.show
        self.api = sim.api

    def selectWhere(self, *fields, **where) -> pandas.DataFrame:
        if not fields:
            fields = self.api['DBModule.getFields']()
        assert 'time' in fields

        delta = self.api['DBModule.getDelta']()
        frame = pandas.DataFrame(data={'time': range(0, clock.time, delta)}, columns=fields).set_index('time').fillna(0)

        records = self.api['DBModule.query'](**where)
        for record in records:
            time = record['time']
            for field in frame.columns:
                try:
                    frame.loc[time][field] += record[field]
                except TypeError:
                    assert field == 'name'
                except ValueError:
                    assert field == 'node_id'
        return frame

    # -------------------------------------------------------------------------
    def frameName(self, name):
        frame = self.selectWhere(name=name)
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['cs_num'] = (frame['store'] - frame['evict']).cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()
        return frame

    def xxx(self, title:str):
        figure= plt.figure(title)
        axes_list = []

        axes= figure.add_subplot(221)  # 获取子图 2*2 的区域中第 1 张
        axes.set_title('Ask Number')  # 设置图说明
        axes.grid(True)  # 添加网格
        axes_list.append(axes)

        axes= figure.add_subplot(222)  # 获取子图 2*2 的区域中第 2 张
        axes.set_title('Send Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格
        axes_list.append(axes)

        axes= figure.add_subplot(223)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Content Store Number')  # 设置图说明
        axes.grid(True)  # 添加网格
        axes_list.append(axes)

        axes= figure.add_subplot(224)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Hit Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格
        axes_list.append(axes)
        return axes_list

    def plotNames(self, *names):
        frame_table = {name: self.frameName(name) for name in names}  # 一句名字生成表

        axes_list= self.xxx(f'名字比较图：{names}')
        for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线

            axes_list[0].plot(frame.index, frame['ask'], label=str(name), )
            axes_list[0].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

            axes_list[1].plot(frame.index, frame['sends'], label=str(name), )
            axes_list[1].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

            axes_list[2].plot(frame.index, frame['cs_num'], label=str(name), )
            axes_list[2].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

            axes_list[3].plot(frame.index, frame['hit_ratio'], label=str(name), )
            axes_list[3].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    # def plotNames(self, *names):
    #     frame_table = {name: self.frameName(name) for name in names}  # 一句名字生成表
    #
    #     figure= plt.figure(f'名字比较图：{names}')
    #
    #     # 绘制请求数量图
    #     axes= figure.add_subplot(221)  # 获取子图 2*2 的区域中第 1 张
    #     axes.set_title('Ask Number')  # 设置图说明
    #     axes.grid(True)  # 添加网格
    #
    #     for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
    #         if frame.empty:
    #             continue
    #         axes.plot(frame.index, frame['ask'], label=str(name), )
    #
    #     axes.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例
    #
    #     # 绘制转发数量图
    #     axes= figure.add_subplot(222)  # 获取子图 2*2 的区域中第 2 张
    #     axes.set_title('Send Packets Number')  # 设置图说明
    #     for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
    #         if frame.empty:
    #             continue
    #
    #         axes.plot(frame.index, frame['sends'], label=str(name), )
    #         axes.grid(True)  # 添加网格
    #         axes.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例
    #
    #     # 绘制缓存数量图
    #     axes= figure.add_subplot(223)  # 获取子图 2*2 的区域中第 3 张
    #     axes.set_title('Content Store Number')  # 设置图说明
    #     for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
    #         if frame.empty:
    #             continue
    #
    #         axes.plot(frame.index, frame['cs_num'], label=str(name), )
    #         axes.grid(True)  # 添加网格
    #         axes.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例
    #
    #     # 绘制命中率图
    #     axes= figure.add_subplot(224)  # 获取子图 2*2 的区域中第 4 张
    #     axes.set_title('Hit Ratio')  # 设置图说明
    #     for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
    #         if frame.empty:
    #             continue
    #
    #         axes.plot(frame.index, frame['hit_ratio'], label=str(name), )
    #         axes.grid(True)  # 添加网格
    #         axes.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    # -------------------------------------------------------------------------
    def frameNode(self, node_id):
        frame = self.selectWhere(node_id=node_id)
        frame['receives'] = frame['in_interest'] + frame['in_data']
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['used_ratio'] = frame['hit'].cumsum() / frame['store'].cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()
        return frame

    def plotNodes(self, *node_ids):
        frame_table = {node_id: self.frameNode(node_id) for node_id in node_ids}

        plt.figure(f'节点比较图：{node_ids}')

        # 绘制接收数量图
        plt.subplot(221)  # 获取子图 2*2 的区域中第 1 张
        plt.title('Receive Number')  # 设置图说明
        for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
            plt.plot(frame.index, frame['receives'], label=str(name), )
            plt.grid(True)  # 添加网格
            plt.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        # 绘制接收数量图
        plt.subplot(222)  # 获取子图 2*2 的区域中第 2 张
        plt.title('Send Packets Number')  # 设置图说明
        for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
            plt.plot(frame.index, frame['sends'], label=str(name), )
            plt.grid(True)  # 添加网格
            plt.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        # 绘制接收数量图
        plt.subplot(223)  # 获取子图 2*2 的区域中第 3 张
        plt.title('Used Ratio')  # 设置图说明
        for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
            plt.plot(frame.index, frame['used_ratio'], label=str(name), )
            plt.grid(True)  # 添加网格
            plt.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        # 绘制接收数量图
        plt.subplot(224)  # 获取子图 2*2 的区域中第 4 张
        plt.title('Hit Ratio')  # 设置图说明
        for name, frame in frame_table.items():  # 逐条绘制 name 比较曲线
            plt.plot(frame.index, frame['hit_ratio'], label=str(name), )
            plt.grid(True)  # 添加网格
            plt.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    def show(self):
        plt.show()
