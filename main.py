from expr import Expr
from atom import symbols
from nums import *
from rule import *

a, b, c, d, e = symbols("a b c d e")

test_expr = Expr("A", [a, b, c, d, e], [Attribute.ASSOCIATIVE, Attribute.COMMUTATIVE])
x = Blank("x")
y = Blank("y")
pattern = Expr("A", [x, b, e])

print(test_expr, x, pattern)
match = match_expr(test_expr, pattern)
print(match[0])
for key in match[1]:
    print(key, match[1][key])