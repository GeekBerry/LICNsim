#!/usr/bin/python3
#coding=utf-8

from collections import deque, OrderedDict, defaultdict, namedtuple

from core.clock import clock, Timer


def top(seq):
    return next(iter(seq))


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


class LazyIter:
    def __init__(self, seq):
        self.iter= iter(seq)
        self.seq= []
        self.traverse= False

    def __iter__(self):
        if not self.traverse:
            return self
        else:
            return iter(self.seq)

    def __next__(self):
        try:
            val= next(self.iter)
            self.seq.append(val)
            return val
        except StopIteration:
            self.traverse= True
            self.iter= iter(self.seq)
            raise StopIteration


# ----------------------------------------------------------------------------------------------------------------------
class List(list):
    def __setitem__(self, index, object):
        if len(self) <= index:
            self.extend( [None]*(index-len(self)) )
            self.append(object)
        else:
            list.__setitem__(self, index, object)

    def size(self):
        return len(self)

    def top(self):
        return self[0]

    def discard(self, x):
        try:
            super().remove(x)
        except ValueError:
            pass

    def index(self, value, start=None, stop=None):
        try:
            return super().index(value, start, stop)
        except Exception:
            return None


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


# ----------------------------------------------------------------------------------------------------------------------
class NameEntry:
    def __init__(self, index:dict, data:list):
        super().__setattr__('__INDEX__', index)
        super().__setattr__('__data__', data)

    def __getitem__(self, key):
        return self.__data__[ self.__INDEX__[key] ]

    def __getattr__(self, key):
        return self[key]

    def __setitem__(self, key, value):
        self.__data__[ self.__INDEX__[key] ]= value

    def __setattr__(self, key, value):
        self[key]= value

    def __len__(self):
        return len(self.__INDEX__)

    def __iter__(self):
        for index in self.__INDEX__.values():
            yield self.__data__[index]

    def keys(self):
        return self.__INDEX__.keys()

    def items(self):
        for field, index in self.__INDEX__.items():
            yield field, self.__data__[index]

    def __str__(self):
        return f'NameEntry{ dict(self.items() )}'

# if __name__ == '__main__':
#     entry= NameEntry( {'name':0, 'age':1}, ['jim', 18,] )
#     print(entry)  # NameEntry{'name': 'jim', 'age': 18}
#     print(entry['age'])  # 18


class NameList:  # 类似于nametuple  TODO 手动修改list的容量
    def __init__(self, **kwargs):
        self.kwargs= kwargs  # {key1:Type1, key2:Type2, ...}
        self.__INDEX__= { field:index
            for index, field in enumerate( kwargs.keys() )
        }  # {key1:0, key2:1, ...}

    def genData(self, kwargs):
        for k,v in self.kwargs.items():
            if k in kwargs:
                yield kwargs[k]
            else:
                yield v()

    def __call__(self, *args, **kwargs)->NameEntry:
        if args:
            if kwargs:
                raise Exception('can use "args" and "kwargs" at same time')
            if len(args) != len(self.kwargs):
                raise Exception(f'len{args} != len{list(self.kwargs.keys())}')
            return NameEntry(self.__INDEX__, list(args))

        self_fileds= set(self.kwargs.keys())
        differ= set( kwargs.keys() ) - self_fileds
        if differ:
            raise Exception(f'no field named, {differ}, field are {self_fileds}')
        return NameEntry(self.__INDEX__, list(self.genData(kwargs)))


# if __name__ == '__main__':
#     Person= NameList(name=str, age=int)
#
#     tom= Person(name='Tom', age=18)
#     jerry= Person('Jerry', 15)
#
#     print(tom, jerry)  # NameEntry{'name': 'Tom', 'age': 18} NameEntry{'name': 'Jerry', 'age': 15}
#
#     tom.age+= 1
#     print(tom.age)  # 19


