from expr import Expr
from atom import symbols
from nums import *
from rule import *

a, b, c, d, e, x, y, _x, _y = symbols("a b c d e x y _x _y")

expr1 = a + b + c + b + d - b + c - c - b
expr2 = (a*b)**c

add_simp = Rule(_x - _x + _y, y)

print(expr1, expr2)
print(add_simp)

res = apply_rule(expr1, add_simp)
while res[0]:
    print(res[1])
    res = apply_rule(res[1], add_simp)