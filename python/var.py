"""
This module includes the Variable class, which represents a single boolean
variable in a SAT model.
"""

from typing import Optional, Union


class Variable:
    """
    The Variable class represents a single variable in the CNF model. Its
    identifier is positive when the variable represents a positive value, and
    negative when refering to its negation.
    """
    identifier: int = 0

    def __init__(self, model, identifier: int):
        self.model = model
        self.identifier = identifier

    def get_value(self) -> Optional[bool]:
        """
        Get the value of the variable: True, False, or None, and updated to
        reflect the sign of the identifier. If negative, the value is negated.
        None when the model is not solved, else a bool when the model has been
        solved.

        Returns:
            bool: value of the variable after solving.
        """
        # pylint: disable=protected-access
        return self.model._get_value_(self.identifier)

    def equals(self, other) -> bool:
        """
        Implements the behavior of __eq__(self, other); checks whether this
        variable is equal to other. Will not raise a type error.

        Note that __eq__ as implemented by this class adds a clause to the
        underlying CNF.

        Args:
            other: the object to compare with

        Returns:
            bool: whether or not this variable is equal to other
        """
        if other is None:
            return False
        if isinstance(other, bool):
            return False
        if isinstance(other, int):
            return self.identifier == other
        if isinstance(other, Variable):
            return self.identifier == other.identifier
        return False

    def not_equals(self, other) -> bool:
        """
        Implements the behavior of __ne__(self, other); checks whether this
        variable is unequal to other. Will not raise a type error.

        Note that __ne__ as implemented by this class adds a clause to the
        underlying CNF.

        Args:
            other: the object to compare with

        Returns:
            bool: whether or not this variable is unequal to other
        """
        return not self.equals(other)

    def __and__(self, other: Union[bool, 'Variable']) -> Union[bool, 'Variable']:
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __xor__(self, other: Union[bool, 'Variable']) -> Union[bool, 'Variable']:
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_xor(self, other)

    def __or__(self, other: Union[bool, 'Variable']) -> Union[bool, 'Variable']:
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __rand__(self, other: Union[bool, 'Variable']) -> Union[bool, 'Variable']:
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __rxor__(self, other: Union[bool, 'Variable']) -> Union[bool, 'Variable']:
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_xor(self, other)

    def __ror__(self, other: Union[bool, 'Variable']) -> Union[bool, 'Variable']:
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __lt__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_lt(self, other)

    def __le__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_le(self, other)

    def __eq__(self, other):
        if other is None:
            msg = "Use `is` to check None-ness of variable. Use "
            msg += "self.equals(other) to compare the values of "
            msg += "variables when you know self is not None."
            raise TypeError(msg)

        if not isinstance(other, (Variable, bool)):
            msg = f"Can't compare Variable with {type(other)}"
            raise TypeError(msg)
        return b_eq(self, other)

    def __ne__(self, other):
        if other is None:
            msg = "Use `is` to check None-ness of variable. Use "
            msg += "self.not_equals(other) to compare the values of "
            msg += "variables when you know self is not None."
            raise TypeError(msg)

        if not isinstance(other, (Variable, bool)):
            msg = f"Can't compare Variable with {type(other)}"
            raise TypeError(msg)
        return b_ne(self, other)

    def __gt__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_gt(self, other)

    def __ge__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_ge(self, other)

    def __neg__(self) -> Union[bool, 'Variable']:
        return b_not(self)

    def __pos__(self) -> Union[bool, 'Variable']:
        return self

    def __abs__(self) -> int:
        return abs(self.identifier)

    def __hash__(self) -> int:
        return self.identifier.__hash__()

    def __int__(self) -> int:
        return self.identifier

    def __str__(self) -> str:
        val = self.get_value()
        if val is None:
            return str(self.identifier)

        return str(self.get_value())

    def __bool__(self) -> bool:
        val = self.get_value()
        if val is None:
            msg = "Cannot call __bool__ before calling solve(). "
            msg += "If trying to negate a var, use -var."
            raise NotImplementedError(msg)

        return val


