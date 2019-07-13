import pytest

from cmsh.var import *


def test_bool_and():
    assert b_and(False, False) == False
    assert b_and(False, True)  == False
    assert b_and(True,  False) == False
    assert b_and(True,  True)  == True


def test_bool_or():
    assert b_or(False, False) == False
    assert b_or(False, True)  == True
    assert b_or(True,  False) == True
    assert b_or(True,  True)  == True


def test_bool_not():
    assert b_not(False) == True
    assert b_not(True)  == False


def test_bool_nand():
    assert b_nand(False, False) == True
    assert b_nand(False, True)  == True
    assert b_nand(True,  False) == True
    assert b_nand(True,  True)  == False

    for left in [False, True]:
        for right in [False, True]:
            assert b_nand(left, right) == b_not(b_and(left, right))


def test_bool_nor():
    assert b_nor(False, False) == True
    assert b_nor(False, True)  == False
    assert b_nor(True,  False) == False
    assert b_nor(True,  True)  == False

    for left in [False, True]:
        for right in [False, True]:
            assert b_nor(left, right) == b_not(b_or(left, right))


def test_bool_xor():
    assert b_xor(False, False) == False
    assert b_xor(False, True)  == True
    assert b_xor(True,  False) == True
    assert b_xor(True,  True)  == False


def test_bool_lt():
    assert b_lt(False, False) == False
    assert b_lt(False, True)  == True
    assert b_lt(True,  False) == False
    assert b_lt(True,  True)  == False


def test_bool_gt():
    assert b_gt(False, False) == False
    assert b_gt(False, True)  == False
    assert b_gt(True,  False) == True
    assert b_gt(True,  True)  == False

def test_bool_eq():
    assert b_eq(False, False) == True
    assert b_eq(False, True)  == False
    assert b_eq(True,  False) == False
    assert b_eq(True,  True)  == True


def test_bool_le():
    assert b_le(False, False) == True
    assert b_le(False, True)  == True
    assert b_le(True,  False) == False
    assert b_le(True,  True)  == True

    for left in [False, True]:
        for right in [False, True]:
            assert b_le(left, right) == b_not(b_gt(left, right))


def test_bool_ge():
    assert b_ge(False, False) == True
    assert b_ge(False, True)  == False
    assert b_ge(True,  False) == True
    assert b_ge(True,  True)  == True

    for left in [False, True]:
        for right in [False, True]:
            assert b_ge(left, right) == b_not(b_lt(left, right))

def test_bool_ne():
    assert b_ne(False, False) == False
    assert b_ne(False, True)  == True
    assert b_ne(True,  False) == True
    assert b_ne(True,  True)  == False

    for left in [False, True]:
        for right in [False, True]:
            assert b_ne(left, right) == b_not(b_eq(left, right))
