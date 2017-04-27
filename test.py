


from core.data_structure import decoratorOfType

class MyDict(dict):
    def myFoo(self):
        print('myFoo')


class DictDecorator(decoratorOfType(MyDict)):
    def __len__(self):
        return len(self._inside_)+1

    def __setattr__(self, key, value):
        self[key]= value

    def __getattr__(self, item):
        return self[item]



core= MyDict()

table= DictDecorator(core)

table.myFoo()

table['A']= 100

print( table.A )

table.B= 200

print( table['B'] )


print(core)

print( len(table), len(core) )
print( id(table), id(core) )

print( isinstance(table, dict) )


