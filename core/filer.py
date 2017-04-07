#!/usr/bin/python3
#coding=utf-8

from core.clock import clock

class FilerPlugin:
    def title(self)->list:
        pass

    def entry(self)->list:
        pass

#-----------------------------------------------------------------------------------------------------------------------
class TimePlugin(FilerPlugin):
    def title(self)->list:
        return ['Time']

    def entry(self)->list:
        cur_time= clock.time()
        return [cur_time]

#-----------------------------------------------------------------------------------------------------------------------
import numpy
def listMean(l)->str:
    if len(l) > 0:
        return "%6f"%( numpy.mean(l) )
    else: return 'NaN'

def division(dividend, divisor)->str:
    if divisor != 0:
        return "%6f"%( dividend/divisor )
    else: return 'NaN'

class PacketTracePlugin(FilerPlugin):
    def __init__(self, packet_name, db):
        self.packet_name= packet_name
        self.db=db

        self.ask_count= 0   # 请求总量
        self.dist_total= 0  # 距离总和
        self.resp_count= 0  # 响应总量
        self.delay_total= 0  # 响应时间总和

        self.last_time= 0  # 上次更新时间

    def title(self)->list:
        return ['CSNum', 'StoreNum', 'EvictNum', 'AskNum', 'CurDist', 'AvgDist', 'RespNum', 'CurTime', 'AvgTime']

    def entry(self)->list:
        cur_time= clock.time()

        cs_num= len( self.db.contents[self.packet_name] )

        records= self.db.packet_t(packet_name= self.packet_name, time= lambda t: self.last_time <= t < cur_time)
        store_num, evict_num, distances, delays= 0, 0, [], []
        for record in records:
            store_num += len( record['storing'] )
            evict_num += len( record['evicting'] )
            distances += record['dist']
            delays    += record['delay']

        ask_num= len(distances)
        cur_dist= listMean(distances)
        self.ask_count  += ask_num
        self.dist_total += sum(distances)
        avg_dist= division(self.dist_total, self.ask_count)

        resp_num= len(delays)
        cur_delay= listMean(delays)
        self.resp_count += resp_num
        self.delay_total += sum(delays)
        avg_delay= division(self.delay_total, self.resp_count)

        # 拼记录
        self.last_time= cur_time
        return [cs_num, store_num, evict_num, ask_num, cur_dist, avg_dist, resp_num, cur_delay, avg_delay]

#-----------------------------------------------------------------------------------------------------------------------
from core.data_structure import Timer
class Filer:
    def __init__(self, filename, delta, plugins:list, print_screen=False):
        self.file= open(filename, 'w')
        self.delta= delta
        self.plugins= plugins
        self.print_screen= print_screen

        self.timer= Timer(self._writeEntry)  # 定时器
        self._writeTitle()

    def _writeTitle(self)->None:
        # 插件标题
        fields= []
        for plugin in self.plugins:
            fields += plugin.title()
        # 拼记录
        string= "\t".join([ "%8s"%(field) for field in fields])
        if self.print_screen:
            print(string)
        self.file.write(string+'\n')
        # 定时器
        self.timer.timing(self.delta)

    def _writeEntry(self)->None:
        # 插件条目
        fields= []
        for plugin in self.plugins:
            fields += plugin.entry()
        # 拼记录
        string= "\t".join(["%8s"%(field) for field in fields])
        if self.print_screen:
            print(string)
        self.file.write(string+'\n')
        # 定时器
        self.timer.timing(self.delta)  # 要不要自循环

    def __del__(self):
        self.file.close()
