"""
Module which contains array based operations.
"""


from .logic import b_and, b_nand, b_or, b_nor, b_not, b_xor, b_lt, b_eq
from .var import Variable


def _from_arg_(arg):
    """
    Parses a vector argument: returns an iterable, a reference to the model if
    present, and whether or not the argument is of fixed length (i.e., is not
    a int).

    Args:
        arg (list, int, or Vector): object to parse

    Returns:
        tuple (list, model, bool): values in the list, int, or Vector, a model
        if present, and the value of whether or not the input was of fixed
        length.
    """
    # ret: [Vector/list/tuple], model, is_fixed
    if isinstance(arg, int):
        value = list(map(lambda x: bool(int(x)), bin(arg)[2:]))
        return value, None, False
    if isinstance(arg, (list, tuple)):
        model = None
        for item in arg:
            if isinstance(item, Variable):
                model = item.model
        return arg, model, True
    return arg, arg.model, True


def __validate_size__(left, l_fixed, right, r_fixed):
    """
    On two value functions, validate that the left and right values are of
    similar enough sizes. If not, and the smaller isn't of fixed size, we
    extend it to match.

    Args:
        left (list): values in the left argument.
        l_fixed (bool): whether or not the left value is fixed.
        right (list): values in the right argument.
        r_fixed (bool): whether or not the right value is fixed.

    Returns:
        tuple (list, list): values in the left and right arguments.
    """
    l_len = len(left)
    r_len = len(right)

    if l_fixed and r_fixed and l_len != r_len:
        raise ValueError("Mismatch sizes: %d vs %d" % (l_len, r_len))
    elif l_fixed and l_len < r_len:
        raise ValueError("Value of constant (%d) exceeds size: %d" % (r_len, l_len))
    elif r_fixed and r_len < l_len:
        raise ValueError("Value of constant (%d) exceeds size: %d" % (l_len, r_len))

    if l_len < r_len:
        prefix = [False] * (r_len - l_len)
        prefix.extend(left)
        left = prefix
    elif r_len < l_len:
        prefix = [False] * (l_len - r_len)
        prefix.extend(right)
        right = prefix

    return left, right


def _parse_args_(left, right):
    """
    Parse arguments to a two valued Vector function. Ensures both are of the
    same size. Returns a model if present.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        tuple (list, list, Model): values in the left and right arguments, and
        the Model, if present.
    """
    l_list, l_model, l_fixed = _from_arg_(left)
    r_list, r_model, r_fixed = _from_arg_(right)
    l_list, r_list = __validate_size__(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model
    return l_list, r_list, model


def l_and(left, right):
    """
    Compute the bitwise AND operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_and(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_nand(left, right):
    """
    Compute the bitwise NAND operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_nand(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_or(left, right):
    """
    Compute the bitwise OR operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_or(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_nor(left, right):
    """
    Compute the bitwise NOR operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_nor(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_not(vec):
    """
    Compute the negation of all items in the Vector.

    Args:
        vec (list, int, or Vector): vector to negate.

    Returns:
        list or Vector: value of the operation.
    """
    v_list, v_model, _ = _from_arg_(vec)

    result = list(map(b_not, v_list))

    if v_model:
        return v_model.to_vector(result)

    return result


def l_xor(left, right):
    """
    Compute the bitwise XOR operation between two vectors.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        list or Vector: value of the operation.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = list(map(lambda x: b_xor(x[0], x[1]), zip(l_list, r_list)))

    if model:
        return model.to_vector(result)

    return result


def l_lt(left, right):
    """
    Checks whether the left argument is less than the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    l_list, r_list, _ = _parse_args_(left, right)

    if not l_list:
        return True

    result = b_lt(l_list[0], r_list[0])
    and_list = True
    for index, (l_item, r_item) in enumerate(zip(l_list[1:], r_list[1:]), 1):
        and_list = b_and(and_list, b_eq(l_list[index-1], r_list[index-1]))
        result = b_or(result, b_and(and_list, b_lt(l_item, r_item)))

    return result


def l_le(left, right):
    """
    Checks whether the left argument is less than or equal to the right
    argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_or(l_lt(left, right), l_eq(left, right))


def l_eq(left, right):
    """
    Checks whether the left argument is equal to the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    l_list, r_list, _ = _parse_args_(left, right)

    if not l_list:
        return True

    result = b_eq(l_list[0], r_list[0])
    for l_item, r_item in zip(l_list[1:], r_list[1:]):
        result = b_and(result, b_eq(l_item, r_item))

    return result


def l_ne(left, right):
    """
    Checks whether the left argument is not equal to the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_not(l_eq(left, right))


def l_gt(left, right):
    """
    Checks whether the left argument is greater than the right argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_not(b_or(l_lt(left, right), l_eq(left, right)))


def l_ge(left, right):
    """
    Checks whether the left argument is greater than or equal to the right
    argument.

    Args:
        left (list, int, or Vector): left argument.
        right (list, int, or Vector): right argument.

    Returns:
        bool or Variable: result of the operation.
    """
    return b_or(l_gt(left, right), l_eq(left, right))