class SheetTable(dict):  # XXX dropField 是非常低效的
    def __init__(self, **kwargs):  # 例如: SheetTable(name= str, number= int, age= lambda:18, sex= lambda:'male' )
        super().__init__()
        self.Entry= NameList(**kwargs)

    def __getitem__(self, key):
        return self.setdefault( key, self.Entry() )

    def addField(self, field, FieldType):  # 如: addField('scort', int)
        if field not in self.Entry.kwargs:
            # 更新域记录
            index= len(self.Entry.kwargs)
            self.Entry.__INDEX__[field]= index
            self.Entry.kwargs[field]= FieldType
            # 更新已有元素
            for entry in self.values():
                List.__setitem__(entry.__data__, index, FieldType() )
        else:
            pass  # TODO

    def dropField(self, field):
        if (field in self.Entry.__INDEX__) and (field in self.Entry.kwargs):
            index= self.Entry.__INDEX__[field]
            # 更新域记录
            for f,i in self.Entry.__INDEX__.items():
                if i > index:
                    self.Entry.__INDEX__[f] -= 1  # 向前移一格
            del self.Entry.kwargs[field]
            del self.Entry.__INDEX__[field]
            # 更新已有元素
            for entry in self.values():
                entry.__data__.pop(index)
        else:
            pass  # TODO


# if __name__ == '__main__':
#     st = SheetTable(name=str)
#     st[10001].name = 'zhao'
#
#     st.addField('address',int)
#     print(st[10001])  # NameEntry{'name': 'zhao', 'address': 0}
#     print(st[10002])  # NameEntry{'name': '', 'address': 0}
#
#     st.dropField('name')
#     print(st[10001])  # NameEntry{'address': 0}


# ======================================================================================================================
def decoratorOfType(Type):
    class Decorator(Type):
        def __new__(cls, inside, *args, **kwargs):
            return Type.__new__(cls, *args, **kwargs)

        def __init__(self, inside, *args, **kwargs):
            super().__setattr__('_inside_', inside)
            super().__init__(self, *args, **kwargs)  # 要在__setattr__之后, 以免调用自身函数

        for method_name in set( dir(Type) ) - set( dir(type) ):
            exec(
        f'def {method_name}(self, *args, **kwargs):\n'
        f'\t\treturn self._inside_.{method_name}(*args, **kwargs)'
        )  # 批量重载函数

        def __str__(self):
            return f'{self.__class__.__name__}({self._inside_.__str__()})'

    return Decorator

# ----------------------------------------------------------------------------------------------------------------------
DictDecorator= decoratorOfType(dict)


class CallBackDictDecorator(DictDecorator):
    """
    例子:
    in= CallBackDictDecorator(table= dict)
    out= CallBackDictDecorator(table= in); in.evict_callback= out.coreEvictEvent

    def in[key] <==> in.__delitem__(key)
        in.get[key] <==> dict.get(key)
        ->value
        in.coreEvictEvent( key, value )
            in.evict_callback <==> out.coreEvictEvent
                out.evict_callback( key, value )
        dict.__delitem__(key)

    del out[key]
        in.__delitem__(key)
            in.get[key] <==> dict.get(key)
            ->value
            in.coreEvictEvent( key, value )
                in.evict_callback <==> out.coreEvictEvent
                    out.evict_callback( key, value )
            dict.__delitem__(key)

    """
    def __init__(self, table):
        super().__init__(table)
        self.evict_callback= lambda key, value:None
        if isinstance(table, CallBackDictDecorator):
            table.evict_callback= self.coreEvictEvent

    def coreEvictEvent(self, key, value):  # 被装饰者将要删除 key value 对
        self.evict_callback(key, value)

    def __delitem__(self, key):
        if not isinstance(self._inside_, CallBackDictDecorator):  # self.table 不是回调装饰器, 删除时进行回调
            self.coreEvictEvent(key, self.get(key) )  # 使用get是因为get不会引起状态变化, 而self[key]可能会引起装饰器状态变化
        self._inside_.__delitem__(key)


