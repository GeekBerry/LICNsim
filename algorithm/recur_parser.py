import re, sys
REGULAR_TYPE = type(re.compile(''))


def cond(func, iterable, end=None, most=None) -> list:
    """
    将func作用于iterable上，生成列表，但遇到第一个None结果时，列表生成结束
    >>> cond(lambda x:x, [1,2,None,3])
    [1,2]
    :param func:
    :param iterable:
    :return: list
    """
    result = []
    for each in map(func, iterable):
        if each != end:
            result.append(each)
        else:
            break

        if (most is not None) and (len(result) >= most):
            break

    return result


# =============================================================================
class Stream:
    def __init__(self, string, begin=0, end=None):
        self.string = string
        self.begin= begin
        self.index = begin
        self.end = len(string) if end is None else end

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < self.end:
            char = self.string[self.index]
            self.index += 1
            return char
        else:
            raise StopIteration

    def eof(self):
        return self.index >= self.end

    def parser(self, symbol):
        save_index = self.index
        #  TODO 可以在此 cache, { (index, symbol):result, }
        match = symbol.match(self)
        if match is None:
            self.index = save_index
            result= None
        else:
            result = symbol.reduce(match)
        return result


class DebugStream(Stream):
    def __init__(self, string, begin=0, end=None, log_stream= sys.stdout):
        super().__init__(string, begin, end)

        self.log_stream= log_stream
        self.stack= []  # [symbol, ...]

    def parser(self, symbol):
        self.log_stream.write(f'{"    "*len(self.stack)}<{symbol.name}, sym={symbol}, behind="{self.behind()}">\n')
        self.stack.append(symbol)
        result= super().parser(symbol)
        self.stack.pop(-1)
        self.log_stream.write(f'{"    "*len(self.stack)}</{symbol.name}, result={repr(result)}">\n')
        return result

    def before(self, count=40):
        return self.string[self.index-count:self.index]

    def behind(self, count=40):
        return self.string[self.index:self.index+count]

# =============================================================================
class Symbol:
    name = ''

    @staticmethod
    def toSymbol(arg):
        if isinstance(arg, Symbol):
            return arg

        if type(arg) is str:
            return SymbolString(arg)

        if type(arg) is tuple:
            return SymbolAll(arg)

        if type(arg) is list:
            return SymbolAny(arg)

        if type(arg) is REGULAR_TYPE:
            return SymbolRegular(arg)

        if arg is None:
            return SymbolEmpty()

        if issubclass(arg, Exception):
            return SymbolException(arg)

        raise Exception(f'未知类型 {type(arg)}')

    def __mul__(self, range_tuple):
        return SymbolRepeats(self, *range_tuple)

    def __add__(self, other):
        sym = Symbol.toSymbol(other)
        return SymbolAll([self, sym])

    def __or__(self, other):
        sym = Symbol.toSymbol(other)
        return SymbolAny([self, sym])

    def match(self, stream):
        raise NotImplementedError

    def reduce(self, result):  # 将 match 的结果映射返回
        return result

    def __repr__(self):
        return self.name if self.name else self.__str__()

    def __str__(self):
        return ''


class SymbolEmpty(Symbol):
    name= 'EMPTY'

    def match(self, stream):
        return ''


class SymbolException(Symbol):
    def __init__(self, ExceptionType):
        self.name= ExceptionType.__name__
        self.ExceptionType= ExceptionType

    def match(self, stream):
        string= []

        if isinstance(stream, DebugStream):
            string.append('\nParserStack(Name:Symbol)\n')
            for i, symbol in enumerate(stream.stack):
                string.append(f'{"    "*i}{symbol.name}: {symbol}\n')

            before= stream.before().replace('\n',r'\n')
            behind= stream.behind().replace('\n',r'\n')
            string.append(f'{before}{behind}\n')
            string.append(f'{" "*len(before)}^\n')

        raise self.ExceptionType(''.join(string))


class SymbolString(Symbol):
    def __init__(self, string):
        self.string = string

    def match(self, stream):
        result = cond(lambda pair: pair[0] if pair[0] == pair[1] else None, zip(self.string, stream))
        result = ''.join(result)
        return result if result == self.string else None

    def __str__(self):
        return repr(self.string)


class SymbolRegular(Symbol):
    def __init__(self, regular):
        self.regular = regular

    def match(self, stream):
        result = self.regular.match(stream.string, stream.index, stream.end)
        if result is not None:
            result = result.group()
            stream.index += len(result)
        return result

    def __str__(self):
        return f"re'{ str(self.regular)[12:-2] }'"  # [12:-2] 固定文字取值


