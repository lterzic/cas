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
    "Plus":  [Attribute.COMMUTATIVE, Attribute.ASSOCIATIVE],
    "Mult":  [Attribute.COMMUTATIVE, Attribute.ASSOCIATIVE],
    "Power": [Attribute.FIXED_ARG_NUM]
})

HeadPrintFormat: Dict[Head, Callable[[list], str]] = {
    "Plus": lambda args: '+'.join(str(i) for i in args),
    "Mult": lambda args: ' '.join(str(i) for i in args),
    "Power": lambda args: '{}^{}'.format(*args),
}

HeadArgNumber: Dict[Head, int] = {
    "Power":    2
}
