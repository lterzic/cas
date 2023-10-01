from typing import List, Union
from head import Head, HeadAttributes, HeadPrintFormat, Attribute, HeadArgNumber

ExprArgType = Union['Expr', str, int]


class Expr:
    def __init__(self, head: Head, args: List[ExprArgType] = [], attr: List[Attribute] = []):
        self.head = head
        self.args = args[:]
        self.attr = set(HeadAttributes[self.head] + attr)

        for i in range(len(self.args)):
            from atom import atomize
            self.args[i] = atomize(self.args[i])
            assert isinstance(self.args[i], Expr)

        if Attribute.FIXED_ARG_NUM in self.attr:
            assert len(self.args) == HeadArgNumber[self.head]

        if Attribute.ASSOCIATIVE in self.attr and Attribute.NO_FLATTEN not in self.attr:
            self.flatten()

        if Attribute.COMMUTATIVE in self.attr:
            self.args.sort(key=lambda x: hash(x))

    def flatten(self, force=False, copy=False, recursive=False):
        assert Attribute.ASSOCIATIVE in self.attr or force

        result = self.copy() if copy else self

        i = 0
        while i < len(result.args):
            if isinstance(result.args[i], Expr) and result.args[i].head is self.head:
                arg_len = len(result.args[i].args)
                result.args[i:i+1] = result.args[i].args
                i += arg_len - 1 if not recursive else -1
            i += 1

        return result

    def copy(self):
        from copy import copy
        obj_copy = copy(self)
        obj_copy.args = obj_copy.args[:]
        obj_copy.attr = obj_copy.attr[:]
        return obj_copy

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        if self.head is not other.head:
            return False
        if len(self.args) is not len(other.args):
            return False
        for i in range(len(self.args)):
            if self.args[i] != other.args[i]:
                return False
        return True

    def __hash__(self):
        return hash((self.head, *self.args))

    def __full__(self):
        return str(self.head) + '(' + ','.join(i.__full__() for i in self.args) + ')'

    def __str__(self):
        if self.head in HeadPrintFormat:
            return HeadPrintFormat[self.head](self.args)
        else:
            return self.__full__()

    def __add__(self, other):
        return Expr("Plus", [self, other])

    def __radd__(self, other):
        return Expr.__add__(self, other)

    def __mul__(self, other):
        return Expr("Mult", [self, other])

    def __rmul__(self, other):
        return Expr.__mul__(self, other)

    def __pow__(self, other, modulo=None):
        return Expr("Power", [self, other])

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, other):
        from atom import atomize
        from nums import Integer
        return self * (atomize(other) ** Integer(-1))
