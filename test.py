from ctypes import *
# PyObject

a= 100
# obj= Structure.from_address( id(a) )
# print(obj.__dict__)
#
#
# l= [1,2,3]
#
#
# class PyObject(Structure):
#     _fields_ = [("refcnt", c_size_t),
#                 ("typeid", c_void_p)]
#
# class PyVarObject(PyObject):
#     _fields_ = [("size", c_size_t)]
#
# class PyList(PyVarObject):
#     _fields_ = [("items", POINTER(POINTER(PyObject))),
#                 ("allocated", c_size_t)]
#
#     def print_field(self):
#         print( self.size, self.allocated, byref(self.items[0]) )
#
#
# alist_obj = PyList.from_address(id(l))
# alist_obj.print_field()
#
# for x in range(100):
#     alist_obj.print_field()
#     l.append(x)

l= []


l.insert(2, 'A')
print(l[0])

