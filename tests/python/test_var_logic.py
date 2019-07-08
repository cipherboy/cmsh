import pytest

from cmsh import Model
from cmsh.var import *


def test_var_and():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_and(l_var, r_var)

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
            assert bool(answer) == b_and(left, right)


def test_var_nand():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_nand(l_var, r_var)

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
            assert bool(answer) == b_nand(left, right)


def test_var_or():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_or(l_var, r_var)

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
            assert bool(answer) == b_or(left, right)


def test_var_nor():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_nor(l_var, r_var)

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
            assert bool(answer) == b_nor(left, right)


def test_var_not():
    for var in [False, True]:
        mod = Model()
        v_var = mod.var()
        answer = b_not(v_var)

        if var:
            mod.add_assert(v_var)
        else:
            mod.add_assert(-v_var)

        mod.solve()
        assert bool(v_var) == var
        assert bool(answer) == b_not(var)


def test_var_xor():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_xor(l_var, r_var)

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
            assert bool(answer) == b_xor(left, right)


def test_var_lt():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_lt(l_var, r_var)

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
            assert bool(answer) == b_lt(left, right)


def test_var_le():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_le(l_var, r_var)

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
            assert bool(answer) == b_le(left, right)


def test_var_eq():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_eq(l_var, r_var)

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
            assert bool(answer) == b_eq(left, right)


def test_var_ne():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_ne(l_var, r_var)

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
            assert bool(answer) == b_ne(left, right)


def test_var_gt():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_gt(l_var, r_var)

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
            assert bool(answer) == b_gt(left, right)


def test_var_ge():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = b_ge(l_var, r_var)

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
            assert bool(answer) == b_ge(left, right)
