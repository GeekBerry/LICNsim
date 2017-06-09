from core import DictDecorator
from pydblite.pydblite import _BasePy3 as PyDataBase


class DataBaseTable:
    class Record(DictDecorator):
        def __init__(self, record, data_base):
            super().__init__(record)
            self.__data_base= data_base

        def __setitem__(self, key, value):
            # XXX 调用'_inside_', 使得只更新内核,以免循环调用
            self.__data_base._setitem(self._inside_, key, value)

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
            var1: [id1, id2, ...],  # pydblite 在此没有使用set
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
        self.db_table= PyDataBase(path=path)
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
        self.db_table.create(*primary_keys, *list(value_dict.items()), mode= self.mode)
        self.db_table.create_index(*primary_keys)
        self.primary_keys= primary_keys
        return self

    def create_index(self, *fields):
        self.db_table.create_index(*fields)

    # -------------------------------------------------------------------------
    def __setitem__(self, key, field_dict):
        """
        插入或更新一个项
        :param key: tuple 或 Var 主键
        :param field_dict:dict
        :return:None

        >>> db_table= DataBaseTable('position', city=0, year=1970)
        >>> db_table[121.45, 95.3]= {'city':'Beijing'}  # 注意, 当主键只有一个值时, 索引 tuple 会视为一个项
        >>> db_table.db_table.records
        {0: {'position': (121.45, 95.3), 'city': 'Beijing', 'year': 1970,  '__id__': 0, '__version__': 0}}

        >>> db_table= DataBaseTable('name', 'age', score=0)
        >>> db_table['Jim', 18]= {}  # 注意, 当主键有多个时, 索引 tuple 会分配到多个项
        >>> db_table.db_table.records
        {0: {'name': 'Jim', 'age': 18, 'score': 0, '__id__': 0, '__version__': 0}}
        """
        assert isinstance(field_dict, dict)

        if key in self.key_table:
            r_id= self.key_table[key]
            record= self.db_table[r_id]
            self.__update(record, field_dict)
        else:
            self.__insert(key, field_dict)

    def __getitem__(self, key):
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
        {0: {'name': 'Jerry', 'age': 12, 'score': 1, 'addr': '', '__id__': 0, '__version__': 1}}
        """
        if key in self.key_table:
            r_id= self.key_table[key]
        else:
            r_id= self.__insert(key)
        record= self.db_table[r_id]
        return self.Record(record, data_base=self)

    def __delitem__(self, key):
        if key in self.key_table:
            r_id= self.key_table.pop(key)
            del self.db_table[r_id]
        # else 没在主键索引表中的一定不在数据库中

    # -------------------------------------------------------------------------
    def __insert(self, key, field_dict=None):
        if len(self.primary_keys) == 0:
            raise KeyError('没有主键, 不能索引')
        elif len(self.primary_keys) == 1:
            key_dict= {self.primary_keys[0]:key}
        else:
            key_dict= dict(zip(self.primary_keys, key))
        # 更新field_dict
        if field_dict is None:
            field_dict= {}
        field_dict.update(key_dict)   # 注意, 是更新 field_dict
        # 插入和注册
        r_id= self.db_table.insert(**field_dict)
        self.key_table[key]= r_id  # 注册key_table
        return r_id

    def __update(self, record, field_dict):
        if set(self.primary_keys) & field_dict.keys():
            p_k= ','.join( set(self.primary_keys) & field_dict.keys() )
            raise ValueError(f'{p_k} 是主键, 不能修改')
        self.db_table.update(record, **field_dict)

    def _setitem(self, record, key, value):  # 设置 record 的一个属性值
        if key in self.primary_keys:
            raise ValueError(f'{key} 是主键, 不能修改')

        if key in self.db_table.indices:
            self.db_table.update(record, **{key:value})
        else:  # XXX 优化项目: 非索引项, 直接修改
            record[key]= value
            record["__version__"] += 1

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
        """
        # 对有索引的项, 进行集合析取
        index_fields = condition_dict.keys() & set(self.db_table.indices.keys())
        indexed_conditions= {field:condition_dict[field] for field in index_fields}

        find_ids= self._matchedIndexedIds(indexed_conditions)
        if find_ids is None:
            find_ids= self.db_table.records.keys()

        # 对无索引的项, 进行遍历过滤
        ordinary_fields= condition_dict.keys() - index_fields
        ordinary_conditions= {field:condition_dict[field] for field in ordinary_fields}

        for record in map(self.db_table.records.__getitem__, find_ids):
            if self.Record.isMatch(record, **ordinary_conditions):
                # yield record  # FIXME 不能返回 Record(record, self); 否则 list( self.query() ) 为[{}, {}, ...]
                yield self.Record(record, self)

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
                0: [Id_1, Id_2, ...],
                10: [Id_11, Id_12, ...],
                100: [Id_21, Id_22, ...],
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
            for var, ids in self.db_table.indices[field].items():
                if condition(var):
                    find_ids.update(ids)
            return find_ids
        else:  # condition 是一个值, 直接查找对应ids, 并转化为set
            return set(self.db_table.indices[field].get(condition, []))


# if __name__ == '__main__':
#
#     db_table= DataBaseTable('name', 'age', score=0, city='')
#
#     db_table['A', 23]= {'score':100, 'city':'BJ'}
#     db_table['B', 17]= {'score':90, 'city':'SH'}
#     db_table['C', 20]= {'score':59, 'city':'SH'}
#     db_table['D', 28]= {'score':40, 'city':'BJ'}
#
#     p= list( db_table.query(city= 'BJ') )
#     # print(p)
#     # [Record({'name': 'A', 'age': 23, 'score': 100, 'city': 'BJ', '__id__': 0, '__version__': 0}),
#     # Record({'name': 'D', 'age': 15, 'score': 40, 'city': 'BJ', '__id__': 3, '__version__': 0})]
#
#     p= list( db_table.query(age= lambda age: 18<=age<25, city='SH') )
#     print(p)
#     # [Record({'name': 'C', 'age': 20, 'score': 59, 'city': 'SH', '__id__': 2, '__version__': 0})]
#
#     p= list( db_table.query(age= lambda age: 25<age, score= lambda num: 60<num) )
#     print(p)
#     # []


# XXX TEST
# ======================================================================================================================
# from collections import defaultdict
#
#
# class DataBase:
#     SUFFIX= 'db_t'
#     def __init__(self, folder=None, mode='override'):
#         """
#         :param folder:str 文件夹路径
#         :param mode:
#         - if mode = 'create' : create a new base (the default value)
#         - if mode = 'open' : open the existing base, ignore the fields
#         - if mode = 'override' : erase the existing base and create a
#         """
#         self.folder= folder
#         self.mode= mode
#         self.tables= {}
#
#     def _createTable(self, table_name):
#         if self.folder:
#             path= f'{self.folder}/{table_name}.{self.SUFFIX}'
#         else:
#             path= ':memory:'
#         return DataBaseTable(path, self.mode)
#
#     def __getitem__(self, table_name:str):
#         db_table= self.tables.get(table_name, None)
#
#         if db_table is None:
#             db_table= self.tables[table_name]= self._createTable(table_name)
#
#         return db_table
#
#
# if __name__ == '__main__':
#     db= DataBase()
#     db['person_t'].create('name', age=18)
#
#     db['person_t']['Tom']['age'] += 1
#
#     print( db['person_t'].db_table.records )
#     # {0: {'name': 'Tom', 'age': 19, '__id__': 0, '__version__': 1}}
































