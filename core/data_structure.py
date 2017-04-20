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

#-----------------------------------------------------------------------------------------------------------------------
class List(list):
    def __new__(cls, *args, **kwargs):
        return list.__new__(cls, *args, **kwargs)

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
class NameEntry:
    def __init__(self, INDEX, data):
        super().__setattr__('__INDEXS__', INDEX)
        super().__setattr__('__data__', data)

    def __getattr__(self, key):
        return self.__data__[ self.__INDEXS__[key] ]

    def __setattr__(self, key, value):
        self.__data__[ self.__INDEXS__[key] ]= value

    def __repr__(self):
        return f'NameEntry{repr(self.__data__)}'


class NameList:  # 类似于nametuple  TODO 手动修改list的容量
    def __init__(self, **kwargs):
        self.__INDEX__= dict(   zip(  kwargs.keys(), range( 0,len(kwargs) )  )   )
        self.kwargs= kwargs

    def genData(self, kwargs):
        for k,v in self.kwargs.items():
            if k in kwargs:
                yield kwargs[k]
            else:
                yield v()

    def __call__(self, *args, **kwargs):
        if args:
            if kwargs:
                raise Exception('can use "args" and "kwargs" at same time')
            if len(args) != len(self.kwargs):
                raise Exception(f'len{args} != len{list(self.kwargs.keys())}')
            return NameEntry(self.__INDEX__, args)

        self_fileds= set(self.kwargs.keys())
        differ= set( kwargs.keys() ) - self_fileds
        if differ:
            raise Exception(f'no field named, {differ}, field are {self_fileds}')
        return NameEntry(self.__INDEX__, list(self.genData(kwargs)))


class SheetTable(dict):
    def __init__(self, **kwargs):  # 例如: SheetTable(name= str, number= int, age= lambda:18, sex= lambda:'male' )
        super().__init__()
        self.Entry= NameList(**kwargs)

    def __getitem__(self, key):
        return self.setdefault(  key, self.Entry()  )


# if __name__ == '__main__':
#     st = SheetTable(name=str, number=int, age=lambda: 18, sex=lambda: 'male')
#     st[10001].name = 'zhao'
#     print(st)  # {10001: NameEntry['zhao', 0, 18, 'male']}
#
#     age= st[20001].age
#     print(age)  # 18
#     print(st)  # {10001: NameEntry['zhao', 0, 18, 'male'], 20001: NameEntry['', 0, 18, 'male']}
#
#     age= st[30001].age
#     print(age)  # 20


#=======================================================================================================================
class DictDecorator(dict):
    REWRITE_METHODS= {'__iter__', 'fromkeys', 'keys', 'update', '__contains__', 'get', '__setitem__', 'setdefault',
                      '__len__', 'pop', 'clear', '__getitem__', 'items', 'copy', '__delitem__', 'values', 'popitem',
                      '__str__'}  # 要被装饰的方法名
    map_id_to_core= {}  # {id(DictDecorator):dict, ...}  装饰器id 和被装饰对象映射

    @classmethod
    def setup(cls):  # 必须在使用前被调用
        def wraper(method_name):  # 将原有方法包装成对core的调用
            def method(self, *args, **kwargs):
                return getattr(self.core(), method_name)(*args, **kwargs)
            return method

        for method_name in cls.REWRITE_METHODS:
            setattr(  cls, method_name, wraper(method_name)  )

    def __new__(cls, table, *args):
        if not isinstance(table, dict):
            raise TypeError("table 必须是 dict 实例")

        decorator= dict.__new__(cls) # 不传入任何参数
        cls.map_id_to_core[ id(decorator)]= table
        return decorator

    def core(self):
        return self.__class__.map_id_to_core[ id(self) ]

    def __init__(self, table):
        super().__init__()  # 不传入任何参数

    def __repr__(self):
        return 'DictDecorator'+str(self)

    def __del__(self):
        del self.__class__.map_id_to_core[ id(self) ]  # 析构前删除在映射表中的信息

DictDecorator.setup()  # !!! 必须在类定义结束后调用

