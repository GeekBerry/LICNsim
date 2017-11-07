from pydblite.pydblite import _BasePy3 as PyDataBase
from core import decorator


class DataBaseTable:
    class Record( decorator(dict) ):
        def __init__(self, record, data_base):
            super().__init__(record)
            self.__data_base= data_base

        def __setitem__(self, key, value):
            # XXX 调用'_inner', 使得只更新内核,以免循环调用
            self.__data_base._setitem(self._inner, key, value)

        def isMatch(self, **kwargs)->bool:
            """
            返回该条记录是否符合检查条件,(且)的关系
            :param kwargs:dict{field:value, ...} 匹配条件

            >>> record= Record( {'name':'Tom', 'age':20, 'score':100} )
            >>> record.isMatch( age= lambda num: 18<=num, score=100 )
            True
            """
            for field, condition in kwargs.items():
                if callable(condition):
                    if not condition(self[field]):
                        return False
                else:
                    if self[field] != condition:
                        return False
            return True

    """
    records 数据结构:
    {
        id1: {'__id__': id1, '__version__':int, 'field1':Any, ...},
        ...
    }

    indices 数据结构:
    {
        field1:
        {
            var1: [id1, id2, ...],  # pydblite 在此没有使用 set
            ...
        },
        ...
    }
    """
    def __init__(self, path=':memory:', mode='override'):
        """
        创建一个数据库表
        :param path:str 数据库路径, ':memory:'代表内存数据库
        :param mode:str 打开模式
        - if mode = 'create' : create a new base (the default value)
        - if mode = 'open' : open the existing base, ignore the fields
        - if mode = 'override' : erase the existing base and create a
        """
        self.dblite= PyDataBase(path=path)
        self.mode= mode
        self.primary_keys= []  # [filed_name, ...]
        self.key_table= {}  # {primary_key:id}

    def create(self, *primary_keys, **value_dict):
        """
        创建一个数据库表
        :param primary_keys: [str, ...] 主键列表
        :param value_dict: 其他域字典
        :return: self

        >>> db_t= DataBaseTable().create('k1', 'k2', v1=0) # 不带默认值的为主键;  k1, k2 为主键
        """
        self.dblite.create(*primary_keys, *list(value_dict.items()), mode= self.mode)
        self.dblite.create_index(*primary_keys)
        self.primary_keys= primary_keys
        return self

    def createIndexs(self, *fields):
        self.dblite.create_index(*fields)

    def getFields(self):
        return self.dblite.fields

    def addFields(self, **value_dict):
        for field, default in value_dict.items():
            self.dblite.add_field(field, default= default)

    # -------------------------------------------------------------------------
    def __setitem__(self, keys, field_dict:dict):
        """
        插入或更新一个项
        :param key: tuple 或 Var 主键
        :param field_dict:dict
        :return:None

        >>> db_table= DataBaseTable('position', city=0, year=1970)
        >>> db_table[121.45, 95.3]= {'city':'Beijing'}  # 注意, 当主键只有一个值时, 索引 tuple 会视为一个项
        >>> db_table.dblite.records
        {0: {'position': (121.45, 95.3), 'city': 'Beijing', 'year': 1970,  '__id__': 0, '__version__': 0}}

        >>> db_table= DataBaseTable('name', 'age', score=0)
        >>> db_table['Jim', 18]= {}  # 注意, 当主键有多个时, 索引 tuple 会分配到多个项
        >>> db_table.dblite.records
        {0: {'name': 'Jim', 'age': 18, 'score': 0, '__id__': 0, '__version__': 0}}
        """
        assert isinstance(field_dict, dict)

        if keys in self.key_table:
            rcd_id= self.key_table[keys]
            record= self.dblite[rcd_id]
            self.__update(record, field_dict)
        else:
            rcd_id= self.__insert(keys, field_dict)
            self.key_table[keys]= rcd_id  # 注册key_table

    def __getitem__(self, keys):
        """
        获得一个项, 如果不存在, 则插入一个默认项
        :param key: tuple 或 Var 主键
        :return: DataBaseTable.Record

        >>> db_table= DataBaseTable('name', 'age', score=0, addr='')
        >>> record= db_table['Tom', 19]
        >>> record
        Record({'name': 'Tom', 'age': 19, 'score': '0', 'addr': '', '__id__': 0, '__version__': 0})

        >>> db_table['Jerry', 12]['score']+= 1
        >>> db_table.data_base.records
        {0: {'name': 'Jerry', 'age': 12, 'score': 1, 'addr': '', '__id__': 0, '__version__': 0}}
        """
        if keys in self.key_table:
            rcd_id= self.key_table[keys]
        else:
            rcd_id= self.__insert(keys, {})
            self.key_table[keys]= rcd_id  # 注册key_table

        return self.Record(self.dblite[rcd_id], data_base=self)

    def __delitem__(self, keys):
        assert keys in self.key_table  # 没在主键索引表中的一定不在数据库中
        rcd_id= self.key_table.pop(keys)
        del self.dblite[rcd_id]

    # -------------------------------------------------------------------------
    def __insert(self, keys, field_dict:dict):
        if len(self.primary_keys) == 0:
            raise KeyError('没有主键, 不能索引')
        elif len(self.primary_keys) == 1:  # 主键只有一个, key 即主键
            key_dict= {self.primary_keys[0]:keys}
        else:  # 主键有多个, key 是主键tuple, 需要将其展开
            key_dict= dict(zip(self.primary_keys, keys))

        field_dict.update(key_dict)   # 注意更新 field_dict 以保证主键来自 key
        return self.dblite.insert(**field_dict)

    def __update(self, record, field_dict):
        if set(self.primary_keys) & field_dict.keys():
            p_k= ','.join( set(self.primary_keys) & field_dict.keys() )
            raise ValueError(f'{p_k} 是主键, 不能修改')
        self.dblite.update(record, **field_dict)

    def _setitem(self, record, key, value):  # 设置 record 的一个属性值
        if key in self.primary_keys:
            raise ValueError(f'{key} 是主键, 不能修改')

        if key in self.dblite.indices:
            self.dblite.update(record, **{key:value})
        else:  # XXX 优化项目: 非索引项, 直接修改
            record[key]= value
            # record["__version__"] += 1 XXX 需要吗 ???

    # -------------------------------------------------------------------------
    def query(self, **condition_dict):
        """
        查询操作, 支持条件查询
        :param condition_dict:
        :return: yield Record

        >>> db_table= DataBaseTable('name', 'age', score=0, city='')
        >>> db_table['A', 23]= {'score':100, 'city':'BJ'}
        >>> db_table['B', 17]= {'score':90, 'city':'SH'}
        >>> db_table['C', 20]= {'score':59, 'city':'SH'}
        >>> db_table['D', 28]= {'score':40, 'city':'BJ'}

        >>> list(  db_table.query(city= 'BJ')  )
        [Record({'name': 'A', 'age': 23, 'score': 100, 'city': 'BJ', '__id__': 0, '__version__': 0}),
        Record({'name': 'D', 'age': 15, 'score': 40, 'city': 'BJ', '__id__': 3, '__version__': 0})]

        >>> list(  db_table.query(age= lambda age: 18<=age<25, city='SH')  )
        [Record({'name': 'C', 'age': 20, 'score': 59, 'city': 'SH', '__id__': 2, '__version__': 0})]

        >>> list(  db_table.query(age= lambda age: 25<age, score= lambda num: 60<num) )  )
        []

        已知Bug: 返回值Bug
        lst= []
        for i in range(...):
            records= self.query(与 i 有关的查询)  # 返回值是一个生成器
            lst.append(records)
        此时 lst 所有成员都是最后一次的查询结果
        """
        # 对有索引的项, 进行集合析取
        index_fields = condition_dict.keys() & set(self.dblite.indices.keys())
        indexed_conditions= {field:condition_dict[field] for field in index_fields}

        find_ids= self._matchedIndexedIds(indexed_conditions)
        if find_ids is None:
            find_ids= self.dblite.records.keys()

        # 对无索引的项, 进行遍历过滤
        ordinary_fields= condition_dict.keys() - index_fields
        ordinary_conditions= {field:condition_dict[field] for field in ordinary_fields}

        for record in map(self.dblite.records.__getitem__, find_ids):
            if self.Record.isMatch(record, **ordinary_conditions):
                yield self.Record(record, self)
        # FIXME 见 __doc__ 中已知bug

    def _matchedIndexedIds(self, condition_dict):
        """
        找到符合 condition_dict (交集)的所有 Ids, 其中condition_dict的主键必须为建立的索引项
        :param condition_dict: {indexed_filed_name:condition}
        :return: set(ids) or None
        """
        ids= None
        for field, condition in condition_dict.items():
            if ids is None:  # 用于生成第一个id 的 set()
                ids= self._filterIndexedIds(field, condition)
            elif len(ids) > 0:
                ids &= self._filterIndexedIds(field, condition)
            else: break  # ids 是空集合, 不再向下比较
        return ids

    def _filterIndexedIds(self, field, condition)->set:
        """
        找到 field 符合 condition 的所有 r_id
        :param field:str 域名
        :param condition: callable 或 Var
        :return:set(r_id)

        设 self.indices
        {
            k1:
            {
                0:  [Id_1,  Id_2,  ...],
                10: [Id_11, Id_12, ...],
                100:[Id_21, Id_22, ...],
                ...
            },
            ...
        }
        >>> self._filterIndexedIds('k1', 10)
        {Id_11, Id_12}
        >>> self._filterIndexedIds('k1', lambda k:k<50)
        {Id_11, Id_12, Id_21, Id_22,}
        """
        if callable(condition):
            find_ids= set()
            for var, ids in self.dblite.indices[field].items():
                if condition(var):
                    find_ids.update(ids)
            return find_ids
        else:  # condition 是一个值, 直接查找对应ids, 并转化为set
            return set(self.dblite.indices[field].get(condition, set()))

    # -------------------------------------------------------------------------
    def minIter(self, field):
        if field in self.dblite.indices:
            var_keys = self.dblite.indices[field]
            for var in sorted( var_keys.keys() ):
                for rcd_id in var_keys[var]:
                    yield self.Record(self.dblite[rcd_id], data_base=self)
        else:
            raise NotImplementedError('没有实现对非索引项的遍历')



