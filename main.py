from expr import Expr
from atom import symbols
from nums import *
from rule import *

a, b, c, d = symbols("a b c d")

test_expr = Expr("A", [a, b, c, d])
x = Blank("x")
pattern = Expr("A", [a, x, d])

print(test_expr, x, pattern)
print(match_expr(test_expr, pattern))