import re, sys

REGULAR_TYPE = type(re.compile(''))


def cond_map(func, iterable, end=None):
    """
    将func 作用于 iterable上，生成列表，但遇到第一个 end 结果时，列表生成结束
    >>> list( cond_map(lambda x:x, [1,2,None,3]) )
    [1,2]
    """
    for each in map(func, iterable):
        if each == end:
            raise StopIteration
        yield each


# =============================================================================
class Stream:
    def __init__(self, string, begin=0, end=None):
        self.string = string
        self.begin = begin
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
        #  TODO 可以在此函数做 cache: { (index, symbol):match, ...}
        index = self.index
        match = symbol.match(self)
        if match is None:
            self.index = index
            result = None
        else:
            result = symbol.func(match)
        return result


class DebugStream(Stream):
    def __init__(self, string, begin=0, end=None, log_stream=None):
        super().__init__(string, begin, end)
        self.log_stream = log_stream
        self.stack = []  # [symbol, ...]

    def parser(self, symbol):
        if self.log_stream:
            self.log_stream.write(f'{"    "*len(self.stack)}<{symbol.name}, sym={symbol}, behind="{self.behind()}">\n')

        self.stack.append(symbol)
        result = super().parser(symbol)
        self.stack.pop(-1)

        if self.log_stream:
            self.log_stream.write(f'{"    "*len(self.stack)}</{symbol.name}, result={repr(result)}">\n')
        return result

    def before(self, count=40):  # 40: 半个dos屏幕宽度
        return self.string[self.index - count:self.index]

    def behind(self, count=40):  # 40: 半个dos屏幕宽度
        return self.string[self.index:self.index + count]


# =============================================================================
def sym(arg, *args, name=None, func=None):
    def toSymbol(arg):
        if type(arg) is RecurParser.SymbolKey:
            return arg

        if isinstance(arg, Symbol):
            symbol = arg
        elif type(arg) is str:
            symbol = SymbolString(arg)
        elif type(arg) is tuple:
            symbol = SymbolAll(*arg)
        elif type(arg) is list:
            symbol = SymbolAny(*arg)
        elif type(arg) is REGULAR_TYPE:
            symbol = SymbolRegular(arg)
        elif arg is None:
            symbol = SymbolEmpty()
        elif isinstance(arg, Exception):
            symbol = SymbolException(arg)
        else:
            raise TypeError(f'未知类型 {type(arg)}')
        return symbol

    symbol = SymbolAll(arg, *args) if args else toSymbol(arg)
    if name is not None:
        symbol.name = name

    if func is not None:
        symbol.func = func

    return symbol


class Symbol:
    name = ''

    def __mul__(self, arg):
        if type(arg) is tuple:
            assert len(arg) == 2
            return SymbolRepeat(self, *arg)

        if type(arg) is int:
            return SymbolRepeat(self, arg, arg)

        raise ValueError(f'未知参数{arg}')

    def __add__(self, other):
        return SymbolAll([self, sym(other)])

    def __or__(self, other):
        return SymbolAny([self, sym(other)])

    def match(self, stream):
        """
        读取流和匹配相应数据
        :param stream: Stream
        :return: Any  通常为str, 只有None代表匹配失败
        """
        raise NotImplementedError

    def func(self, match):  # 将 match 的结果映射返回
        return match

    def __repr__(self):
        return self.name if self.name else self.__str__()


class SymbolEmpty(Symbol):
    name = 'EMPTY'

    def match(self, stream):
        return ''


class SymbolException(Symbol):
    name = 'EXCEPT'

    def __init__(self, exception):
        self.exception = exception

    def match(self, stream):
        if isinstance(stream, DebugStream):  # 是 debug 模式
            expect_str = []
            expect_str.append('\nParserStack(Name: Symbol)\n')
            for i, symbol in enumerate(stream.stack):
                expect_str.append(f'{"    "*i}{symbol.name}: {symbol}\n')

            before = stream.before().replace('\n', r'\n')
            behind = stream.behind().replace('\n', r'\n')
            expect_str.append(f'{before}{behind}\n')
            expect_str.append(f'{" "*len(before)}^\n')

            sys.stderr.write(''.join(expect_str))

        raise self.exception

    def __str__(self):
        return f'{self.exception.__class__.__name__}({"".join(map(repr, self.exception.args))})'


class SymbolString(Symbol):
    def __init__(self, string):
        self.string = string

    def match(self, stream):
        result = cond_map(lambda pair: pair[0] if pair[0] == pair[1] else None, zip(self.string, stream))
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
        return f"re'{ str(self.regular)[12:-2] }'"  # [12:-2] 提取正则字符串部分


class SymbolAll(Symbol):
    def __init__(self, *seq):
        self.seq = list(map(sym, seq))

    def __add__(self, other):
        self.seq.append(sym(other))
        return self

    def match(self, stream):
        result = list(cond_map(lambda each: stream.parser(each), self.seq))
        return result if len(result) == len(self.seq) else None

    def __str__(self):
        return f"({','.join(map(repr, self.seq))})"


class SymbolAny(Symbol):
    def __init__(self, *seq):
        self.seq = list(map(sym, seq))

    def __or__(self, other):
        self.seq.append(sym(other))
        return self

    def match(self, stream):
        for each in self.seq:
            each_match = stream.parser(each)
            if each_match is not None:
                return each_match
        return None

    def __str__(self):
        return f'[{ "|".join( map(repr, self.seq) ) }]'


