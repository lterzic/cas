from expr import Expr
from atom import symbols
from nums import *
from rule import *

# ----- TESTING ONLY -----
#GLOBAL_RULES["Inequality"].append(Rule())
# ------------------------

a, b, c, d, e, x, y, _x, _y = symbols("a b c d e x y _x _y")

s1 = a**2 + c + 2*a*b + b**2
r1 = Rule(_x**2 + 2*_x*_y + _y ** 2, (x+y)**2)
print(s1, r1)
print(apply_rule(s1, r1)[1])