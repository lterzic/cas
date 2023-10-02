from expr import Expr
from atom import symbols
from nums import *
from rule import *

a, b, c, d, e, x, y, _x, _y = symbols("a b c d e x y _x _y")

s1 = a ** b ** c
r1 = Rule(_x ** _y, y)
print(s1, r1)

print(apply_rule(s1, r1)[1])