#!/usr/bin/python3
#coding=utf-8

from collections import deque, OrderedDict, defaultdict
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

    # def __repr__(self):
    #     values_names= self.TypeDict.keys_names()
    #     string= '\n%16s\t'%('key') + '\t'.join([ '%16s'%(field) for field in values_names ]) + '\n'
    #     row= 0
    #     for key, entry in self.items():
    #         string+= '%16s\t'%(str(key)[0:16])
    #         for field in values_names:
    #             cell= str( entry[field] )
    #             cell= cell[0:16]
    #             string+= '%16s\t'%(cell)
    #         string+= '\n'
    #
    #         row += 1
    #         if row > 20:
    #             string+= '...\n'
    #             break
    #     return string

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
    def __init__(self, table, capacity, set_refresh= True, get_refresh= True):
        super().__init__(table)
        self.deque= deque()
        self._capacity= capacity
        self.set_refresh= set_refresh
        self.get_refresh= get_refresh

    def coreEvictEvent(self, key, value):
        self.deque.remove(key)
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
            discard(self.deque, key)
            self.deque.append(key)
        return result

    def _evict(self):
        while len(self) > self._capacity:
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
#
# if __name__ == '__main__':
#     t= TimeDictDecorator({}, 1)
#     info= t.info
#     t= TimeDictDecorator( t, 5 )
#
#     t['A'] = 100
#     print(t, t.info, info)  # {'A': 100} OrderedDict([('A', 9)]) OrderedDict([('A', 5)])
#
#     clock.step()
#     print(t, t.info, info)  # {'A': 100} OrderedDict([('A', 9)]) OrderedDict([('A', 5)])
#
#     clock.step()
#     print(t, t.info, info)  # {} OrderedDict() OrderedDict()


#=======================================================================================================================
# class DefaultDictDecorator(dict):  # XXX 如何用 defaultdict 实现 ???
#     def __init__(self, table, DefaultType):
#         super().__init__(table)
#         self.DefaultType= DefaultType
#
#     def __getitem__(self, key):
#         if key in self:
#             return super().__getitem__(key)
#         else:
#             self[key]= value= self.DefaultType()
#             return value

#=======================================================================================================================
EMPTY_FUNC= lambda *args: None

class Bind:
    def __init__(self, func, *args):
        self.func= func
        self.args= args  # 注意, 没有进行拷贝

    def __call__(self, *args, **kwargs):
        return self.func(*self.args, *args, **kwargs)

#-----------------------------------------------------------------------------------------------------------------------
class CallTable(dict):  # FIXME 能否利用defaultdict实现
    class CallBack:  # 用于CallTable[name]还不存在时,返回一个绑定指向列表的量
        def __init__(self):
            self.func= None

        def __eq__(self, other):
            return self.func is other

        def __call__(self, *args):
            if self.func is not None:
                return self.func(*args)
            # else: raise RuntimeError('未找到对应函数',self.func,'无法执行')

    def __getitem__(self, name):
        return self.setdefault( name, CallTable.CallBack() )

    def __setitem__(self, name, func):
        callback= self.setdefault( name, CallTable.CallBack() )
        callback.func= func

# if __name__ == '__main__':
#     t= CallTable()
#     p= t['1']
#     t['1']= print
#     p(1,2,3)

class Announce(List):
    def __call__(self, *args, **kwargs):
        for callback in self:
            callback(*args, **kwargs)

        # if not self: raise RuntimeWarning(self, args, "没人订阅")

class AnnounceTable(defaultdict):
    def __init__(self):
        super().__init__(Announce)

#-----------------------------------------------------------------------------------------------------------------------
import inspect
import pydblite