# ----------------------------------------------------------------------------------------------------------------------
class SizeDictDecorator(CallBackDictDecorator):
    def __init__(self, table, max_size, set_refresh= True, get_refresh= True):
        super().__init__(table)
        self.deque= deque()
        self._max_size= max_size
        self.set_refresh= set_refresh
        self.get_refresh= get_refresh

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, value):
        if value < 0:
            raise RuntimeError('max_size 必须大于 0')
        else:
            self._max_size= value
            self._evict()

    def coreEvictEvent(self, key, value):
        self.deque.remove(key)
        super().coreEvictEvent(key, value)

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
            discard(self.deque, key)
            self.deque.append(key)
        return result

    def _evict(self):
        while len(self) > self._max_size:
            key= self.deque[0]  # top
            del self[key]

# if __name__ == '__main__':
#     t= SizeDictDecorator({}, 2)
#     deq= t.deque
#
#     t= SizeDictDecorator(t, 1)
#     t.evict_callback= print
#     t[1]= 100
#     t[2]= 200  # print: 1 100
#     print(t.deque, deq)  # deque([2]) deque([2])
#
#     print(t)  # SizeDictDecorator(SizeDictDecorator({2: 200}))
#
# if __name__ == '__main__':
#     t= SizeDictDecorator({}, 0)
#     t[1]= 100
#     print(t)  # SizeDictDecorator({})
#
#     try:
#         i= t[1]  # KeyError: 1
#     except KeyError:
#         pass



# ----------------------------------------------------------------------------------------------------------------------
class TimeDictDecorator(CallBackDictDecorator):
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
#     print(t, t.info)  # TimeDictDecorator{'A':100} OrderedDict([('A', 2)])
#
#     clock.step()
#     t['B']= 200
#     print(t, t.info)  # TimeDictDecorator{'A': 100, 'B': 200} OrderedDict([('A', 2), ('B', 3)])
#
#     clock.step()
#     clock.step()
#     print(t, t.info)  # TimeDictDecorator{'B': 200} OrderedDict([('B', 3)])
#
#     clock.step()
#     print(t, t.info)  # TimeDictDecorator({}) OrderedDict()

# if __name__ == '__main__':
#     t= TimeDictDecorator({}, 1)
#     info= t.info
#     t= TimeDictDecorator( t, 5 )
#
#     t['A'] = 100
#     print(t, t.info, info)  # TimeDictDecorator(TimeDictDecorator({'A': 100})) OrderedDict([('A', 5)]) OrderedDict([('A', 1)])
#
#     clock.step()
#     print(t, t.info, info)  # TimeDictDecorator(TimeDictDecorator({'A': 100})) OrderedDict([('A', 5)]) OrderedDict([('A', 1)])  FIXME
#
#     clock.step()
#     print(t, t.info, info)  # TimeDictDecorator(TimeDictDecorator({})) OrderedDict() OrderedDict()


# ======================================================================================================================
class SizeQueue:
    def __init__(self, max_size):
        self.max_size= max_size
        self._cur_size= 0
        self._queue= deque()

    def __bool__(self):
        return bool(self._queue)

    def __iter__(self):
        return iter(self._queue)

    def __len__(self):
        return len(self._queue)

    def append(self, size, data) ->bool:
        if self._cur_size + size > self.max_size:
            return False
        else:
            self._cur_size += size
            self._queue.append( (size,data,) )
            return True

    def top(self):
        return next(iter(self._queue))

    def pop(self):
        try:
            size,data= self._queue.popleft()
        except IndexError:
            return None
        else:
            self._cur_size -= size
            assert self._cur_size >= 0  # DEBUG
            return size, data


# ======================================================================================================================
EMPTY_FUNC= lambda *args: None

class Bind:
    def __init__(self, func= EMPTY_FUNC, *args):
        self.func= func
        self.args= args  # 注意, 没有进行拷贝

    def __bool__(self):
        return self.func is EMPTY_FUNC

    def clear(self):
        self.func= EMPTY_FUNC
        self.args= None

    def __call__(self, *args, **kwargs):
        return self.func(*self.args, *args, **kwargs)

    def __str__(self):
        from core.common import objName
        return f'Bind( {objName(self.func)}, {", ".join([str(each) for each in self.args])})'


#-----------------------------------------------------------------------------------------------------------------------
class CallTable(dict):  # FIXME 能否利用defaultdict实现
    def __getitem__(self, name):
        return self.setdefault( name, Bind(EMPTY_FUNC) )

    def __setitem__(self, name, func):
        callback= self.setdefault( name,  Bind(EMPTY_FUNC) )
        callback.func= func

