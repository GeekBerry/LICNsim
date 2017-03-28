#!/usr/bin/python3
#coding=utf-8

from collections import deque, OrderedDict, defaultdict
from core.clock import clock, Timer

from core.common import log, label

def discard(obj, key):
    if hasattr(obj, '__delitem__'):
        try: del obj[key]
        except: pass
    elif hasattr(obj, 'remove'):
        try: obj.remove(key)
        except: pass
    else: raise RuntimeError('不能使用discard函数')

def topValue(obj):
    if isinstance( obj, dict ):
        return next( obj.values().__iter__() )

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
        def __init__(self, TypeDict):
            super().__init__()
            super().__setattr__('TypeDict', TypeDict)  # 绕过self.__setattr__

        def __getitem__(self, item):
            return self.setdefault( item, self.TypeDict[item]() )  # call或者init

        def __getattr__(self, item):  # arg= entry['name'] 和 arg= entry.name 等效
            return self.__getitem__(item)

        def __setattr__(self, key, value): # entry['name']= arg 和 entry.name= arg 等效
            self.__setitem__(key, value)

    def __init__(self, **kwargs):  # 例如: SheetTable(name= str, number= int, age= lambda:18, sex= lambda:'male' )
        super().__init__()
        self.TypeDict= kwargs

    def updateFields(self, **kwargs):
        self.TypeDict.update(kwargs)

    def __getitem__(self, item):
        return self.setdefault(item, SheetTable.Entry(self.TypeDict))


# if __name__ == '__main__':
#     st = SheetTable(name=str, number=int, age=lambda: 18, sex=lambda: 'male')
#     st[10001].name = 'zhao'
#     print(st)  # {10001: {'name':'zhao'}}
#
#     age= st[20001].age
#     print(age)  # 18
#     print(st)  # {10001: {'name': 'zhao'}, 20001: {'age': 18}}
#
#     st.updateFields(age=lambda: 20)
#     age= st[30001].age
#     print(age)  # 20
#
#     st[30001].food= 'Apple'
#     print(st[30001])  # {'food': Apple, 'age': 20}


#=======================================================================================================================
class DictDecorator:
    """
    为了减少子类重载数量, 不提供setdefault和get方法

    例子:
    in= DictDecorator(table= None)
    middle= DictDecorator(table= in); in.evict_callback= middle.coreEvictEvent
    out= DictDecorator(table= middle); middle.evict_callback= out.coreEvictEvent

    def in[key]
        in.table[key] <==> dict.__getitem__(key)
        ->value
        in.coreEvictEvent( key, value )
            in.evict_callback
        del in.table[key] <==> dict.__delitem__(key)

    del middle[key]
        del in[key]
            in.table[key] <==> dict.__getitem__(key)
            ->value
            in.coreEvictEvent( key, value )
                in.evict_callback
                    middle.coreEvictEvent
                        middle.evict_callback
            del in.table[key] <==> dict.__delitem__(key)

    del out[key]
        del middle[key]
            del in[key]
                in.table[key] <==> dict.__getitem__(key)
                ->value
                in.coreEvictEvent( key, value )
                    in.evict_callback
                        middle.coreEvictEvent
                            middle.evict_callback
                                out.coreEvictEvent
                                    out.evict_callback
                del in.table[key] <==> dict.__delitem__(key)
    """
    def __init__(self, table):
        if isinstance(table, dict):
            self.table= table
        elif isinstance(table, DictDecorator):
            self.table= table
            self.table.evict_callback= self.coreEvictEvent
        else:
            raise TypeError("table 必须是 DictDecorator实例 或 dict实例")

        self.evict_callback= lambda key, value:None

    def coreEvictEvent(self, key, value):  # 被装饰者将要删除 key value 对
        self.evict_callback(key, value)

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
        if not isinstance( self.table, DictDecorator ): # self.table 不是装饰器, 删除时进行回调
            self.coreEvictEvent(key, self.table[key])
        del self.table[key]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.table)

