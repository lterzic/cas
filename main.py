from expr import Expr
from atom import symbols
from nums import *
from rule import *

a, b, c, d, e = symbols("a b c d e")
x = Blank("x")
y = Blank("y")

s1 = a + b * (c ** d * e ** a * b)
r1 = Rule(x ** y, 3 * x)
print(s1, r1)

print(apply_rule(s1, r1))