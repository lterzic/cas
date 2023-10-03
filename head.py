from enum import Enum
from typing import Callable, Dict, List
from collections import defaultdict
from itertools import product

# Head: TypeAlias = str - TypeAlias python >= 3.11
Head = str # todo: Change to Expr


class Attribute(Enum):
    COMMUTATIVE = 0     # orderless
    ASSOCIATIVE = 1     # flattenable
    FIXED_ARG_NUM = 2   # arg number defined in HeadArgNumber
    NO_FLATTEN = 3      # don't flatten on create
    UNEVALUATED = 4     # don't evaluate in eval_expr
    NUMERIC = 5         # has special evaluation if all args are numeric
    HAS_IDENTITY = 6    # defined in HeadIdentity, remove arguments of this type and return this when len(args)=0


# rename global variables to all caps
HeadAttributes: Dict[Head, List[Attribute]] = defaultdict(list, {
    "Plus": [Attribute.COMMUTATIVE, Attribute.ASSOCIATIVE, Attribute.NUMERIC, Attribute.HAS_IDENTITY],
    "Mult": [Attribute.COMMUTATIVE, Attribute.ASSOCIATIVE, Attribute.NUMERIC, Attribute.HAS_IDENTITY],
    "Power": [Attribute.FIXED_ARG_NUM, Attribute.NUMERIC],
    "Neg": [Attribute.FIXED_ARG_NUM, Attribute.NUMERIC],
    "Less": [Attribute.FIXED_ARG_NUM, Attribute.NUMERIC],
    "Greater": [Attribute.FIXED_ARG_NUM, Attribute.NUMERIC]
})

# add parenthesis
HeadPrintFormat: Dict[Head, Callable[[Head, list], str]] = {
    "Plus": lambda head, args: '+'.join(str_parenth(head, args)),
    "Mult": lambda head, args: '*'.join(str_parenth(head, args)),
    "Power": lambda head, args: '{}^{}'.format(*str_parenth(head, args)),
    "Neg": lambda head, args: '-{}'.format(*str_parenth(head, args)),
    "Less": lambda head, args: '{}<{}'.format_map(*str_parenth(head, args)),
    "Greater": lambda head, args: '{}>{}'.format_map(*str_parenth(head, args))
}

HeadArgNumber: Dict[Head, int] = {
    "Power":    2,
    "Neg":      1,
    "Less":     2,
    "Greater":  2
}

HeadParenthesisPriority: Dict[Head, int] = {
    "Neg":      1,
    "Plus":     2,
    "Mult":     3,
    "Power":    4
}

HeadNumericEval: Dict[Head, Callable[[List['Expr']], 'Expr']] = {
    "Plus": lambda args: sum(args),
    "Mult": lambda args: product(args),
    "Power": lambda args: args[0] ** args[1],
    "Neg": lambda args: -args[0],
    "Less": lambda args: args[0] < args[1],
    "Greater": lambda args: args[0] > args[1]
}

HeadIdentity: Dict[Head, 'Expr'] = {
    "Plus": 0, # check if needs to be replaced with expr types
    "Mult": 1
}


def str_parenth(head: Head, args: list) -> List[str]:
    head_prio = HeadParenthesisPriority[head]
    out_args = []
    for arg in args:
        if arg.head not in HeadParenthesisPriority:
            out_args.append(str(arg))
        else:
            arg_prio = HeadParenthesisPriority[arg.head]
            out_args.append('({})'.format(str(arg)) if arg_prio < head_prio else str(arg))
    return out_args
