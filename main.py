from expr import Expr
from atom import symbols
from nums import *

a = Expr("Plus", ["x", "y", "a"])
b = Expr("Plus", [3, a])
d = Expr("Plus", ["a", "x", "y", 3])
x, y = symbols("x y")

print(b, d, b == d)
print(x/2)