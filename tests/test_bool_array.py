import pytest

from cmsh.array import *


def test_bool_and():
    left   = [False, False, True,  True]
    right  = [False, True,  False, True]
    answer = [False, False, False, True]
    assert l_and(left, right) == answer


def test_bool_nand():
    left   = [False, False, True,  True]
    right  = [False, True,  False, True]
    answer = [True,  True,  True,  False]
    assert l_nand(left, right) == answer


def test_bool_or():
    left   = [False, False, True,  True]
    right  = [False, True,  False, True]
    answer = [False, True,  True,  True]
    assert l_or(left, right) == answer


def test_bool_nor():
    left   = [False, False, True,  True]
    right  = [False, True,  False, True]
    answer = [True,  False, False, False]
    assert l_nor(left, right) == answer


def test_bool_not():
    case   = [False, True]
    answer = [True, False]
    assert l_not(case) == answer


def test_bool_xor():
    left   = [False, False, True,  True]
    right  = [False, True,  False, True]
    answer = [False, True,  True,  False]
    assert l_xor(left, right) == answer


def test_bool_lt():
    for left in range(0, 3):
        for right in range(0, 3):
            assert l_lt(left, right) == (left < right)


def test_bool_le():
    for left in range(0, 3):
        for right in range(0, 3):
            assert l_le(left, right) == (left <= right)


def test_bool_eq():
    assert l_eq([], []) == True
    for left in range(0, 3):
        for right in range(0, 3):
            assert l_eq(left, right) == (left == right)


def test_bool_ne():
    for left in range(0, 3):
        for right in range(0, 3):
            assert l_ne(left, right) == (left != right)


def test_bool_gt():
    for left in range(0, 3):
        for right in range(0, 3):
            assert l_gt(left, right) == (left > right)


def test_bool_ge():
    for left in range(0, 3):
        for right in range(0, 3):
            assert l_ge(left, right) == (left >= right)
