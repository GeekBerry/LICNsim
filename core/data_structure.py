#!/usr/bin/python3
#coding=utf-8

from collections import deque, OrderedDict
from core.clock import clock, Timer
from copy import deepcopy
#-----------------------------------------------------------------------------------------------------------------------
class List(list):
    def size(self):
        return len(self)

    def top(self):
        return self[0]

    def discard(self, x):
        try:
            super().remove(x)
        except ValueError:
            pass


class Dict(dict):
    def discard(self, key):
        try:
            del self[key]
            return True
        except KeyError:
            return False

    def pop(self, k, d=None):
        try:
            return super().pop(k, d)
        except KeyError:
            return None

#-----------------------------------------------------------------------------------------------------------------------
class SheetTable(dict):
    class Entry(dict):
        def __init__(self, getType):
            super().__init__()
            super().__setattr__('getType', getType)

        def __getitem__(self, item):
            return self.setdefault( item, self.getType(item)() )#call或者init

        def __getattr__(self, item):# entry['name'] 和 entry.name 等效
            return self.__getitem__(item)

        def __setattr__(self, key, value):
            self.__setitem__(key, value)


    def __init__(self, **kwargs):#例如: SheetTable(name= str, number= int, age= lambda:18, sex= lambda:'male' )
        super().__init__()
        self.TypeDict= kwargs

    def addFields(self, **kwargs):
        self.TypeDict.update(kwargs)

    def __getitem__(self, item):
        return self.setdefault(item, SheetTable.Entry(self.TypeDict.__getitem__))


#=======================================================================================================================
class DictDecorator:
    """
    为了减少子类重载数量, 不提供setdefault和get方法
    """
    def __init__(self, table):
        if isinstance(table, dict) or isinstance(table, DictDecorator):
            self.table= table
        else:
            raise TypeError("table 必须是 dict 或 DictDecorator 实例")

    def __len__(self):
        return len(self.table)

    def __contains__(self, key):
        return key in self.table

    def __iter__(self):
        return iter(self.table)

    def __setitem__(self, key, value):
        self.table[key]= value

    def __getitem__(self, key):
        return self.table[key]

    def items(self):
        return self.table.items()

    def __delitem__(self, key):
        del self.table[key]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.table)


#-----------------------------------------------------------------------------------------------------------------------
class SizeDictDecorator(DictDecorator):
    def __init__(self, table, capacity, set_refresh= True, get_refresh= True):
        super().__init__(table)
        self._deque= deque()
        self._capacity= capacity
        self.set_refresh= set_refresh
        self.get_refresh= get_refresh
        self.evict_call_back= lambda *args:None

    def setCapacity(self, capacity):
        if capacity<0:
            raise RuntimeError('capacity 必须大于 0')
        else:
            self._capacity= capacity
            self._evict()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self._deque:
            self._deque.append(key)
            self._evict()
        elif self.set_refresh:# move_to_end
            self._deque.remove(key)
            self._deque.append(key)

    def __getitem__(self, key):
        result= super().__getitem__(key)
        if self.get_refresh:
            self._deque.remove(key)
            self._deque.append(key)
        return result

    def __delitem__(self, key):
        super().__delitem__(key)
        self._deque.remove(key)

    def _evict(self):
        while len(self.table) > self._capacity:
            key= self._deque[0]# top
            value= self.table[key] # 绕过自身的__getitem__
            self.evict_call_back(key, value)
            self.__delitem__(key)


class TimeDictDecorator(DictDecorator):
    def __init__(self, table, time, set_refresh= True, get_refresh= True):
        super().__init__(table)
        self.timer= Timer(self.flush)
        self.time= time
        self.info= OrderedDict()
        self.set_refresh= set_refresh
        self.get_refresh= get_refresh
        self.evict_call_back= lambda *args:None


    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self.info  or  self.set_refresh:
            self.info[key]= clock.time() + self.time
            self.info.move_to_end(key)

            if not self.timer:
                self.timer.timing(self.time)


    def __getitem__(self, key):
        result= super().__getitem__(key)
        if self.get_refresh:
            del self.info[key]
            self.info[key]= clock.time() + self.time #自己就排到后面去了
        return result


    def flush(self):
        next_flush_time= None
        delete_keys= []
        for key in self.info:
            if self.info[key]<= clock.time():
                delete_keys.append(key)
            else:#获取下一次驱逐事件的时间
                next_flush_time= self.info[key] - clock.time()
                break #找到第一个 next_flush_time 即可

        for key in delete_keys:
            self.evict_call_back(key, self.table[key])# 绕过自身的__getitem__
            super().__delitem__(key)
            self.info.popitem(last=False) # 一定在最前面

        if next_flush_time:
            self.timer.timing(next_flush_time)

#-----------------------------------------------------------------------------------------------------------------------
class DefaultDictDecorator:# 注意!!! 不是DictDecorator的子类
    def __init__(self, table, DefaultType):# 例如 DefaultDictDecorator({}, int)
        self.table= table
        self.DefaultType= DefaultType

    def __contains__(self, key):
        return self.table.__contains__(key)

    def __iter__(self):
        return self.table.__iter__()

    def items(self):#FIXME　是否需要
        return self.table.items()

    def __setitem__(self, key, value):
        self.table[key]= value

    def __getitem__(self, key):
        if key not in self:
            self.table[key]= self.DefaultType()

        if key in self:# 由于self.table可能是装饰过的表, 所以此操作后self.table中不一定有key项
            return self.table[key]
        else:
            return self.DefaultType()

    def __repr__(self):
        return str(self.table)

# if __name__ == '__main__':
#     t= TimeDictDecorator(SizeDictDecorator({}, 2), 2)
#
#     t[1]= 1
#     t[2]= 2
#
#     clock.step()
#     print(t, t.info, t.timer)
#
#     p= t[1]
#     clock.step()
#     print(t, t.info, t.timer)
#
#     t[2]= 22
#     clock.step()
#     print(t, t.info, t.timer)
#     clock.step()
#     print(t, t.info)
#     clock.step()
#     print(t)
#     clock.step()
#     print(t)