#-----------------------------------------------------------------------------------------------------------------------
class SizeDictDecorator(DictDecorator):
    def __init__(self, table, capacity, set_refresh= True, get_refresh= True):
        super().__init__(table)
        self.deque= deque()
        self._capacity= capacity
        self.set_refresh= set_refresh
        self.get_refresh= get_refresh

    def coreEvictEvent(self, key, value):
        self.deque.remove(key)  # FIXME try?
        super().coreEvictEvent(key, value)

    def setCapacity(self, capacity):
        if capacity < 0:
            raise RuntimeError('capacity 必须大于 0')
        else:
            self._capacity= capacity
            self._evict()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)  # 执行后 key 有可能不在 table 中
        if key not in self.deque:
            self.deque.append(key)
            self._evict()
        elif self.set_refresh:  # move_to_end
            self.deque.remove(key)
            self.deque.append(key)

    def __getitem__(self, key):
        result= super().__getitem__(key)
        if self.get_refresh:
            discard( self.deque, key )
            self.deque.append(key)
        return result

    def _evict(self):
        while len(self.table) > self._capacity:
            key= self.deque[0]  # top
            self.__delitem__(key)

# if __name__ == '__main__':
#     t= SizeDictDecorator(SizeDictDecorator({}, 1), 2 )
#     t.evict_callback= print
#     t[1]= 1
#     t[2]= 2
#     print(t.deque, t.table.deque)

#-----------------------------------------------------------------------------------------------------------------------
class TimeDictDecorator(DictDecorator):
    def __init__(self, table, life_time, set_refresh= True, get_refresh= True):
        super().__init__(table)
        self.timer= Timer(self.flush)
        self.life_time= life_time
        self.info= OrderedDict()  # {key:dead_time, ...}

        self.set_refresh= set_refresh
        self.get_refresh= get_refresh

    def coreEvictEvent(self, key, value):
        del self.info[key]  # 使用 discard ???
        super().coreEvictEvent(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if (key not in self.info)  or  self.set_refresh:  # 不存在 或 需要重置
            self.info[key]= clock.time() + self.life_time
            self.info.move_to_end(key)

            if not self.timer:
                self.timer.timing(self.life_time)

    def __getitem__(self, key):
        result= super().__getitem__(key)  # 放在最前面, 以 super().__getitem__ 来对 key 的存在性进行检查
        if self.get_refresh:  # 需要重置
            self.info[key]= clock.time() + self.life_time
            self.info.move_to_end(key)
        return result

    def flush(self):
        delete_keys= [  key  for key in self.info
            if self.info[key] <= clock.time()
        ]

        for key in delete_keys:
            self.__delitem__(key)

        if self.info:
            self.timer.timing( topValue(self.info) - clock.time() )

# if __name__ == '__main__':
#     t= TimeDictDecorator({}, 2)
#     t['A']= 100
#     print(t, t.info)  # {'A':100} OrderedDict([('A', 2)])
#
#     clock.step()
#     t['B']= 200
#     print(t, t.info)  # {'A': 100, 'B': 200} OrderedDict([('A', 2), ('B', 3)])
#
#     clock.step()
#     clock.step()
#     print(t, t.info)  # {'B': 200} OrderedDict([('B', 3)])
#
#     clock.step()
#     print(t, t.info)  # {} OrderedDict()

# if __name__ == '__main__':
#     t= TimeDictDecorator( TimeDictDecorator({}, 1), 5 )
#
#     t['A'] = 100
#     print(t, t.info, t.table.info)
#
#     clock.step()
#     print(t, t.info, t.table.info)
#
#     clock.step()
#     print(t, t.info, t.table.info)


#=======================================================================================================================
class DefaultDictDecorator(dict):  # XXX 如何用 defaultdict 实现 ???
    def __init__(self, table, DefaultType):
        super().__init__(table)
        self.DefaultType= DefaultType

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        else:
            self[key]= value= self.DefaultType()
            return value



