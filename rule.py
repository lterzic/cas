from typing import Tuple, Dict, List, Callable
from expr import Expr
from atom import Atom, Symbol, TRUE, atomize, is_numeric
from head import Attribute, Head, HeadNumericEval, HeadIdentity
from collections import defaultdict

# assert rule sortedness
# rule base is {head: [(pattern, lambda expr: return expr)]}
GLOBAL_RULES: Dict[Head, List[Tuple[Expr, Callable[[Expr], Expr]]]] = defaultdict(list)
# GLOBAL_ASSUMPTIONS: Dict[Head, List[Expr]] = defaultdict(list)


class Rule: # todo: Change to Expr type
    def __init__(self, lhs: Expr, rhs: Expr, *conditions: List[Expr]):
        self.lhs = lhs
        self.rhs = rhs
        self.conditions = conditions

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
        return type(other) is type(self) and self.text == other.text

    def __hash__(self):
        return hash((self.head, self.text))


class BlankTyped(Atom):
    def __init__(self, text: str, head_type: Head):
        super().__init__("BlankTyped")
        assert " " not in text
        self.text = text
        self.head_type = head_type

    def __str__(self):
        return '_' + self.text + '_' + str(self.head_type)

    def __eq__(self, other):
        return type(other) is type(self) and self.text == other.text and self.head_type == other.head_type

    def __hash__(self):
        return hash((self.head, self.text, self.head_type))

    # ADD TYPED BLANKS AND THEN ADD GLOBAL RULE FOR TESTING Less[_Integer, _Integer] -> lambda return _I1 < _I2


# test_expr = kx + 7x + 2y
# test_rule = a_ x | a > 4 -> (2a)x

# define rule specificity as depth of expression
# then sort rules for every head type based on depth

# ax + by
# _t y + _w

def check_conditions(conditions: List[Expr], blank_map: Dict[str, Expr]) -> bool:
    if len(conditions) == 0:
        return True

    for cond in conditions:
        repl_cond = cond
        for blank in blank_map:
            if blank is "UNMATCHED":
                continue
            repl_cond = replace(repl_cond, Symbol(blank), blank_map[blank])[1]
        eval_cond = eval_expr(repl_cond)
        if eval_cond[1] != TRUE:
            return False

    return True


def match_expr(expr: Expr, pattern: Expr, conditions: List[Expr], blank_map: Dict[str, Expr] = {}) -> Tuple[bool, dict]:
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

            if type(pattern_arg) in (Blank, BlankTyped) and pattern_arg.text in blank_map:
                matched_value = blank_map[pattern_arg.text]

                recursive_match = match_expr(expr.args[expr_index], matched_value, conditions, blank_map)
                if not recursive_match[0]:
                    return False, blank_map
            elif type(pattern_arg) is Blank:
                blank_map[pattern_arg.text] = expr.args[expr_index]
            elif type(pattern_arg) is BlankTyped:
                if expr.args[expr_index].head == pattern_arg.head_type:
                    blank_map[pattern_arg.text] = expr.args[expr_index]
                else:
                    return False, blank_map
            else:
                recursive_match = match_expr(expr.args[expr_index], pattern_arg, conditions, blank_map)
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
        pattern_blanks = [x for x in pattern.args if type(x) in (Blank, BlankTyped)]
        pattern_args = [x for x in pattern.args if type(x) not in (Blank, BlankTyped)]

        expr_unmatched = expr.args[:]

        # match every non-blank pattern arg first, then fill with blanks
        for pattern_arg in pattern_args:
            matched = False
            for expr_index in range(len(expr_unmatched)):
                matched = match_expr(expr_unmatched[expr_index], pattern_arg, conditions, blank_map)[0]
                if matched:
                    del expr_unmatched[expr_index]
                    break
            if not matched:
                return False, blank_map

        if len(expr_unmatched) == 0:
            assert len(pattern_blanks) == 0
            return check_conditions(conditions, blank_map), blank_map

        # match and remove all non-empty blanks
        for pb in pattern_blanks:
            if pb.text in blank_map:
                matched = False
                for expr_index in range(len(expr_unmatched)):
                    matched = match_expr(expr_unmatched[expr_index], blank_map[pb.text], conditions, blank_map)[0]
                    if matched:
                        del expr_unmatched[expr_index]
                        break
                if not matched:
                    return False, blank_map
            elif type(pb) is BlankTyped:
                matched = False
                for expr_index in range(len(expr_unmatched)):
                    if expr_unmatched[expr_index].head == pb.head_type:
                        blank_map[pb.text] = expr_unmatched[expr_index]
                        del expr_unmatched[expr_index]
                        matched = True
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

    return check_conditions(conditions, blank_map), blank_map


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
    match = match_expr(expr, rule.lhs, list(*rule.conditions), blank_map={})
    if match[0]:
        rhs = rule.rhs
        for s in match[1]:
            rhs = replace(rhs, Symbol(s), match[1][s])[1]
        if "UNMATCHED" in match[1]:
            unmatched = match[1]["UNMATCHED"]
            assert unmatched.head is expr.head
            rhs = expr.copy(match[1]["UNMATCHED"].args + [rhs])
        return True, eval_expr(rhs)[1]

    if isinstance(expr, Atom):
        return False, expr

    apply_to_args = [apply_rule(arg, rule) for arg in expr.args]
    modified = any(x[0] for x in apply_to_args)

    if modified:
        return True, eval_expr(expr.copy(list(x[1] for x in apply_to_args)))[1]
    return False, expr


def eval_expr(expr: Expr) -> Tuple[bool, Expr]:
    if Attribute.UNEVALUATED in expr.attr:
        return False, expr

    eval_args = [eval_expr(arg) for arg in expr.args]
    modified = any(x[0] for x in eval_args)

    if modified:
        expr = expr.copy(eval_args)

    if Attribute.NUMERIC in expr.attr and all(is_numeric(arg) for arg in expr.args):
        expr = atomize(HeadNumericEval[expr.head](expr.args))

    while len(GLOBAL_RULES[expr.head]) > 0:
        for rule in GLOBAL_RULES[expr.head]:
            pattern_match = match_expr(expr, rule[0], [], {})   # todo: add conditional rules
            if pattern_match[0]:
                modified = True
                expr = rule[1](expr)
                break

    if len(expr.args) == 0 and Attribute.HAS_IDENTITY in expr.attr:
        return True, HeadIdentity[expr.head]

    return modified, expr