class SymbolAll(Symbol):
    def __init__(self, seq):
        self.seq = list(map(Symbol.toSymbol, seq))

    def __add__(self, other):
        sym = Symbol.toSymbol(other)
        self.seq.append(sym)
        return self

    def match(self, stream):
        result = cond(lambda each: stream.parser(each), self.seq)
        return result if len(result) == len(self.seq) else None

    def __str__(self):
        return f"({','.join(map(repr, self.seq))})"


class SymbolAny(Symbol):
    def __init__(self, seq):
        self.seq = list(map(Symbol.toSymbol, seq))

    def __or__(self, other):
        sym = Symbol.toSymbol(other)
        self.seq.append(sym)
        return self

    def match(self, stream):
        for each in self.seq:
            each_rst = stream.parser(each)
            if each_rst is not None:
                return each_rst
        return None

    def __str__(self):
        return f'[{ "|".join( map(repr, self.seq) ) }]'


class SymbolRepeats(Symbol):
    def __init__(self, symbol, least, most):
        self.symbol = symbol
        self.least = least
        self.most = most

    def match(self, stream):
        result = []
        while True:
            each_rst = stream.parser(self.symbol)
            if each_rst is None:
                break
            elif (self.most is not ...) and (len(result) > self.most):
                break
            else:
                result.append(each_rst)
        return result if len(result) >= self.least else None

    def __str__(self):
        most = "..." if self.most is ... else self.most
        return f'{repr(self.symbol)}*({self.least},{most})'


class SymbolRef(Symbol):
    def __init__(self, table, key):
        self.table= table
        self.key= key

    def __getattribute__(self, item):
        table= super().__getattribute__('table')
        key= super().__getattribute__('key')

        symbol= table.get(key)
        if symbol is not None:
            return getattr(symbol, item)
        else:
            raise KeyError(f'{table} 中没有键 {key}')


def sym(*args, name=None):
    if len(args) == 0:
        symbol = Symbol.toSymbol(None)
    elif len(args) == 1:
        symbol = Symbol.toSymbol(args[0])
    else:  # len(args) >= 1:
        symbol = SymbolAll(args)

    if name is not None:
        symbol.name = name

    return symbol


class RecurParser(dict):
    def __setitem__(self, key, value):
        symbol = sym(value, name=key)
        if hasattr(self, key):
            symbol.reduce = getattr(self, key)
        super().__setitem__(key, symbol)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return SymbolRef(self, item)


# ==========================================================================================
if __name__ == '__main__':
    class CaluParser(RecurParser):
        def __init__(self):
            # 终结符
            ends= sym(re.compile('\s*'))
            self['integer']= re.compile(r'[0-9]+')
            # 非终结符
            self['Start'] = ends, self['AddSub'], ends
            self['AddSub']= self['MulDiv'], self['AddSubMore']
            self['AddSubMore']= sym(ends, ['+','-'], ends, self['MulDiv'], self['AddSubMore']) | None
            self['MulDiv']= self['Var'], self['MulDivMore']
            self['MulDivMore']= sym(ends, ['*','/'], ends, self['Var'], self['MulDivMore']) | None
            self['Var']= sym('(', ends, self['AddSub'], ends, ')') | self['integer']

        def integer(self, rst):
            return int(rst)

        def Start(self, rst):
            return rst[1]  # Start -> Ends Var Ends

        def AddSub(self, rst):
            num, more= rst[0], rst[1]
            while more:  # AddSub -> Var [Ends Operate Ends Var AddSubMore]
                if more[1] == '+': num += more[3]
                if more[1] == '-': num -= more[3]
                more= more[4]
            return num

        def MulDiv(self, rst):
            num, more= rst[0], rst[1]
            while more:  # MulDiv -> Var [Ends Operate Ends Var MulDivMore]
                if more[1] == '*': num *= more[3]
                if more[1] == '/': num /= more[3]
                more= more[4]
            return num

        def Var(self, rst):
            if type(rst) is list:  # Var -> ( Ends AddSub Ends )
                return rst[2]
            else:  # Var -> Int
                return rst


    s= DebugStream(' 10 + ( 1 + 2 ) * 4 - 2')
    p = s.parser( CaluParser()['Start'] )
    print(p, s.eof())

