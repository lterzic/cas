from typing import Tuple
from expr import Expr
from atom import Atom, Symbol
from head import Attribute


class Rule:
    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return str(self.lhs) + '->' + str(self.rhs)


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

    if len(pattern.args) > len(expr.args):
        return False, blank_map

    if Attribute.COMMUTATIVE not in expr.attr:
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
                    if Attribute.ASSOCIATIVE in expr.attr and type(prev_pattern_arg) is Blank:
                        matched_value = blank_map[prev_pattern_arg.text]
                        if matched_value != expr.head:
                            match_multiple = expr.copy([matched_value, expr.args[expr_index]])
                            blank_map[prev_pattern_arg.text] = match_multiple  # check for coherence problems
                        else:
                            assert matched_value.args[-1] == expr.args[expr_index - 1]
                            matched_value.args.append(expr.args[expr_index])
                        expr_index += 1
                        continue
                    else:
                        return False, blank_map

            expr_index += 1
            pattern_index += 1
    else:
        non_blanks = [x for x in pattern.args if type(x) is not Blank]
        non_blanks.sort(key=lambda x: hash(x))

        blanks = [x for x in pattern.args if type(x) is Blank]
        last_blank = None

        nb_index = 0
        # assuming same order of elements due to sort
        for expr_arg in expr.args:
            if nb_index < len(non_blanks):
                match = match_expr(expr_arg, non_blanks[nb_index], blank_map)
                if match[0]:
                    nb_index += 1
                    continue
            if nb_index >= len(non_blanks) or not match[0]:
                if len(blanks) == 0:
                    if Attribute.ASSOCIATIVE in expr.attr and type(last_blank) is Blank:
                        matched_value = blank_map[last_blank.text]
                        if matched_value.head != expr.head:
                            match_multiple = expr.copy([matched_value, expr_arg])
                            blank_map[last_blank.text] = match_multiple  # check for coherence problems
                        else:
                            matched_value.args.append(expr_arg)
                    else:
                        return False, blank_map
                else:
                    blank_map[blanks[0].text] = expr_arg
                    last_blank = blanks[0]
                    del blanks[0]

    return True, blank_map


def replace(expr: Expr, to_replace: Expr, replace_with: Expr) -> Tuple[bool, Expr]:
    if expr == to_replace:
        return True, replace_with

    replace_args = [replace(arg, to_replace, replace_with) for arg in expr.args]
    modified = any(x[0] for x in replace_args)

    new_expr = expr if not modified else expr.copy(list(x[1] for x in replace_args))
    if new_expr == to_replace:
        return True, replace_with

    return modified, new_expr


def apply_rule(expr: Expr, rule: Rule) -> Tuple[bool, Expr]:
    match = match_expr(expr, rule.lhs, blank_map={})
    if match[0]:
        rhs = rule.rhs
        for s in match[1]:
            rhs = replace(rhs, Symbol(s), match[1][s])[1]
        return True, rhs

    if isinstance(expr, Atom):
        return False, expr

    apply_to_args = [apply_rule(arg, rule) for arg in expr.args]
    modified = any(x[0] for x in apply_to_args)

    return modified, expr if not modified else expr.copy(list(x[1] for x in apply_to_args))