class DataBaseTable(pydblite.pydblite._BasePy3):
    class AccessRecord(DictDecorator):  # 提供元素访问语法糖, 使得对元素的修改可以更新索引
        def __init__(self, record, db):  # 必须第一个参数就是被装饰者
            super().__init__(record)  # 其实不需要初始化
            super().__setattr__('_db', db)

        def __setattr__(self, key, value):
            self._db.update(self, **{key:value})

        def __getattr__(self, item):
            return self[item]

    def __init__(self, path= ':memory:', *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.mode= 'override'

    def insert(self, *args, **kw):
        raise RuntimeError('insert 被禁用, 请使用 access')

    def ids(self):
        for _id in self.records:
            yield _id

    def fromIds(self, ids):
        for _id in ids:
            yield self[_id]

    def __call__(self, *args, **kwargs):  # select
        """
        db('a') 同 pydblite._BasePy3 用法
        db(a= 1, b= lambda num: 1<num<2, ...)  之间为 'and' 关系
        itertools.chain( db(a= 1), db(b= 2) ) 之间为 'or' 关系
        :param args:
        :param kwargs:
        :return: 迭代器
        """
        if args:
            return super()(*args, **kwargs)
        # 区分有索引项和无索引项
        keys = kwargs.keys()  # 加速提取
        ixs = set(keys) & set(self.indices.keys())
        no_ix = set(keys) - ixs
        # 对有索引的项进行集合并操作
        if ixs:
            ix = ixs.pop()
            res= set( self.keyIndex(ix, kwargs[ix]) )  # 解决如何产生第一个集合的问题
            while res and ixs:
                ix = ixs.pop()
                res &= set( self.keyIndex(ix, kwargs[ix]) )
        else:
            res= self.ids()
        # 对无索引的项进行过滤
        for field in no_ix:
            value= kwargs[field]
            res= self.keyFilter(field, value, res)
        # 必须返回可反复遍历的对象
        return LazyIter( self.fromIds(res) )  # LazyIter 惰性生成列表

    def keyIndex(self, field, value)->list:  # list[_id, ...]
         if inspect.isfunction(value):  # 表达式
            _ids= []
            for key, ids in self.indices[field].items():  # 遍历索引键
                if value(key):
                    _ids += ids
            return _ids
         else:
            return self.indices[field].get(value, [])

    def keyFilter(self, field, value, ids_iter):
        if ids_iter is None:
            ids_iter= self.ids()  # 不存在带索引的项, 则在全局中查找

        if inspect.isfunction( value ):  # 表达式
            return filter(lambda _id: value( self[_id][field] ), ids_iter)
        else:
            return filter(lambda _id: value == self[_id][field], ids_iter)

    def create(self, *keys, **values):
        """
        mydb.create('a', 'b', c=0) 不带默认值的为主键 (a,b)为主键
        :param keys: 主键列表
        :param values: 域字典
        :return:None
        """
        self._primary= keys

        pairs= [ pair for pair in zip( values.keys(), values.values() ) ]
        super().create(*keys, *pairs, mode= self.mode)
        self.create_index(*self._primary)
        return self

    def access(self, *keys, **kwargs)->AccessRecord:
        """
        indices:('k1', 'k2')
        access(k1= 1, k2= 2) -> KeyError
        access(k1, k2)
        access(k1, k2, k1= new_k1)
        access(k1, k2).k1 += 1
        access(k1, k2)['k1']= new_k1  错误, 不能直接对索引项进行修改
        :param keys:
        :param kwargs:
        :return:
        """
        if len(keys) != len(self._primary):
            raise KeyError('keys 参数数量必须与主键长度一致')

        primarys= {k:v for k, v in zip(self._primary, keys)}

        record= self._find(**primarys)
        if record is None:  # 插入
            kwargs.update(primarys)  # 注意, 是更新kwargs, 而非更新primarys
            record= self._insert(**kwargs)
        else:
            if kwargs:
                self.update(record, **kwargs)
        return self.AccessRecord(record, self)

    def _insert(self, **kwargs)->dict:
        _id= super().insert(**kwargs)
        return self[_id]

    def _find(self, **primarys)->dict or None:
        try:
            return top( self(**primarys) )
        except StopIteration:
            return None


# if __name__ == '__main__':
#     mydb = DataBaseTable()
#     mydb.create('k1', 'k2', v1=0, v2=0)
#     mydb.create_index('v1')
#
#     p= mydb.access(1,2, v2= 100)
#     print('insert', p)  # insert {'k1': 1, 'k2': 2, 'v1': 0, 'v2': 100, '__id__': 0, '__version__': 0}
#
#     p= mydb.access(1,2, v2= 200)
#     print('update', p)  # update {'k1': 1, 'k2': 2, 'v1': 0, 'v2': 200, '__id__': 0, '__version__': 1}
#     p.update({'v2':222})
#     print('unsafe', p)  # unsafe {'k1': 1, 'k2': 2, 'v1': 0, 'v2': 222, '__id__': 0, '__version__': 1}
#
#     mydb.access(1,2).v1+= 1  # 索引项可以这样修改
#     # mydb.access(1,2)['v1']+= 1  索引项不能这样修改 !!!
#     print('records', mydb.records)  # records {0: {'k1': 1, 'k2': 2, 'v1': 1, 'v2': 200, '__id__': 0, '__version__': 2}}
#
#     mydb.access(1,2)['v2']= 300  # 非索引项可以这样修改, 但'__version__'不会更新
#     print('records', mydb.records)  # records {0: {'k1': 1, 'k2': 2, 'v1': 1, 'v2': 300, '__id__': 0, '__version__': 2}}
#
#     print('========')
#     records= mydb(k1=1,k2=2)
#     mydb.update(records, k1= 3)
#     print('records', mydb.records)  # records {0: {'k1': 3, 'k2': 2, 'v1': 1, 'v2': 300, '__id__': 0, '__version__': 3}}
#     print(mydb.indices)  # {'k1': {3: [0]}, 'k2': {2: [0]}, 'v1': {1: [0]}}


