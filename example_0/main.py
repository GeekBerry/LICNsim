if __name__ == '__main__':
    import networkx

    from example_0.sim import Simulator
    from example_0.node import *
    from example_0.channel import *

    sim = Simulator()

    graph = networkx.grid_2d_graph(10, 10)
    # graph= networkx.random_graphs.watts_strogatz_graph(20, 3, 0.2)
    sim.createRouterNet(graph, RouterNode, ChannelType1)

    sim.createServerNodes(5, ServerNode, ChannelType1)
    sim.createClientNodes(10, ClientNode, ChannelType1)

    sim.startGenerateData(50)
    sim.startGenerateAsk(5, 2)


    # ------------------------------------------------
    from debug import timeProfile, exeScript, print_clock


    @showCall
    def main():
        sim.api['Gui.start']()


    timeProfile('main()')

    numpy.random.poisson()
