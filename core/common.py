import logging
logging.basicConfig(level=logging.INFO)

import math
import random
from collections import defaultdict


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
def top(iterable):
    """
    iterable 中有 None 和 StopIteration 将无法区别, 请分清使用场景
    :param iterable:
    :return: None or Any
    """
    try:
        return next(iter(iterable))
    except StopIteration:
        return None


def tops(iterable, num):
    return [value for index, value in zip(range(num), iterable) ]


def floor(num:int, alpha:int):
    return (num//alpha)*alpha


def threshold(min, value, max):
    if value<min: return min
    if value>max: return max
    return value


def strPercent(value):
    return '%0.2f%%'%( value*100 )


def normalizeINF(value):
    return 1 - math.exp( -7e-4 * value )


# -----------------------------------------------------------
def outer_join(d1:dict, d2:dict)->dict:
    """
    >>> d1= {1:100, 2:200}
    >>> d2= {1:100, 3:300}
    >>> outer_join(d1, d2)
    {1: (100, 100), 2: (200, None), 3: (None, 300)}
    """
    d= {}

    for key in d1:
        d[key]= d1.get(key), d2.get(key)

    for key in d2:
        d[key]= d1.get(key), d2.get(key)

    return d




















