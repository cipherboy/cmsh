"""
The arith module provides implementations of various arithmetic functions.

You should likely use the operators on Vectors instead of calling these
directly.
"""


import math

from .array import _parse_args_, _from_arg_
from .var import Variable, b_and, b_or, b_xor


def full_adder(left_bit, right_bit, carry_in):
    """
    Implements a single full adder across two bits and a carry bit.

    Args:
        left_bit (bool or Variable): first bit to add.
        right_bit (bool or Variable): second bit to add.
        carry_in (bool or Variable): carry in bit.

    Returns:
        tuple (bool or Variable, bool or Variable): the output bit and the
        carry out from adding the two specified bits.
    """
    output = b_xor(b_xor(left_bit, right_bit), carry_in)
    carry_out = b_or(b_and(left_bit, right_bit), b_and(carry_in, b_or(left_bit, right_bit)))
    return output, carry_out


def ripple_carry_adder(left, right, carry=False):
    """
    Implements a ripple carry adder, returning the result and the carry bit.

    Args:
        left (iterable, int, or Vector): first value to add
        right (iterable, int, or Vector): second value to add
        carry (bool, Variable): carry in bit.

    Returns:
        tuple (list or Vector, bool or Variable): the output value and the
        carry out.
    """
    l_list, r_list, model = _parse_args_(left, right)

    result = []
    for index in range(len(l_list) - 1, -1, -1):
        new_bit, carry = full_adder(l_list[index], r_list[index], carry)
        result = [new_bit] + result

    if model:
        result = model.to_vector(result)

    return result, carry


def sum_array(vec):
    """
    Computes the sum of all the bits in the vector, i.e., the number of bits
    set to True.

    Args:
        vec (iterable, int, or Vector): the value to sum.

    Returns:
        list or Vector: the value of the sum.
    """
    v_list, v_model, _ = _from_arg_(vec)
    length = len(v_list)
    if length == 0:
        return [False]
    if length == 1:
        return vec

    result = [v_list[0]]
    prefix = []

    for index in range(1, length):
        item = v_list[index]
        if math.log(index+1, 2) % 1 == 0:
            result.insert(0, False)
            prefix.append(False)
        result, _ = ripple_carry_adder(result, prefix + [item])

    if v_model:
        result = v_model.to_vector(result)

    return result


def flatten(vec, func):
    """
    Flatten a vector by applying a two argument boolean function to the values.
    That is, result = func(vec[0], func(vec[1], ...)).

    Args:
        vec (list, int, or Vector): vector to flatten.
        func (function): function to use to flatten vec.

    Returns:
        list or Vector: result of the flattening.
    """
    v_list, _, _ = _from_arg_(vec)

    result = v_list[0]
    for item in v_list[1:]:
        result = func(result, item)

    return result


def splat(var, vec, func):
    """
    Splat a variable across all values in the vector, via application of a
    boolean function to all values.
    That is, result = [func(var, vec[0]), func(var, vec[1]), ...]

    Args:
        var (bool or Variable): variable to splat with.
        vec (list, int, or Vector): vector to splat against.
        func (function): function to splat.

    Returns:
        list or Vector: result of the splatting.
    """
    v_list, v_model, _ = _from_arg_(vec)
    if not v_model and isinstance(var, Variable):
        v_model = var.model

    result = [
        func(var, item)
        for item in v_list
    ]

    if v_model:
        result = v_model.to_vector(result)

    return result
