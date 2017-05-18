import inspect
import itertools

import pydblite

from core.clock import clock
from core.data_structure import DictDecorator, LazyIter, top, Bind


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
        self._primary= ()

    def insert(self, *args, **kw):
        raise RuntimeError('insert 被禁用, 请使用 access')

    def ids(self):
        for _id in self.records:
            yield _id

    def fromIds(self, ids):
        for _id in ids:
            yield self[_id]  # FIXME 要不要返回 AccessRecord

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
        # return LazyIter( self.fromIds(res) )  # LazyIter 惰性生成列表 FIXME
        return list( self.fromIds(res) )

    def keyIndex(self, field, value)->list:  # list[_id, ...]
         if inspect.isfunction(value):  # 表达式
            _ids= []
            for key, ids in self.indices[field].items():  # 遍历索引键
                if value(key):
                    _ids += ids
            return _ids
         else:
            return self.indices[field].get(value, [])

    def keyFilter(self, field, value, ids_iter)->filter:
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

        primarys= dict(zip(self._primary, keys))
        record= self._find(primarys)
        if record is None:  # 插入
            kwargs.update(primarys)  # 注意, 是更新kwargs, 而非更新primarys
            record= self._insert(kwargs)
        else:
            self._update(record, kwargs)
        return self.AccessRecord(record, self)

    def _insert(self, kwargs)->dict:
        _id= super().insert(**kwargs)
        return self[_id]

    def _update(self, record, kwargs)->None:
        if kwargs:
            super().update(record, **kwargs)

    def _find(self, primarys)->dict or None:
        if not primarys:
            return None
        else:
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

# if __name__ == '__main__':
#     from constants import INF
#     mydb = DataBaseTable()
#     mydb.create('k1', 'k2', v1=0, v2=0)
#     mydb.create_index('v1')
#
#
#     mydb.access(1,1, v1=100, v2=INF)
#
#     rs= mydb(v1= lambda v:v==100, v2=INF)
#     for r in rs:
#         print(r)


if __name__ == '__main__':
    from constants import INF
    mydb = DataBaseTable()
    mydb.create('k1', 'k2', v1=0, v2=0)
    mydb.create_index('v1')


    mydb.access(0, 'hello', v1=100, v2=INF)
    mydb.access(1, 'hello', v1=99, v2=INF)

    rs= mydb(k2='hello', v1= lambda v1:v1>=100)
    for r in rs:
        print(r)

# ======================================================================================================================

from core.common import Hardware, singleton


# @singleton
class AnnounceTableLog(DataBaseTable):
    def __init__(self, path=':memory:'):
        super().__init__(path)
        self.order_iter= itertools.count()

        self.create(order= -1, step=None, hardware='', action='', args= '')
        self.create_index('step', 'hardware')
        self.file= open(f'C:\\Users\\bupt632\\Desktop\\LICNsim\\AnnounceTableLog.txt', 'w')  # DEBUG

    def addAnnounceTable(self, label, announces):
        announces.logger.append(Bind(self._write, label))

    def addHardwares(self, seq):  # 过于耦合
        for hardware in seq:
            if isinstance(hardware, Hardware):
                hardware.announces.logger.append(Bind(self._write, hardware.name))

    def _write(self, hardware, action, *args):
        order= next(self.order_iter)
        self.access( order= order, step= clock.time(), hardware=hardware, action= action, args= str(args) )

        string= f'{order}:\t[{clock.time()}] {hardware}.{action}{args}\n'
        print(string, end='')  # debug
        self.file.write(string) # debug

