class SymbolRepeat(Symbol):
    def __init__(self, symbol, least, most):
        self.symbol = symbol
        self.least = least
        self.most = most

    def match(self, stream):
        result = []
        while True:
            each_match = stream.parser(self.symbol)
            if each_match is None:
                break
            elif (self.most is not ...) and (len(result) > self.most):
                break
            else:
                result.append(each_match)
        return result if len(result) >= self.least else None

    def __str__(self):
        most = "..." if self.most is ... else self.most
        return f'{self.symbol}*({self.least},{most})'


# class SymbolRef(Symbol):
#     """
#     用于引用一个还未存在的列表中Symbol(效率低, 尽量少用)
#     为了绑定机制需要，有必要将父类中已有方法和成员重写一遍
#     """
#     def __init__(self, table, key):
#         self.__table = table
#         self._key = key
#
#     @property
#     def __symbol(self):
#         symbol = self.__table.get(self._key)  # 用 get 以避免递归调用
#         if symbol is not None:
#             return symbol
#         else:
#             raise KeyError(f"{self.__table.__class__.__name__} {self.__table.keys()} 中没有 '{self._key}' 项")
#
#     def __getattr__(self, item):
#         return self.__symbol.__getattr__(item)
#
#     @property
#     def name(self):
#         return self.__symbol.name
#
#     def match(self, stream):
#         return self.__symbol.match(stream)
#
#     def func(self, match):
#         return self.__symbol.func(match)
#
#     def __mul__(self, other):
#         return self.__symbol.__mul__(other)
#
#     def __add__(self, other):
#         return self.__symbol.__add__(other)
#
#     def __or__(self, other):
#         return self.__symbol.__or__(other)
#
#     def __str__(self):
#         return self.__symbol.__str__()


# ==========================================================================================
class RecurParser(dict):
    class SymbolKey(str):
        pass

    def __setitem__(self, key, value):
        assert type(value) is not self.SymbolKey  # 不允许 self[Key] = self[一个未绑定Key]

        symbol = sym(value, name=key)
        if hasattr(self, key):  # 查找对应的翻译函数
            symbol.func = getattr(self, key)
        super().__setitem__(key, symbol)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return self.SymbolKey(item)

    def backFill(self):
        self.__checked_seq = set()  # 记录检查过的序列，注意只有序列会被递归检查， 所以只检查序列
        for k, each in self.items():
            if isinstance(each, self.SymbolKey):
                self[k] = self.get(each)
            else:
                self._backFillSymbol(each)

    def _backFillSeq(self, seq):
        if id(seq) in self.__checked_seq:
            return

        for i, each in enumerate(seq):
            if isinstance(each, self.SymbolKey):
                seq[i] = self.get(each)
            else:
                self._backFillSymbol(each)
        self.__checked_seq.add(id(seq))

    def _backFillSymbol(self, symbol):
        assert type(symbol) is not self.SymbolKey
        if type(symbol) in (SymbolAll, SymbolAny):
            self._backFillSeq(symbol.seq)
        elif type(symbol) is SymbolRepeat:
            if isinstance(symbol.symbol, self.SymbolKey):
                symbol.symbol = self.get(symbol.symbol)
        else:  # 终结符
            pass


# ==========================================================================================
if __name__ == '__main__':
    class CaluParser(RecurParser):  # 正整数加减乘除计算器
        def __init__(self):
            # 终结符
            ends = sym(re.compile('\s*'), name='ends')
            integer = sym(re.compile(r'[0-9]+'), name='integer', func=int)
            # 非终结符
            self['Start'] = ends, self['AddSub'], ends
            self['AddSub'] = self['MulDiv'], self['AddSubMore']
            self['AddSubMore'] = sym(ends, ['+', '-'], ends, self['MulDiv'], self['AddSubMore']) | None
            self['MulDiv'] = self['Var'], self['MulDivMore']
            self['MulDivMore'] = sym(ends, ['*', '/'], ends, self['Var'], self['MulDivMore']) | None
            self['Var'] = sym('(', ends, self['AddSub'], ends, ')') | integer | Exception('expect a Var')
            self.backFill()  # 需要回填地址

        def Start(self, match):
            return match[1]  # Start -> Ends Var Ends

        def AddSub(self, match):
            num, more = match[0], match[1]
            while more:  # AddSub -> Var [Ends Operate Ends Var AddSubMore]
                if more[1] == '+': num += more[3]
                if more[1] == '-': num -= more[3]
                more = more[4]
            return num

        def MulDiv(self, match):
            num, more = match[0], match[1]
            while more:  # MulDiv -> Var [Ends Operate Ends Var MulDivMore]
                if more[1] == '*': num *= more[3]
                if more[1] == '/': num /= more[3]
                more = more[4]
            return num

        def Var(self, match):
            if type(match) is list:  # Var -> ( Ends AddSub Ends )
                return match[2]
            else:  # Var -> Int
                return match


    s = DebugStream(' 1+ 2*3', )  # log_stream=sys.stdout
    p = s.parser(CaluParser()['Start'])
    print(p, s.eof())

# print(CaluParser()['AddSubMore'])
