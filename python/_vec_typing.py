"""
This module includes typing for the Vector class.
"""

from typing import Iterable, List, Tuple, Union

from .var import Variable

# VariableLike is a any class which can be coerced to a Variable
VariableLike = Union[bool, int]

# VariableIs is a class which can either be coerced to a Variable or is a
# Variable.
VariableIs = Union[VariableLike, Variable]

# A "soft" Variable is either a boolean (a value for the variable) or an
# instance of the Variable class. int's (which are variable identifiers),
# but lack references to the model, can't be coerced to model in some
# instances.
VariableSoft = Union[bool, Variable]

# An iterable of things which are Variables or are variable-like.
IVariableIs = Iterable[VariableIs]

# VectorLike items are things which aren't quite Vectors but can be cast
# to a Vector.
VectorLike = Union[Tuple[VariableSoft, ...], List[VariableSoft], int]