def b_and(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the binary AND between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    if isinstance(left, bool) and isinstance(right, bool):
        return left and right

    if isinstance(left, bool):
        if not left:
            return False
        return right

    if isinstance(right, bool):
        if not right:
            return False
        return left

    return v_and(left, right)


def b_nand(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the binary NAND between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    if isinstance(left, bool) and isinstance(right, bool):
        return not (left and right)

    if isinstance(left, bool):
        if not left:
            return True
        return b_not(right)

    if isinstance(right, bool):
        if not right:
            return True
        return b_not(left)

    return v_nand(left, right)


def b_or(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the binary OR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    if isinstance(left, bool) and isinstance(right, bool):
        return left or right

    if isinstance(left, bool):
        if left:
            return True
        return right

    if isinstance(right, bool):
        if right:
            return True
        return left

    return v_or(left, right)


def b_nor(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the binary NOR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    if isinstance(left, bool) and isinstance(right, bool):
        return not (left or right)

    if isinstance(left, bool):
        if left:
            return False
        return b_not(right)

    if isinstance(right, bool):
        if right:
            return False
        return b_not(left)

    return v_nor(left, right)


def b_not(var: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the binary negation of a variable.

    Args:
        var (bool or Variable): operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    if isinstance(var, bool):
        return not var

    return v_not(var)


def b_xor(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the binary XOR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    if isinstance(left, bool) and isinstance(right, bool):
        return left ^ right

    if isinstance(left, bool):
        if left:
            return b_not(right)
        return right

    if isinstance(right, bool):
        if right:
            return b_not(left)
        return left

    return v_xor(left, right)


def b_lt(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the less than operation between the left and right operands.
    That is, left < right <=> left == False & right == True

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_and(b_xor(left, right), right)


def b_le(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the less than or equal to operation between the left and right
    operands. That is:
    left <= right <=> (left == False & right == True) | (left == right)

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_or(b_eq(left, right), right)


def b_eq(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the equal to operation between the left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_xor(b_not(left), right)


def b_ne(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the not equal to operation between the left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_xor(left, right)


def b_gt(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the greater than operation between the left and right operands.
    That is, left > right <=> left == True & right == False

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_and(b_xor(left, right), left)


def b_ge(left: Union[bool, Variable], right: Union[bool, Variable]) -> Union[bool, Variable]:
    """
    Computes the greater than or equal to operation between the left and
    right operands. That is:
    left >= right <=> (left == True & right == False) | (left == right)

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_or(b_eq(left, right), left)

def v_and(left: Variable, right: Variable) -> Variable:
    """
    Computes the binary AND between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model
    assert mod == right.model
    return mod.add_constraint(left.identifier, 'and', right.identifier)


def v_nand(left: Variable, right: Variable) -> Variable:
    """
    Computes the binary NAND between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model
    assert mod == right.model
    return mod.add_constraint(left.identifier, 'nand', right.identifier)


def v_or(left: Variable, right: Variable) -> Variable:
    """
    Computes the binary OR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model
    assert mod == right.model
    return mod.add_constraint(left.identifier, 'or', right.identifier)


def v_nor(left: Variable, right: Variable) -> Variable:
    """
    Computes the binary NOR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model
    assert mod == right.model
    return mod.add_constraint(left.identifier, 'nor', right.identifier)


def v_not(var: Variable) -> Variable:
    """
    Computes the binary NOT operation on the operands.

    Args:
        var (Variable): operand.

    Returns:
        Variable: the result of the operation.
    """
    return var.model.neg_var(var)


def v_xor(left: Variable, right: Variable) -> Variable:
    """
    Computes the binary XOR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model
    assert mod == right.model
    return mod.add_constraint(left.identifier, 'xor', right.identifier)