# if __name__ == '__main__':
#     t= CallTable()
#     p= t['1']
#     t['1']= print
#     p(1,2,3)  # 打印:1 2 3


class Announce:
    def __init__(self):
        self.callbacks= []

    def __len__(self):
        return len(self.callbacks)

    def __iter__(self):
        return iter(self.callbacks)

    def __call__(self, *args):
        for callback in self.callbacks:
            callback(*args)

    def append(self, func):
        self.callbacks.append(func)

    def discard(self, func):
        try:
            self.callbacks.remove(func)
        except ValueError:
            pass

    def __repr__(self):
        from core.common import objName
        return str([objName(callback) for callback in self.callbacks])


# class AnnounceTable(defaultdict):  # 不带Log版
#     def __init__(self):
#         super().__init__(Announce)


class AnnounceTable:  # 带log版本
    def __init__(self):
        self.logger= Announce()
        self._table= {}  # {name:Announce(), ...}

    def items(self):
        return self._table.items()

    def __getitem__(self, name):
        """
        在新建一个Announce时, 自动为Announce添加一个绑定到self.Announce的项
        :param name: Announce名称
        :return: Announce
        
        AnnounceTable[name](*args) => [self.logger(name, *args), 其他... ]
        """
        announce= self._table.get(name)
        if announce is None:
            self._table[name]= announce= Announce()
            announce.append(Bind(self.logger, name))
        return announce

    def __setitem__(self, action, announce):
        if not isinstance(announce, Announce):
            raise TypeError('value 必须是 Announce 子类型')
        self._table[action]= announce

#-----------------------------------------------------------------------------------------------------------------------

import math

class SizeLeakyBucket:
    def __init__(self, rate, max_size):
        self.rate= rate
        self._queue= SizeQueue(max_size)
        self._accum= self.rate
        self._last_activated_time= clock.time()
        self._blocked= False
        self.callbacks= CallTable()

    @property
    def max_size(self):
        return self._queue.max_size

    @max_size.setter
    def max_size(self, value):
        self._queue.max_size= value

    def __iter__(self):  # 不返回 size
        for size, args in self._queue:
            yield args

    def __len__(self):
        return len(self._queue)

    def append(self, size, *args):
        if self._queue.append(size, args):
            self.callbacks['queue'](*args)
            if not self._blocked:
                self._leaky()
        else:
            self.callbacks['full'](*args)

    def _leaky(self):
        if self._last_activated_time < clock.time():
            self._accum= self.rate
            self._last_activated_time= clock.time()

        if self._queue and (not self._blocked):
            size, args= self._queue.top()
            delay= math.ceil( (size - self._accum)/self.rate )
            self._accum += delay*self.rate - size

            self.callbacks['begin'](*args)
            clock.timing(delay, self._pop)
            self._blocked= True

    def _pop(self):
        size, args= self._queue.pop()
        self.callbacks['end'](*args)
        self._blocked= False
        self._last_activated_time= clock.time()
        self._leaky()


# if __name__ == '__main__':
#     bucket= SizeLeakyBucket(2, 10)
#     bucket.callbacks['full']= Bind( print, 'full' )
#     bucket.callbacks['queue']= Bind( print, 'queue' )
#     bucket.callbacks['begin']= Bind( print, 'begin' )
#     bucket.callbacks['end']= Bind( print, 'end' )
#
#     print(clock.time())  # 0
#     bucket.append(5, 'A')
#     bucket.append(6, 'X')
#     clock.step()
#
#     print(clock.time())  # 1
#     bucket.append(1, 'B')
#     clock.step()
#
#     print(clock.time())  # 2
#     bucket.append(3, 'C')
#     clock.step()
#
#     print(clock.time())  # 3
#     clock.step()
#
#     print(clock.time())  # 4
#     clock.step()
#
#     print(clock.time())  # 5
#     clock.step()
#
#     print(clock.time())  # 6
#     bucket.append(2, 'D')
#     clock.step()
