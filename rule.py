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
        pattern_blanks = [x for x in pattern.args if type(x) is Blank]
        pattern_args = [x for x in pattern.args if type(x) is not Blank]

        expr_unmatched = expr.args[:]

        # match every non-blank pattern arg first, then fill with blanks
        for pattern_arg in pattern_args:
            matched = False
            for expr_index in range(len(expr_unmatched)):
                matched = match_expr(expr_unmatched[expr_index], pattern_arg, blank_map)[0]
                if matched:
                    del expr_unmatched[expr_index]
                    break
            if not matched:
                return False, blank_map

        if len(expr_unmatched) == 0:
            assert len(pattern_blanks) == 0
            return True, blank_map

        # match and remove all non-empty blanks
        for pb in pattern_blanks:
            if pb.text in blank_map:
                matched = False
                for expr_index in range(len(expr_unmatched)):
                    matched = match_expr(expr_unmatched[expr_index], blank_map[pb.text], blank_map)[0]
                    if matched:
                        del expr_unmatched[expr_index]
                        break
                if not matched:
                    return False, blank_map
        pattern_blanks = [x for x in pattern_blanks if x.text not in blank_map]

        if len(pattern_blanks) == 0:
            blank_map["UNMATCHED"] = expr.copy(expr_unmatched)
            return Attribute.ASSOCIATIVE in expr.attr, blank_map

        if len(expr_unmatched) > len(pattern_blanks) and Attribute.ASSOCIATIVE not in expr.attr:
            return False, blank_map

        for i in range(len(pattern_blanks)):
            blank_map[pattern_blanks[i].text] = expr_unmatched[i]
        if len(pattern_blanks) < len(expr_unmatched):
            blank_map[pattern_blanks[-1].text] = expr.copy(expr_unmatched[len(pattern_blanks)-1:])

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
        if "UNMATCHED" in match[1]:
            unmatched = match[1]["UNMATCHED"]
            assert unmatched.head is expr.head
            rhs = expr.copy(match[1]["UNMATCHED"].args + [rhs])
        return True, rhs

    if isinstance(expr, Atom):
        return False, expr

    apply_to_args = [apply_rule(arg, rule) for arg in expr.args]
    modified = any(x[0] for x in apply_to_args)

    return modified, expr if not modified else expr.copy(list(x[1] for x in apply_to_args))
