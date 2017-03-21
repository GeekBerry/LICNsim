# Lightweight Information-Centric Networking simulator 轻量级信息中心网络模拟器

该模拟器搭建了一个ICN网络的框架, 使研究人员以此框架, 能快速搭建若需的实验环境.  

LICNsim是一个python库, 使用了以下包:
* numpy  
* matplotlib
* networkx
* pyqt5

LICNsim在网络拓扑上, 使用networkx的图形类, 使得开发者能像networkx中一样方便的在LICNsim中配置拓扑, 也能直接导入用networkx配置好的拓扑结构
LICNsim内置网络信息监控, 能监控如节点的兴趣\数据包吞吐量, 节点缓存命中率, 节点缓存替换率, 信道传输速率, 请求响应时间, 网络缓存分布等一系列研究中常用的指标, 使用者能通过获取这些信息完成研究.
