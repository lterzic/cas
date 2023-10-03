from expr import Expr
from head import Head


class Atom(Expr):
    def __init__(self, head: Head):
        super().__init__(head, args=[], attr=[])

    def __full__(self):
        return self.__str__()

    def __str__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError


class String(Atom):
    def __init__(self, text: str):
        super().__init__("String")
        self.text = text

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return type(other) is String and self.text == other.text

    def __hash__(self):
        return hash((self.head, self.text))


class Symbol(Atom):
    def __init__(self, text: str):
        super().__init__("Symbol")
        assert " " not in text
        self.text = text

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return type(other) is Symbol and self.text == other.text

    def __hash__(self):
        return hash((self.head, self.text))


class Boolean(Atom):
    def __init__(self, value: bool):
        super().__init__("Boolean")
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return type(other) is Boolean and self.value == other.value

    def __hash__(self):
        return hash((self.head, self.value))


TRUE = Boolean(True)
FALSE = Boolean(False)


def symbols(text: str):
    from rule import Blank
    return ((Blank(c[1:]) if c[0] is '_' else Symbol(c)) for c in text.split(" ") if len(c) > 0)


def atomize(primitive):
    if isinstance(primitive, Expr):
        return primitive

    from nums import Integer, Real, Complex

    if type(primitive) is str:
        return String(primitive)
    elif type(primitive) is bool:
        return Boolean(primitive)
    elif type(primitive) is int:
        return Integer(primitive)
    elif type(primitive) is float:
        return Real(primitive)
    elif type(primitive) is complex:
        return Complex(primitive.real, primitive.imag)

    raise "Primitive not atomizable"


def is_numeric(expr: Expr):
    from nums import Integer, Rational, Real, Complex
    return type(expr) in (Integer, Rational, Real, Complex)