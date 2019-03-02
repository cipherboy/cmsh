import pytest

from cmsh import Model
from cmsh.logic import *


def test_mixed_and():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_and(l_var, right)
            r_answer = b_and(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_and(left, right)
            assert bool(r_answer) == b_and(left, right)


def test_mixed_nand():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_nand(l_var, right)
            r_answer = b_nand(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_nand(left, right)
            assert bool(r_answer) == b_nand(left, right)


def test_mixed_or():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_or(l_var, right)
            r_answer = b_or(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_or(left, right)
            assert bool(r_answer) == b_or(left, right)


def test_mixed_nor():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_nor(l_var, right)
            r_answer = b_nor(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_nor(left, right)
            assert bool(r_answer) == b_nor(left, right)


def test_mixed_xor():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_xor(l_var, right)
            r_answer = b_xor(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_xor(left, right)
            assert bool(r_answer) == b_xor(left, right)


def test_mixed_lt():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_lt(l_var, right)
            r_answer = b_lt(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_lt(left, right)
            assert bool(r_answer) == b_lt(left, right)


def test_mixed_le():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_le(l_var, right)
            r_answer = b_le(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_le(left, right)
            assert bool(r_answer) == b_le(left, right)


def test_mixed_eq():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_eq(l_var, right)
            r_answer = b_eq(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_eq(left, right)
            assert bool(r_answer) == b_eq(left, right)


def test_mixed_ne():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_ne(l_var, right)
            r_answer = b_ne(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_ne(left, right)
            assert bool(r_answer) == b_ne(left, right)


def test_mixed_gt():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_gt(l_var, r_var)
            r_answer = b_gt(l_var, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_gt(left, right)
            assert bool(r_answer) == b_gt(left, right)


def test_mixed_ge():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_ge(l_var, right)
            r_answer = b_ge(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_ge(left, right)
            assert bool(r_answer) == b_ge(left, right)
