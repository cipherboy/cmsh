import pytest

import cmsh
from cmsh.array import *
from cmsh.arith import sum_array


def test_op_add():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)
    c = mod.vector(4)

    constraint = ((a + b) == (4 + c)) & (a < 4) & (4 > b) & (c < 4) & (a != b)
    mod.add_assert(constraint)
    assert mod.solve()

    assert (int(a) + int(b)) == (4 + int(c))


def test_op_and():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    constraint = (a & b) == 2
    constraint2 = (2 & a) == 2
    constraint3 = (b & 1) == 1

    mod.add_assert(constraint & constraint2 & constraint3)
    assert mod.solve()
    assert int(a) == 2
    assert int(b) == 3


def test_op_xor():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    constraint = (a ^ b) == 3
    constraint2 = (2 ^ a) == 3
    constraint3 = (b ^ 1) == 3

    mod.add_assert(constraint & constraint2 & constraint3)
    assert mod.solve()
    assert int(a) == 1
    assert int(b) == 2


def test_op_or():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    c1 = (a | b) == 3
    c2 = (2 | a) == 2
    c3 = (b | 1) == 1
    c4 = a > b

    mod.add_assert(c1 & c2 & c3 & c4)
    assert mod.solve()
    assert int(a) == 2
    assert int(b) == 1


def test_op_bits():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)

    constraint = (a.bit_sum() <= 3) & (a.bit_odd() == b.bit_even())
    constraint2 = (a + b) >= 0
    constraint3 = a.odd() & b.even()
    mod.add_assert(constraint & constraint2)
    assert mod.solve()
    assert (int(a) + int(b)) >= 0


def test_op_flatten():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)
    c = mod.vector(4)
    d = mod.vector(4)
    e = mod.vector(4)

    constraint = (a.bit_and() & b.bit_or() & c.bit_nor() &
                  d.bit_nand() & e.bit_xor())

    mod.add_assert(constraint)
    assert mod.solve()

    assert int(a) == 0b1111
    assert int(b) >= 1
    assert int(c) != int(b)
    assert int(d) != 0b1111
    assert int(e) != 0


def test_sum_array():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()
    my_list = [False, True, a, b]

    assume = sum_array(my_list) == 3
    mod.add_assert(assume)
    assert mod.solve()
    assert bool(a) == True
    assert bool(b) == True


def test_misc():
    mod = cmsh.Model()
    a1 = mod.var()
    a2 = mod.var()
    a3 = mod.var()

    a = mod.to_vector([a1, -a2, a3])

    mod.add_assert((+a).bit_and())
    mod.add_assert(-a == 0)
    assert mod.solve()

    assert abs(a) == (int(a1), int(a2), int(a3))


def test_hashable():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)

    container = set()
    container.add(a)
    assert a in container
    assert len(container) == 1
    container.add(b)
    assert a in container
    assert b in container
    assert len(container) == 2

    for var in a.variables:
        assert str(var) in str(a)

    c = mod.to_vector(a)
    assert abs(a) == abs(c)


def test_rotations():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)
    c = mod.vector(4)
    d = mod.vector(4)

    con = True
    for left in [a, b, c, d]:
        for right in [a, b, c, d]:
            if abs(right) == abs(left):
                continue
            con = b_and(con, left.rotl() == right.rotr())
            con = b_and(con, left.rotl(amount=2) == right.rotr(amount=2))
            con = b_and(con, left.shiftl() == right.shiftr())
            con = b_and(con, left.shiftl(amount=2) == right.shiftr(amount=2))

    mod.add_assert(con)
    assert mod.solve()
    assert int(a) == 0
    assert int(b) == 0
    assert int(c) == 0
    assert int(d) == 0


def test_invalid_usages():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(8)

    with pytest.raises(TypeError):
        a + set()
    with pytest.raises(TypeError):
        set() + a
    with pytest.raises(TypeError):
        a & set()
    with pytest.raises(TypeError):
        set() & a
    with pytest.raises(TypeError):
        a ^ set()
    with pytest.raises(TypeError):
        set() ^ a
    with pytest.raises(TypeError):
        a | set()
    with pytest.raises(TypeError):
        set() | a
    with pytest.raises(TypeError):
        a < set()
    with pytest.raises(TypeError):
        set() < a
    with pytest.raises(TypeError):
        a <= set()
    with pytest.raises(TypeError):
        set() <= a
    with pytest.raises(TypeError):
        a > set()
    with pytest.raises(TypeError):
        set() > a
    with pytest.raises(TypeError):
        a >= set()
    with pytest.raises(TypeError):
        set() >= a
    with pytest.raises(TypeError):
        a == set()
    with pytest.raises(TypeError):
        set() == a
    with pytest.raises(TypeError):
        a != set()
    with pytest.raises(TypeError):
        set() != a
    with pytest.raises(ValueError):
        a < 400
    with pytest.raises(ValueError):
        a < b
    with pytest.raises(ValueError):
        b < a
    with pytest.raises(ValueError):
        l_and(1000, a)
    with pytest.raises(ValueError):
        a & 10000
    with pytest.raises(ValueError):
        cmsh.Vector(mod)
    with pytest.raises(ValueError):
        cmsh.Vector(mod, width=True, vector=True)
