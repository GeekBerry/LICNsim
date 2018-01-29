import re, sys

REGULAR_TYPE = type(re.compile(''))


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
        #  TODO 可以在此函数做 cache: { (index, symbol):result, ...}
        index = self.index

        result = symbol.match(self)
        if result is not None:  # 使得 func 不用处理 None
            result = symbol.func(result)

        if result is None:  # 解析失败
            self.index = index

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
def sym(*args, name=None, func=None):
    # 生成 arg
    if len(args) > 1:
        arg = args  # type(arg) is tuple
    elif len(args) < 0:
        arg = None
    else:
        arg = args[0]

    # 依据 arg 生成 symbol
    if type(arg) is SymbolKey:
        assert name is None and func is None
        return arg
    elif isinstance(arg, Symbol):
        assert name is None and func is None
        return arg
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

    if name is not None:
        symbol.name = name

    if func is not None:
        symbol.func = func

    return symbol


class Symbol:
    name = ''

    def __mul__(self, arg):
        if type(arg) is tuple:
            assert len(arg) == 2  # 两个数值，起始到结束
            return SymbolRepeat(self, *arg)

        if type(arg) is int:
            return SymbolRepeat(self, arg, arg)

        raise ValueError(f'未知参数{arg}')

    def __hash__(self):
        return id(self)

    def __add__(self, other):
        return SymbolAll(self, sym(other))

    def __or__(self, other):
        return SymbolAny(self, sym(other))

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


class SymbolString(Symbol):
    def __init__(self, string):
        self.string = string

    def match(self, stream):
        result = stream.string[stream.index: stream.index + len(self.string)]
        if result == self.string:
            stream.index += len(self.string)
            return result
        else:
            return None

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
        results = []
        for each in self.seq:
            result = stream.parser(each)
            if result is not None:
                results.append(result)
            else:
                return None
        return results

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
            result = stream.parser(each)
            if result is not None:
                return result
        return None

    def __str__(self):
        return f'[{ "|".join( map(repr, self.seq) ) }]'


class SymbolRepeat(Symbol):
    def __init__(self, symbol, least, most):
        self.symbol = symbol
        self.least = least
        self.most = most

    def match(self, stream):
        results = []
        while (self.most is ...) or (len(results) < self.most):
            result = stream.parser(self.symbol)
            if result is not None:
                results.append(result)
            else:
                break
        return results if len(results) >= self.least else None

    def __str__(self):
        most = "..." if self.most is ... else self.most
        return f'{self.symbol}*({self.least},{most})'


class SymbolException(Symbol):
    name = 'EXCEPT'

    def __init__(self, exception):
        self.exception = exception

    def match(self, stream):
        if isinstance(stream, DebugStream):  # 是 debug 模式
            expect_str = list()
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


# ==========================================================================================
class SymbolKey(str):  # 非终结符占位符
    pass


class SymbolTable(dict):
    def __setitem__(self, key, value):
        assert type(value) is not SymbolKey  # 不能直接使用未绑定符号

        symbol = sym(value)
        if not symbol.name:
            symbol.name = key
        if hasattr(self, key):  # 查找对应的翻译函数
            symbol.func = getattr(self, key)
        super().__setitem__(key, symbol)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            return SymbolKey(item)  # 创建一个引用

    def backfill(self):
        self.__checked_seq = set()
        for key, each in self.items():
            self[key] = self._check(each)
        del self.__checked_seq

    def _check(self, symbol) -> Symbol:
        if type(symbol) is SymbolKey:
            return self[symbol]

        assert isinstance(symbol, Symbol)
        if symbol not in self.__checked_seq:
            self.__checked_seq.add(symbol)

            if type(symbol) is SymbolRepeat:
                symbol.symbol = self._check(symbol.symbol)
            elif type(symbol) in (SymbolAll, SymbolAny):
                for i, each in enumerate(symbol.seq):
                    symbol.seq[i] = self._check(each)
            else:
                pass  # 终结符

        return symbol


# ==========================================================================================
if __name__ == '__main__':
    class CaluParser(SymbolTable):  # 正整数加减乘除计算器
        def __init__(self):
            # 终结符
            ends = sym(re.compile('\s*'), name='ends')
            integer = sym(re.compile(r'[0-9]+'), name='integer', func=int)
            # 非终结符
            self['Start'] = ends, self['Expr'], ends
            self['Expr'] = self['Term'], sym(ends, ['+', '-'], ends, self['Term']) * (0, ...)
            self['Term'] = self['Fact'], sym(ends, ['*', '/'], ends, self['Fact']) * (0, ...)
            self['Fact'] = sym('(', ends, self['Expr'], ends, ')') | integer | Exception('expect Fact')
            self.backfill()  # 回填地址

        def Start(self, match):
            return match[1]  # Start -> Ends Var Ends

        def Expr(self, match):
            var, vars = match
            for each in vars:  # [ends, + or -, ends, Fact]
                if each[1] == '+':
                    var += each[3]
                if each[1] == '-':
                    var -= each[3]
            return var

        def Term(self, match):
            var, vars = match
            for each in vars:  # [ends, * or /, ends, Fact]
                if each[1] == '*':
                    var *= each[3]
                if each[1] == '/':
                    var /= each[3]
            return var

        def Fact(self, match):
            if type(match) is list:  # Var -> ( Ends AddSub Ends )
                return match[2]
            else:  # Var -> Int
                return match


    s = DebugStream(' 1 / 2 * 3 ', )  # log_stream=sys.stdout
    parser = CaluParser()

    p = s.parser(parser['Start'])
    print(p, s.eof())  # 1.5 True
