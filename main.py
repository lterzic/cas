from expr import Expr
from atom import symbols
from nums import *
from rule import *

a, b, c, d, e, x, y, _x, _y = symbols("a b c d e x y _x _y")

s = a > b
r1 = Rule(a, atomize(2))
r2 = Rule(b, atomize(-3))
s = apply_rule(s, r1)[1]
s = apply_rule(s, r2)[1]
print(s)