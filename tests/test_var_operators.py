import pytest

from cmsh import Model
from cmsh.logic import *


def test_op_and():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = l_var & r_var
            r_answer = False & r_var

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
            assert bool(r_answer) == b_and(False, right)


def test_op_nand():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = -(l_var & r_var)
            r_answer = b_not(False & r_var)

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
            assert bool(r_answer) == b_nand(False, right)


def test_op_or():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = l_var | r_var
            r_answer = False | r_var

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
            assert bool(r_answer) == b_or(False, right)


def test_op_nor():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = -(l_var | r_var)

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


def test_op_not():
    for var in [False, True]:
        mod = Model()
        v_var = mod.var()
        neg_answer = -v_var
        pos_answer = +v_var

        if var:
            mod.add_assert(v_var)
        else:
            mod.add_assert(-v_var)

        mod.solve()
        assert bool(v_var) == var
        assert bool(neg_answer) == b_not(var)
        assert bool(pos_answer) == var


def test_op_xor():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = l_var ^ r_var
            r_answer = False ^ r_var

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
            assert bool(r_answer) == b_xor(False, right)


def test_op_lt():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = l_var < r_var

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


def test_op_le():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = l_var <= r_var

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


def test_op_eq():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = l_var == r_var

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


def test_op_ne():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = l_var != r_var

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


def test_op_gt():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = l_var > r_var

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


def test_op_ge():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            answer = l_var >= r_var

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


def test_invalid_usages():
    mod = Model()
    a = mod.var()

    with pytest.raises(TypeError):
        a & 1
    with pytest.raises(TypeError):
        a | 1
    with pytest.raises(TypeError):
        a ^ 1
    with pytest.raises(TypeError):
        1 & a
    with pytest.raises(TypeError):
        1 | a
    with pytest.raises(TypeError):
        1 ^ a
    with pytest.raises(TypeError):
        a < 1
    with pytest.raises(TypeError):
        a <= 1
    with pytest.raises(TypeError):
        a > 1
    with pytest.raises(TypeError):
        a >= 1

    b = mod.named_var("Hi")
    assert "Hi" in str(b)