# def disableClassMethod(cls, methods):
#     """
#     例子:
#         disableClassMethod(dict, ['update', 'items']) 禁用dict的update和items方法
#     :param cls:type 要被禁用的类型名
#     :param methods:seq 被禁用的方法列表
#     :return:None
#     """
#     def error(method_name):
#         raise RuntimeError(cls, '的', method_name, '方法已被禁用')
#
#     for method_name in methods:
#         setattr(  cls, method_name, error(method_name)  )

#-----------------------------------------------------------------------------------------------------------------------
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
        if not isinstance(self.core(), CallBackDictDecorator):  # self.table 不是回调装饰器, 删除时进行回调
            self.coreEvictEvent(key, self.get(key) )  # 使用get是因为get不会引起状态变化, 而self[key]可能会引起装饰器状态变化
        self.core().__delitem__(key)

#-----------------------------------------------------------------------------------------------------------------------
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
#     t[2]= 200 # print: 1 100
#     print(t.deque, deq) # deque([2]) deque([2])
#
#     print(t)

#-----------------------------------------------------------------------------------------------------------------------
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
#     t= TimeDictDecorator({}, 1)
#     info= t.info
#     t= TimeDictDecorator( t, 5 )
#
#     t['A'] = 100
#     print(t, t.info, info)  # {'A': 100} OrderedDict([('A', 9)]) OrderedDict([('A', 5)])
#
#     clock.step()
#     print(t, t.info, info)  # {} OrderedDict() OrderedDict()


#=======================================================================================================================
class SizeQueue:
    def __init__(self, max_size):
        self.max_size= max_size
        self._cur_size= 0
        self._queue= deque()

    def __bool__(self):
        return bool(self._queue)

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


class SizeLeakyBucket:
    def __init__(self, callback, rate, max_size):
        self.callback= callback
        self.rate= rate

        self._queue= SizeQueue(max_size)
        self._accum= self.rate
        self._block= False
        self._exe_time= 0  # 安排执行leaky时间

    @property
    def max_size(self):
        return self._queue.max_size

    @max_size.setter
    def max_size(self, value):
        self._queue.max_size= value

    def __call__(self, *args, size=1)->bool:
        if self._queue.append(size, args):
            if not self._block:
                self._leaky()
            return True
        else:
            return False

    def _leaky(self):
        if self._exe_time != clock.time():
            self._accum= self.rate
            self._exe_time= clock.time()

        while self._queue:
            size, args= self._queue.top()
            if size <= self._accum:
                self._queue.pop()
                self._accum -= size
                self.callback(*args)
                self._block= False
            else:
                self._exe_time+= 1
                self._accum += self.rate
                clock.timing(1, self._leaky)  # 下回合继续
                self._block= True
                return


# if __name__ == '__main__':
#     bucket= SizeLeakyBucket(2, 10, print)
#
#     print(clock.time())  # 0
#     bucket.append('ABCEDFG')
#     clock.step()
#
#     print(clock.time())  # 1
#     bucket.append('D')
#     clock.step()
#
#     print(clock.time())  # 2
#     # bucket.append('DEF')
#     clock.step()
#
#     print(clock.time())  # 3
#     clock.step()
#
#     print(clock.time())  # 4
#     clock.step()

#=======================================================================================================================
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
#     p(1,2,3)

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

    def __repr__(self):
        from core.common import objName
        return str([objName(callback) for callback in self.callbacks])


# class AnnounceTable(defaultdict):
#     def __init__(self):
#         super().__init__(Announce)


class AnnounceTable:  # 带log版本
    def __init__(self):
        self.logger= Announce()
        self._table= {}

    def items(self):
        return self._table.items()

    def __getitem__(self, action):
        announce= self._table.get(action)
        if announce is None:
            self._table[action]= announce= Announce()
            announce.append( Bind(self.logger, action) )
        return announce

    def __setitem__(self, action, announce):
        if not isinstance(announce, Announce):
            raise TypeError('value 必须是 Announce 子类型')
        self._table[action]= announce

#-----------------------------------------------------------------------------------------------------------------------

