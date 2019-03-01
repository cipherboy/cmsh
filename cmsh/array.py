from .logic import *


def __from_arg(arg):
    # ret: [Variable:bool], model, is_fixed
    if isinstance(arg, (list, tuple)):
        return arg, None, True
    elif isinstance(arg, int):
        value = list(map(lambda x: bool(int(x)), bin(arg)[2:]))
        return value, None, False
    else:
        return arg.variables, arg.model, True


def __validate_size(left, l_fixed, right, r_fixed):
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
        l_len = r_len
    elif r_len < l_len:
        prefix = [False] * (l_len - r_len)
        prefix.extend(right)
        right = prefix
        r_len = l_len

    return left, right, l_len


def l_and(left, right):
    l_list, l_model, l_fixed = __from_arg(left)
    r_list, r_model, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model

    result = []
    for index in range(0, length):
        item = b_and(l_list[index], r_list[index])
        result.append(item)

    if model:
        return model.to_vector(result)

    return result


def l_nand(left, right):
    l_list, l_model, l_fixed = __from_arg(left)
    r_list, r_model, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model

    result = []
    for index in range(0, length):
        item = b_nand(l_list[index], r_list[index])
        result.append(item)

    if model:
        return model.to_vector(result)

    return result


def l_or(left, right):
    l_list, l_model, l_fixed = __from_arg(left)
    r_list, r_model, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model

    result = []
    for index in range(0, length):
        item = b_or(l_list[index], r_list[index])
        result.append(item)

    if model:
        return model.to_vector(result)

    return result


def l_nor(left, right):
    l_list, l_model, l_fixed = __from_arg(left)
    r_list, r_model, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model

    result = []
    for index in range(0, length):
        item = b_nor(l_list[index], r_list[index])
        result.append(item)

    if model:
        return model.to_vector(result)

    return result


def l_not(vec):
    v_list, v_model, _ = __from_arg(vec)

    result = []
    for orig in v_list:
        item = b_not(orig)
        result.append(item)

    if v_model:
        return v_model.to_vector(result)

    return result


def l_xor(left, right):
    l_list, l_model, l_fixed = __from_arg(left)
    r_list, r_model, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model

    result = []
    for index in range(0, length):
        item = b_xor(l_list[index], r_list[index])
        result.append(item)

    if model:
        return model.to_vector(result)

    return result


def l_lt(left, right):
    l_list, _, l_fixed = __from_arg(left)
    r_list, _, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)

    if length == 0:
        return True

    result = b_lt(l_list[0], r_list[0])
    and_list = True
    for index in range(1, length):
        and_list = b_and(and_list, b_eq(l_list[index-1], r_list[index-1]))
        result = b_or(result, b_and(and_list, b_lt(l_list[index], r_list[index])))

    return result


def l_le(left, right):
    return b_not(l_gt(left, right))


def l_eq(left, right):
    l_list, _, l_fixed = __from_arg(left)
    r_list, _, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)

    if length == 0:
        return True

    result = b_eq(l_list[0], r_list[0])
    for index in range(1, length):
        result = b_and(result, b_eq(l_list[index], r_list[index]))

    return result


def l_ne(left, right):
    return b_not(l_eq(left, right))


def l_gt(left, right):
    return b_not(b_or(l_lt(left, right), l_eq(left, right)))

def l_ge(left, right):
    return b_not(l_lt(left, right))
