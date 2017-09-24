import logging as logging
logging.basicConfig(level=logging.INFO)

import math

# import sys
# INF= sys.maxsize  # 无穷大
INF= 0x7FFFFFFF  # 无穷大 此处用4byte整形最大正数


# --------------------  装饰器  -------------------------------
def singleton(cls, *args, **kw):
    instance={}

    def _singleton():
        if cls not in instance:
            instance[cls]=cls(*args, **kw)
        return instance[cls]
    return _singleton


# ------------------- 工具函数 -----------------------------
def threshold(min, value, max):
    if value<min: return min
    if value>max: return max
    return value


def strPercent(value):
    return '%0.2f%%'%( value*100 )


def normalizeINF(value):
    return 1 - math.exp( -7e-4 * value )  # FIXME


# ---------------------  数据结构定义  ----------------------------
class Hardware:
    def __init__(self, hardware_id):
        from base.core import CallTable, AnnounceTable
        self.api= CallTable()
        self.announces= AnnounceTable()
        self.units= {}

        self.api['Hardware.getId']= lambda : hardware_id

    def install(self, unit_name, unit):
        unit.install(self.announces, self.api)
        self.units[unit_name]= unit

    def uninstall(self, unit_name):
        unit= self.units[unit_name]
        unit.uninstall(self.announces, self.api)
        del self.units[unit_name]


class Unit:
    def install(self, announces, api):
        self.announces= announces
        self.api= api

    def uninstall(self, announces, api):
        # self.announces= None
        # self.api= None
        pass


