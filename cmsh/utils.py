"""
The utils module defines several helper methods for handling Vector arguments.
"""

from .var import Variable

def _from_arg_(arg, have_model=False):
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

    atype = type(arg)
    if atype == int:
        value = list(map(lambda x: bool(int(x)), bin(arg)[2:]))
        return value, None, False

    if atype == list or atype == tuple:
        model = None
        if not have_model:
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
    r_list, r_model, r_fixed = _from_arg_(right, l_model is not None)
    l_list, r_list = __validate_size__(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model
    return l_list, r_list, model
