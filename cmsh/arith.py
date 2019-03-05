from .logic import *
from .array import __from_arg, __validate_size
from .var import Variable

import math


def full_adder(x, y, c):
    output = b_xor(b_xor(x, y), c)
    carry = b_or(b_and(x, y), b_and(c, b_or(x, y)))
    return output, carry


def ripple_carry_adder(left, right, carry=False):
    l_list, l_model, l_fixed = __from_arg(left)
    r_list, r_model, r_fixed = __from_arg(right)
    l_list, r_list, length = __validate_size(l_list, l_fixed, r_list, r_fixed)
    model = l_model or r_model

    result = []
    for index in range(length -1, -1, -1):
        new_bit, carry = full_adder(l_list[index], r_list[index], carry)
        result = [new_bit] + result

    if model:
        result = model.to_vector(result)

    return result, carry


def sum_array(vec):
    v_list, v_model, _ = __from_arg(vec)
    length = len(v_list)
    if length == 0:
        return [False]
    elif length == 1:
        return vec

    result = [v_list[0]]

    for index in range(1, length):
        item = v_list[index]
        if math.log(index+1, 2) % 1 == 0:
            result.insert(0, False)
        prefix = [False] * (len(result) - 1)
        result, _ = ripple_carry_adder(result, prefix + [item])

    if v_model:
        result = v_model.to_vector(result)

    return result


def flatten(vec, func):
    v_list, v_model, _ = __from_arg(vec)

    result = v_list[0]
    for item in v_list[1:]:
        result = func(result, item)

    return result
