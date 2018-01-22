import networkx
from core import *
from debug import *
from exper_cb.modules import ReporterModule, ExperDBModule
from exper_cb.test_bed_graph import test_bed_graph
from module import *
from unit import *

# -----------------------------  类型定义  -----------------------------------
SourceNode = nodeFactory(
    cs_capacity=100,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
)

ExperNode = nodeFactory(
    cs_capacity=100,
    cs_probability=0.5,
    evict_mode='FIFO',
    evict_life_time=1000,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
    ContentStoreType= LCPContentStoreUnit,
)

MarginNode = nodeFactory(
    cs_capacity=100,

    evict_mode='GEOMETRIC',
    evict_life_time=1000,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
)

NAME = Name('P')

i_packet = Packet(NAME, Packet.INTEREST, 1)
d_packet = Packet(NAME, Packet.DATA, 100)

# -------------------------  模拟器组建  ---------------------------------------
sim = Simulator()
sim.install('hub', HubModule())
sim.install('monitor', MonitorModule())
sim.install('gui', GUIModule())

sim.install('track', StoreTrackModule())

sim.install('log', LogModule())
sim.install('db', ExperDBModule(10))
sim.install('statistics', StatisticsModule())

# -------------------------  拓扑结构创建  -------------------------------------

STORE_NODE = 'BUPT'
sim.createNode(STORE_NODE, SourceNode)
sim.createGraph(test_bed_graph, ExperNode, OneStepChannel)
# for node_id in test_bed_graph:
#     sub_node_ids = [f'{node_id}_{i}' for i in range(4)]
#     sim.createGraph({node_id: sub_node_ids}, MarginNode, OneStepChannel)
sim.install('reporter', ReporterModule(STORE_NODE, NAME, 'result.txt', 100))

# STORE_NODE = (5,5)
# graph= networkx.grid_2d_graph(11, 11)
# sim.createNode(STORE_NODE, SourceNode)
# sim.createGraph(graph, ExperNode, OneStepChannel)
# sim.install('reporter', ReporterModule(STORE_NODE, NAME, 'result.txt', 100))

# ---------------------------  实验配置  -------------------------------------

sim.node(STORE_NODE).store(d_packet)  # 储存数据包


def uniformAsk(node_ids):
    node_id = random.choice(node_ids)
    sim.node(node_id).ask(i_packet.fission())


Loop(uniformAsk, list(sim.nodes()), delta=10)

if __name__ == '__main__':
    # sim.showGUI()

    for i in range(10000):
        clock.step()
    #
    # sim.plotNames(NAME)
    # sim.showPlot()

    print(list(sim.modules['db'].db_table.query()))
