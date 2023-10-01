from typing import Union
from atom import Atom
from math import gcd


# to int add arithmetic when other is int
class Integer(Atom):
    def __init__(self, n: int):
        super().__init__("Integer")
        assert type(n) is int
        self.value = n

    def __eq__(self, other):
        return type(other) is Integer and self.value == other.value

    def __hash__(self):
        return hash((self.head, self.value))

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        if type(other) is int:
            return Integer(self.value + other)
        if type(other) is Integer:
            return Integer(self.value + other.value)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return Integer(-self.value)

    def __sub__(self, other):
        if type(other) is int:
            return Integer(self.value - other)
        if type(other) is Integer:
            return Integer(self.value - other.value)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is int:
            return Integer(self.value * other)
        if type(other) is Integer:
            return Integer(self.value * other.value)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) is int:
            if self.value % other == 0:
                return Integer(self.value // other)
            else:
                return Rational(self, other)
        if type(other) is Integer:
            if self.value % other.value == 0:
                return Integer(self.value // other.value)
            else:
                return Rational(self, other)
        return NotImplemented

    def __pow__(self, other, modulo=None):
        if type(other) is int:
            if other < 0:
                return Rational(1, self.value ** -other)
            else:
                return Integer(self.value ** other)
        if type(other) is Integer:
            if other < 0:
                return Rational(1, self.value ** -other.value)
            else:
                return Integer(self.value ** other.value)
        return NotImplemented

    def __lt__(self, other):
        if type(other) is Integer:
            return self.value < other.value
        elif type(other) is int:
            return self.value < other  # should be used only in this file for internal implementations
        return NotImplemented

    def __gt__(self, other):
        if type(other) is Integer:
            return self.value > other.value
        elif type(other) is int:
            return self.value > other  # should be used only in this file for internal implementations
        return NotImplemented


class Rational(Atom):
    def __init__(self, num: Union[int, Integer], den: Union[int, Integer]):
        super().__init__("Rational")
        self.num = num if type(num) is Integer else Integer(num)
        self.den = den if type(den) is Integer else Integer(den)

        comm_factor = gcd(self.num.value, self.den.value)
        if comm_factor != 1:
            self.num.value //= comm_factor
            self.den.value //= comm_factor

        if self.den < 0:
            self.num *= -1
            self.den *= -1

    def __eq__(self, other):
        return type(other) is Rational and (self.num * other.den == self.den * other.num)

    def __hash__(self):
        return hash((self.head, self.num, self.den))

    def __str__(self):
        return str(self.num) + '/' + str(self.den)

    def __add__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.den + other.num * self.den, self.den * other.den)
        elif type(other) is Integer or type(other) is int:
            return Rational(self.num + other * self.den, self.den)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return Rational(-self.num, self.den)

    def __sub__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.den - other.num * self.den, self.den * other.den)
        elif type(other) is Integer or type(other) is int:
            return Rational(self.num - other * self.den, self.den)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.num, self.den * other.den)
        elif type(other) is Integer or type(other) is int:
            return Rational(self.num * other, self.den)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.den, self.den * other.num)
        elif type(other) is Integer or type(other) is int:
            return Rational(self.num, self.den * other)
        return NotImplemented

    def __pow__(self, other, modulo=None):
        if type(other) is Integer or type(other) is int:
            if other == 0:
                return Integer(1)
            elif other < 0:
                return Rational(self.den ** -other, self.num ** -other)
            else:
                return Rational(self.num ** other, self.den ** other)
        return NotImplemented

    def __lt__(self, other):
        if type(other) is Rational:
            return self.num * other.den < self.den * other.num
        elif type(other) is Integer or type(other) is int:
            return self.num < self.den * other
        return NotImplemented

    def __gt__(self, other):
        if type(other) is Rational:
            return self.num * other.den > self.den * other.num
        elif type(other) is Integer or type(other) is int:
            return self.num > self.den * other
        return NotImplemented


class Real(Atom):
    def __init__(self, r: float):
        super().__init__("Real")
        assert type(r) is float
        self.value = r

    def __eq__(self, other):
        return type(other) is Real and self.value == other.value

    def __hash__(self):
        return hash((self.head, self.value))

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        if type(other) is int or type(other) is float:
            return Real(self.value + other)
        if type(other) is Integer or type(other) is Real:
            return Real(self.value + other.value)
        if type(other) is Rational:
            return Real(self.value + other.num / other.den)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return Real(-self.value)

    def __sub__(self, other):
        if type(other) is int or type(other) is float:
            return Real(self.value - other)
        if type(other) is Integer or type(other) is Real:
            return Real(self.value - other.value)
        if type(other) is Rational:
            return Real(self.value - other.num / other.den)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is int or type(other) is float:
            return Real(self.value * other)
        if type(other) is Integer or type(other) is Real:
            return Real(self.value * other.value)
        if type(other) is Rational:
            return Real(self.value * other.num / other.den)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) is int or type(other) is float:
            return Real(self.value / other)
        if type(other) is Integer or type(other) is Real:
            return Real(self.value / other.value)
        if type(other) is Rational:
            return Real(self.value * other.den * other.num)
        return NotImplemented

    def __pow__(self, other, modulo=None):
        if type(other) is int or type(other) is float:
            return Real(self.value ** other)
        if type(other) is Integer or type(other) is Real:
            return Real(self.value ** other.value)
        if type(other) is Rational:
            return Real(self.value ** (other.num / other.den))
        return NotImplemented

    def __lt__(self, other):
        if type(other) is int or type(other) is float:
            return self.value < other
        if type(other) is Integer or type(other) is Real:
            return self.value < other.value
        if type(other) is Rational:
            return self.value < other.num / other.den
        return NotImplemented

    def __gt__(self, other):
        if type(other) is int or type(other) is float:
            return self.value > other
        if type(other) is Integer or type(other) is Real:
            return self.value > other.value
        if type(other) is Rational:
            return self.value > other.num / other.den
        return NotImplemented


class Complex(Atom):
    def __init__(self, real: Union[Integer, Rational, Real], imag: Union[Integer, Rational, Real]):
        super().__init__("Complex")
        self.real = real
        self.imag = imag

    def __eq__(self, other):
        return type(other) is Real and self.real == other.real and self.imag == other.imag

    def __hash__(self):
        return hash((self.head, self.real, self.imag))

    def __str__(self):
        return '{}+i{}'.format(self.real, self.imag)
