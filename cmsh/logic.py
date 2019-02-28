from .tseitin import *


def b_and(left, right):
    if isinstance(left, bool) and isinstance(right, bool):
        return left and right

    if isinstance(left, bool):
        if left == False:
            return False
        return right

    if isinstance(right, bool):
        if right == False:
            return False
        return left

    return v_and(left, right)


def b_nand(left, right):
    if isinstance(left, bool) and isinstance(right, bool):
        return not (left and right)

    if isinstance(left, bool):
        if left == False:
            return True
        return v_not(right)

    if isinstance(right, bool):
        if right == False:
            return True
        return v_not(left)

    return v_nand(left, right)


def b_or(left, right):
    if isinstance(left, bool) and isinstance(right, bool):
        return left or right

    if isinstance(left, bool):
        if left == True:
            return True
        return right

    if isinstance(right, bool):
        if right == True:
            return True
        return left

    return v_or(left, right)


def b_nor(left, right):
    if isinstance(left, bool) and isinstance(right, bool):
        return not (left or right)

    if isinstance(left, bool):
        if left == True:
            return False
        return v_not(right)

    if isinstance(right, bool):
        if right == True:
            return False
        return v_not(left)

    return v_nor(left, right)


def b_not(var):
    if isinstance(var, bool):
        return not var

    return v_not(var)


def b_xor(left, right):
    if isinstance(left, bool) and isinstance(right, bool):
        return (left ^ right)

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
    return b_and(b_eq(left, False), b_eq(right, True))


def b_le(left, right):
    return b_not(b_gt(left, right))


def b_eq(left, right):
    return b_or(b_and(left, right), b_nor(left, right))


def b_ne(left, right):
    return b_not(b_eq(left, right))


def b_gt(left, right):
    return b_and(b_eq(left, True), b_eq(left, False))


def b_ge(left, right):
    return b_not(b_lt(left, right))