if __name__ == '__main__':
    db_table= DataBaseTable().create('name', 'age', score=0, city='') # 不带默认值的为主键;  k1, k2 为主键

    db_table['A', 23]= {'score':100, 'city':'BJ'}
    db_table['B', 17]= {'score':90, 'city':'SH'}
    db_table['C', 20]= {'score':59, 'city':'SH'}
    db_table['D', 28]= {'score':40, 'city':'BJ'}

    p= list( db_table.query(city= 'BJ') )
    print(p)
    # [Record({'name': 'A', 'age': 23, 'score': 100, 'city': 'BJ', '__id__': 0, '__version__': 0}),
    # Record({'name': 'D', 'age': 15, 'score': 40, 'city': 'BJ', '__id__': 3, '__version__': 0})]

    p= list( db_table.query(age= lambda age: 18<=age<25, city='SH') )
    print(p)
    # [Record({'name': 'C', 'age': 20, 'score': 59, 'city': 'SH', '__id__': 2, '__version__': 0})]

    p= list( db_table.query(age= lambda age: 25<age, score= lambda num: 60<num) )
    print(p)
    # []

    p= list( db_table.query() )
    print(p)
    # [Record({'name': 'A', 'age': 23, 'score': 100, 'city': 'BJ', '__id__': 0, '__version__': 0}), Record({'name': 'B', 'age': 17, 'score': 90, 'city': 'SH', '__id__': 1, '__version__': 0}), Record({'name': 'C', 'age': 20, 'score': 59, 'city': 'SH', '__id__': 2, '__version__': 0}), Record({'name': 'D', 'age': 28, 'score': 40, 'city': 'BJ', '__id__': 3, '__version__': 0})]































