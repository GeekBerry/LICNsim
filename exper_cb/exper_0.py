import networkx, time
from core import *
from debug import *
from exper_cb.modules import ReporterModule, ExperDBModule
from exper_cb.test_bed_graph import test_bed_graph
from module import *
from unit import *

RATIO = 1000  # 单位 step/second
LAMBDA = 100  # 请求频率

EVICT_MODE = 'LRU'  # LRU FIFO GEOMETRIC
CS_TIME = 20

PROBABILITY = 1

# -----------------------------  类型定义  -----------------------------------
SourceNode = nodeFactory(
    cs_capacity=100,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
)

ExperNode = nodeFactory(
    cs_capacity=100,
    cs_probability=PROBABILITY,
    evict_mode=EVICT_MODE,
    evict_life_time=CS_TIME * RATIO,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
    ContentStoreType=LCPContentStoreUnit,
)

MarginNode = nodeFactory(
    cs_capacity=100,

    evict_mode=EVICT_MODE,
    evict_life_time=CS_TIME * RATIO,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
)

NAME = Name('P')

i_packet = Packet(NAME, Packet.INTEREST, 1)
d_packet = Packet(NAME, Packet.DATA, 100)

# -------------------------  模拟器组建  ---------------------------------------
sim = Simulator()
sim.install('hub', HubModule())
# sim.install('monitor', MonitorModule())
# sim.install('gui', GUIModule())

sim.install('track', StoreTrackModule())

sim.install('log', LogModule())
sim.install('db', ExperDBModule(RATIO))
# sim.install('statistics', StatisticsModule())

# -------------------------  拓扑结构创建  -------------------------------------

# STORE_NODE = 'BUPT'
# sim.createNode(STORE_NODE, SourceNode)
# sim.createGraph(test_bed_graph, ExperNode, OneStepChannel)
# for node_id in test_bed_graph:
#     sub_node_ids = [f'{node_id}_{i}' for i in range(100)]
#     sim.createGraph({node_id: sub_node_ids}, ExperNode, OneStepChannel)
#
# sim.install('reporter', ReporterModule(STORE_NODE, NAME, RATIO,
#     f'result/{int(time.time())} test_bed lam{LAMBDA} cs{EVICT_MODE}{CS_TIME} LCP{PROBABILITY} .txt'))


STORE_NODE = (50, 50)
graph = networkx.grid_2d_graph(101, 101)
sim.createNode(STORE_NODE, SourceNode)
sim.createGraph(graph, ExperNode, OneStepChannel)

sim.install('reporter', ReporterModule(STORE_NODE, NAME, RATIO,
    f'result/{int(time.time())} grid lam{LAMBDA} cs{EVICT_MODE}{CS_TIME} LCP{PROBABILITY} .txt'))

# ---------------------------  实验配置  -------------------------------------

sim.node(STORE_NODE).store(d_packet)  # 储存数据包


def uniformAsk(node_ids):
    node_id = random.choice(node_ids)
    sim.node(node_id).ask(i_packet.fission())


Loop(uniformAsk, list(sim.nodes()), delta=RATIO // LAMBDA)


# ======================================================================================================================
def main():
    # sim.showGUI()
    for i in range(300_000 + 1):
        clock.step()
    # sim.plotNames(NAME)


# prcfile('main()')
main()
