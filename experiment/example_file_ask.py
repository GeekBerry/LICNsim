import time
import networkx

from debug import *
from experiment import *
from module import *
from unit.channel import *
from algorithm.graph_algo import graphApproximateDiameter


graph= networkx.barabasi_albert_graph(10000, 3)
GRAPH_NAME= 'BA'
DATA_NODE = 0
DIAMETER = graphApproximateDiameter(graph)


NONCE= time.strftime("%Y%m%d%H%M%S", time.localtime())

SECOND = DIAMETER

CS_TYPE= 'LCE'  # LCE, LCP, LCD
EVICT_MODE = 'FIFO'  # FIFO, LRU, RANDOM, GEOMETRIC

# cs_time = 100
SIM_STEP = 500 * SECOND

for cs_time in (20,40,60,80,100):
    file_name = f'result/{GRAPH_NAME} 直径{DIAMETER} 文件请求 {EVICT_MODE}{cs_time} {CS_TYPE} {NONCE}.txt'

    sim = SuperSimulator()
    sim.install('cs_track', StoreTrackMoudle(ip_A.name))
    sim.install('db', DBMoudle())
    sim.install('reporter', ReporterModule(sim.modules['db'].db_table, SECOND, file_name) )

    node_map = sim.addGraph(graph, NodeFactor(cs_type= CS_TYPE, p=0.5, cs_time= cs_time*SECOND, evict_mode= EVICT_MODE), OneStepChannel)
    sim.install('asker', AskMoudle(ip_A, FileAsk('ask_num.txt'), UniformDistribute(sim.nodes()), delta=SECOND))

    sim.getNode(node_map[DATA_NODE]).setEvictMode('CONST')
    sim.getNode(node_map[DATA_NODE]).insert(dp_A)

    for i in range(SIM_STEP + 1):
        clock.step()

    clock.clear()



