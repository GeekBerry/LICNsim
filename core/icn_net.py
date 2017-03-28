from core.common import Bind, AnnounceTable

class ICNNet:
    def __init__(self, graph, NodeType, ChannelType):
        self.graph= graph
        self.publish= AnnounceTable()

        for nodename in self.graph:# 构造节点
            node= NodeType()
            # 监听节点所有操作
            for name, announce in node.announces.items():
                announce.append( Bind(self.publish[name], nodename) )
            self.graph.node[nodename]['icn']= node

        # 构造信道, 要先建立所有节点再建立Channel
        for src,dst in self.graph.edges():
            if type( self.graph[dst][src] ) != ChannelType:# 反向没有
                src_dst_channel= self.graph[src][dst]['icn']= ChannelType()
                src_dst_channel.append( Bind(self.publish['transfer'], src, dst) )

                dst_src_channel= self.graph[dst][src]['icn']= ChannelType()
                dst_src_channel.append( Bind(self.publish['transfer'], dst, src) )
                self.graph.node[src]['icn'].api['Face::create']( dst, src_dst_channel, dst_src_channel )
                self.graph.node[dst]['icn'].api['Face::create']( src, dst_src_channel, src_dst_channel )

    def listen(self, function):
        for src,dst in self.graph.edges():
            self.graph[src][dst]['icn'].append( Bind(function, src, dst) )


    def loadAnnounce(self, anno_name, function, pushhead= False)->None:
        """ 将节点 announces 中的 evict_callback 连接到固定函数, 即:
        node[nodename].annouces[anno_name](*_args) => function( nodename, *_args )
        :param anno_name: 节点中的Announce名
        :param function:def(nodename, *_args) 映射函数名
        :param pushhead:bool 是否将func排在节点的 announces 头部
        """
        for nodename in self.graph:
            announce= self.graph.node[nodename]['icn'].announces[anno_name]
            if pushhead:
                announce.insert(0, Bind(function, nodename))
            else:
                announce.append(Bind(function, nodename))

    def storeAPI(self, api_name, function)->None:
        """
        将节点 function 绑定到节点的 api 中, 即:
        node[nodename].api[api_name]( *_args ) <= function( nodename, *_args )
        :param api_name: 节点中的api名称
        :param function: def(nodename, *_args)
        """
        for nodename in self.graph:
            self.graph.node[nodename]['icn'].api[api_name]= Bind(function, nodename)


    # def nodeNames(self):
    #     return self.graph.nodes()
    #
    def nodes(self):
        for nodename in self.graph:
            yield self.graph.node[nodename]['icn']

    def node(self, nodename):
        return self.graph.node[nodename]['icn']
    #
    # def edgeNames(self):# -> edgename
    #     return self.graph.edges()
    #
    # def edges(self):
    #     for src, dst in self.edgeNames():
    #         yield self.graph[src][dst]['icn']
    #
    # def edge(self, scr, dst):
    #     return self.graph[scr][dst]['icn']
