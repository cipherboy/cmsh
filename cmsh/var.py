"""
This module includes the Variable class, which represents a single boolean
variable in a SAT model.
"""

class Variable:
    """
    The Variable class represents a single variable in the CNF model. Its
    identifier is positive when the variable represents a positive value, and
    negative when refering to its negation.
    """
    identifier: int = 0
    model = None

    def __init__(self, model, identifier=None):
        if identifier:
            self.identifier = identifier
        else:
            self.identifier = model._next_var_identifier_()
        self.model = model

    def get_value(self):
        """
        Get the value of the variable: True, False, or None, and updated to
        reflect the sign of the identifier. If negative, the value is negated.
        None when the model is not solved, else a bool when the model has been
        solved.

        Returns:
            bool: value of the variable after solving.
        """
        return self.model._get_value_(self.identifier)

    def __and__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __xor__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_xor(self, other)

    def __or__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __rand__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __rxor__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_xor(self, other)

    def __ror__(self, other):
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
        if not isinstance(other, (Variable, bool)):
            msg = "Can't compare Variable with %s" % type(other)
            raise TypeError(msg)
        return b_eq(self, other)

    def __ne__(self, other):
        if not isinstance(other, (Variable, bool)):
            msg = "Can't compare Variable with %s" % type(other)
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

    def __neg__(self):
        return b_not(self)

    def __pos__(self):
        return self

    def __abs__(self):
        return abs(self.identifier)

    def __hash__(self):
        return self.identifier.__hash__()

    def __int__(self):
        return self.identifier

    def __str__(self):
        val = self.get_value()
        if val is None:
            return str(self.identifier)

        return str(self.get_value())

    def __bool__(self):
        val = self.get_value()
        if val is None:
            msg = "Cannot call __bool__ before calling solve(). "
            msg += "If trying to negate a var, use -var."
            raise NotImplementedError(msg)

        return val


def b_and(left, right):
    """
    Computes the binary AND between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    lbool = isinstance(left, bool)
    rbool = isinstance(right, bool)

    if lbool and rbool:
        return left and right

    if lbool:
        if not left:
            return False
        return right

    if rbool:
        if not right:
            return False
        return left

    return v_and(left, right)


def b_nand(left, right):
    """
    Computes the binary NAND between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    lbool = isinstance(left, bool)
    rbool = isinstance(right, bool)

    if lbool and rbool:
        return not (left and right)

    if lbool:
        if not left:
            return True
        return v_not(right)

    if rbool:
        if not right:
            return True
        return v_not(left)

    return v_nand(left, right)


def b_or(left, right):
    """
    Computes the binary OR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    lbool = isinstance(left, bool)
    rbool = isinstance(right, bool)

    if lbool and rbool:
        return left or right

    if lbool:
        if left:
            return True
        return right

    if rbool:
        if right:
            return True
        return left

    return v_or(left, right)


def b_nor(left, right):
    """
    Computes the binary NOR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    lbool = isinstance(left, bool)
    rbool = isinstance(right, bool)

    if lbool and rbool:
        return not (left or right)

    if lbool:
        if left:
            return False
        return v_not(right)

    if rbool:
        if right:
            return False
        return v_not(left)

    return v_nor(left, right)


def b_not(var):
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


def b_xor(left, right):
    """
    Computes the binary XOR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    lbool = isinstance(left, bool)
    rbool = isinstance(right, bool)

    if lbool and rbool:
        return left ^ right

    if lbool:
        if left:
            return v_not(right)
        return right

    if rbool:
        if right:
            return v_not(left)
        return left

    return v_xor(left, right)


def b_lt(left, right):
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


def b_le(left, right):
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


def b_eq(left, right):
    """
    Computes the equal to operation between the left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_xor(b_not(left), right)


def b_ne(left, right):
    """
    Computes the not equal to operation between the left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    return b_xor(left, right)


def b_gt(left, right):
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


def b_ge(left, right):
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

def v_and(left, right):
    """
    Computes the binary AND between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('and', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, new_var.identifier),
        (left.identifier, -new_var.identifier),
        (right.identifier, -new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_nand(left, right):
    """
    Computes the binary NAND between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('nand', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, new_var.identifier),
        (right.identifier, new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_or(left, right):
    """
    Computes the binary OR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('or', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (left.identifier, right.identifier, -new_var.identifier),
        (-left.identifier, new_var.identifier),
        (-right.identifier, new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_nor(left, right):
    """
    Computes the binary NOR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('nor', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (left.identifier, right.identifier, new_var.identifier),
        (-left.identifier, -new_var.identifier),
        (-right.identifier, -new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_not(var):
    """
    Computes the binary NOT operation on the operands.

    Args:
        var (Variable): operand.

    Returns:
        Variable: the result of the operation.
    """
    return var.model.neg_var(var)


def v_xor(left, right):
    """
    Computes the binary XOR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('xor', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, right.identifier, -new_var.identifier),
        (left.identifier, -right.identifier, new_var.identifier),
        (-left.identifier, right.identifier, new_var.identifier),
    ])

    mod._add_constraint_(transform, new_var)
    return new_var
