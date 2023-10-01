from typing import Tuple
from expr import Expr
from atom import Atom
from head import Attribute, HeadAttributes


class Rule:
    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs
        self.rhs = rhs


class Blank(Atom):
    def __init__(self, text: str):
        super().__init__("Blank")
        assert " " not in text
        self.text = text

    def __str__(self):
        return '_' + self.text

    def __eq__(self, other):
        return type(other) is Blank and self.text == other.text

    def __hash__(self):
        return hash((self.head, self.text))


# class BlankSequence(Atom):
#     def __init__(self, text: str):
#         super().__init__("BlankSequence")
#         assert " " not in text
#         self.text = text
#
#     def __str__(self):
#         return '__' + self.text
#
#     def __eq__(self, other):
#         return type(other) is BlankSequence and self.text == other.text
#
#     def __hash__(self):
#         return hash((self.head, self.text))


class ExprCondition(Expr):
    def __init__(self):
        super().__init__("Condition")

# test_expr = kx + 7x + 2y
# test_rule = a_ x | a > 4 -> (2a)x

# define rule specificity as depth of expression
# then sort rules for every head type based on depth

# ax + by
# _t y + _w


def match_expr(expr: Expr, pattern: Expr, blank_map: dict = {}) -> Tuple[bool, dict]:
    assert isinstance(expr, Expr) and isinstance(pattern, Expr)

    if isinstance(pattern, Atom):
        return pattern == expr, blank_map

    if expr.head is not pattern.head:
        return False, blank_map

    if Attribute.COMMUTATIVE not in HeadAttributes[expr.head]:
        if len(pattern.args) > len(expr.args):
            return False, blank_map

        for i in range(len(pattern.args)):
            pattern_arg = pattern.args[i]

            if type(pattern_arg) is Blank:
                if pattern_arg.text in blank_map:
                    blank_value = blank_map[pattern_arg.text]
                    recursive_match = match_expr(expr.args[i], blank_value, blank_map)
                    if not recursive_match[0]:
                        return False, blank_map
                else:
                    blank_map[pattern_arg.text] = expr.args[i]
            else:
                recursive_match = match_expr(expr.args[i], pattern_arg, blank_map)
                if not recursive_match[0]:
                    return False, blank_map

        return True, blank_map
    else:
        pass

