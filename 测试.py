

class A:
    def __init__(self, arg1):
        print('A', arg1)
        pass


class B:
    def __init__(self, arg2, arg3):
        print('B', arg2, arg3)
        pass


class X(A, B):
    def __init__(self, arg1, arg2, arg3):
        A.__init__(self, arg1)
        B.__init__(self, arg2, arg3)


x= X(1,2, 3)

