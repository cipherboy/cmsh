"""
The logic module provides wrappers over Tseitin transforms, supporting
both bools and Variables.
"""


from .tseitin import v_and, v_nand, v_or, v_nor, v_not, v_xor


def b_and(left, right):
    """
    Computes the binary AND between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    assert isinstance(left, bool) or not isinstance(left, (list, tuple, int))
    assert isinstance(right, bool) or not isinstance(right, (list, tuple, int))

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


def b_nand(left, right):
    """
    Computes the binary NAND between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    assert isinstance(left, bool) or not isinstance(left, (list, tuple, int))
    assert isinstance(right, bool) or not isinstance(right, (list, tuple, int))

    if isinstance(left, bool) and isinstance(right, bool):
        return not (left and right)

    if isinstance(left, bool):
        if not left:
            return True
        return v_not(right)

    if isinstance(right, bool):
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
    assert isinstance(left, bool) or not isinstance(left, (list, tuple, int))
    assert isinstance(right, bool) or not isinstance(right, (list, tuple, int))

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


def b_nor(left, right):
    """
    Computes the binary NOR between left and right operands.

    Args:
        left (bool or Variable): left operand.
        right (bool or Variable): right operand.

    Returns:
        bool or Variable: the result of the operation.
    """
    assert isinstance(left, bool) or not isinstance(left, (list, tuple, int))
    assert isinstance(right, bool) or not isinstance(right, (list, tuple, int))

    if isinstance(left, bool) and isinstance(right, bool):
        return not (left or right)

    if isinstance(left, bool):
        if left:
            return False
        return v_not(right)

    if isinstance(right, bool):
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
    assert isinstance(var, bool) or not isinstance(var, (list, tuple, int))

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
    assert isinstance(left, bool) or not isinstance(left, (list, tuple, int))
    assert isinstance(right, bool) or not isinstance(right, (list, tuple, int))

    if isinstance(left, bool) and isinstance(right, bool):
        return left ^ right

    if isinstance(left, bool):
        if left:
            return v_not(right)
        return right

    if isinstance(right, bool):
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
