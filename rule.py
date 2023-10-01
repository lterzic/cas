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

        expr_index = 0
        pattern_index = 0

        while pattern_index < len(pattern.args):
            if expr_index >= len(expr.args):
                return False, blank_map

            pattern_arg = pattern.args[pattern_index]

            if type(pattern_arg) is Blank:
                if pattern_arg.text in blank_map:
                    matched_value = blank_map[pattern_arg.text]

                    recursive_match = match_expr(expr.args[expr_index], matched_value, blank_map)
                    if not recursive_match[0]:
                        return False, blank_map
                else:
                    blank_map[pattern_arg.text] = expr.args[expr_index]
            else:
                recursive_match = match_expr(expr.args[expr_index], pattern_arg, blank_map)
                if not recursive_match[0]:
                    prev_pattern_arg = pattern.args[pattern_index - 1]
                    if type(prev_pattern_arg) is Blank:
                        matched_value = blank_map[prev_pattern_arg.text]
                        if matched_value == expr.args[expr_index - 1]:
                            match_multiple = Expr(expr.head, [matched_value, expr.args[expr_index]])
                            # todo: set type of attr to Set and pass them every time when creating new Expr from old one
                            blank_map[prev_pattern_arg.text] = match_multiple # this might cause problems w
                        else:
                            assert matched_value.args[-1] == expr.args[expr_index - 1]
                            matched_value.args.append(expr.args[expr_index])
                        expr_index += 1
                        continue
                    else:
                        return False, blank_map

            expr_index += 1
            pattern_index += 1

        return True, blank_map
    else:
        pass

