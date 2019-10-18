"""
This module includes typing for the Model class.
"""

from typing import Iterable, List, Tuple, Union

from ._vec_typing import VariableSoft, VectorLike

from .var import Variable
from .vec import Vector

# A hard variable is different than a VariableSoft in that in can must contain
# or be a variable identifier. It is grounded in the native circuit model.
VariableHard = Union[int, Variable]

# An iterable of hard variables.
IVariableHard = Iterable[VariableHard]

# VectorIs is something that is either like a vector (i.e., can be cast to one
# via model.to_vector(...) or is an instance of the Vector class.
VectorIs = Union[VectorLike, Vector]

# A subset of Vectors that have __len__ implemented (notably, int doesn't
# implement __len__ and can't because width can be variable).
VectorSized = Union[Tuple[VariableSoft, ...], List[VariableSoft], Vector]

# An iterable of Vector instances.
IVector = Iterable[Vector]
