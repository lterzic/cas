from typing import Union
from atom import Atom
from math import gcd


# to int add arithmetic when other is int
class Integer(Atom):
    def __init__(self, n: int):
        super().__init__("Integer")
        assert type(n) is int
        self.n = n

    def __eq__(self, other):
        return type(other) is Integer and self.n == other.n

    def __hash__(self):
        return hash((self.head, self.n))

    def __str__(self):
        return str(self.n)

    def __add__(self, other):
        if type(other) is Integer:
            return Integer(self.n + other.n)
        return NotImplemented

    def __radd__(self, other):
        return Integer.__add__(self, other)

    def __neg__(self):
        return Integer(-self.n)

    def __sub__(self, other):
        if type(other) is Integer:
            return Integer(self.n - other.n)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is Integer:
            return Integer(self.n * other.n)
        return NotImplemented

    def __rmul__(self, other):
        return Integer.__mul__(self, other)

    def __truediv__(self, other):
        if type(other) is Integer:
            if self.n % other.n == 0:
                return Integer(self.n // other.n)
            else:
                return Rational(self, other)
        return NotImplemented

    def __pow__(self, other, modulo=None):
        if type(other) is Integer:
            if other < 0:
                return Rational(1, self.n ** -other.n)
            else:
                return Integer(self.n ** other.n)
        return NotImplemented

    def __lt__(self, other):
        if type(other) is Integer:
            return self.n < other.n
        elif type(other) is int:
            return self.n < other  # should be used only in this file for internal implementations
        return NotImplemented

    def __gt__(self, other):
        if type(other) is Integer:
            return self.n > other.n
        elif type(other) is int:
            return self.n > other  # should be used only in this file for internal implementations
        return NotImplemented


class Rational(Atom):
    def __init__(self, num: Union[int, Integer], den: Union[int, Integer]):
        super().__init__("Rational")
        self.num = num if type(num) is Integer else Integer(num)
        self.den = den if type(den) is Integer else Integer(den)

        comm_factor = gcd(self.num.n, self.den.n)
        if comm_factor != 1:
            self.num.n //= comm_factor
            self.den.n //= comm_factor

        assert self.den > 0

    def __eq__(self, other):
        return type(other) is Rational and (self.num * other.den == self.den * other.num)

    def __hash__(self):
        return hash((self.head, self.num, self.den))

    def __str__(self):
        return str(self.num) + '/' + str(self.den)

    def __add__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.den + other.num * self.den, self.den * other.den)
        elif type(other) is Integer:
            return Rational(self.num + other * self.den, self.den)
        return NotImplemented

    def __radd__(self, other):
        return Rational.__add__(self, other)

    def __neg__(self):
        return Rational(-self.num, self.den)

    def __sub__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.den - other.num * self.den, self.den * other.den)
        elif type(other) is Integer:
            return Rational(self.num - other * self.den, self.den)
        return NotImplemented

    def __mul__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.num, self.den * other.den)
        elif type(other) is Integer:
            return Rational(self.num * other, self.den)
        return NotImplemented

    def __rmul__(self, other):
        return Rational.__mul__(self, other)

    def __truediv__(self, other):
        if type(other) is Rational:
            return Rational(self.num * other.den, self.den * other.num)
        elif type(other) is Integer:
            return Rational(self.num, self.den * other)
        return NotImplemented

    def __pow__(self, other, modulo=None):
        if type(other) is Integer:
            return Rational(self.num ** other, self.den ** other)
        return NotImplemented

    def __lt__(self, other):
        if type(other) is Rational:
            return self.num * other.den < self.den * other.num
        elif type(other) is Integer:
            return self.num < self.den * other
        return NotImplemented

    def __gt__(self, other):
        if type(other) is Rational:
            return self.num * other.den > self.den * other.num
        elif type(other) is Integer:
            return self.num > self.den * other
        return NotImplemented


class Real(Atom):
    def __init__(self, r: float):
        super().__init__("Real")
        assert type(r) is float
        self.r = r

    def __eq__(self, other):
        return type(other) is Real and self.r == other.r

    def __hash__(self):
        return hash((self.head, self.r))

    def __str__(self):
        return str(self.r)


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
