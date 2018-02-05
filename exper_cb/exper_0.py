import networkx, time
from core import *
from debug import *
from exper_cb.modules import ReporterModule, ExperDBModule
from exper_cb.test_bed_graph import test_bed_graph
from module import *
from unit import *

RATIO = 1000  # 单位 step/second
REPORT_DELTA = 10
LAMBDA = 100  # 请求频率

EVICT_MODE = 'FIFO'  # LRU FIFO GEOMETRIC
CS_TIME = 4

PROBABILITY = 1.0

# -----------------------------  类型定义  -----------------------------------
SourceNode = nodeFactory(
    cs_capacity=100,
    evict_mode='CONST',

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
sim.install('db', ExperDBModule(REPORT_DELTA))
# sim.install('statistics', StatisticsModule())

# -------------------------  拓扑结构创建  -------------------------------------
STORE_NODE = (9, 9);  graph = networkx.grid_2d_graph(19, 19)
# STORE_NODE = 0; graph = networkx.barabasi_albert_graph(360, 3)
# STORE_NODE = 0; graph = networkx.balanced_tree(3, 5)

sim.createNode(STORE_NODE, SourceNode)
sim.createGraph(graph, ExperNode, OneStepChannel)

# ---------------------------  实验配置  -------------------------------------

sim.node(STORE_NODE).store(d_packet)  # 储存数据包
for node_id in sim.nodes():
    # 设置grid网络坐标
    # sim.node(node_id).pos= node_id[0]*50, node_id[1]*50
    # 设置符合正态分布的驱逐时间
    # t= numpy.random.normal(loc= CS_TIME*RATIO)
    # sim.node(node_id).units['evict'].life_time= int(t)
    pass


def uniformAsk(node_ids):
    node_id = random.choice(node_ids)
    sim.node(node_id).ask(i_packet.fission())

Loop(uniformAsk, list(sim.nodes()), delta=RATIO // LAMBDA)

sim.install('reporter', ReporterModule(STORE_NODE, NAME, REPORT_DELTA,
                                       f'result/{int(time.time())} {len(graph.nodes())} lam{LAMBDA} cs{EVICT_MODE}{CS_TIME} LCP{PROBABILITY} .txt'))


# ======================================================================================================================
def main():
    sim.showGUI()
    # for i in range(10000 + 1):
    #     clock.step()
    # sim.plotNames(NAME)

# prcfile('main()')
main()
