import matplotlib.pyplot as plt
from module import ModuleBase


class StatisticsModule(ModuleBase):  # 依赖于DBModule及其内部数据结构
    def setup(self, sim):
        sim.api['Statistics.accessNamesFigure'] = self.accessNamesFigure
        sim.api['Statistics.drawName'] = self.drawName
        sim.api['Statistics.accessNodesFigure'] = self.accessNodesFigure
        sim.api['Statistics.drawNode'] = self.drawNode
        sim.api['Statistics.show'] = self.show

        sim.plotNames = self.plotNames
        sim.plotNodes = self.plotNodes
        sim.showPlot = self.show

        self.selectWhere = sim.api['DBModule.selectWhere']

    # -------------------------------------------------------------------------
    def accessNamesFigure(self, title: str):
        """
        创建或打开一个名为 title 的名字窗口
        :param title: str 窗口名字
        :return: figure
        """
        figure = plt.figure(title)

        axes = figure.add_subplot(221)  # 获取子图 2*2 的区域中第 1 张
        axes.set_title('Ask Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes = figure.add_subplot(222)  # 获取子图 2*2 的区域中第 2 张
        axes.set_title('Send Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes = figure.add_subplot(223)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Content Store Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes = figure.add_subplot(224)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Hit Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格

        return figure

    def drawName(self, figure, name):
        """
        将名为 name 的名字信息绘制
        :param figure:
        :param name:
        :return:
        """
        frame = self.selectWhere(name=name)
        if frame.empty:  # 对空数据不绘制
            return

        # 对名字数据进行处理
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['cs_num'] = (frame['store'] - frame['evict']).cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()

        figure.axes[0].plot(frame.index, frame['ask'], label=str(name), )
        figure.axes[0].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[1].plot(frame.index, frame['sends'], label=str(name), )
        figure.axes[1].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[2].plot(frame.index, frame['cs_num'], label=str(name), )
        figure.axes[2].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[3].plot(frame.index, frame['hit_ratio'], label=str(name), )
        figure.axes[3].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    def plotNames(self, *names):
        """
        绘制多个名字的比较图
        :param names: (Name, ...)
        :return: None
        """
        figure = self.accessNamesFigure(f'名字比较图：{names}')
        for name in names:  # 逐条绘制 name 比较曲线
            self.drawName(figure, name)

    # -------------------------------------------------------------------------
    def accessNodesFigure(self, title: str):
        figure = plt.figure(title)
        axes = figure.add_subplot(221)  # 获取子图 2*2 的区域中第 1 张
        axes.set_title('Receive Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes = figure.add_subplot(222)  # 获取子图 2*2 的区域中第 2 张
        axes.set_title('Send Packets Number')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes = figure.add_subplot(223)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Used Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格

        axes = figure.add_subplot(224)  # 获取子图 2*2 的区域中第 3 张
        axes.set_title('Hit Ratio')  # 设置图说明
        axes.grid(True)  # 添加网格

        return figure

    def drawNode(self, figure, node_id):
        frame = self.selectWhere(node_id=node_id)
        if frame.empty:  # 对空数据不绘制
            return

        frame['receives'] = frame['in_interest'] + frame['in_data']
        frame['sends'] = frame['out_interest'] + frame['out_data']
        frame['used_ratio'] = frame['hit'].cumsum() / frame['store'].cumsum()
        frame['hit_ratio'] = frame['hit'].cumsum() / (frame['hit'] + frame['miss']).cumsum()

        figure.axes[0].plot(frame.index, frame['receives'], label=str(node_id), )
        figure.axes[0].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[1].plot(frame.index, frame['sends'], label=str(node_id), )
        figure.axes[1].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[2].plot(frame.index, frame['used_ratio'], label=str(node_id), )
        figure.axes[2].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

        figure.axes[3].plot(frame.index, frame['hit_ratio'], label=str(node_id), )
        figure.axes[3].legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.)  # 添加图例

    def plotNodes(self, *node_ids):
        """
        绘制多个节点的比较图
        :param node_ids: (node_id, ...)
        :return: None
        """
        figure = self.accessNamesFigure(f'节点比较图：{node_ids}')
        for node_id in node_ids:  # 逐条绘制 node 比较曲线
            self.drawNode(figure, node_id)

    def show(self):
        plt.show()
