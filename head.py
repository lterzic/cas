from enum import Enum
from typing import Callable, Dict, List
from collections import defaultdict

# Head: TypeAlias = str - TypeAlias python >= 3.11
Head = str


class Attribute(Enum):
    COMMUTATIVE = 0     # orderless
    ASSOCIATIVE = 1     # flattenable
    FIXED_ARG_NUM = 2   # arg number defined in HeadArgNumber
    NO_FLATTEN = 3      # don't flatten on create
    UNEVALUATED = 4     # don't evaluate on create


# rename global variables to all caps
HeadAttributes: Dict[Head, List[Attribute]] = defaultdict(list, {
    "Plus": [Attribute.COMMUTATIVE, Attribute.ASSOCIATIVE],
    "Mult": [Attribute.COMMUTATIVE, Attribute.ASSOCIATIVE],
    "Power": [Attribute.FIXED_ARG_NUM],
    "Neg": [Attribute.FIXED_ARG_NUM]
})

# add parenthesis
HeadPrintFormat: Dict[Head, Callable[[Head, list], str]] = {
    "Plus": lambda head, args: '+'.join(str_parenth(head, args)),
    "Mult": lambda head, args: '*'.join(str_parenth(head, args)),
    "Power": lambda head, args: '{}^{}'.format(*str_parenth(head, args)),
    "Neg": lambda head, args: '-{}'.format(*str_parenth(head, args))
}

HeadArgNumber: Dict[Head, int] = {
    "Power":    2,
    "Neg":      1
}

HeadParenthesisPriority: Dict[Head, int] = {
    "Neg":      1,
    "Plus":     2,
    "Mult":     3,
    "Power":    4
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
